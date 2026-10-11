#!/bin/sh
# SessionStart hook: prints the handbook rules so Claude Code adds them to the
# session context. Claude Code does not load CLAUDE.md or rules/ from a plugin
# on its own, so this script concatenates every file under rules/ instead.
# Keep the total under 10,000 characters; Claude Code truncates hook output past that.
set -eu

root="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
dir="$root/rules"
[ -d "$dir" ] || exit 0

printf '# Handbook rules\n\n'
printf 'Team rules that apply in every repository. They are shipped by the handbook plugin; to change one, open a PR against the rules/ folder of the handbook repository.\n\n'

for f in "$dir"/*.md; do
  [ -f "$f" ] || continue
  cat "$f"
  printf '\n'
done
