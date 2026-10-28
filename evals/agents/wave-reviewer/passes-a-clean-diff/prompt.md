---
description: Launched by its namespaced name on a scaffolded calc package whose uncommitted diff adds a correct subtract returning a - b, wave-reviewer finds nothing to report and gives the verdict `holds`, so it is not rewarded for always finding something. The launch says the changes come from a spec wave, so the missing test is not a finding. Property 6, Requirement 5.6. Needs the Makefile's agent target, which grants Bash, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, wave-reviewer]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type ponderly:wave-reviewer, giving it the spec-wave sentence, the changed file and the requirement, and does nothing else itself. The sub-agent runs git status and git diff, sees subtract return a - b as the requirement says, and returns Findings with an empty list. Claude's reply is those Findings verbatim, whose first line says the verdict is holds.
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
