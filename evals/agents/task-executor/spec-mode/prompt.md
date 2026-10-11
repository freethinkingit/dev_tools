---
description: Launched by its namespaced name with the mode sentence present, task-executor builds one spec task on a scaffolded calc package. It adds subtract to calc/ops.py in the style of add, writes no test because in spec mode tests are tasks of their own, proves the change with the existing suite and an ephemeral check, and returns the fixed-shape Summary reporting done. Needs the Makefile's agent target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, task-executor]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type freethinking:task-executor, giving it the mode sentence and the task, and does nothing else itself. The sub-agent adds subtract(a, b) to calc/ops.py next to add, leaves tests/test_ops.py alone, runs python3 -m unittest and an ephemeral check, and returns its Summary. Claude's reply is that Summary verbatim, whose first line says the status is done and whose sections list the files changed, the checks run and the ephemeral check.
---
Launch one sub-agent with the Agent tool, `subagent_type` `freethinking:task-executor`, and give it exactly this prompt:

```text
This task is a leaf task from a spec; tests are tasks of their own.

Add subtract(a, b) to calc/ops.py returning a minus b, in the style of add
```

Do nothing else yourself: do not read, edit or test anything. When the sub-agent returns, reply with its Summary verbatim, the whole of it and nothing else.
