#!/bin/sh
# SubagentStart hook: prints the handbook rules so Claude Code adds them to a
# sub-agent's context. For that event plain stdout is not added to the context;
# only the additionalContext field of a JSON object on stdout is. So this script
# runs load-rules.sh, the SessionStart hook, and wraps its output in that JSON,
# which keeps rules/ the one source for both. The JSON string encoding is POSIX
# awk, so the plugin needs no python3, node or jq. Given `-` as its only
# argument it encodes stdin instead of the rules, which is what the hook check
# feeds it. Exits non-zero on any failure.
set -eu

hooks="$(dirname "$0")"

# Read the whole text with a sentinel after it, so that trailing newlines,
# which command substitution strips, reach the encoder and come back out.
if [ $# -eq 0 ]; then
  text=$("$hooks/load-rules.sh" && printf X) || {
    echo "${0##*/}: load-rules.sh failed, so this sub-agent gets no rules" >&2
    exit 1
  }
elif [ $# -eq 1 ] && [ "$1" = - ]; then
  text=$(cat && printf X)
else
  echo "usage: ${0##*/} [-]" >&2
  exit 1
fi

# Escape backslash, double quote and every control character (0x01-0x1f) and
# pass every other byte through, so non-ASCII text stays as its UTF-8 bytes.
# awk reads a line at a time: each line is printed one behind, with \n between
# lines, and the sentinel ends the last one, so the text is reproduced exactly.
printf '%s' "$text" | awk '
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
}
NR > 1 { emit(prev); printf "\\n" }
{ prev = $0 }
END {
  emit(substr(prev, 1, length(prev) - 1))
  printf "\"}}\n"
}'
