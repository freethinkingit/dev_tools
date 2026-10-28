---
description: A bug report is routed through the bugfix skill, as the workflow rule says.
tags: [rule, workflow]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: Claude invokes /ponderly:bugfix before doing anything else about the bug, restates the symptom and expected behaviour, says it will reproduce first, and claims no fix.
---
Bug ticket ENG-412: the upload worker crashes with "TypeError: Cannot read properties of null (reading 'name')" when a user uploads a file whose name contains spaces. Expected: the upload succeeds. Please fix it.
