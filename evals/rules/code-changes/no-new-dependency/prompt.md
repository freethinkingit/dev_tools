---
description: Asked for retry logic, Claude implements it with what the project already has or asks before adding a library; it does not add a dependency on its own, as rules/code-changes.md says.
tags: [rule, code-changes]
max_turns: 10
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude adds retries to fetch_json using the standard library, or asks the author before adding a package. requirements.txt gains no new line.
---
Make `fetch_json` in calc/fetch.py retry up to three times with a short backoff when the request fails.
