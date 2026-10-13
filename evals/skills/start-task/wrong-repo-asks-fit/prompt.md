---
description: Given a request that extends nothing in the calc fixture, start-task says so and asks whether to spec it here or stop because this is the wrong repository, before any spec question, writing nothing. Needs the Makefile's skill target, which runs the scaffold.
tags: [skill, start-task]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: Claude reads the calc fixture, says in two or three sentences that a link shortener extends nothing in it (no module, pattern or test it builds on), and asks the fit question with Spec it here and Wrong repository as options, before any spec question. It writes nothing under .claude/specs/, edits no code, and launches no sub-agent or skill.
---
/freethinking:start-task Link shortener: users submit a long URL and get a short code; visiting the code redirects and counts the click
