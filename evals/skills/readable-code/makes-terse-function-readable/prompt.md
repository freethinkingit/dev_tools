---
description: 'On a branch that adds one terse function, calc/stats.py median with one-letter locals, a dense one-line ternary and a docstring that walks through the algorithm step by step, plus its passing test, readable-code proposes calc/stats.py as a group of one, takes the pre-answered approval, launches the executor for that group and leaves the function with descriptive names and a docstring that states the contract, not the steps. The existing tests still pass, no test file is added and nothing is committed. Needs the Makefile''s readable-code target, which grants Bash, Write, Edit and Agent, runs the scaffold and puts the wrappers in bin on the PATH.'
tags: [skill, readable-code]
max_turns: 40
allowed_tools: [Read, Glob, Grep, Agent, Skill]
expected_outcome: 'Claude states the Scope (calc/stats.py the one source file, against main), takes the Baseline with python3 -m unittest, shows calc/stats.py as one File_Group with its Shared_Decisions and takes the approval the prompt gives instead of waiting, launches one task-executor for that group, which renames s, n and m to descriptive names and drops the steps from the docstring without changing behaviour, runs the suite again and finds it unchanged, launches the wave-reviewer once, and hands back with the report skill. It adds no test file and commits nothing.'
---
/freethinking:readable-code

I will not be able to answer questions during this run. Approve the groups and decisions you propose. The branch is add-median; make it readable and hand back.
