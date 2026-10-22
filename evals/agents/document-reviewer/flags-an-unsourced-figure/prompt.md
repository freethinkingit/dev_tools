---
description: 'Launched by its namespaced name on a scaffolded tree of a strategy, a shortener service HLD and an LLD for the HLD''s Metrics Reader that agrees with its template, its parent and itself except that its Risks section states "The Link Store holds at most 50 GB of Link records", a figure the HLD does not give and the LLD neither attributes to the author nor derives, document-reviewer reports that figure as a should-fix with an exact quote. Requirements 5.8, 9.5. Needs the Makefile''s eval-agent-document-reviewer target, which runs the scaffold and grants no tool beyond the case''s own.'
tags: [agent, document-reviewer]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: 'Claude launches one sub-agent with subagent_type freethinking:document-reviewer, giving it the document, template and parent paths, and does nothing else itself. The sub-agent reads the three files and returns Findings with the verdict findings, among them one for the Risks section that quotes the line stating the Link Store holds at most 50 GB, says the HLD does not give that figure and the LLD does not attribute it, and gives it the severity should-fix. Claude''s reply is those Findings verbatim, whose first line gives the verdict.'
---
Launch one sub-agent with the Agent tool, `subagent_type` `freethinking:document-reviewer`, and give it exactly this prompt:

```text
Review this document before the author sees it.
Document: .freethinking/designs/links-2027/shortener-service/lld-metrics-reader.md
Template: templates/lld-template.md
Parent: .freethinking/designs/links-2027/shortener-service/hld-shortener-service.md
```

Do nothing else yourself: do not read, run or check anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Findings verbatim, the whole of them and nothing else.
