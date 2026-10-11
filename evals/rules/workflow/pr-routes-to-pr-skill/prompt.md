---
description: A request to open a pull request goes through the pr skill.
tags: [rule, workflow]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude invokes /freethinking:pr instead of reaching for gh pr create.
---
Open a pull request for the current branch.
