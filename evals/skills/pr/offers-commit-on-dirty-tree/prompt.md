---
description: On a feature branch one commit ahead of main, with a GitHub origin and a signed-in gh (both provided by scaffold stubs) and a file modified but not committed, pr offers to commit the uncommitted change after the walkthrough, and stops at that question without committing anything. Needs the Makefile's pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.
tags: [skill, pr]
max_turns: 8
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude runs the starting checks, finds the branch `add-greeting` with `demo/greeting.py` modified and uncommitted, and makes the commit offer, listing the file, with the options `Commit after the walkthrough` (Recommended) and `Leave them out`, rendered as list items in prose since the AskUserQuestion tool is absent in the sandbox. It then stops and waits. It commits nothing, does not push, and does not run `gh pr create`.
---
/freethinking:pr

I am the author. I will not answer any question during this run, so stop at the first question you ask and wait for me.
