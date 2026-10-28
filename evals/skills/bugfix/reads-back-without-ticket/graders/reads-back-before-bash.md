---
type: regex
pattern: '^(?:(?!Symptom[*_]*\s*:)[\s\S])*"name"\s*:\s*"Bash"'
flags: i
match: not_contains
target: trace
---
