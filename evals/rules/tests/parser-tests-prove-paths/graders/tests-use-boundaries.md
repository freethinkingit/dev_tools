---
type: regex
pattern: '^(?=[\s\S]*["''][ \t]*(?:0|-[0-9]+)[ \t]*["''])(?=[\s\S]*["''][ \t]*1000[ \t]*["''])'
target: { source: file, path: tests/test_quantity.py }
---
