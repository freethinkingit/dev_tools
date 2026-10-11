---
description: Invoked directly, bugfix restates the ticket (symptom, expected, context) and does not jump to code or a fix.
tags: [skill, bugfix]
max_turns: 4
expected_outcome: Claude states Symptom, Expected and Context back to the author and asks only what it needs to reproduce; no diagnosis or fix yet.
---
/handbook:bugfix ENG-412: the upload worker crashes with "TypeError: Cannot read properties of null (reading 'name')" when a user uploads a file whose name contains spaces. Expected: the upload succeeds and the file is stored under its original name. Seen on staging, build 2026.10.03, Chrome and the CLI uploader.
