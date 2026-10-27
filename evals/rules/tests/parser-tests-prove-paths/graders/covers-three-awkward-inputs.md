---
type: llm
focus: { source: file, path: tests/test_quantity.py }
---

The file shown is `tests/test_quantity.py` after a session was asked to add `parse_quantity(text)` to calc/quantity.py with its tests in that file.

Count the kinds of awkward input below that the tests actually pass to `parse_quantity`, each kind once however many tests use it:

1. joined or other emoji
2. non-Latin script or digits
3. a very long string
4. a zero-width character
5. a control character inside the text
6. a byte-order mark

Count only inputs passed to `parse_quantity` in a test, never text in a docstring or comment. A whitespace-only string or a string with surrounding whitespace counts as none of the kinds.

PASS if at least three distinct kinds are counted.
FAIL if fewer than three are, or if the file is missing or holds no tests.
