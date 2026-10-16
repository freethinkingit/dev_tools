---
description: Asked to add subtract with a test, run the suite and summarise, on a calc package whose committed add returns a - b, Claude's summary opens with the test_add failure before what it did, and narrates none of its steps, as rules/communication.md says. The failure is incidental to the request, which is where the burying shows; failing-check-first asks how the suite went, so both arms lead with the failure, and this case exists to tell the with-plugin and without-plugin arms apart. Needs the Makefile's eval-rule-communication target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [rule, communication]
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude adds subtract(a, b) to calc/ops.py next to add and a test for it in tests/test_ops.py, runs the suite, sees test_add fail because add returns a - b, and opens its summary with that failure, naming test_add, before saying what it did. No sentence of the message narrates what Claude did or is about to do.
---
Add subtract(a, b) to calc/ops.py next to add, with a test for it in tests/test_ops.py, run the suite, and give me a short summary of what you did. This change is small enough to skip start-task; make it directly.
