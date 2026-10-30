---
description: 'Launched by its namespaced name with the security lens on the shop fixture''s branch shop-search, whose uncommitted shop/handlers.py builds the search SQL by concatenating the search term on line 14, review-arm returns its arm block for the security lens with a finding anchored on that line. Requirement 9.2. Needs the Makefile''s review-arm target, which grants Bash, runs the scaffold and puts the wrappers in bin on the PATH.'
tags: [agent, review-arm]
max_turns: 20
allowed_tools: [Read, Glob, Grep, Agent]
expected_outcome: 'Claude launches one sub-agent with subagent_type ponderly:review-arm, giving it the shared standard, the security lens, the range and the changed file, and does nothing else itself. The sub-agent runs git diff main -- shop/handlers.py, reads the file at the working tree and returns an arm block beginning lens: security with a high security finding on shop/handlers.py, start_line 14, for the term concatenated into the LIKE clause. Claude''s reply is that arm block verbatim.'
---
Launch one sub-agent with the Agent tool, `subagent_type` `ponderly:review-arm`, and give it exactly this prompt:

```text
Shared standard, quoted:
"Across every lens, a finding worth reporting is one a competent senior reviewer would expect the author to address before merge: true and verifiable against the code at head, a real concern that would improve the change, and specific enough to act on. A finding not worth reporting is an incorrect or unverifiable claim, a duplicate, a style nit below the project's bar, or advice that would not improve the change or would make it worse. A pre-existing problem in a touched file counts when it is verifiable."

Lens, quoted:
"## security

This lens looks for concrete, exploitable vulnerabilities, covering at least injection (SQL, shell, template and similar, where untrusted input reaches an interpreter by concatenation or formatting), authentication and authorisation (a missing check, a check on the wrong subject, a bypass path, broken access control), secrets in code (a credential, key or token written into the source, configuration or tests, with its actual value), unsafe deserialisation of input the user controls, and path traversal (a path built from input that can escape its intended directory); it also covers cryptographic misuse, data exposure and supply-chain risks. It carries the category `security`, the smallest share of a review and the highest bar, because a security finding that cannot be exploited here costs the reviewer more trust than any other kind. A true positive traces a specific data flow from the untrusted source to the dangerous sink in this code, or shows the bypass path, the secret's value or the deserialised input, and says what an attacker gains; when the code that builds the sink's input can be run on its own, the finding runs it on a crafted input and quotes the string that reaches the sink. A false positive restates a best practice without showing how it is exploited here, such as boilerplate sanitisation advice, a generic warning to pin an action to a SHA or a mutable-tag alert, even when it names the variable or the action; it also includes a flow whose input is not in fact user-controlled or is already validated. A bug with no attacker in it belongs to the correctness or reliability lens."

Range: base main, head the working tree.

Changed files:
- shop/handlers.py

Pull request title: Add product search
Pull request body: none given
```

Do nothing else yourself: do not read, run or check anything, do not answer anything the sub-agent asks, and do not launch it again; I cannot answer questions during this run. When the sub-agent returns, reply with its arm block verbatim, the whole of it and nothing else.
