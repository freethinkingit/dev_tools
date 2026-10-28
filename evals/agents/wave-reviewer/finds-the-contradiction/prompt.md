---
description: Launched by its namespaced name on a scaffolded calc package whose uncommitted diff adds subtract returning b - a, while the cited requirement says a minus b, wave-reviewer gathers the diff itself and reports the contradiction. Its Findings give the verdict `findings` and name calc/ops.py and subtract. Property 6, Requirement 5.6. Needs the Makefile's agent target, which grants Bash, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, wave-reviewer]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type ponderly:wave-reviewer, giving it the spec-wave sentence, the changed file and the requirement, and does nothing else itself. The sub-agent runs git status and git diff, sees subtract return b - a against a requirement that says a minus b, and returns Findings with a blocker on calc/ops.py quoting the wrong line. Claude's reply is those Findings verbatim, whose first line says the verdict is findings.
---
Launch one sub-agent with the Agent tool, `subagent_type` `ponderly:wave-reviewer`, and give it exactly this prompt:

```text
Review the changes of one wave of a spec. The changes come from a spec wave, where tests are tasks of their own, so the code tasks correctly carry no test. The changes are uncommitted in the working tree.

Changed files:
- calc/ops.py

Requirement the changes implement, quoted:
"1.1 THE calc package SHALL provide subtract(a, b) in calc/ops.py, returning a minus b, in the style of add."

The file that cites it: tests/test_ops.py, which imports from calc.ops.
```

Do nothing else yourself: do not read, run or check anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Findings verbatim, the whole of them and nothing else.
