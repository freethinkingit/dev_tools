---
description: 'On the calc fixture''s branch calc-subtract, whose uncommitted calc/ops.py adds a correct subtract returning a - b and whose uncommitted tests/test_ops.py adds its test_subtract, review launches its arms and reports no high-severity finding, so it is not rewarded for always finding something serious. Requirement 9.3. Needs the Makefile''s review target, which grants Bash, runs the scaffold and puts the wrappers in bin on the PATH.'
tags: [skill, review]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: 'Claude resolves the range from the merge base of main and HEAD to the working tree, with calc/ops.py and tests/test_ops.py the changed files, launches one review-arm per lens and the wave-reviewer, and replies with "No findings." or only medium and low findings, then the count line. No line of the reply begins with high. It changes no file and commits nothing.'
---
/ponderly:review
