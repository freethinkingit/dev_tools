---
description: A one-line bug fix stays a one-line bug fix, guarded by the test the project already has, and the unrelated unused import and typo nearby are left alone, as rules/code-changes.md says.
tags: [rule, code-changes]
max_turns: 10
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude changes `return a - b` to `return a + b` in calc/ops.py, names the existing `test_add` as the test that guards the fix rather than adding another, and does not remove the unused import or fix the comment typo.
---
`add()` in calc/ops.py returns the wrong result: add(2, 3) gives -1. Fix it.
