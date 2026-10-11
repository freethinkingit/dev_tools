---
description: Invoked in a bare sandbox workspace (a git repo on main with no commits, no origin, no gh), pr runs its starting-state checks, stops, and says which check failed instead of drafting or creating anything.
tags: [skill, pr]
max_turns: 5
expected_outcome: Claude names a step-1 failure (on the default branch, no origin, not a GitHub repo, or gh not signed in), tells the author what to do, and never reaches the walkthrough or the PR draft.
---
/handbook:pr
