---
type: regex
pattern: 'def test_many_values[\s\S]*def test_default_high_is_100[\s\S]*def test_clamp_gives_the_same_answer_twice'
target: { source: file, path: tests/test_clamp.py }
---
