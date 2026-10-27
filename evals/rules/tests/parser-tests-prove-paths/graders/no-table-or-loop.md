---
type: regex
pattern: '^[ \t]*(?:async[ \t]+)?for\b|subTest\(|parametrize'
flags: m
match: not_contains
target: { source: file, path: tests/test_quantity.py }
---
