---
description: When the strategy's path already exists, the strategy skill does not overwrite it and offers to resume it at its first unfinished section, with Resume and Overwrite as options. Needs the Makefile's eval-skill-strategy target, which grants Write and Edit and runs the scaffold.
tags: [skill, strategy]
max_turns: 12
allowed_tools: [Read, Glob, Grep, Write, Edit, Agent, Skill]
expected_outcome: Claude derives the name links-2027, finds .freethinking/strategies/links-2027.md already written up to its Goals section, and asks whether to resume it from Current state or overwrite it, offering Resume and Overwrite each on its own line, then waits. The existing file keeps its two sections and gains no new one, and no other strategy file is written.
---
/freethinking:strategy links 2027
