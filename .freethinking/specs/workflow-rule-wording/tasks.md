# Implementation Plan

## Overview

The rule and skill edits come first and are independent of each other, since the design quotes every new sentence. The eval cases come next, with the case fix the author chose to keep in the branch, so that `make validate` can check them before anything runs. The README is edited once the rule text is final. Wave 3 is GitHub issue #15, added after wave 1, with its own eval run so that its rule edit does not land in the middle of wave 2's runs. The wave before it is the measure: the eval targets, run by the author at the terminal rather than by an executor, because every run is a real model call on the author's seat and a nested `claude plugin eval` inside an executor is not something the sandbox has been tried with. `make check` proves the hook limit after every rule edit; `make validate` proves the case structure.

## Tasks

- [x] 1. Rewrite `rules/workflow.md` to the text quoted in the design: the opening paragraph, the check-the-skills bullet with its four guards, the small-change bullet, the sentence introducing the standing rules, the default-branch bullet with the author's yes, the merged-spec record bullet, and the unchanged keep-in-the-loop bullet. GitHub issues #7 (template claim removed, yes to an offer) and #6 (record rule).
  - _Requirements: 1.1, 1.2, 1.3, 1.5, 2.1, 2.2, 3.1, 3.2, 6.3_

- [x] 2. Extend the smallest-change bullet of `rules/code-changes.md` with the discovery sentence quoted in the design. GitHub issue #6, third addition as revised.
  - _Requirements: 4.1, 4.2, 4.6, 6.3_

- [x] 3. Edit the `description` of `skills/start-task/SKILL.md` so its exclusion clause names the four requests it does not take, as quoted in the design, without pointing at the workflow rule.
  - _Requirements: 1.6_

- [x] 4. Change `skills/report/templates/handback.md` and steps 6 and 7 of `skills/implement-spec/SKILL.md` as the design says: the Problems item with a size for something found outside the work, the step 6 discovery paragraph with its options and the spec-cadence sentence, and the step 7 paragraph handling the author's answer.
  - _Requirements: 4.3, 4.4, 4.5_

- [x] 5. Edit `README.md`: the `rules/workflow.md` and `rules/code-changes.md` rows and the `implement-spec` row, as quoted in the design.
  - _Requirements: 6.1, 6.2_

- [x] 6. Add the four eval cases from the design's table
  - [x] 6.1 `evals/rules/workflow/closed-spec-is-a-record/`: scaffold, ticked spec under `files/`, prompt, the two Skill graders and the route grader; add `eval-rule-workflow: CASE_ARGS += --scaffold` to the Makefile
    - _Requirements: 3.3, 5.3, 5.7_
  - [x] 6.2 `evals/skills/pr/follows-repo-template/`: scaffold with the three-section template, prompt, the three Bash graders and the URL grader
    - _Requirements: 2.3, 5.4, 5.7_
  - [x] 6.3 `evals/skills/pr/offers-commit-on-dirty-tree/`: scaffold on a feature branch with an uncommitted change, prompt, the two option graders and the three must-not graders
    - _Requirements: 2.2, 5.5, 5.7_
  - [x] 6.4 `evals/skills/implement-spec/offers-choice-on-discovery/`: scaffold overlaying `files/tests/test_ops.py` with the leftover import, prompt, the six graders
    - _Requirements: 4.3, 5.6, 5.7_
  - [x] 6.5 `evals/fixtures/setup.sh` copies a fixture file only where the workspace has none, so a case's `files/` overlay wins; the evals README sentence on `files/` says so
    - _Requirements: 5.3, 5.6, 5.7_

- [x] 7. Fix `evals/rules/code-changes/no-new-dependency/prompt.md`: one sentence saying the change is already decided and is to be made directly, and the description updated to say why.
  - _Requirements: 5.7; the discovery the author chose to keep in the branch_

- [x] 8. Run the evals and record the tables for the PR's Testing section. Done by the author at the terminal; each sub-task's check is the table it produces.
  - [x] 8.1 `make eval-skill-bugfix`, `make eval-skill-implement-spec`, `make eval-skill-pr`, `make eval-skill-start-task`, each with `EVAL_MAX_COST_USD=10`; compare with the skill baseline in the design; patch the skill and rerun if a case the rule used to describe drops
    - _Requirements: 5.1, 5.2_
  - [x] 8.2 `make eval-rule-workflow` and `make eval-rule-code-changes` with `EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=10`; compare with the rule baseline; if feature-routes-to-start-task scores below 1.00 with the plugin, restore the one start-task bullet in `rules/workflow.md` and rerun that target
    - _Requirements: 1.7, 5.8_
  - [x] 8.3 The four new cases, each with `EVAL_ARGS="--runs 1 --case <name>"` on its target until it passes, then `--runs 2` to confirm; for 6.4 iterate the plant as the design's risk note says
    - _Requirements: 5.3, 5.4, 5.5, 5.6_

- [x] 9. Add the repository's README and contributing guide to the "Read before you write" bullet of `rules/code-changes.md`, as quoted in the design, and the opening clause of the README's `rules/code-changes.md` row. GitHub issue #15.
  - _Requirements: 7.1, 7.2, 7.4, 6.2_

- [x] 10. Add `evals/rules/code-changes/reads-contributing-guide/` from the design: scaffold with `files/CONTRIBUTING.md` and `files/README.md`, prompt, the two graders.
  - _Requirements: 7.3, 5.7_

- [x] 11. `make eval-rule-code-changes` with `EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=10` after tasks 9 and 10, and `make eval-skill-start-task` with `EVAL_MAX_COST_USD=10` after task 12; record both tables beside wave 2's. Run from the session, as wave 2 was.
  - _Requirements: 7.3, 8.3_

- [x] 12. In `skills/start-task/SKILL.md` step 3, place the route statement with the task and branch names before the Fit question in the same message, as quoted in the design; move `evals/skills/start-task/names-task-and-asks/` onto the calc fixture with the design's prompt and graders.
  - _Requirements: 8.1, 8.2, 5.7_

## Notes

- Every sentence of new rule, skill and README text is quoted in `design.md`; copy it, do not paraphrase.
- Run `make check` after tasks 1 and 2 and `make validate` after tasks 6 and 7; these are the free checks and the executor runs them.
- Tasks under 8 are manual: the executor does not run `make eval-…`. Each is ticked when the author has run it and pasted its table into the conversation.
- Scaffolds are regular executable files that find the repository root with `git -C "$(dirname "$0")" rev-parse --show-toplevel`, as the existing ones do; the pr scaffolds carry their own fake `gh` and git wrapper, copied from a sibling case.
- Task numbers identify tasks; the graph decides the order.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1", "2", "3", "4", "7"] },
    { "id": 1, "tasks": ["5", "6.1", "6.2", "6.3", "6.4", "6.5"] },
    { "id": 2, "tasks": ["8.1", "8.2", "8.3"] },
    { "id": 3, "tasks": ["9", "10", "11", "12"] }
  ]
}
```
