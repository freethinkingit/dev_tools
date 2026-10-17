# Handback report

Sections are `## <Name>` headings, in this order. With a Problem the Message opens with `## Problems`; with none, its first line is `No problems.` and `## Done` follows.

1. **Problems.** One bullet each: what it is, why it matters, the options; for something found outside the work, roughly how much it would add to the branch. Never a name coined in the work.
2. **Done.** Each item with the check that proved it and the result seen; for a spec, `<task id> <text> (Requirements <ids>)`.
3. **Checks.** The full-suite result; `Wave review of wave <n>: <verdict>` and, at spec cadence, `Final review of the run: <verdict>`, each followed by `carried: see Problems` or `nothing carried`. No carried item restated.
4. **Files.** The paths changed or created, undescribed.
5. **Next.** The next task and wave, proposal, hand-off or question; skipped optional tests named as unticked. No offer or restatement.

An agent's report is translated, never pasted as-is. A `stopped` status and its `stopped because` are always a Problem. An `unsure` entry the session has since checked goes under Done or Checks as verified, naming the check; one not checked is a Problem; `unsure: nothing` is not mentioned. Quotes stay verbatim.

## Before

```text
## Done
- 2.2 Bug_Route and Executor_Route bodies
## Tests
- Wave review of wave 2: findings fixed. Carried: README list; launcher wording; write-grader gap.
## Next
- Three follow-ups to file. Wave 3 next. Say go.
```

## After

```text
## Problems
- Two eval cases have a grader asserting that nothing is written. Under the skill target those graders cannot fail, because that target grants no tool that writes; they only catch a write under `make eval`. Options: file an issue, or grant a write tool in those cases.
- The README's list of unit-test files omits two files under `checks/`, so a reader looking for a check's tests misses them. Options: fix it in this PR, or file an issue.
- The executor's description says it is launched only by `implement-spec`; `start-task` now launches it too, so the description misleads anyone choosing how to launch it. Options: fix it in this PR, or file an issue.

## Done
- 2.2 The bug and executor routes in `start-task` (Requirements 2.1, 2.2): wave review passed after fixes.
- 3.2 Eval case `contained-change-offers-executor` (Requirement 5.3): `make validate` passes; the case itself runs in wave 3.

## Checks
- `make validate`: passes, 11 checks and both plugin validations.
- Wave review of wave 2: findings, all fixed; carried: see Problems.

## Files
- `skills/start-task/SKILL.md`, `Makefile`, `evals/skills/start-task/contained-change-offers-executor/`

## Next
Wave 3, task 5.1: run the three eval targets twice each. These are real model calls billed to your seat, about one to two dollars. Say go to start.
```
