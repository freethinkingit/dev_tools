---
description: Given a contained change against the calc fixture, start-task triages it as Executor_Route, offers the route question with Executor_Route recommended and Spec_Route as the alternative, and stops there, writing no spec and launching nothing before the author answers. Needs the Makefile's skill target, which runs the scaffold.
tags: [skill, start-task]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: Claude reads calc/ops.py and the tests, says in two or three sentences that adding subtract next to add is a contained change taking Executor_Route, naming the code it touches, proposes `subtract` (or similar) as the task name and a branch name, and asks the route question with Executor_Route (Recommended) and Spec_Route as options. It writes nothing under .ponderly/specs/, edits no code, and launches no sub-agent or skill.
---
/ponderly:start-task Add subtract(a, b) to calc/ops.py returning a minus b, in the style of add
