---
description: The SessionStart hook injects both rule files into a fresh session.
tags: [hook]
max_turns: 2
expected_outcome: Claude names the "Workflow" and "Code changes" rule sections without using any tool.
---
Without using any tools, answer from what is already in your context: were any handbook rules loaded into this session? If so, list the exact H1 headings of each rule section, one per line. If not, reply exactly NO RULES.
