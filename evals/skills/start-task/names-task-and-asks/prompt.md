---
description: Given a request that extends the calc fixture, start-task proposes a kebab-case task name and a branch name, says the request takes Spec_Route, and asks its spec questions instead of writing the spec or code. Needs the Makefile's skill target, which runs the scaffold.
tags: [skill, start-task]
max_turns: 6
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: Claude reads the calc fixture, proposes `calculation-history` (or a similar kebab-case name) and a branch name, says in one sentence that the request takes Spec_Route, and asks its spec questions in prose. It writes nothing under .freethinking/specs/ and edits no code.
---
/freethinking:start-task Keep a history of every calculation: record each operation with its operands and result as it runs, and add a way to list the history.
