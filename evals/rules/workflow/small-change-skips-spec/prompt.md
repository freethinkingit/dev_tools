---
description: A trivial change does not trigger the spec workflow.
tags: [rule, workflow]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude does not invoke start-task for a one-word typo fix.
---
The README spells "receive" as "recieve" in the first paragraph. Fix the typo.
