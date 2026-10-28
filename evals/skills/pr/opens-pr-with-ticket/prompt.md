---
description: 'On a feature branch with commits, a GitHub origin and a signed-in gh (both provided by scaffold stubs), pr is passed the ticket #7 as its argument, reads it with the fake gh, and opens the PR with the ticket in the title, a Closes line in Why, and a Changes bullet carrying the author''s confirmed explanation with its correction; serves Requirement 7.1. Needs the Makefile''s pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.'
tags: [skill, pr]
max_turns: 20
allowed_tools: [Read, Glob, Grep]
expected_outcome: 'Claude reads ticket #7 with `gh issue view`, takes the author''s advance confirmation of every explanation, with its one correction, without waiting, drafts a title starting with [#7] and a description whose Why carries `Closes #7` once and whose Changes bullet carries the correction that the CLI needed a greeting helper, pushes, calls `gh pr create` with that title, and reports the PR URL the stub returns (Requirement 7.1).'
---
/ponderly:pr #7

I cannot answer during this run. Confirm every explanation as written, with one correction: the why is that the CLI needed a greeting helper. Merging finishes the ticket; not a draft; treat the draft as approved.
