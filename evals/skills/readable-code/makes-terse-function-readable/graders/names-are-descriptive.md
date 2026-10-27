---
type: regex
pattern: '(?<![\w''])[snm](?!\w)\s*(?:=|\[|\]|\)|,|%|//|\+|-|\bif\b|\belse\b)'
match: not_contains
target: { source: file, path: calc/stats.py }
---
