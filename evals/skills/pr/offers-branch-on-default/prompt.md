---
description: On the default branch, with two unpushed commits on main, a GitHub origin and a signed-in gh (both provided by scaffold stubs), pr offers to create a branch and move the changes onto it, and stops at that question instead of stopping with an error. Needs the Makefile's pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.
tags: [skill, pr]
max_turns: 8
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude runs the starting checks, finds the current branch is main, the default branch, and asks the branch question with the options `Create <name>` (Recommended), the name a slug from the changes since no ticket was given, and `Stop`, rendered as list items in prose since the AskUserQuestion tool is absent in the sandbox. It then stops and waits. It creates no branch, does not push, does not run `gh pr create`, and does not end with the stop sentence saying a pull request needs its own branch.
---
/freethinking:pr

I am the author. I will not answer any question during this run, so stop at the first question you ask and wait for me.
