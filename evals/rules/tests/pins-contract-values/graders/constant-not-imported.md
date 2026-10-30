---
type: regex
pattern: '\bORDER_PLACED\b'
match: not_contains
target: { source: file, path: tests/test_events.py }
---
