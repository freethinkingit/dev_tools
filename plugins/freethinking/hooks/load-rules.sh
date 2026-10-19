#!/bin/sh
# SessionStart hook: prints the handbook rules so Claude Code adds them to the
# session context. Claude Code does not load CLAUDE.md or rules/ from a plugin
# on its own, so this script prints every file under rules/ instead.
# Keep the total under 10,000 characters; Claude Code truncates hook output past that.
#
# The plugin directory's validator only accepts a hook script that writes every
# path in full from CLAUDE_PLUGIN_ROOT, uses no other variable, no command
# substitution and calls no other file in the plugin. So the rule files are
# printed by one awk program, and load-rules-subagent.sh, the SubagentStart
# hook, writes the same header and text itself. checks/test_hook_encoder.py
# pins the same header in its HEADER constant, so a header change touches the
# three together. With no .md file under rules/ the glob stays unexpanded, so
# ls fails and only the header is printed.
set -eu

[ -d "${CLAUDE_PLUGIN_ROOT:-}/rules" ] || exit 0

printf '# Handbook rules\n\n'
printf 'Team rules that apply in every repository. They are shipped by the handbook plugin; to change one, open a PR against the rules/ folder of the handbook repository.\n\n'

ls "${CLAUDE_PLUGIN_ROOT}"/rules/*.md >/dev/null 2>&1 || exit 0

awk '
FNR == 1 && NR > 1 { print "" }
{ print }
END { print "" }
' "${CLAUDE_PLUGIN_ROOT}"/rules/*.md
