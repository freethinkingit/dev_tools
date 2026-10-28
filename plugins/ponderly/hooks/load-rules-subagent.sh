#!/bin/sh
# SubagentStart hook: prints the handbook rules so Claude Code adds them to a
# sub-agent's context. For that event plain stdout is not added to the context;
# only the additionalContext field of a JSON object on stdout is. So this script
# prints the same text as load-rules.sh, the SessionStart hook, wrapped in that
# JSON. The JSON string encoding is POSIX awk, so the plugin needs no python3,
# node or jq. Exits non-zero on any failure.
#
# The plugin directory's validator only accepts a hook script that writes every
# path in full from CLAUDE_PLUGIN_ROOT, uses no other variable, no command
# substitution and calls no other file in the plugin. So this script cannot run
# load-rules.sh: it writes the same header and reads rules/ itself.
# checks/test_hook_encoder.py pins the same header in its HEADER constant, so a
# header change touches the three together.
set -eu

[ -d "${CLAUDE_PLUGIN_ROOT:-}/rules" ] || {
  echo "load-rules-subagent.sh: no rules under CLAUDE_PLUGIN_ROOT, so this sub-agent gets no rules" >&2
  exit 1
}

# With no .md file under rules/ the glob stays unexpanded and ls fails; an empty
# rules/ gives the sub-agent no rules, so it fails the same way as its own
# no-rules/ check above. load-rules.sh, by contrast, prints the header and exits 0.
ls "${CLAUDE_PLUGIN_ROOT}"/rules/*.md >/dev/null 2>&1 || {
  echo "load-rules-subagent.sh: no rule files under CLAUDE_PLUGIN_ROOT/rules, so this sub-agent gets no rules" >&2
  exit 1
}

# Escape backslash, double quote and every control character (0x01-0x1f) and
# pass every other byte through, so non-ASCII text stays as its UTF-8 bytes.
# Each record ends with an escaped newline, as load-rules.sh prints it with one.
awk '
function emit(s,    i, n, c) {
  n = length(s)
  for (i = 1; i <= n; i++) {
    c = substr(s, i, 1)
    if (c in esc) c = esc[c]
    printf "%s", c
  }
}
BEGIN {
  for (code = 1; code < 32; code++) esc[sprintf("%c", code)] = sprintf("\\u%04x", code)
  esc["\b"] = "\\b"; esc["\t"] = "\\t"; esc["\n"] = "\\n"; esc["\f"] = "\\f"; esc["\r"] = "\\r"
  esc["\""] = "\\\""; esc["\\"] = "\\\\"
  printf "{\"hookSpecificOutput\": {\"hookEventName\": \"SubagentStart\", \"additionalContext\": \""
  printf "# Handbook rules\\n\\n"
  printf "Team rules that apply in every repository. They are shipped by the handbook plugin; to change one, open a PR against the rules/ folder of the handbook repository.\\n\\n"
}
FNR == 1 && NR > 1 { printf "\\n" }
{ emit($0); printf "\\n" }
END { printf "\\n\"}}\n" }
' "${CLAUDE_PLUGIN_ROOT}"/rules/*.md
