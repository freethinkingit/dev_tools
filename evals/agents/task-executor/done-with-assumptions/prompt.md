---
description: Launched on a spec task with one small gap, what divide should do for a zero divisor, which the task names but does not settle, task-executor does the task and lists the zero behaviour under `unsure`, as its own choice or as the default it left alone, instead of stopping or passing it off as specified. It returns a Summary whose first line gives the status `done`, with `divide` added to `calc/ops.py` and the zero behaviour named under `unsure`, and leaves no scratch script; the test suite it runs writes `__pycache__`, so the no-file grader looks at `.py` files only. The other half of the hypothesis, a task too vague to do, is `stops-on-vague-bundle`. Needs the Makefile's agent target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, task-executor]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type freethinking:task-executor, giving it the mode sentence and the task, and does nothing else itself. The sub-agent adds divide(a, b) to calc/ops.py next to add, picks or leaves alone the behaviour for a zero divisor, writes no test since tests are tasks of their own, runs python3 -m unittest and an ephemeral check, deletes the check, and returns its Summary with the status `done` and the zero behaviour listed under `unsure` as unsettled by the task. Claude's reply is that Summary verbatim; the workspace gains no file.
---
Launch one sub-agent with the Agent tool, `subagent_type` `freethinking:task-executor`, and give it exactly this prompt:

```text
This task is a leaf task from a spec; tests are tasks of their own.

Add divide(a, b) to calc/ops.py returning a divided by b, in the style of add. The spec does not say what to do when b is zero.
```

Do nothing else yourself: do not read, edit or test anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Summary verbatim, the whole of it and nothing else.
