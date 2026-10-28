---
description: On the works-one-wave scaffold, with tests/test_ops.py committed carrying a leftover `import os` as its first line, in a file no task of the first wave changes, implement-spec works the first wave and its hand-back lists the leftover import as a discovery. Graded on the hand-back naming it under Problems with a rough size and its two options, a task in tasks.md or an issue, and on the import being left in place rather than fixed unasked. The Agent tool has no fork in a headless run, so the hand-back is written inline by the report skill. Needs the Makefile's implement-spec target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [skill, implement-spec]
max_turns: 40
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: Claude launches the task-executor agent for task 1, which adds subtract to calc/ops.py, runs the tests, notices the unused `import os` marked as left over on the first line of tests/test_ops.py, and reports it under `unsure` without removing it. The wave's hand-back, written inline with the report skill, lists the leftover import under `## Problems` with where it is (tests/test_ops.py, line 1), roughly how much work it would add to the branch, and its two options, a proposed task in tasks.md or an issue, for the author to choose. `import os` is still in tests/test_ops.py at the end of the run.
---
/ponderly:implement-spec calc-subtract wave

I will not be able to answer questions during this run. Cadence: one wave. There are no optional tests. The branch is already calc-subtract. Work the first wave and hand back. The Agent tool has no fork in this run; write the hand-back inline.
