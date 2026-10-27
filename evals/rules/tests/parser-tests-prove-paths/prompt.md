---
description: Tests for a new parser prove its paths with boundary values and awkward input, one test per path, as rules/tests.md says, rather than a table of many values. With the plugin, the workflow rule routes the request to start-task and the prompt pre-answers its route question, so the task-executor it launches writes the tests; without the plugin, the session writes them itself.
tags: [rule, tests]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: parse_quantity(text) lands in calc/quantity.py with its tests in tests/test_quantity.py, written by the task-executor start-task launches in the with-plugin arm and by the session itself in the without-plugin arm. There is one test per path, each named as the behaviour sentence it proves, such as test_refuses_the_limit_plus_one, with no generic label such as test_valid and no test bundling several cases. The tests use the limits 1 and 999 and the values either side of them, feed at least three distinct kinds of awkward input from emoji, a non-Latin script, a very long string, a zero-width character, a control character and a byte-order mark, and use no loop, subTest or table over many values.
---
Add a `parse_quantity(text)` function in a new module calc/quantity.py. It turns the quantity a user typed into an order form into an int: a whole number of items from 1 to 999, surrounding whitespace allowed. Anything else raises ValueError. Add its tests in tests/test_quantity.py. Take the executor route without asking; I can't answer questions during this run.
