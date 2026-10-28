---
description: On a feature branch one commit ahead of main, with a GitHub origin and a signed-in gh (both provided by scaffold stubs) and a file modified but not committed, pr offers to commit the uncommitted change after the walkthrough, and stops at that question without committing anything. It serves Requirement 7.5, every existing pr case keeps passing, and Requirement 5.1, with the commit offer made in the one fixed-choice call after the walkthrough. Needs the Makefile's pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.
tags: [skill, pr]
max_turns: 20
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude runs the starting checks, finds the branch `add-greeting` with `demo/greeting.py` modified and uncommitted, notes it, and makes the commit offer in the one fixed-choice call after the walkthrough, listing the file, with the options `Commit after the walkthrough` (Recommended) and `Leave them out`, rendered as list items in prose since the AskUserQuestion tool is absent in the sandbox. It then stops and waits. It commits nothing, does not push, and does not run `gh pr create`.
---
/ponderly:pr

I am the author. I cannot answer during this run. Why: the CLI needed a greeting helper. Confirm every group as you explain it. For the questions still missing: there is no ticket; I did not test it; there is no risk or rollout to note; there is no review focus. Stop at the branch, commit, Closes and draft questions and wait for me.
