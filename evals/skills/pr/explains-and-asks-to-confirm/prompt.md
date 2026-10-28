---
description: 'Proves Property 1 and serves Requirement 7.2: on a feature branch with no spec whose two commits add `demo/greeting.py` and `tests/test_greeting.py`, with a GitHub origin and a signed-in gh (both provided by scaffold stubs), pr run with nothing answered in advance takes the Confirm_Form: its first walkthrough message names both groups, explains the helper by what changes for its user and what the author takes on before how it was done, asks one question to confirm or correct each group, lists none of the five review prompts, and stops there without creating the PR. Needs the Makefile''s pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.'
tags: [skill, pr]
max_turns: 20
allowed_tools: [Read, Glob, Grep]
expected_outcome: 'Claude finds no ticked spec in the branch, says it is explaining each change for the author to confirm, and puts both groups in one message: group 1 the greet helper in `demo/greeting.py`, explained first by what changes for whoever uses it and what the author takes on, then how it was done; group 2 its test in `tests/test_greeting.py`. It ends with one prose question asking the author to confirm, correct or add to each group, puts none of the five review prompts, and waits without calling `gh pr create` (Property 1, Requirement 7.2).'
---
/ponderly:pr
