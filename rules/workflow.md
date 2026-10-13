# Workflow

These rules say which handbook skill to reach for and when. They apply in every repository this handbook applies to.

The first bullet that matches the request is the route.

- **Bug named: reproduce before fixing.** When the author calls the request a bug, or hands over a ticket filed as one, run `/freethinking:bugfix`. Reproduce the bug first, confirm the root cause with the author before changing code, and guard the fix with a regression test. "It works now" is not a fix.
- **Spec exists: follow it.** If `.claude/specs/<task>/tasks.md` exists for the work in hand, run `/freethinking:implement-spec`. It works the tasks in wave order, ticks a task's checkbox when its tests pass, and stops for review at the author's cadence, after each task or after each wave. Do not skip ahead or merge tasks.
- **Pull request: use the skill.** Open and update PRs with `/freethinking:pr`. It walks the changes with the author and drafts the description to the team template. Do not open a PR with a bare `gh pr create`.
- **Small changes stay small.** A typo, a one-line fix or a rename needs no skill. Say that the change is small enough to skip `start-task`, then make it.
- **Anything else that changes code: start the task.** Run `/freethinking:start-task`. It reads the code and decides between the executor for one contained change, `bugfix` for a defect, and a spec for the rest, and asks before taking the first two. Do not judge the size yourself.
- **Never work on the default branch.** Create a branch before the first commit. Do not commit or push unless the author asks.
- **Keep the author in the loop.** When the approach changes, or a step turns out to be bigger than expected, say so before carrying on. Ask only what the code and the request cannot answer, and batch the questions.
