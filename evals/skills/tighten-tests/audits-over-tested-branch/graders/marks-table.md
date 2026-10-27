---
type: llm
focus: trace
---

The trace is a tighten-tests run on a branch that adds tests for `clamp(value, low, high)` in `tests/test_clamp.py`. It ends with the Audit, the read-only list of a keep, merge or drop verdict per test, followed by a question asking the author to approve it. Judge only the Audit in Claude's own text, not the test file's contents shown in tool results.

PASS if the Audit gives `test_many_values`, the test that checks nineteen values in one subTest table, the verdict drop or merge, in any layout: a table row, a record, a Drop or Merge section that lists it, or prose.
FAIL if the Audit keeps `test_many_values`, names it only as the test others merge into, or never reaches a verdict for it, or if the trace holds no Audit.
