---
description: On a scaffolded project with a committed two-wave spec, implement-spec works the first wave at wave cadence. It launches the executor agent for the task, runs the tests itself, has the reviewer agent read the wave, ticks the task, runs the full suite, and hands back without starting wave 1. The Agent tool has no fork in a headless run, so the hand-back is written inline by the report skill, the fallback of implement-spec's step 6, and that is the path graded. Needs the Makefile's implement-spec target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [skill, implement-spec]
max_turns: 40
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: Claude validates the graph, launches the task-executor agent for task 1, runs the tests itself, launches the wave-reviewer agent once for the wave and reports its verdict, and leaves wave 1 alone (no test_subtract written). It writes the hand-back inline with the report skill, and the Message opens with `## Problems` or `No problems.` before `## Done`, and keeps the `Wave review of wave n:` line under Checks. It also tries to tick task 1 and is refused, because the sandbox denies edits under .claude/, and says so rather than working around it.
---
/freethinking:implement-spec calc-subtract wave

I will not be able to answer questions during this run. Cadence: one wave. There are no optional tests. The branch is already calc-subtract. Work the first wave and hand back. The Agent tool has no fork in this run; write the hand-back inline.
