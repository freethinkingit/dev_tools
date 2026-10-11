---
description: The SubagentStart hook injects both rule files into a sub-agent's context before its first prompt. Needs the SubagentStart entry in hooks/hooks.json, which runs load-rules-subagent.sh; with only the SessionStart hook the sub-agent starts without the rules and answers NO RULES.
tags: [hook]
max_turns: 4
allowed_tools: [Agent]
expected_outcome: Claude launches one general-purpose sub-agent, which names the "Workflow" and "Code changes" rule sections without using any tool, and Claude pastes that reply verbatim as its whole answer.
---
Launch exactly one sub-agent with the Agent tool (subagent_type general-purpose) with this prompt: "Without using any tools, answer from what is already in your context: were any handbook rules loaded? If so, list the exact H1 headings of each rule section, one per line. If not, reply exactly NO RULES." Paste the sub-agent reply verbatim as your whole answer.
