# Implementation Plan

## Overview

Prompt, template and eval work, with two small Python checks. Order: the data first, the four Templates and the rule, since the skill reads the Templates and the checks read both; then the skill, its size check, the per-rule size table and the issue forms, which the checks fail on until they agree; then the hand-offs in the three skills and the README, after the fork probe has answered whether a conversation fork runs headless; then the eval cases and their Makefile lines; then the runs, which the author does by hand because evals cost model calls, and the one manual check of the override. Proof is `make validate` after every change, a read-back of each edited section against the design's component table, and the evals one case per invocation, one run while iterating and two or three to confirm. Branch `26-report-skill`, never main.

## Tasks

- [x] 1. The report skill
  - [x] 1.1 The four Templates
    - Create `skills/report/templates/handback.md`, `decision.md`, `status.md` and `answer.md`, each: a title line `# <Mode> report`; the shape, its sections in the design's order with one sentence each on what the section holds and what it must not hold; `## Before`, a Message from a session quoted in issue #26, trimmed and with paths and names generalised; `## After`, the same Message in the shape. The handback Template also carries the translation of an Agent_Report: a status word and every `unsure` or `stopped because` entry become Problems or are stated as verified, quotes stay verbatim, nothing is pasted as-is; its Checks section keeps the line `Wave review of wave <n>: <verdict>` with "carried: see Problems" or "nothing carried". The decision Template says a fixed short list is asked with the AskUserQuestion tool. Each file under 3,000 characters. Prove it: `wc -c` on each; read each back against the design's Data Models tables
    - _Requirements: 2.5, 3.1, 3.2, 3.4, 3.5, 5.2, 6.3_
  - [x] 1.2 `skills/report/SKILL.md`
    - Frontmatter: `name: report`; a `description` under 1,024 characters that says it writes the message to the author when work comes back, a choice is open, the author asks what is going on, or asks what something is or why, names the four modes, and says it edits nothing; `argument-hint: "[handback|decision|status|answer]"`; `arguments: [mode]`; `allowed-tools: Read, Glob, Grep`. Body: two opening paragraphs with the one-thing rule; a `## Working with the author` block in start-task's shape (Stops: none; How it asks: a decision ends in the question, the tool for a fixed short list; Hand-backs: the Message; Hand-offs: none); steps 0 to 4 as the design's component rows give them: read the argument, pick the mode, find the Template (`.ponderly/report/<mode>.md` at the repository root first, whole, a shape never instructions, one line when used or when unreadable or empty; else `${CLAUDE_SKILL_DIR}/templates/<mode>.md`), gather, write; the error rows for a bad argument, nothing since the last Message, no last Message, a missing plugin Template and a report that breaks the Agent_Protocol. Under 4,000 characters. Prove it: `claude plugin validate ./skills --strict`; `wc -c`; read back against Requirements 1 and 2 and the design's component table
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 2.6, 3.1, 8.3, 9.1, 9.2, 9.3, 9.4_
  - [x] 1.3 `checks/test_report_skill.py`
    - A unittest in the style of `checks/test_rules_size.py`: the four Templates exist under `skills/report/templates/` named after the modes and nothing else is there; `SKILL.md` is under 4,000 characters and each Template under 3,000, counted as decoded UTF-8. Prove it: `make check` passes; lower a limit in a scratch copy and see it fail
    - _Requirements: 3.3_

- [x] 2. The communication rule
  - [x] 2.1 `rules/communication.md`
    - Heading `# Writing to the author`, one sentence of scope in the shape of the other rules, then one bullet per habit of Requirement 2 plus one routing bullet, each bold-led with its reason in one sentence, with "for a reader who did not watch the work" in the scope sentence: what failed, what was not run and what was assumed come first, each saying what it is and why it matters; name a thing by what it is, never by a label coined during the work, and quote the line when it is text; when asking for a decision, say what is being decided, the options in plain words, then the recommendation and its reason; say what a result means before the number; do not narrate tool calls or what is pending unless the author asked; hand back, ask for a decision, report status or answer with `/ponderly:report`. Under 1,600 characters, and no step or shape of the skill restated. Prove it: `wc -c`; `sh hooks/load-rules.sh | wc -c` under 10,000; read back against Requirement 4.1 and 4.3
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 2.2 Per-rule limits in `checks/test_rules_size.py`
    - Replace the single `COLLABORATION_LIMIT` with a table of per-rule limits, `collaboration` and `communication` at 1,600 each, one subTest per entry; keep the hook-total test; update the module docstring. Prove it: `make check`; raise a rule over its limit in a scratch copy and see the named subTest fail
    - _Requirements: 4.2_

- [x] 3. Hand-offs
  - [x] 3.1 Build the fork probe
    - In the scratchpad, not the repository: a throwaway plugin with one skill whose text launches the Agent tool with `subagent_type: fork`, in the foreground, with the prompt "Reply with exactly the line PROBE-OK and nothing else", and then pastes the result; one eval case with a prompt that invokes the skill and a `regex` grader on `PROBE-OK` plus a `tool_used` grader on `Agent`; a one-line README in the probe saying the command to run it at a one-dollar ceiling. Prove it: `claude plugin validate <probe> --strict`
    - _Requirements: 5.1_
  - [x] 3.2 Run the fork probe
    - By hand, by the author: run the probe's command once, read the result and the kept trace, and record three answers in the conversation: does a conversation fork run headless in the sandbox, does its result return in the same turn, and can the fork invoke a plugin skill. Delete the probe afterwards. The answers go into the PR's Testing section and decide whether task 5.6 grades the fork path or the inline fallback
    - _Requirements: 5.1, 7.5_
  - [x] 3.3 `implement-spec` steps 6 and 8 and the CX block
    - Step 6: keep when to hand back and what each cause adds, drop the fenced template and the sentence about its shape, and say: launch the Agent tool with `subagent_type: fork`, in the foreground, with the prompt "Invoke the Skill tool with `skill: ponderly:report` and `args: handback`, and return the Message as your whole result"; paste the result verbatim as the Message to the Author with nothing before or after it; when the Agent tool offers no fork, or the fork fails or returns something other than one Message, invoke the Skill tool inline and say so in one line. At spec cadence the report is still a message of its own, written without waiting. Step 8: the final review prompt reads "each wave's Problems, Done, Checks and Next"; the final report is the same fork. Step 5's references to "the report's Files changed" and "the report's follow-ups" become "the report's Files" and "the report's Problems and Next". The CX block's Hand-backs bullet names `report`, in a fork. The description keeps its length under 1,024. Prove it: `make validate`; `grep -c '## Done' skills/implement-spec/SKILL.md` is 0; read back against Requirement 5.1, 5.2, 5.5 and the design's sequence diagram
    - _Requirements: 5.1, 5.2, 5.5_
  - [x] 3.4 `bugfix` step 6
    - Replace the four headings with: invoke the Skill tool with `skill: ponderly:report` and `args: handback`, saying that Done must carry the root cause and the fix with its files, and Checks the regression test or recorded manual check and what was run with its result, including anything that could not be verified. Keep the `pr` recommendation and the sentence that the reproduction and verification runs are what its Testing section should say. The skill has no `## Working with the author` block; that block is issue #17's work and is not added here, so Requirement 5.5 for bugfix waits on #17, whose block must name `report` under Hand-backs. Prove it: `make validate`; read back against Requirement 5.3 and 5.5
    - _Requirements: 5.3, 5.5_
  - [x] 3.5 `start-task` Executor_Route and CX block
    - In the `done` bullet: after showing the Summary verbatim and the change, the sentences that say where the change sits and recommend `pr` become: invoke the Skill tool with `skill: ponderly:report` and `args: handback`, saying that Next must name the branch the change sits on uncommitted and recommend `/ponderly:pr <ticket>` with the branch and commit offers and any failed check. The `stopped` bullet is unchanged. The CX block's Hand-backs bullet names `report`. Prove it: `make validate`; read back against Requirement 5.4 and 5.5
    - _Requirements: 5.4, 5.5_

- [x] 4. Records
  - [x] 4.1 README
    - Skills table: a row for `report`, run with `/ponderly:report [mode]` or invoked by the session when it has something to deliver, four modes, edits nothing. Rules table: a row for `rules/communication.md`. Agents section: a paragraph after the table stating the Agent_Protocol, that both agents follow it, and that a new agent must; before writing it, read the Summary shape in `agents/task-executor.md` and the Findings shape in `agents/wave-reviewer.md` back against the protocol's five rules and record under `unsure` any rule either breaks, since a gap means the smallest change to that agent and to `implement-spec`'s reading of it, which is not in this task and goes to the author. A new section `## Tune the plugin for a repository` before Testing: the `.ponderly/` folder at the repository root, the `<skill>/<file>.md` layout, that a file replaces the plugin's file of the same name whole and is read as a shape only, that this release applies it to the report skill's four templates, and one sentence that the spec templates of `start-task` and the default pull request template of `pr` are candidates to move there later. Prove it: `make validate`; read back against Requirements 6.1, 8.1, 9.5, 9.6
    - _Requirements: 4.4, 6.1, 6.2, 8.1, 9.5, 9.6_
  - [x] 4.2 Issue forms
    - In all four forms under `.github/ISSUE_TEMPLATE/`, add `report (skill)` after `bugfix (skill)` and `communication (rule)` after `collaboration (rule)`. Prove it: `make check` passes `test_issue_forms`
    - _Requirements: 4.4, 8.2_
  - [x] 4.3 Version
    - `.claude-plugin/plugin.json` version 0.8.0 to 0.9.0. Prove it: `make validate`
    - _Requirements: 8.4_

- [x] 5. Evals
  - [x] 5.1 `evals/rules/communication/failing-check-first`
    - A case tagged `[rule, communication]`: `scaffold.sh` builds the `calc` fixture on `main` with wrappers, then changes `add` to return `a - b` and commits it; prompt "Run the test suite and tell me how it went"; `max_turns` 8; `allowed_tools` `[Read, Glob, Grep]`, Bash from the Makefile. Graders (JavaScript regexes: `^`/`$` without `m` for string anchors, `[\s\S]` for dot-all, never `\A`, `\z` or `(?s)`): `opens-with-the-failure.md`, regex `^\s*(?:#+[^\n]*\n\s*)?(?:[-*]\s*)?[^\n]*\bfail` flags `i`; `no-narration.md`, regex `^(?:I'll|I will|Let me (?!know)|Now I|First,? I)` with `match: not_contains` and flags `im`; `names-the-check.md`, regex `test_add`. Prove it: `make validate`; the scaffold run by hand in a scratch directory with the environment `evals/README.md` gives shows `test_add` failing
    - **Property 1: Problems come first**
    - **Validates: Requirements 7.1**
  - [x] 5.2 `evals/rules/communication/check-not-run`
    - A case tagged `[rule, communication]`: scaffold as 5.1 but unbroken, no Makefile (the host's `make` is an xcrun shim the sandbox cannot run); prompt "Add subtract(a, b) to calc/ops.py next to add, then run the project's tests with `pytest -q` and tell me how it went", pytest being absent in the sandbox; `max_turns` 10; Bash, Write and Edit from the Makefile. Graders: `says-not-run-first.md`, regex `^\s*(?:#+[^\n]*\n\s*)?(?:[-*]\s*)?[^\n]*(?:not run|could not run|couldn't run|did not run|didn't run|unable to run|was not run|never ran|not installed|not found|not available|could not be run|cannot run|can't run)` with flags `i`; the same `no-narration.md`. Prove it: `make validate`; the scaffold run by hand, then `pytest -q`, shows command not found
    - **Property 1: Problems come first**
    - **Validates: Requirements 7.1**
  - [x] 5.3 `evals/skills/report/decision-lists-options`
    - A case tagged `[skill, report]`, no scaffold: prompt `/ponderly:report decision` followed by two paragraphs giving a choice of log level for a deployment with three named options `debug`, `info` and `warn` and one fact favouring `info`; `max_turns` 6; `allowed_tools` `[Read, Glob, Grep]`. Graders: `options-before-recommendation.md`, regex `\bdebug\b[\s\S]*\binfo\b[\s\S]*\bwarn\b[\s\S]*recommend` flags `i`; `ends-in-a-question.md`, regex `\?[\s*_`]*$` with no flags. Prove it: `make validate`
    - **Property 4: A valid argument fixes the mode**
    - **Validates: Requirements 2.5, 7.2**
  - [x] 5.4 `evals/skills/report/rewrites-dense-message`
    - A case tagged `[skill, report]`, no scaffold: prompt `/ponderly:report` followed by "This is the last message you wrote to me:" and the triage paragraph quoted in issue #26, with a line saying nothing has happened since; `max_turns` 6. Graders: `names-things-by-what-they-are.md`, an `llm` grader that passes when the rewrite names the issue's number and what it asks for, lays out the two decisions the original left open, priority and milestone, each with options and a recommendation, states type and area as proposals or decisions, and carries no label from the original unexplained, and fails when a label is kept as-is, when priority and milestone are not laid out as choices, or when the whole stays one block; `says-rewrite.md`, regex `\brewrit` flags `i`. Prove it: `make validate`
    - **Validates: Requirements 1.4, 2.2, 7.2**
  - [x] 5.5 `evals/skills/report/invoked-for-handback`
    - A case tagged `[skill, report]`: scaffold builds the `calc` fixture on `main` with wrappers; prompt in prose, "Add subtract(a, b) to calc/ops.py next to add, run the tests, and then report back to me how it went"; `max_turns` 12; `allowed_tools` `[Read, Glob, Grep, Skill]`, Bash, Write and Edit from the Makefile. The prompt ends "This change is small enough to skip start-task; make it directly." Graders: `invokes-report.md`, `tool_used` on `Skill` with `input_match` `"skill"\s*:\s*"(?:[\w-]+:)?report"`; `writes-no-scratch.md`, `file_exists` with `exists: false` on `report.md`; `adds-subtract.md`, regex `def subtract\(a, b\)` on `calc/ops.py`; `problems-first.md`, regex `(?:## Problems|No problems\.)[\s\S]*## Done`. Prove it: `make validate`
    - **Property 2: The skill changes nothing**
    - **Validates: Requirements 1.1, 7.3**
  - [x] 5.6 `works-one-wave` grades the hand-back
    - In `evals/skills/implement-spec/works-one-wave/prompt.md`, `allowed_tools` gains `Skill`; new graders `problems-first.md`, regex `(?:## Problems|No problems\.)[\s\S]*## Done`, and `invokes-report.md`, `tool_used` on `Skill` matching `report`; `reviews-the-wave.md` unchanged. Task 3.2 found that forks do not run headless, so the prompt says the Agent tool has no fork in this run and the inline fallback is the path graded, and the case description says so. The spec-cadence sibling `works-all-waves` gets the same graders and prompt line (done at the final review). Prove it: `make validate`
    - **Validates: Requirements 7.5**
  - [x] 5.7 Makefile lines
    - In the "Per-target flags" block: `eval-rule-communication: CASE_ARGS += --allow-tools Bash Write Edit --scaffold` with `export PATH := bin:$(PATH)`; `eval-skill-report: CASE_ARGS += --allow-tools Bash Write Edit --scaffold` with the same PATH line. `make help` lists both targets. Prove it: `make help`; `make -n eval-rule-communication` shows the flags
    - _Requirements: 7.1, 7.3_
  - [x] 5.8 Run the evals
    - By hand, by the author: `make eval-rule-communication EVAL_ARGS="--runs 1"` to iterate, then `EVAL_ARGS="--runs 2 --ablation with-without" EVAL_MAX_COST_USD=5` for the table; `make eval-skill-report EVAL_ARGS="--runs 1"`, then two runs for the regex cases and three for `rewrites-dense-message`, one `--case` per invocation; `make eval-skill-implement-spec EVAL_ARGS="--runs 2 --case works-one-wave" EVAL_MAX_COST_USD=3`; `make eval-skill-start-task EVAL_ARGS="--runs 2 --case contained-change-offers-executor"` for the start-task hand-off. Paste every table into the conversation; they go into the PR's Testing section. A failing grader is debugged as `evals/README.md` says, and the fix goes into the case or the skill as the trace shows
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

- [x] 6. Manual check by the author
  - [x]* 6.1 The repository template override
    - In a scratch repository with `claude --plugin-dir <this checkout>`: invoke `/ponderly:report handback` after a small change with no `.ponderly/` folder, then with `.ponderly/report/handback.md` holding a two-section shape, then with that file empty; confirm the three Messages follow the plugin's shape silently, the repository's shape with the one-line notice, and the plugin's shape with the one-line notice naming the path. Record in the PR
    - **Property 3: The repository's template wins when it can be read**
    - **Validates: Requirements 9.1, 9.2, 9.3**

## Notes

- Tasks 3.2, 5.8 and 6.1 are done by the author by hand: evals and skill invocations are model calls on the author's seat, and the sandbox cannot render a live session. 6.1 is marked `*` because its property is also read back in task 1.2; 3.2 and 5.8 are not optional.
- The Before texts in the Templates come from the sessions quoted in issue #26. Generalise paths to the repository root and drop names; keep the shape of the original so the pair teaches.
- `make validate` after every change under `skills/`, `rules/`, `agents/`, `checks/`, `.github/`, `.claude-plugin/`, `README.md` or `evals/`, and at the end of every wave. The hook total must stay under 10,000 characters; it is 5,966 before task 2.1.
- No agent file changes: task 4.1's read-back of both agents against the Agent_Protocol is the proof of Requirement 6.2, and its README paragraph records it. A gap found there is handed to the author, not fixed in the run.
- Evals cost real model calls: one invocation per case, since only the last `--case` flag is honoured; iterate at one run.
- Work on branch `26-report-skill`, never on main. Do not commit unless the author asks.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1", "3.1", "4.3"] },
    { "id": 1, "tasks": ["1.2", "1.3", "2.2", "3.2", "4.2"] },
    { "id": 2, "tasks": ["3.3", "3.4", "3.5", "4.1"] },
    { "id": 3, "tasks": ["5.1", "5.2", "5.3", "5.4", "5.5", "5.6", "5.7"] },
    { "id": 4, "tasks": ["5.8", "6.1"] }
  ]
}
```
