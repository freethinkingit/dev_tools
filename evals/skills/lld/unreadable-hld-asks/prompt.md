---
description: Given an HLD path that does not exist, lld says it cannot read that path, names it, and asks the author to paste the HLD's candidates section and the parts the LLD will serve, writing nothing. Needs the Makefile's eval-skill-lld target, which grants Write and Edit and runs the scaffold.
tags: [skill, lld]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Write, Edit, Agent, Skill]
expected_outcome: Claude tries to read .freethinking/designs/x/y/hld-y.md, finds it missing, and says so in its final message, naming the path and asking the author to paste the HLD's candidates section and the parts the visit counter design will serve. It writes no lld-*.md file.
---
/freethinking:lld .freethinking/designs/x/y/hld-y.md visit counter
