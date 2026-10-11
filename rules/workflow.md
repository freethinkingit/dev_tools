# Workflow

These rules say which handbook skill to reach for and when. They apply in every repository this handbook applies to.

- **New feature or sizeable task: spec first.** Before writing code for a new feature, or for any request large enough that coding straight away would be guessing, run `/freethinking:start-task`. It writes `requirements.md`, `design.md` and `tasks.md` in `.claude/specs/<task>/`, each approved by the author before the next.
- **Existing spec: follow it.** If `.claude/specs/<task>/tasks.md` exists for the work in hand, run `/freethinking:implement-spec`. It works the tasks in wave order, ticks a task's checkbox when its tests pass, and stops for review at the author's cadence, after each task or after each wave. Do not skip ahead or merge tasks.
- **Bug: reproduce before fixing.** For a bug, issue or defect, run `/freethinking:bugfix`. Reproduce the bug first, confirm the root cause with the author before changing code, and guard the fix with a regression test. "It works now" is not a fix.
- **Pull request: use the skill.** Open and update PRs with `/freethinking:pr`. It walks the changes with the author and drafts the description to the team template. Do not open a PR with a bare `gh pr create`.
- **Never work on the default branch.** Create a branch before the first commit. Do not commit or push unless the author asks.
- **Small changes stay small.** A typo, a one-line fix or a rename does not need a spec. Say that the change is small enough to skip the skill, then make it.
- **Keep the author in the loop.** When the approach changes, or a step turns out to be bigger than expected, say so before carrying on. Ask only what the code and the request cannot answer, and batch the questions.
