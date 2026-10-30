---
type: regex
pattern: 'emitted_by|EMITTER|calc\.events["'']'
match: not_contains
target: { source: file, path: tests/test_events.py }
---
