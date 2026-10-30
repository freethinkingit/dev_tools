#!/usr/bin/env bash
#
# Drives ReviewBench's own runner and judge for the Makefile beside it.
#
#   run.sh check-tools
#   run.sh setup
#   run.sh run <pr|test|full> <command> [<pr index>]
#   run.sh judge <run folder> <command>
#   run.sh record <run folder> <command>
#
# <command> is the make command that called it, appended to the run folder's
# run.json. Reads REVIEWBENCH_COMMIT, IMAGE, JUDGE_MODEL and JUDGE_BASE_URL from the
# environment, which the Makefile sets. Runs by hand only, never in CI: every
# run and judge is a real model call.
set -euo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
root="$(cd "$here/../.." && pwd)"
clone="$here/.reviewbench"
plugin_manifest="$root/plugins/ponderly/.claude-plugin/plugin.json"
reviewbench_url="https://github.com/review-bench/ReviewBench"

usage() { sed -n '5,9p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }

check_tools() {
  local tool
  for tool in docker node jq; do
    if ! command -v "$tool" >/dev/null 2>&1; then
      echo "missing: $tool is not on PATH" >&2; exit 1
    fi
  done
  if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "missing: ANTHROPIC_API_KEY is not set" >&2; exit 1
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

run_set() {
  local set_kind="$1" command="$2" pr_index="${3:-}"
  : "${IMAGE:?IMAGE is not set}"
  local set_label runner_args
  case "$set_kind" in
    pr)
      case "$pr_index" in
        '' | *[!0-9]*) echo "PR must be a pull request index such as 0, not '$pr_index'" >&2; exit 2 ;;
      esac
      set_label="pr$pr_index"; runner_args=(--set test --pr "$pr_index") ;;
    test | full) set_label="$set_kind"; runner_args=(--set "$set_kind") ;;
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
  echo "run folder: $run_dir" >&2

  # try-agent.sh writes findings/ under its working directory, so it runs from the run folder.
  local status=0
  (
    cd "$run_dir"
    TRY_AGENT_WORK="${TRY_AGENT_WORK:-$clone/.try-agent}" \
      "$clone/scripts/try-agent.sh" "$IMAGE" "${runner_args[@]}" \
      -e ANTHROPIC_API_KEY -e RB_CONFIG_MODEL -e RB_CONFIG_EFFORT -e RB_CONFIG_BUDGET_USD
  ) 2>&1 | tee "$run_dir/logs/try-agent.log" || status=$?
  echo "run folder: $run_dir" >&2
  return "$status"
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
  local judge_config="$clone/.judge"
  mkdir -p "$judge_config"
  jq -n --arg model "$JUDGE_MODEL" --arg base_url "$JUDGE_BASE_URL" \
    '{providers: {anthropic: {baseUrl: $base_url, apiKey: "ANTHROPIC_API_KEY",
      models: [{id: $model, reasoning: true, contextWindow: 1000000, maxTokens: 64000}]}}}' \
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
  judge) [ $# -eq 2 ] || usage; judge "$@" ;;
  record) [ $# -eq 2 ] || usage; append_command "$(cd "$1" && pwd)" "$2" ;;
  *) usage ;;
esac
