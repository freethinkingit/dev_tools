---
description: 'On the shop fixture''s branch shop-search, whose uncommitted shop/handlers.py adds search_products with a SQL string built by concatenating the search term (line 14) and a page slice one item too long (line 16), review takes the range from the merge base with main to the working tree, launches one review-arm per lens, then the wave-reviewer once, folds the reviewer''s findings into the list and launches again only the arms whose findings the reviewer contradicted, when the budget allows, and its reply names both defects with their file and line range. Requirement 9.2. Needs the Makefile''s review target, which grants Bash, runs the scaffold and puts the wrappers in bin on the PATH.'
tags: [skill, review]
max_turns: 40
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: 'Claude resolves the range from the merge base of main and HEAD to the working tree, with shop/handlers.py the one changed file, launches five review-arm agents at once, merges their arm blocks, launches the wave-reviewer once, folds its findings into the list as high for a blocker, medium for a should-fix and low for a nit, and launches again only the arms whose findings the reviewer contradicted, when the budget allows. Its reply lists one finding per line as <severity> <category> <file>:<start_line>-<end_line> <message>, among them a high security finding on shop/handlers.py at line 14 for the SQL built by concatenating term, and a correctness finding on shop/handlers.py at line 16 for the slice of offset + size + 1 items, then the count line. It changes no file and commits nothing.'
---
/ponderly:review
