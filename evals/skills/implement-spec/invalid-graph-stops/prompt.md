---
description: Invoked on a spec whose Task Dependency Graph omits a leaf task, implement-spec lists the problem by task id, proposes a corrected `waves` block, and waits for the author instead of building anything. Needs the fixture spec, which scaffold.sh writes; the Makefile passes --scaffold for this target.
tags: [skill, implement-spec]
max_turns: 8
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude reads `.claude/specs/link-shortener/`, finds that leaf task 4.2 is missing from the graph, proposes a corrected `waves` block that includes 4.2, and stops for approval. It writes nothing.
---
/freethinking:implement-spec link-shortener
