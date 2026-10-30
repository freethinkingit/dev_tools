#!/usr/bin/env bash
#
# Drives ReviewBench's own runner and judge for the Makefile beside it.
#
#   run.sh check-tools
#   run.sh setup
#   run.sh run <pr|test|full> <command> [<pr index>]
#   run.sh run prs <command> <pr index>...
#   run.sh collect <command> <run folder>...
#   run.sh judge <run folder> <command>
#   run.sh record <run folder> <command>
#
# <command> is the make command that called it, appended to the run folder's
# run.json. collect copies the listed run folders' findings into one new run
# folder for a single judge. Reads REVIEWBENCH_COMMIT, IMAGE, JUDGE_MODEL and JUDGE_BASE_URL from the
# environment, which the Makefile sets. Runs by hand only, never in CI: every
# run and judge is a real model call.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
clone="$here/.reviewbench"
plugin_manifest="$root/plugins/ponderly/.claude-plugin/plugin.json"
reviewbench_url="https://github.com/review-bench/ReviewBench"

usage() { sed -n '5,11p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }

check_tools() {
  local tool
  for tool in docker node jq; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      echo "missing: $tool is not on PATH" >&2; exit 1
    fi
  done
  if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]; then
    echo "missing: neither ANTHROPIC_API_KEY nor CLAUDE_CODE_OAUTH_TOKEN is set" >&2; exit 1
  fi
}

setup() {
  : "${REVIEWBENCH_COMMIT:?REVIEWBENCH_COMMIT is not set}"
  if [ ! -d "$clone/.git" ]; then
    git clone -q "$reviewbench_url" "$clone"
  fi
  if ! git -C "$clone" cat-file -e "$REVIEWBENCH_COMMIT^{commit}" 2>/dev/null; then
    git -C "$clone" fetch -q origin
  fi
  git -C "$clone" checkout -q --detach "$REVIEWBENCH_COMMIT"
  (cd "$clone" && npm ci --no-audit --no-fund)
}

append_command() {
  local run_dir="$1" command="$2"
  local record="$run_dir/run.json"
  if [ ! -f "$record" ]; then
    echo "no run.json in $run_dir; pass RUN=<run folder> as make pr, test-set or full-set printed it" >&2; exit 1
  fi
  jq --arg command "$command" '.commands += [$command]' "$record" > "$record.tmp"
  mv "$record.tmp" "$record"
}

# try-agent.sh writes findings/ under its working directory, so it runs from the run folder.
try_agent() {
  local run_dir="$1"; shift
  (
    cd "$run_dir"
    TRY_AGENT_WORK="${TRY_AGENT_WORK:-$clone/.try-agent}" \
      "$clone/scripts/try-agent.sh" "$IMAGE" "$@" \
      -e ANTHROPIC_API_KEY -e CLAUDE_CODE_OAUTH_TOKEN -e RB_CONFIG_MODEL -e RB_CONFIG_EFFORT -e RB_CONFIG_BUDGET_USD
  ) 2>&1 | tee -a "$run_dir/logs/try-agent.log"
}

run_set() {
  local set_kind="$1" command="$2"; shift 2
  : "${IMAGE:?IMAGE is not set}"
  local set_label pr_index
  case "$set_kind" in
    pr)
      [ $# -le 1 ] || usage
      pr_index="${1:-}"
      case "$pr_index" in
        '' | *[!0-9]*) echo "PR must be a pull request index such as 0, not '$pr_index'" >&2; exit 2 ;;
      esac
      set_label="pr$pr_index" ;;
    prs)
      [ $# -ge 1 ] || { echo "PRS must list pull request indices such as 0 1 2" >&2; exit 2; }
      for pr_index in "$@"; do
        case "$pr_index" in
          '' | *[!0-9]*) echo "PRS must list pull request indices such as 0 1 2, not '$pr_index'" >&2; exit 2 ;;
        esac
      done
      set_label="prs$1-${!#}" ;;
    test | full) [ $# -eq 0 ] || usage; set_label="$set_kind" ;;
    *) usage ;;
  esac

  # Recorded and passed through by name, so run.json names what the adapter used.
  export RB_CONFIG_MODEL="${RB_CONFIG_MODEL:-opus}"
  export RB_CONFIG_EFFORT="${RB_CONFIG_EFFORT:-high}"
  export RB_CONFIG_BUDGET_USD="${RB_CONFIG_BUDGET_USD:-15}"

  local run_dir="$here/runs/$(date +%Y-%m-%dT%H-%M-%S)-$set_label"
  mkdir -p "$run_dir/findings" "$run_dir/scoring" "$run_dir/logs"
  jq -n \
    --arg set "$set_label" \
    --arg model "$RB_CONFIG_MODEL" \
    --arg effort "$RB_CONFIG_EFFORT" \
    --arg budget_usd "$RB_CONFIG_BUDGET_USD" \
    --arg image "$IMAGE" \
    --arg plugin_version "$(jq -r .version "$plugin_manifest")" \
    --arg started "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg command "$command" \
    '{set: $set, model: $model, effort: $effort, budget_usd: ($budget_usd | tonumber? // $budget_usd), image: $image,
      plugin_version: $plugin_version, started: $started, commands: [$command],
      judge_model: null, judge_base_url: null}' > "$run_dir/run.json"
  if [ "$set_kind" = prs ]; then
    jq '.prs = ($ARGS.positional | map(tonumber))' "$run_dir/run.json" --args "$@" > "$run_dir/run.json.tmp"
    mv "$run_dir/run.json.tmp" "$run_dir/run.json"
  fi
  echo "run folder: $run_dir" >&2

  # One failed pull request in a prs list does not stop the rest; the status reports it at the end.
  local status=0
  case "$set_kind" in
    pr) try_agent "$run_dir" --set test --pr "$pr_index" || status=$? ;;
    prs)
      for pr_index in "$@"; do
        try_agent "$run_dir" --set test --pr "$pr_index" || status=$?
      done ;;
    *) try_agent "$run_dir" --set "$set_kind" || status=$? ;;
  esac
  echo "run folder: $run_dir" >&2
  return "$status"
}

collect() {
  local command="$1"; shift
  local first="$1" source_dir earlier finding name
  local shared_fields='{model, effort, budget_usd, image, plugin_version}'
  for source_dir in "$@"; do
    if [ ! -f "$source_dir/run.json" ]; then
      echo "no run.json in $source_dir; RUNS lists run folders as make pr, prs, test-set or full-set printed them" >&2; exit 1
    fi
    if [ "$(jq -c "$shared_fields" "$source_dir/run.json")" != "$(jq -c "$shared_fields" "$first/run.json")" ]; then
      echo "$source_dir and $first ran differently, so their findings cannot be judged as one run:" >&2
      echo "  $source_dir: $(jq -c "$shared_fields" "$source_dir/run.json")" >&2
      echo "  $first: $(jq -c "$shared_fields" "$first/run.json")" >&2
      exit 1
    fi
  done

  local checked=()
  for source_dir in "$@"; do
    for finding in "$source_dir"/findings/*.json; do
      [ -e "$finding" ] || continue
      name="$(basename "$finding")"
      for earlier in ${checked[@]+"${checked[@]}"}; do
        if [ -e "$earlier/findings/$name" ]; then
          echo "pull request ${name%.json} has findings in both $earlier and $source_dir" >&2; exit 1
        fi
      done
    done
    checked+=("$source_dir")
  done

  local run_dir="$here/runs/$(date +%Y-%m-%dT%H-%M-%S)-collected"
  mkdir -p "$run_dir/findings" "$run_dir/scoring" "$run_dir/logs"
  for source_dir in "$@"; do
    for finding in "$source_dir"/findings/*.json; do
      [ -e "$finding" ] || continue
      cp "$finding" "$run_dir/findings/"
    done
  done
  local records=()
  for source_dir in "$@"; do
    records+=("$source_dir/run.json")
  done
  jq -s \
    --arg started "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg command "$command" \
    '{set: "collected", model: .[0].model, effort: .[0].effort, budget_usd: .[0].budget_usd, image: .[0].image,
      plugin_version: .[0].plugin_version, started: $started, commands: ([.[].commands[]] + [$command]),
      sources: $ARGS.positional, judge_model: null, judge_base_url: null}' \
    "${records[@]}" --args "$@" > "$run_dir/run.json"
  echo "run folder: $run_dir" >&2
}

judge() {
  local run_dir="$1" command="$2"
  : "${JUDGE_MODEL:?JUDGE_MODEL is not set}"
  : "${JUDGE_BASE_URL:?JUDGE_BASE_URL is not set}"
  run_dir="$(cd "$run_dir" && pwd)"
  append_command "$run_dir" "$command"
  local record="$run_dir/run.json"
  jq --arg judge_model "$JUDGE_MODEL" --arg judge_base_url "$JUDGE_BASE_URL" \
    '.judge_model = $judge_model | .judge_base_url = $judge_base_url' "$record" > "$record.tmp"
  mv "$record.tmp" "$record"

  # pi's bundled registry may not list the judge model yet, so it is declared here,
  # as ReviewBench's docs/OFFLINE_EVAL.md does; the clone's .gitignore covers .judge/.
  # forceAdaptiveThinking makes pi send the adaptive thinking form: on an API key the
  # API refuses the older budget form for this model, and the judge gets an empty reply.
  local judge_config="$clone/.judge"
  mkdir -p "$judge_config"
  jq -n --arg model "$JUDGE_MODEL" --arg base_url "$JUDGE_BASE_URL" \
    '{providers: {anthropic: {baseUrl: $base_url, apiKey: "ANTHROPIC_API_KEY",
      models: [{id: $model, reasoning: true, contextWindow: 1000000, maxTokens: 64000,
                compat: {forceAdaptiveThinking: true}}]}}}' \
    > "$judge_config/models.json"
  (cd "$clone" && PI_CODING_AGENT_DIR="$judge_config" npm run judge -- \
    --candidate "$run_dir/findings" \
    --provider anthropic \
    --model "$JUDGE_MODEL" \
    --output "$run_dir/scoring/results.json")
}

[ $# -ge 1 ] || usage
action="$1"; shift
case "$action" in
  check-tools) check_tools ;;
  setup) setup ;;
  run) [ $# -ge 2 ] || usage; run_set "$@" ;;
  collect) [ $# -ge 2 ] || usage; collect "$@" ;;
  judge) [ $# -eq 2 ] || usage; judge "$@" ;;
  record) [ $# -eq 2 ] || usage; append_command "$(cd "$1" && pwd)" "$2" ;;
  *) usage ;;
esac
