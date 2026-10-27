---
description: 'Proves Property 3 and serves Requirement 7.3: on a feature branch whose commits add `.freethinking/specs/add-greeting/` with requirements, design and a fully ticked `tasks.md` naming `demo/greeting.py` and `tests/test_greeting.py`, with no implement-spec reports in the sandbox, pr passed the ticket #7 with nothing answered in advance takes the Spec_Form: it names the spec and the form, groups the changes by the spec''s tasks, asks one prose round about risk, rollout or review focus, and puts none of the five review prompts. Needs the Makefile''s pr target, which grants Bash, runs the scaffold, and puts the stub bin on the PATH.'
tags: [skill, pr]
max_turns: 20
allowed_tools: [Read, Glob, Grep]
expected_outcome: 'Claude reads ticket #7 with `gh issue view`, finds the add-greeting spec in the branch''s diff with every task ticked, says it is drafting from that spec, shows task 1 (the greet helper) and task 2 (its test) in one message, each with what changed and the why drafted from the requirement it cites, says the testing is as written in the tasks since no reports are in the conversation, then asks one prose round about risk and rollout and review focus and stops there without asking the five review prompts or calling `gh pr create` (Property 3, Requirement 7.3).'
---
/freethinking:pr #7
