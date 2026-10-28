---
description: On a feature branch with commits, a GitHub origin and a signed-in gh (both provided by scaffold stubs), pr walks the changes, drafts the description and creates the PR with gh. Needs the Makefile's pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.
tags: [skill, pr]
max_turns: 20
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude runs the starting checks, reads the branch's two commits, takes the author's advance answers to all five review prompts without waiting, drafts a title and description from those answers, pushes, and calls `gh pr create` with `--base main` and a body file, then reports the PR URL the stub returns.
---
/ponderly:pr

I am the author and I will not be able to answer questions during this run, so here are my answers in advance. They apply to every change you walk, so do not wait for me. Why was it made: the CLI needed a greeting helper, so the branch adds `greet` and its test. What it does not cover: anything beyond a fixed "Hello, name!" string; there is no localisation. What would break it: `greet` no longer returning a string. What was run: I ran `pytest tests/test_greeting.py` and it passed. What a reviewer should question: nothing in particular beyond `demo/greeting.py`. No ticket. Risk and rollout: none. Open it as a normal PR, not a draft. Treat the draft as approved and create the PR.
