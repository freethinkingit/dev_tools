---
description: Launched by its namespaced name with the review skill's repository-bar sentence, on a scaffolded calc package whose committed modules are split by divider comments and whose uncommitted diff adds calc/stats.py with the same dividers and a mean that floor-divides, wave-reviewer reports no divider-comment finding above nit, since the repository already does it and it costs nothing here, and reports the floor division as should-fix or blocker. Requirements 4.1, 4.2, 4.3 and 5.3. Needs the Makefile's agent target, which grants Bash, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [agent, wave-reviewer]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type ponderly:wave-reviewer, giving it the range, the repository-bar sentence and the requirement, and does nothing else itself. The sub-agent runs git status and git diff, reads the new calc/stats.py and the code around it, sees that calc/ops.py and calc/compare.py use the same divider comments, and returns Findings with the floor division in mean as a blocker or should-fix quoting the wrong line, and any divider-comment finding as a nit or not at all. Claude's reply is those Findings verbatim.
---
Launch one sub-agent with the Agent tool, `subagent_type` `ponderly:wave-reviewer`, and give it exactly this prompt:

```text
Review the changes from main to the working tree. These changes are a pull request reviewed for the review skill: judge style, structure, comments and tests against the repository's own bar, what its CLAUDE.md, its contributing guide and the code around the change already do, and report a team-rule departure the repository also shows, or one with no concrete cost in this change, as a nit.

Changed files:
- calc/stats.py

Requirement the changes implement, quoted from the pull request:
"1.1 THE calc package SHALL provide mean(values) in calc/stats.py, returning the arithmetic mean of a non-empty list of numbers, so that mean([1, 2]) is 1.5."
```

Do nothing else yourself: do not read, run or check anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Findings verbatim, the whole of them and nothing else.
