---
description: Asked in prose to report back on finished work, Claude does the work and then invokes the report skill to write the hand-back, writing no report file. Needs the plugin arm, so it proves the skill's description and the communication rule's routing together. Needs the Makefile's eval-skill-report target, which grants Bash, Write and Edit and puts the wrappers in bin on the PATH.
tags: [skill, report]
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude adds subtract(a, b) to calc/ops.py, runs `python3 -m unittest`, then invokes the report skill to write the hand-back, and writes nothing but calc/ops.py and its test in tests/test_ops.py.
---
Add subtract(a, b) to calc/ops.py next to add, run the tests, and then report back to me how it went. This change is small enough to skip start-task; make it directly.
