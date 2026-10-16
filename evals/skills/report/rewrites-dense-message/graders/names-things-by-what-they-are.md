---
type: llm
---

The reply is a rewrite, by the report skill, of a dense triage message about issue #6, which asks for three additions to the workflow rule; the original proposed its type, priority, area and milestone in one block and used labels such as "spec lifecycle", "the listing" and "the collaboration and workflow work".

PASS if the rewrite names issue #6 by its number and says in plain words what it asks for (the three additions need not be spelled out or invented), AND states the decisions the original left open, the priority and the milestone, each with its options and a recommendation with its reason, AND states type and area either as proposals with their reason or as decisions, AND carries no label from the original unexplained: "spec lifecycle", "the listing" and "the collaboration and workflow work" count as labels unless the rewrite says in plain words what they mean.
FAIL if any of those labels is kept as-is without explanation, if priority and milestone are not laid out as choices with options, or if the whole stays one dense block.
