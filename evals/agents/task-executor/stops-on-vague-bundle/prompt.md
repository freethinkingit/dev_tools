---
description: Launched on a spec task that is vague and bundles two changes with an either/or between them, task-executor does not quietly pick a reading. It returns a Summary that either stops with the question the launcher must answer under `stopped because`, or reports done with every reading it chose listed under `unsure`; either way it leaves no scratch file in the workspace. Needs the Makefile's agent target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, task-executor]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type freethinking:task-executor, giving it the mode sentence and the task, and does nothing else itself. The sub-agent finds that the task names two changes joined by "or optionally", with a third conditional on the second and none of them specified, and either stops with its Summary saying status stopped and a question under stopped because, or builds one reading and says status done with each assumption under unsure, never "nothing". Claude's reply is that Summary verbatim; the workspace gains no file, since both readings are edits to calc/ops.py and scratch work is deleted.
---
Launch one sub-agent with the Agent tool, `subagent_type` `freethinking:task-executor`, and give it exactly this prompt:

```text
This task is a leaf task from a spec; tests are tasks of their own.

Add rounding to the results in calc/ops.py or optionally a divide, and if divide then something sensible for zero.
```

Do nothing else yourself: do not read, edit or test anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Summary verbatim, the whole of it and nothing else.
