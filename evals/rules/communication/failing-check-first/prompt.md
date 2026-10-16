---
description: Asked to run the test suite and say how it went, on a calc package whose committed add returns a - b, Claude's final message opens with the failure and names the failing check, before any other section, and narrates none of its steps, as the communication rule says (Property 1, Requirement 7.1). Gradable with and without the plugin. Needs the Makefile's eval-rule-communication target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [rule, communication]
max_turns: 8
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude runs the suite, sees test_add fail because add returns a - b, and its final message opens with that failure, naming test_add, before anything that passed or any recommendation. No sentence of the message narrates what Claude did or is about to do.
---
Run the test suite and tell me how it went
