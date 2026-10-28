---
description: 'On a feature branch whose third commit bumps the version line in demo/__init__.py from 0.1.0 to 0.2.0, with a GitHub origin and a signed-in gh (both provided by scaffold stubs), pr is passed the ticket #7 and an advance answer for the greeting group and the version bump; it proves that the version bump is sorted as a mechanical group that gets the one question "anything a reviewer should know?" or its advance answer taken, that no answered question is put again (Property 2), and that the Changes section carries a bullet for the version; serves Requirement 7.4. Needs the Makefile''s pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.'
tags: [skill, pr]
max_turns: 20
allowed_tools: [Read, Glob, Grep]
expected_outcome: 'Claude reads ticket #7 with `gh issue view`, walks the greeting group and confirms it from the advance text, treats the version bump as a mechanical group and takes the advance answer that a reviewer needs nothing, without asking "anything a reviewer should know?" more than once, pushes, calls `gh pr create` with a Changes bullet naming the version bump to 0.2.0, and reports the PR URL the stub returns (Property 2, Requirement 7.4).'
---
/ponderly:pr #7

I cannot answer during this run. The greeting group and its test: confirmed as you explain it. The version bump: nothing a reviewer needs. Merging finishes the ticket; not a draft; treat the draft as approved.
