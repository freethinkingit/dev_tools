---
description: Invoked directly, start-task proposes a kebab-case task name and asks its first round of questions instead of writing the spec or code.
tags: [skill, start-task]
max_turns: 4
expected_outcome: Claude proposes `link-shortener` (or similar kebab-case name) and a branch name, says in one sentence that the request takes Spec_Route, says the spec will live under .claude/specs/, and asks the author questions. It writes nothing.
---
/freethinking:start-task Link shortener: users submit a long URL and get a short code; visiting the code redirects and counts the click.
