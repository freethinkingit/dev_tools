---
description: A request on an area whose only spec is closed takes the route the skill descriptions give it, not implement-spec.
tags: [rule, workflow]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude reads .freethinking/specs/calc-subtract/ as a record of merged work, since every task is ticked, subtract is already in calc/ops.py and the prompt says its branch merged, and does not invoke /freethinking:implement-spec. The request is a new change, so /freethinking:start-task is invoked, proposes a route for divide and asks the author which to take. Nothing is written.
---
Add divide(a, b) to calc/ops.py in the style of add, raising ValueError with a message when b is 0, and cover it in tests/test_ops.py. An earlier task left a spec in .freethinking/specs/calc-subtract/; its branch merged.
