---
type: regex
pattern: '^\s*(?:#+[^\n]*\n\s*)?(?:[-*]\s*)?(?:\*\*|`)?(?:test_|digest/|tests/|[\w./-]+\.py\b)'
match: not_contains
flags: i
---
