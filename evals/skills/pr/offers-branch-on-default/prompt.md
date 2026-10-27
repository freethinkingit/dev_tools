---
description: On the default branch, with two unpushed commits on main, a GitHub origin and a signed-in gh (both provided by scaffold stubs), pr offers to create a branch and move the changes onto it, and stops at that question instead of stopping with an error. It serves Requirement 7.5, every existing pr case keeps passing, and Requirement 5.1, with the branch question asked in the one fixed-choice call after the walkthrough. Needs the Makefile's pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.
tags: [skill, pr]
max_turns: 20
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude runs the starting checks, finds the current branch is main, the default branch, notes it, and asks the branch question in the one fixed-choice call after the walkthrough with the options `Create <name>` (Recommended), the name a slug from the changes since no ticket was given, and `Stop`, rendered as list items in prose since the AskUserQuestion tool is absent in the sandbox. It then stops and waits. It creates no branch, does not push, does not run `gh pr create`, and does not end with the stop sentence saying a pull request needs its own branch.
---
/freethinking:pr

I am the author. I cannot answer during this run. Why: the CLI needed a greeting helper. Confirm every group as you explain it. For the questions still missing: there is no ticket; I did not test it; there is no risk or rollout to note; there is no review focus. Stop at the branch, commit, Closes and draft questions and wait for me.
