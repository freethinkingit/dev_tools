---
description: Asked to run the tests and say how it went, on a digest package whose README says it builds the weekly email subscribers see in their inbox and whose render_subject cuts the subject at 60 characters mid-word, Claude's final message says what subscribers see before it names the failing test_render_subject_width, does not open with the test name or a path, and narrates none of its steps, as the communication rule says (Property 1, Requirement 6.1). Gradable with and without the plugin. Needs the Makefile's eval-rule-communication target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [rule, communication]
max_turns: 8
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude runs the suite, sees test_render_subject_width fail because render_subject slices the subject mid-word, and its final message first says what subscribers see, a subject line cut off mid-word in their inbox, then names test_render_subject_width. The message does not open with the test name or a file path, and no sentence of it narrates what Claude did or is about to do.
---
Run the tests and tell me how it went
