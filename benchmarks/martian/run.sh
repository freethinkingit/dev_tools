#!/usr/bin/env bash
#
# Runs the review image on the Martian pull requests in prs.json, one fresh
# container per pull request, with the mounts and variables of ReviewBench's
# agent contract, into a new run folder.
#
#   ./run.sh <image> [<index>]
#
# <index> runs only that entry of prs.json, counting from 0. The run folder is
# runs/<timestamp>/ beside this script: run.json, findings/<key>.json and
# logs/run.log; repository caches go to work/. ANTHROPIC_API_KEY,
# RB_CONFIG_MODEL, RB_CONFIG_EFFORT and RB_CONFIG_BUDGET_USD are passed
# through to the container by name. A pull request whose base or head cannot
# be fetched, or whose container fails, is logged and skipped; the script
# exits 1 only when no findings file was written.
#
# Needs docker, git and jq.
set -euo pipefail

usage() { sed -n '7,15p' "$0" | sed 's/^# \{0,1\}//' >&2; exit 2; }
[ $# -ge 1 ] && [ $# -le 2 ] || usage
image="$1"
only="${2:-}"

here="$(cd "$(dirname "$0")" && pwd)"
prs="$here/prs.json"
plugin_json="$here/../../plugins/ponderly/.claude-plugin/plugin.json"
[ -f "$prs" ] || { echo "$prs not found; run the prs target first" >&2; exit 1; }

run_dir="$here/runs/$(date +%Y-%m-%dT%H-%M-%S)"
work="$here/work"
mkdir -p "$run_dir/findings" "$run_dir/logs" "$work/repos"
exec > >(tee -a "$run_dir/logs/run.log") 2>&1

command="make run IMAGE=$image"
[ -z "$only" ] || command="$command ONLY=$only"
jq -n \
  --arg model "${RB_CONFIG_MODEL:-opus}" \
  --arg effort "${RB_CONFIG_EFFORT:-high}" \
  --arg budget_usd "${RB_CONFIG_BUDGET_USD:-15}" \
  --arg image "$image" \
  --arg plugin_version "$(jq -r .version "$plugin_json")" \
  --arg started "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg command "$command" \
  '{model: $model, effort: $effort, budget_usd: ($budget_usd | tonumber? // $budget_usd), image: $image,
    plugin_version: $plugin_version, started: $started, commands: [$command],
    judge_model: null, judge_base_url: null}' > "$run_dir/run.json"

has_commits() {
  local dir="$1"; shift
  local sha
  for sha in "$@"; do
    GIT_NO_LAZY_FETCH=1 git -C "$dir" cat-file -e "$sha^{commit}" 2>/dev/null || return 1
  done
}

count=$(jq length "$prs")
indices=$(if [ -n "$only" ]; then echo "$only"; else seq 0 $((count - 1)); fi)
passed=0; failed=0

for i in $indices; do
  entry=$(jq -c ".[$i]" "$prs")
  nwo=$(jq -r .nwo <<<"$entry"); pr=$(jq -r .pr_number <<<"$entry")
  base=$(jq -r .base <<<"$entry"); head=$(jq -r .head <<<"$entry")
  key="${nwo/\//_}_${pr}-${head:0:8}"
  repo="$work/repos/${nwo/\//_}"
  echo "== [$i] $nwo#$pr ($key)"

  if [ ! -d "$repo/.git" ]; then
    git init -q "$repo"
    git -C "$repo" remote add upstream "https://github.com/$nwo.git"
  fi
  if ! has_commits "$repo" "$base" "$head"; then
    GIT_LFS_SKIP_SMUDGE=1 git -C "$repo" fetch -q --filter=blob:none upstream "$base" "pull/$pr/head" 2>/dev/null \
      || GIT_LFS_SKIP_SMUDGE=1 git -C "$repo" fetch -q --filter=blob:none upstream "$base" "$head" 2>/dev/null || true
  fi
  if ! has_commits "$repo" "$base" "$head"; then
    echo "   SKIP: could not fetch base $base and head $head from $nwo"; failed=$((failed + 1)); continue
  fi
  GIT_LFS_SKIP_SMUDGE=1 git -C "$repo" checkout -q --force --detach "$head"
  git -C "$repo" clean -qfdx

  pr_dir="$work/pr/$key"; out="$work/out/$key"
  rm -rf "$pr_dir" "$out"; mkdir -p "$pr_dir" "$out"
  git -C "$repo" diff "$base...$head" > "$pr_dir/diff.patch"
  jq '{repo: ("https://github.com/" + .nwo), pr_number, base, head, nwo, title, body}' <<<"$entry" > "$pr_dir/pr.json"

  status=0
  docker run --rm --platform linux/amd64 \
    -v "$repo:/work/repo" -v "$pr_dir:/work/pr:ro" -v "$out:/work/out" \
    -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0='*' \
    -e RB_NWO="$nwo" -e RB_PR_NUMBER="$pr" -e RB_BASE="$base" -e RB_HEAD="$head" \
    -e RB_AGENT=ponderly -e RB_REPO=/work/repo \
    -e RB_DIFF=/work/pr/diff.patch -e RB_PR_JSON=/work/pr/pr.json -e RB_OUT=/work/out/findings.json \
    -e RB_ATTEMPT=1 \
    -e ANTHROPIC_API_KEY -e RB_CONFIG_MODEL -e RB_CONFIG_EFFORT -e RB_CONFIG_BUDGET_USD \
    "$image" || status=$?

  file="$out/findings.json"
  if [ "$status" -ne 0 ]; then
    echo "   FAIL: exit code $status"; failed=$((failed + 1)); continue
  fi
  if ! jq -e . "$file" >/dev/null 2>&1; then
    echo "   FAIL: no valid JSON at RB_OUT"; failed=$((failed + 1)); continue
  fi
  cp "$file" "$run_dir/findings/$key.json"
  echo "   ok: $(jq '.findings | length' "$file") finding(s)"
  passed=$((passed + 1))
done

echo "passed $passed, skipped or failed $failed; run folder ${run_dir#"$here"/}"
[ "$passed" -gt 0 ]
