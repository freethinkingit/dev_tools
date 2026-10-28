# Implementation Plan

## Overview

Rules first, because the skill's CX block refers to the collaboration rule and the free checks cap the rules' size. Then the skill change, then the eval cases and the probe of how the eval harness treats an interactive question, then README, forms, version and the runs. The handbook has no code and no unit-test framework beyond the stdlib `unittest` files under `checks/` that `make validate` runs; one such check is added here. Behaviour is proved by eval cases, run by hand at the task that says so, and by one manual session the author runs. Nothing here touches `implement-spec`, `bugfix` or `pr`, whose CX blocks are issues #16, #17 and #18.

## Tasks

- [x] 1. The rules
  - [x] 1.1 Write `rules/collaboration.md`
    - Heading "Working with the author", a one-line scope sentence, then six bold-led bullets in the voice of `rules/code-changes.md`: ask with the AskUserQuestion tool when the answers are a short fixed list, offering the options plus free text, and in prose when the answer is the author's own words; batch questions into one round unless an answer decides the next question; state the plan in two or three sentences before acting; approval is explicit and "looks good" with a "but" is a change request; report failures and anything not run before any recommendation; a skill that ends says where the work is and which skill is next. Under 1,600 characters. Prove it with `wc -c`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  - [x] 1.2 Rewrite the routing bullets of `rules/workflow.md`
    - Replace the "New feature or sizeable task" bullet with the design's bullet 5, "Anything else that changes code: start the task", placed after "Small changes stay small"; retitle the bug bullet "Bug named: reproduce before fixing"; leave the spec, PR, default-branch and keep-in-the-loop bullets as they are. No bullet other than "Small changes stay small" asks Claude to judge size. Prove it by reading the file back and by `sh hooks/load-rules.sh | wc -c`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
    - Wave 1 fix, agreed at the wave 0 hand-back: add "The first bullet that matches the request is the route." under the rule's heading, and a clause in `.github/CONTRIBUTING.md`'s "Make a change" passage saying `start-task` proposes the branch name on every route
  - [x] 1.3 Add `checks/test_rules_size.py`
    - A stdlib `unittest` file in the style of `checks/test_issue_forms.py`: one test runs `hooks/load-rules.sh` with `CLAUDE_PLUGIN_ROOT` set to the repository root and asserts its output is under 10,000 characters; one asserts `rules/collaboration.md` is under 1,600. Failure messages give the measured count. Run `make check`
    - **Property 4: Rules fit the hook**
    - _Requirements: 4.4, 6.8_
  - [x] 1.4 Add `collaboration (rule)` to the three issue forms
    - In `.github/ISSUE_TEMPLATE/eval-case.yml`, `misbehaving-skill-or-agent.yml` and `proposal.yml`, insert `collaboration (rule)` into the component dropdown directly after `code-changes (rule)`, since the check sorts rule stems alphabetically. Run `make check`
    - **Property 5: Forms match disk**
    - _Requirements: 6.1_

- [x] 2. The skill
  - [x] 2.1 Add the CX block and the triage step to `skills/start-task/SKILL.md`
    - Frontmatter `description`: add that the skill is the front door for any request to change code and decides between the executor, bugfix and a spec. After "Ground rules", a section "Working with the author" with the design's four bullets: stops, how it asks (AskUserQuestion with fixed options at every stop; the step 3 spec questions in prose), hand-backs, hand-offs; state only what is specific to this skill. In step 1, say that an existing spec directory means Spec_Route with no triage, and that beside the task name the skill proposes a branch name in the contributing guide's shape (issue number and task name when the request names or links an issue, task name alone otherwise) without creating it; the CX block's hand-offs bullet says the author or `implement-spec` creates it. Split step 2 into "2. Read the code" (today's first paragraph) and "3. Triage" with: the three routes and the Contained_Change and defect definitions from the requirements glossary; state the chosen route and the reason in two or three sentences naming the code read; on Bug_Route or Executor_Route put one AskUserQuestion, header `Route`, chosen route first marked "(Recommended)", `Spec_Route` second, each with a one-sentence description, and act only on the answer; take the author's route without arguing; on Spec_Route say so in one sentence and continue; if the free-text answer is neither route, restate the two in a sentence and ask once more. Renumber the later steps and the spec questions move to the head of the requirements step. Run `make validate`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10_
    - Wave 4 fix, found in the manual session: a fit check in triage. When the request extends nothing in the codebase, the route statement says so and a question with header `Fit` offers `Spec it here` and `Wrong repository` before any spec question; on the second the skill stops and says where the work belongs if known. The CX block's Stops bullet lists it. Eval case `evals/skills/start-task/wrong-repo-asks-fit/`: calc scaffold, the link-shortener prompt, graders for the two options as list items, no spec written, no Agent or Skill call (Requirement 1.11)
  - [x] 2.2 Write the Bug_Route and Executor_Route paths in the triage step
    - Bug_Route: invoke the Skill tool with `freethinking:bugfix` and the request as its argument, then stop; do not reproduce, diagnose or fix. Executor_Route: launch the Agent tool once with `subagent_type: freethinking:task-executor` and the design's Launch_Prompt (request verbatim, context found as `path: what is there`, the author's free-text additions, then "Make only this change. Commit nothing. Return the Summary."), with no sentence saying the task comes from a spec; edit no source file, commit nothing, create no branch. On `status: done`: show the Summary verbatim, run `git diff -- <files changed>` and show it, name any failed check before anything else, then recommend `/freethinking:pr`. On `status: stopped`: show the Summary and put one AskUserQuestion offering "answer and relaunch" and "Spec_Route"; never relaunch unprompted. If either plugin component is missing, say so and stop. Run `make validate`
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 3. The eval cases
  - [x] 3.1 Probe how the eval harness treats AskUserQuestion
    - In the scratchpad, make a one-case plugin whose only skill puts an AskUserQuestion, run `claude plugin eval` on it with `allowed_tools` including `AskUserQuestion` and `max_turns: 3`, and record in the task's result: whether the tool is callable headless, whether the harness answers it or ends the turn, whether a `tool_used` grader with `tool: AskUserQuestion` counts it, and whether the transcript a `regex` grader sees contains the question's option labels. Delete the scratch plugin. The answer decides the question grader's shape in 3.2, 3.3 and 3.5
    - _Requirements: 5.3, 5.4, 6.10_
  - [x] 3.2 Eval case `evals/skills/start-task/contained-change-offers-executor/`
    - `case.yaml` with `scaffold_script: scaffold.sh` copying `evals/fixtures/calc` into the workspace, as the implement-spec and task-executor cases do; `prompt.md` with tags `[skill, start-task]`, `max_turns: 6`, `allowed_tools: [Read, Glob, Grep, AskUserQuestion, Agent, Skill]`, prompt `/freethinking:start-task Add subtract(a, b) to calc/ops.py returning a minus b, in the style of add`; graders: regex `(?i)executor` on the output; `file_exists` `.claude/specs/**` false; `tool_used` Agent max 0; `tool_used` Skill max 0; the question grader in the shape 3.1 found. Add `eval-skill-start-task: CASE_ARGS += --scaffold` to the Makefile's per-target block. Wave 2 fix, agreed at the wave 2 hand-back: the Makefile line becomes `CASE_ARGS += --allow-tools Write Edit --scaffold`, which per `evals/README.md` is the only way a case gets those tools, so the no-write graders can fail; the cases' `allowed_tools` stay read-only (Requirement 5.11)
    - **Property 1: No document before the answer**
    - **Property 3: Standalone launch**
    - _Requirements: 5.3_
  - [x] 3.3 Eval case `evals/skills/start-task/bug-offers-bugfix/`
    - Same scaffold, but the script then rewrites `add` in `calc/ops.py` to return `a - b`; prompt `/freethinking:start-task calc.add(2, 3) returns -1; it should return 5`; graders: regex `(?i)bug`; regex `return a - b` on `calc/ops.py` (the defect is still there); `tool_used` Skill max 0; `file_exists` `.claude/specs/**` false; the question grader
    - **Property 1: No document before the answer**
    - _Requirements: 5.4_
  - [x] 3.4 Keep `evals/skills/start-task/names-task-and-asks/` on Spec_Route
    - Prompt unchanged; `expected_outcome` says the skill states Spec_Route in one sentence before proposing the task name and a branch name and asking its questions; `allowed_tools` adds `AskUserQuestion` if 3.1 found it callable. Check `evals/rules/workflow/bug-routes-to-bugfix/prompt.md` names the request as a bug in the author's words, and change the prompt only if it does not
    - _Requirements: 5.5, 5.6_
  - [x] 3.5 Eval case `evals/rules/collaboration/short-list-asks-with-tool/`
    - `prompt.md` with tags `[rule, collaboration]`, `max_turns: 4`, `allowed_tools: [Read, Glob, Grep, AskUserQuestion]`, a prompt that asks Claude to set a log level in a config file to one of three named levels without saying which, so it must ask; graders: the question grader, plus a regex that the three level names appear. The new `eval-rule-collaboration` target comes from the Makefile's directory enumeration and needs no Makefile change
    - _Requirements: 6.10_

- [x] 4. Docs and version
  - [x] 4.1 README rows
    - Skills table, `start-task` row: it is the front door for any change, reads the code, and decides between the executor for one contained change, `bugfix` for a defect and a spec for the rest, asking before the first two. Rules table, `rules/workflow.md` row: route on what the author said or a file on disk, default to `start-task`. New row for `rules/collaboration.md` after the `comments` row, in the voice of the others. The Rules paragraph's sentence on the 10,000-character limit gains "and `make validate` fails when they go over". Nothing else in the README changes
    - _Requirements: 5.1, 5.8, 6.9_
    - Wave 2 fix, agreed at the wave 2 hand-back: the README's Testing section describes the checks as the `unittest` files under `checks/` that `make check` discovers, each one concern named by its module docstring, with no list of file names; the README's Agents section and the `description` in `agents/task-executor.md` name `start-task` as a launcher of the executor beside `implement-spec`
    - _Requirements: 5.9, 5.10_
  - [x] 4.2 Version `0.6.0`
    - `.claude-plugin/plugin.json` version to `0.6.0`. Run `make validate`
    - _Requirements: 5.2_

- [x] 5. Runs
  - [x] 5.1 Run the evals
    - `make eval-skill-start-task EVAL_ARGS="--runs 2"`, `make eval-rule-workflow EVAL_ARGS="--runs 2"`, `make eval-rule-collaboration EVAL_ARGS="--runs 2"`. Fix the case or the skill until each case passes both runs, and record the three result tables for the PR's Testing section
    - Run on 2026-10-13: first pass found the harness rejects inline `(?i)` (two graders switched to `flags: i`) and that the prose route question does not always end in `?` (the `\?` grader dropped from the two route cases, whose option graders prove the question). Second pass: all nine cases 100% on both runs, $2.18 total
    - _Requirements: 5.3, 5.4, 5.5, 5.6, 6.10_
  - [x] 5.2 Manual session, done by the author
    - In a session started with `claude --plugin-dir .` in a scratch copy of `evals/fixtures/calc`, run the contained-change prompt, the bug prompt and the link-shortener prompt by hand. Confirm the Route question renders as the interactive form, that answering Spec_Route continues to the spec questions, and that accepting Executor_Route ends with the Summary, the diff and the `pr` recommendation. Record what was seen in the PR
    - **Property 2: The Author's answer is the Route**
    - _Requirements: 1.4, 1.6, 3.4, 5.7_
    - Run on 2026-10-13. Headless first, with `claude -p --plugin-dir` against four calc workspaces: the contained change answered Executor_Route ran the executor and ended with the Summary, the diff, the branch-and-commit line and the `pr` recommendation; the same change answered Spec_Route went to four task-sized spec questions; the unnamed defect named `add` at `calc/ops.py:2`, offered Bug_Route, and after the answer `bugfix` reproduced it and stopped to confirm the cause; the link shortener went straight to spec questions, which exposed the missing fit check, added as Requirement 1.11 with its eval case. Then interactively by the author: the Fit form rendered and Wrong repository stopped with nothing written; the Route form rendered and Executor_Route ran through to the `pr` recommendation

## Notes

- Every file here is prose or YAML; "the project's style" means the voice and shape of the neighbouring file, which the executor reads first.
- `make validate` is the free check and runs after every task that touches a manifest, a form, a check or a skill; evals run only at task 5.1.
- The question grader's exact shape is unknown until task 3.1 reports; tasks 3.2, 3.3 and 3.5 take it from that report.
- Issue #1 is the ticket for this work; the branch is `1-standalone-task-routing` and the PR closes #1.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "3.1"] },
    { "id": 1, "tasks": ["1.3", "1.4", "2.1", "3.4", "3.5", "4.2"] },
    { "id": 2, "tasks": ["2.2", "3.2", "3.3", "4.1"] },
    { "id": 3, "tasks": ["5.1"] },
    { "id": 4, "tasks": ["5.2"] }
  ]
}
```
