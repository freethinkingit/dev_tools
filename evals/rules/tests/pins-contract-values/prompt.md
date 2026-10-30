---
description: Tests for an event builder pin the values another system relies on as literals, name who relies on them, and leave out a field nothing reads, as rules/tests.md says. calc/events.py documents that the billing service subscribes to type "order.placed" and reads order_id and total_cents, and that emitted_by is read by nothing. With the plugin, the workflow rule routes the request to start-task and the prompt pre-answers its route question, so the task-executor it launches writes the tests; without the plugin, the session writes them itself.
tags: [rule, tests]
max_turns: 30
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: tests/test_events.py holds tests for order_placed_event that assert the event type as the literal "order.placed" rather than through the ORDER_PLACED constant, name the billing service, or what it does with the event, in the test that checks the type, check order_id and total_cents, and never assert the emitted_by field or the EMITTER constant.
---
Add tests for `order_placed_event` in calc/events.py, in a new file tests/test_events.py. Read the module first. Take the executor route without asking; I can't answer questions during this run.
