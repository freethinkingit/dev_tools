---
description: A sizeable feature request is routed through the start-task skill before any code.
tags: [rule, workflow]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude invokes /handbook:start-task rather than designing or coding straight away.
---
We need a link shortener in this service: users submit a long URL, get a short code back, and visiting the short code redirects to the original URL with click counting. Please build it.
