---
description: Given a strategy path that does not exist, hld says it cannot read it, naming the path, asks the author to paste the strategy's candidates and the parts the design will serve, and writes no design. Needs the Makefile's skill target, which grants Write and Edit and runs the scaffold.
tags: [skill, hld]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Write, Edit, Agent, Skill]
expected_outcome: Claude tries to read .ponderly/strategies/missing.md, finds it does not exist, says so naming missing.md, and asks the author to paste the strategy's candidates section and the parts this design will serve. It writes no file under .ponderly/designs/ and no code.
---
/ponderly:hld .ponderly/strategies/missing.md shortener service
