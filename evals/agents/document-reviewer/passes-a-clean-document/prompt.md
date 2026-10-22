---
description: 'Launched by its namespaced name on a scaffolded tree of a strategy, a shortener service HLD and a short LLD for the HLD''s Metrics Reader that agrees with its template, its parent and itself, document-reviewer returns its Findings in shape, verdict first, with no blocker among them, so it is not rewarded for inventing a contradiction; a strict reviewer may still offer should-fix or nit advice on a sound document. Requirements 5.3, 5.4, 9.2. Needs the Makefile''s eval-agent-document-reviewer target, which runs the scaffold and grants no tool beyond the case''s own.'
tags: [agent, document-reviewer]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: 'Claude launches one sub-agent with subagent_type freethinking:document-reviewer, giving it the document, template and parent paths, and does nothing else itself. The sub-agent reads the three files, finds every section of the LLD doing what the template says it is for and agreeing with the HLD and with the LLD''s other sections, and returns Findings with no blocker: an empty list with the verdict holds, or the verdict findings with only should-fix or nit advice. Claude''s reply is those Findings verbatim, whose first line gives the verdict.'
---
Launch one sub-agent with the Agent tool, `subagent_type` `freethinking:document-reviewer`, and give it exactly this prompt:

```text
Review this document before the author sees it.
Document: .freethinking/designs/links-2027/shortener-service/lld-metrics-reader.md
Template: templates/lld-template.md
Parent: .freethinking/designs/links-2027/shortener-service/hld-shortener-service.md
```

Do nothing else yourself: do not read, run or check anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Findings verbatim, the whole of them and nothing else.
