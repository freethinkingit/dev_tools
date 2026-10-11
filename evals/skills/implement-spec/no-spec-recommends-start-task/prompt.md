---
description: Invoked on a task that has no spec, implement-spec says so and recommends start-task instead of building anything.
tags: [skill, implement-spec]
max_turns: 6
expected_outcome: Claude finds no `.claude/specs/link-shortener/tasks.md`, says the spec does not exist, and recommends `/freethinking:start-task`. It writes nothing.
---
/freethinking:implement-spec link-shortener
