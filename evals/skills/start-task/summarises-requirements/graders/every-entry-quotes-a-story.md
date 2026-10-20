---
type: llm
---

The reply is start-task's hand-back of the requirements.md it wrote for a calculation-history feature on a small calc package, ending with the approval question; the judge sees only the reply, not the file.

Check only these two things, and nothing else.
1. Before the approval options, the reply has a list with one item per requirement, and every item quotes a user story: text that begins "As a" and contains "I want" and "so that".
2. The reply does not print a section of the document: there is no heading or block such as Introduction, Glossary or Acceptance Criteria, and no numbered list of criteria.

PASS when both hold. FAIL when either does not.

Allowed, and never a reason to fail: a short summary sentence after a quoted story; a bracketed reference such as (2.2); a list of decisions or open questions after the items; bold or backticks anywhere; the approval options written in plain text.
