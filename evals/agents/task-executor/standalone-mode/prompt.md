---
description: Launched by its namespaced name with only the task text, no sentence saying the task is a leaf task from a spec, task-executor is in standalone mode. It adds subtract to calc/ops.py in the style of add together with a test in the project's existing test file, written the way the project writes tests, proves the change with the suite, and returns the fixed-shape Summary reporting done. Needs the Makefile's agent target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, task-executor]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type ponderly:task-executor, giving it the task text alone, and does nothing else itself. The sub-agent adds subtract(a, b) to calc/ops.py next to add, adds test_subtract to OpsTest in tests/test_ops.py, runs python3 -m unittest, and returns its Summary. Claude's reply is that Summary verbatim, whose first line says the status is done.
---
Launch one sub-agent with the Agent tool, `subagent_type` `ponderly:task-executor`, and give it exactly this prompt:

```text
Add subtract(a, b) to calc/ops.py returning a minus b, in the style of add
```

Do nothing else yourself: do not read, edit or test anything. When the sub-agent returns, reply with its Summary verbatim, the whole of it and nothing else.
