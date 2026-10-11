---
description: Launched on a spec task that names a module the project does not have, task-executor stops instead of inventing one. It returns a Summary whose first line gives the status `stopped`, names the missing module under `stopped because`, and creates no file. Needs the Makefile's agent target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, task-executor]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type freethinking:task-executor, giving it the mode sentence and the task, and does nothing else itself. The sub-agent finds no `calc/stats.py` and no `mean` to sit next to, changes nothing, and returns its Summary with the status `stopped` and the missing module as its evidence or question. Claude's reply is that Summary verbatim; the workspace gains no file and `calc/ops.py` gains no `percent_of`.
---
Launch one sub-agent with the Agent tool, `subagent_type` `freethinking:task-executor`, and give it exactly this prompt:

```text
This task is a leaf task from a spec; tests are tasks of their own.

Add `percent_of(part, whole)` to `calc/stats.py`, next to `mean`, returning part as a percentage of whole, in the style of the functions already there.
```

Do nothing else yourself: do not read, edit or test anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Summary verbatim, the whole of it and nothing else.
