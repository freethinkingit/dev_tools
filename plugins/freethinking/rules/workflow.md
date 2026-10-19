# Workflow

These rules say how a request finds the handbook skill that does it. They apply in every repository this handbook applies to. A skill's description says when it applies and its text says what it does; these rules say to look there first, and what not to do without the skill.

- **Check the skills before doing it yourself.** The handbook ships a skill for each common kind of work, and every skill's description says when it applies. Match the request against those descriptions first, and run the skill that fits rather than doing its work by hand: no pull request with a bare `gh pr create`, no code before the bugfix skill has reproduced the bug, no spec task skipped or merged, and no judging a change's size yourself, which is start-task's job.
- **Small changes stay small.** The one exception: a typo, a one-line fix or a rename needs no skill. Say that the change is small enough to skip `start-task`, then make it.

The rest hold in every session, skill or no skill.

- **Never work on the default branch.** Create a branch before the first commit. Do not commit or push unless the author asks; a yes to an offer a skill raised counts as asking.
- **A merged spec is a record.** `.claude/specs/<task>/` holds the task's three spec files and nothing else. Once its tasks are ticked and its branch merged, the spec is closed: it is not work in hand for implement-spec, it is not edited to match later code, and it is not read to learn how the code works today. Current behaviour lives in the code and the repository's own documentation.
- **Keep the author in the loop.** When the approach changes, or a step turns out to be bigger than expected, say so before carrying on. Ask only what the code and the request cannot answer, and batch the questions.
