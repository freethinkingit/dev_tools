---
description: Invoked directly with observed versus intended behaviour that never uses the word bug, start-task triages the defect to Bug_Route, offers the routes as a question, and neither reproduces, fixes, nor invokes bugfix before the author answers. Needs the scaffold, which plants add returning a - b in calc/ops.py.
tags: [skill, start-task]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: Claude reads calc/ops.py and tests/test_ops.py, states in two or three sentences that this is a bug and takes Bug_Route, naming add in calc/ops.py returning a - b, and asks the author which route to take, with Bug_Route and Spec_Route as options on their own lines. It launches no sub-agent, invokes no skill, writes nothing under .claude/specs/, and leaves calc/ops.py unchanged.
---
/freethinking:start-task calc.add(2, 3) returns -1; it should return 5
