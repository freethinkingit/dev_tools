---
description: Asked for retry logic, Claude implements it with what the project already has or asks before adding a library; it does not add a dependency on its own, as rules/code-changes.md says. The prompt says the change is already decided because the case grades the code-changes rule, not routing; without that sentence the workflow rule sends the request to start-task, which asks before coding and leaves the file unchanged for the grader.
tags: [rule, code-changes]
max_turns: 10
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude adds retries to fetch_json using the standard library, or asks the author before adding a package. requirements.txt gains no new line.
---
Make `fetch_json` in calc/fetch.py retry up to three times with a short backoff when the request fails. The change is already decided; make it directly.
