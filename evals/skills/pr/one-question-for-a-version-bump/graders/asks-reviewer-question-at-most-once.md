---
type: regex
target: trace
pattern: '(?:demo/__init__\.py|0\.[12]\.0)[^\n]{0,300}?anything a reviewer should know[\s\S]*(?:demo/__init__\.py|0\.[12]\.0)[^\n]{0,300}?anything a reviewer should know'
flags: i
match: not_contains
---
