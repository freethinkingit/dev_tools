---
description: A new function comes with a test in the project's existing test file, as rules/code-changes.md says, written the way the project writes tests.
tags: [rule, code-changes]
max_turns: 10
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude adds subtract(a, b) to calc/ops.py and a test for it in tests/test_ops.py, matching the existing test style.
---
Add a `subtract(a, b)` function to calc/ops.py that returns a minus b.
