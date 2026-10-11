# Implementation Plan

## Overview

The plan does the prerequisite first: `start-task` and its template learn that the graph is the only statement of execution order, with every leaf task in it and no checkpoint tasks, because `implement-spec` validates against that rule. Then the skill itself is written in three sittings, front to back. Then it is wired into the handbook, given its eval cases, and run once by hand on this spec.

The handbook has no code and no unit-test framework. Each task's check is `make validate` for anything under `skills/`, `rules/` or `.claude-plugin/`, an eval case where one can observe the behaviour cheaply, and a recorded manual check otherwise. `make validate` is also the full suite that runs at the end of every wave. Evals are real model calls, so they run by hand at the task that says so, not after every edit. Each leaf task cites the requirements it implements.

## Tasks

- [x] 1. Prerequisite: start-task writes a graph the skill can execute
  - [x] 1.1 Update the task-list step in `skills/start-task/SKILL.md`
    - In step 5, drop the checkpoint clause from the Tasks bullet, and make the Graph bullet say that every leaf task appears exactly once, optional tests included, and that task numbers only identify tasks while the waves decide the order of execution. Run `make validate`
    - _Requirements: 1.1, 1.2_
  - [x] 1.2 Update `skills/start-task/spec-template/tasks.md`
    - Remove the two checkpoint tasks and renumber the metrics tasks 4.x; drop the checkpoint clause from the Overview and the Notes bullet; rewrite the Task Dependency Graph prose to define a leaf task and state the two rules; replace the example `waves` block with the five-wave version from the design's Data Models. Check Property 1 by hand against the example tasks
    - _Requirements: 1.3, 1.4_
  - [x] 1.3 Point the start-task hand-off at the new skill
    - In step 6, tell the author to run `/freethinking:implement-spec <task-name>`, which builds each task in its own sub-agent in wave order, ticks each checkbox when its tests pass, runs the full suite at the end of each wave, and stops for review after each task or each wave as the author chooses
    - _Requirements: 7.5_

- [x] 2. Write the implement-spec skill
  - [x] 2.1 Frontmatter and steps 1 to 4: find, validate, position, set up
    - Create `skills/implement-spec/SKILL.md` in the house pattern (purpose, accountability, `$ARGUMENTS`, numbered steps). Frontmatter per the design table. Step 1 parses the task name and a `task`/`wave` word, finds or asks for the spec, stops on a missing `tasks.md`. Step 2 builds the Leaf_Task and Graph tables, shows them, runs the three checks, proposes a corrected graph or the removal of a task with no work on failure. Step 3 finds the first unticked task, or reports done and asks about unticked optional tests. With no task name, one open spec is named and confirmed, several are listed, none recommends start-task. Step 4 states the next wave and asks the batched start questions. Run `make validate`
    - _Requirements: 1.5, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 7.1_
  - [x] 2.2 Step 5: the wave loop with sub-agents and the end-of-wave suite
    - Step 5 asks once per new wave about optional tests, checks the code for tasks that already appear done, then for each remaining task states id, text and cited requirements and launches a sub-agent with the task text, cited requirements, matching design sections, the code-changes rules with their spec exception, the other tasks in flight and the instruction to stop on drift, which gathers context, implements only what the task describes (tests are tasks of their own), proves it with an ephemeral check and the existing tests, and returns a summary with the check's code. Sub-agents run in parallel at wave cadence and one at a time at task cadence. When one returns the skill re-runs the task's tests, reads any file two sub-agents both changed, ticks on pass and ticks the parent when complete, runs the full suite when a wave's last task is ticked, and leaves for step 6 after two failed fixes, on Drift, or on a failed suite. Run `make validate`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 4.10, 4.11, 4.12, 4.13, 4.14, 4.15, 4.16, 4.17, 5.2, 5.3_
  - [x] 2.3 Steps 6 to 8: report, continue, finish
    - Step 6 writes the Report in the design's fixed shape, adding evidence and a proposed spec edit on Drift, or verbatim output and open and confirmed causes on failure, and never commits. Step 7 resumes on "continue" with the same choices, applies an approved spec edit to the named file, and names dependents from the graph before any skip or reorder. Step 8 reports with the final wave's suite result when everything not skipped is ticked, and recommends `/freethinking:pr`. Run `make validate`
    - _Requirements: 5.1, 5.4, 5.5, 5.6, 5.7, 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3. Wire the skill into the handbook
  - [x] 3.1 Route the workflow rule to the skill
    - In `rules/workflow.md`, change the "Existing spec: follow it" bullet to run `/freethinking:implement-spec` and to describe stops as the author's cadence, after each task or each wave, with no checkpoint wording. Confirm the combined `rules/` text stays under 10,000 characters
    - _Requirements: 7.2, 7.7_
  - [x] 3.2 Add the README row
    - Add `implement-spec` to the skills table, in the same voice as the other rows and with no checkpoint wording, and mention `make eval-skill-implement-spec` where the README lists eval targets
    - _Requirements: 7.3, 7.7_
  - [x] 3.3 Bump the plugin version
    - Set `.claude-plugin/plugin.json` to `0.4.0` and run `make validate`
    - _Requirements: 7.6_

- [x] 4. Eval cases
  - [x] 4.1 Skill case: no spec recommends start-task
    - `evals/skills/implement-spec/no-spec-recommends-start-task/` with a `prompt.md` (`/freethinking:implement-spec link-shortener`, `runs: 1`, small `max_turns`) and graders: `regex` for `start-task`, `file_exists` with `exists: false` for `**/*`
    - _Requirements: 2.4, 3.6, 7.4_
  - [x] 4.2 Rule case: existing spec routes to implement-spec
    - `evals/rules/workflow/spec-routes-to-implement-spec/` with a prompt that says a `tasks.md` exists for the work and asks to continue it, and a `regex` grader for `implement-spec`
    - _Requirements: 7.2_
  - [x]* 4.3 Graph-validation case, if fixtures are supported
    - Check the plugin-evals docs for a way to seed files into the sandbox. If there is one, add `evals/skills/implement-spec/invalid-graph-stops/` with a fixture `tasks.md` whose graph omits a leaf task, and graders for a proposed corrected graph and no code written. If there is none, record that in the PR and skip
    - **Property 1: The Graph is a partition of the Leaf_Tasks**
    - **Validates: Requirements 1.1, 1.4, 2.5**
    - _Requirements: 2.5, 2.6_
  - [x] 4.4 Run the evals
    - `make eval-skill-implement-spec` and `make eval-rule-workflow`, each twice. Fix the case or the skill until both pass twice. Keep the printed tables for the PR's Testing section
    - _Requirements: 7.4_

- [x] 5. Manual check: run the skill on this spec
  - In a session started with `claude --plugin-dir .`, run `/freethinking:implement-spec implement-spec`. Confirm it reads the three files, shows the Leaf_Task and Graph tables with no validation errors, reports the first unticked task, and asks the start questions without changing any file. Stop there and record the transcript summary for the PR
  - _Requirements: 2.1, 2.5, 2.7, 3.1, 3.2, 3.4, 3.6_

## Notes

- Sub-tasks marked `*` are optional; implementation sub-tasks are never optional.
- `make validate` is the unit test and the full suite for this repository: run it after every change under `skills/`, `rules/` or `.claude-plugin/`, and at the end of every wave.
- Evals cost real model calls. Run them only at task 4.4, never after each edit.
- Task numbers identify tasks; the graph below decides the order. Review happens at the end of each task or each wave, by the author's cadence.
- Work on the `implement-spec-skill` branch, never on main.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2"] },
    { "id": 3, "tasks": ["2.3"] },
    { "id": 4, "tasks": ["3.1", "3.2", "3.3", "4.1", "4.2", "4.3"] },
    { "id": 5, "tasks": ["4.4", "5"] }
  ]
}
```
