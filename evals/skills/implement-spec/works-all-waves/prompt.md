---
description: On a scaffolded project with a committed two-wave spec, implement-spec works the whole spec at spec cadence. It works wave 0 and wave 1 without waiting between them, each with its executor agent, its own test run, its wave-reviewer agent and its full suite, writes a report after each wave, has the reviewer agent read the whole run once more in a final review, and hands back once at the end. Each wave report and the final report are written by the report skill, invoked inline by implement-spec's step 6. Needs the Makefile's implement-spec target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [skill, implement-spec]
max_turns: 70
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: Claude validates the graph, launches the task-executor agent for task 1, runs the tests itself, launches the wave-reviewer agent for wave 0, writes the wave's report and starts wave 1 without waiting, does the same for task 2, then launches the wave-reviewer agent once more over the whole run and hands back with a final report carrying a Wave review line for each wave and the `Final review of the run:` line. It writes each wave report and the final report inline with the report skill, each opening with `## Problems` or `No problems.` before `## Done`. Its attempts to tick the tasks are refused, because the sandbox denies edits under .claude/, and it says so rather than working around it.
---
/freethinking:implement-spec calc-subtract spec

I will not be able to answer questions during this run. Cadence: spec, run every wave and hand back only at the end. There are no optional tests. The branch is already calc-subtract. This sandbox refuses edits under .claude/, so if ticking a task in tasks.md is refused, say so in the report and carry on to the next wave as if it were ticked.
