# Implementation Plan

## Overview

The skill text comes first, since the README row and the eval case both describe what it says. The README row and the eval case follow in one wave, touching disjoint files. The spec folder move, found necessary when the eval sandbox refused the write under `.claude/`, is one wave of three tasks on disjoint file groups. The last wave is the author's: the eval runs that cost tokens, with the table for the pull request. Each task is proved by `make validate` plus the ephemeral check its text names; the eval run is the integration proof. GitHub issue #47 is the ticket.

## Tasks

- [x] 1. Change the start-task skill's hand-back
  - In `plugins/ponderly/skills/start-task/SKILL.md`, make the five edits of the design's SKILL.md section, each quoted there as it will read: the Hand-backs bullet; the new "Showing a document" section after "Working with the author" and before step 1, with its two paragraphs; the resume sentence in step 1; the closing paragraph of steps 4, 5 and 6, each saying its summary's depth and the Showing a document section, with the AskUserQuestion sentence kept as it is; and nothing else. Ephemeral check: `grep -c 'in full' SKILL.md` is 0, `grep -c 'Showing a document' SKILL.md` is 6 (the heading, the Hand-backs bullet, step 1 and the three steps), the Approve question's header, options and wording are unchanged by `git diff`; `make validate` passes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4, 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.4_

- [x] 2. Update the README row
  - In `plugins/ponderly/README.md`, replace the last clause of the `start-task` row, "with you approving each document before the next", with "showing you each document as its path and a short summary and asking you to approve it before the next", as the design's README section gives it; `make validate` passes, which runs `checks/test_descriptions.py`
  - _Requirements: 6.3_

- [x] 3. Add the eval case
  - Create `evals/skills/start-task/summarises-requirements/` as the design's eval section lays it out: `case.yaml` naming `scaffold.sh`; `scaffold.sh` as a regular executable file that finds the repository root and runs `evals/fixtures/setup.sh calc main`; `prompt.md` with the frontmatter fields and the prompt quoted in the design; and the eight graders of the design's table, `writes-requirements`, `names-the-path`, `not-reprinted`, `offers-approval`, `quotes-a-user-story`, `no-criteria-reproduced`, `every-entry-quotes-a-story` and `no-code-written`, each with the type and fields the table gives. Ephemeral check: run the scaffold by hand in an empty directory as `evals/README.md` shows and confirm `calc/ops.py` and `tests/test_ops.py` exist on `main`; `make validate` passes, which runs `checks/test_eval_cases.py`
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 4. Run the start-task evals
  - The author runs `make eval-skill-start-task EVAL_ARGS="--runs 1 --case summarises-requirements"` to iterate the new case, fixing a grader or the skill text as the design's error-handling rows say, then `make eval-skill-start-task` at the default three runs, and pastes the table into the pull request's Testing section with every existing case still passing
  - **Property 1: A document is never printed for approval**
  - **Validates: Requirements 7.4, 1.1, 1.2, 1.4, 2.2**

- [x] 5. Move the spec folder in the plugin text
  - In `plugins/ponderly/skills/start-task/SKILL.md`, `plugins/ponderly/skills/implement-spec/SKILL.md`, `plugins/ponderly/agents/task-executor.md`, `plugins/ponderly/rules/workflow.md` and `plugins/ponderly/README.md`, replace `.claude/specs` with `.ponderly/specs`; add the "Tune the plugin" sentence the design's move table gives; replace the path in the root `README.md`. Ephemeral check: `grep -r '\.claude/specs' plugins/ README.md` finds nothing; `make validate` passes
  - _Requirements: 8.1, 8.2_

- [x] 6. Move the spec folder in the evals
  - `git mv` the four `files/.claude/specs` fixture folders to `files/.ponderly/specs`; replace `.claude/specs` with `.ponderly/specs` in every prompt, grader, scaffold and case README under `evals/`; rewrite the sandbox note in `evals/README.md` as the design's move table gives it. Ephemeral check: `grep -r '\.claude/specs' evals` finds nothing; the `works-one-wave` and `closed-spec-is-a-record` scaffolds run by hand in an empty directory plant the spec at the new path; `make validate` passes
  - _Requirements: 8.3_

- [x] 7. Move the records
  - `git mv .claude/specs .ponderly/specs`, the untracked `spec-approval-summary` folder moving with the directory; `git status` shows renames and the untracked folder at the new path only, and `.claude/settings.json` stays
  - _Requirements: 8.4_

## Notes

- Every task runs `make validate` before it is done; an ephemeral check is created in a scratch location and deleted afterwards.
- Tasks 1 and 5 are the only edits to the skill; the executor quotes the design's text as given and changes no other sentence, so the four existing start-task cases stay the regression check.
- Task 4 is the author's, since the eval runs cost tokens; it gets no sub-agent.
- The `report` skill's templates, the `pr` skill and `bugfix` are not touched, beyond the path replacement of task 5 where one of them names the spec folder.
- After task 7 this spec lives at `.ponderly/specs/spec-approval-summary/`; ticks after that go there.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2", "3"] },
    { "id": 2, "tasks": ["5", "6", "7"] },
    { "id": 3, "tasks": ["4"] }
  ]
}
```
