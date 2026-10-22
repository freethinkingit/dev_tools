---
description: Launched by its namespaced name on a scaffolded tree of a strategy, a shortener service HLD and a visit counter LLD, document-reviewer reads the LLD, its template and its parent HLD itself and reports that the LLD's Data section has the redirect handler increment the count before returning, against the HLD's key decision that visit counting is asynchronous and off the redirect path. Its Findings give the verdict `findings`, name the Data section and quote the contradicting line. Requirements 5.3, 5.4, 9.2. Needs the Makefile's eval-agent-document-reviewer target, which runs the scaffold and grants no tool beyond the case's own.
tags: [agent, document-reviewer]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: Claude launches one sub-agent with subagent_type freethinking:document-reviewer, giving it the document, template and parent paths, and does nothing else itself. The sub-agent reads the three files, holds each section of the LLD against the template, the HLD and the LLD's other sections, and returns Findings with a blocker on the Data section quoting "The redirect handler increments `visitCount` in the Link Store before it returns the redirect." as contradicting the HLD's asynchronous counting. Claude's reply is those Findings verbatim, whose first line says the verdict is findings.
---
Launch one sub-agent with the Agent tool, `subagent_type` `freethinking:document-reviewer`, and give it exactly this prompt:

```text
Review this document before the author sees it.
Document: .freethinking/designs/links-2027/shortener-service/lld-visit-counter.md
Template: templates/lld-template.md
Parent: .freethinking/designs/links-2027/shortener-service/hld-shortener-service.md
```

Do nothing else yourself: do not read, run or check anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its Findings verbatim, the whole of them and nothing else.
