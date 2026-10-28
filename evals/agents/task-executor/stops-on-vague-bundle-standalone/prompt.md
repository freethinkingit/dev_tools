---
description: Launched in standalone mode, no spec sentence, on a task that is vague and bundles two changes with an either/or between them, task-executor stops instead of picking a reading, although standalone mode also owes a test, which is one more reason to guess. It returns a Summary whose first line gives the status `stopped`, asks under `stopped because` which change is wanted and what it should do, changes `calc/ops.py` nothing, and leaves no scratch file. Its twin `stops-on-vague-bundle` asks the same in spec mode, and `done-with-assumptions` covers the other half of the hypothesis, a task with one small gap that is done with the assumption listed. Needs the Makefile's agent target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, task-executor]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type ponderly:task-executor, giving it the task text alone, and does nothing else itself. The sub-agent finds that the task names two changes joined by "or optionally", with a third conditional on the second and none of them specified, changes nothing, and returns its Summary with the status `stopped` and, under `stopped because`, the questions the launcher must answer, which change and what rounding or division by zero should do. Claude's reply is that Summary verbatim; `calc/ops.py` gains neither rounding nor a divide, and the workspace gains no file.
---
Launch one sub-agent with the Agent tool, `subagent_type` `ponderly:task-executor`, and give it exactly this prompt:

```text
Add rounding to the results in calc/ops.py or optionally a divide, and if divide then something sensible for zero.
```

Do nothing else yourself: do not read, edit or test anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Summary verbatim, the whole of it and nothing else.
