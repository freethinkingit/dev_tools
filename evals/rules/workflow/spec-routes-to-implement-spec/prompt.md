---
description: Work with an existing spec is routed through the implement-spec skill, as the workflow rule says.
tags: [rule, workflow]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude invokes /handbook:implement-spec (the Skill tool) rather than reading the spec and coding straight away. The sandbox has no spec, so the skill then stops; only the routing is graded.
---
There is an approved spec in .claude/specs/link-shortener/ with a tasks.md. Pick up the work and continue it.
