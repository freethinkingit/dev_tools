---
description: Asked to add an operation, Claude reads the repository's contributing guide before the surrounding code, as rules/code-changes.md says, and follows the convention it states that the code does not show, listing the new operation in the README's Operations table. The prompt says the change is already decided because the case grades the code-changes rule, not routing; without that sentence the workflow rule sends the request to start-task, which asks before coding and leaves the files unchanged for the graders.
tags: [rule, code-changes]
max_turns: 10
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude reads CONTRIBUTING.md, adds `subtract(a, b)` returning `a - b` to calc/ops.py in the style of add, and adds a row for subtract to the Operations table in README.md.
---
Add subtract(a, b) to calc/ops.py returning a minus b, in the style of add. The change is already decided; make it directly.
