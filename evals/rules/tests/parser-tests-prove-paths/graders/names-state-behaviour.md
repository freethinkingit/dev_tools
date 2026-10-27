---
type: llm
focus: { source: file, path: tests/test_quantity.py }
---

The file shown is `tests/test_quantity.py` after a session was asked to add `parse_quantity(text)` to calc/quantity.py with its tests in that file. Judge only the test function names and what each test body checks.

PASS if every test function's name states, as a sentence, the one behaviour its body proves, such as `test_refuses_the_limit_plus_one` or `test_accepts_surrounding_whitespace`, and each test checks that one case.
FAIL if any name is a generic label rather than a behaviour sentence, such as `test_valid`, `test_out_of_range` or `test_invalid_inputs`, or if a test bundles several cases under one name (several inputs asserted in a row, or a loop or subTest over inputs), or if the file is missing or holds no tests.
