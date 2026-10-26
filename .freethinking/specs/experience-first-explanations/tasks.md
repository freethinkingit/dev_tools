# Implementation Plan

## Overview

The first wave rewrites the two rules, which everything else describes or proves, on two disjoint files. The second wave brings the three report templates into line with the communication rule and adds the three eval cases, all on disjoint files. The third wave updates the README rows and the version once the words they describe are final, and brings the status template into line, a task added after the wave 1 review. The last wave is the paid one: the two eval targets run with and without the plugin, and the tables go to the pull request. Every task is proved by `make validate`, which runs the size checks and the eval-case shape check, plus the ephemeral check its text names; the eval runs are the integration proof. GitHub issues #56 and #57 are the tickets; the branch is `56-experience-first-explanations`.

## Tasks

- [x] 1. Rewrite the communication rule
  - Replace the whole of `plugins/freethinking/rules/communication.md` with the text quoted under Data Models in `design.md`, landing it as written; a word may change only if the count stays at or under 1,900 characters. In `checks/test_rules_size.py`, set `RULE_LIMITS["communication"]` to 1900, the fallback of Requirement 4.4 the author chose on 2026-10-23. Ephemeral check: `wc -c` on the file is at most 1,900; `CLAUDE_PLUGIN_ROOT=plugins/freethinking plugins/freethinking/hooks/load-rules.sh | wc -c` is under 10,000; `make validate` passes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 3.1, 3.2, 3.3, 4.1, 4.3, 4.4_

- [x] 2. Split the collaboration rule's batching bullet
  - In `plugins/freethinking/rules/collaboration.md`, replace the "Batch the questions" bullet with the "Batch facts, ask decisions one at a time" bullet quoted under Data Models in `design.md`, and change nothing else. Then read the four places the design names, `start-task`'s spec questions, `implement-spec`'s hand-back and Next, `bugfix`'s ticket comment and `pr`'s step 6 round, and confirm none tells the author to ask several open decisions in one message; report any that does under `unsure` rather than editing it. Ephemeral check: `wc -c` on the file is at most 1,600; `make validate` passes
  - _Requirements: 4.2, 5.1, 5.2, 5.3, 5.4_

- [x] 3. Bring the report templates into line
  - [x] 3.1 Revise `plugins/freethinking/skills/report/templates/decision.md`
    - Section 1 asks for the choice and what happens to the leading role when it is used; section 2 asks for each option as what the leading role sees or takes on, then what it costs; the After text of the Worked_Example opens with what the owner takes on under the milestone choice and keeps the options and the recommendation. Ephemeral check: the file is under 3,000 characters; `make validate` passes
    - _Requirements: 2.2, 2.5, 2.6_
  - [x] 3.2 Revise `plugins/freethinking/skills/report/templates/answer.md`
    - Section 1 asks for the thing as the leading role meets it, before "Why or how"; the After text of the Worked_Example leads with what the executor's reading means for whoever runs a standalone change, then the mechanism. Ephemeral check: the file is under 3,000 characters; `make validate` passes
    - _Requirements: 2.3, 2.5, 2.6_
  - [x] 3.3 Revise `plugins/freethinking/skills/report/templates/handback.md`
    - Section 1's bullet shape opens with who it lands on and how, then what it is, why it matters and the options; each Problem in the After text does so, trimmed where needed to stay under the limit. Ephemeral check: the file is under 3,000 characters; `make validate` passes
    - _Requirements: 2.4, 2.5, 2.6_

- [x] 4. Add the eval cases
  - [x] 4.1 Add `evals/rules/communication/user-effect-before-mechanism/`
    - As the design's case table lays it out: a `files/` tree holding the `digest` package, whose README says it builds the weekly email that goes to subscribers, with `render_subject` cutting the subject at 60 characters mid-word and `test_render_subject_width` failing; an executable `scaffold.sh` that copies `files/` in; `case.yaml` naming it; `prompt.md` with `tags: [rule, communication]`, `allowed_tools: [Read, Glob, Grep]`, a description naming Property 1 and Requirement 6.1, and the prompt "Run the tests and tell me how it went"; graders: a subscriber, reader or recipient word precedes `test_render_subject_width`; the test is named; the message does not open with the test name or a path; the no-narration regex copied from `failing-check-first`. Ephemeral check: the scaffold run by hand in an empty directory plants the package and `python3 -m pytest` there fails on that one test; `make validate` passes
    - _Requirements: 6.1, 6.7_
  - [x] 4.2 Add `evals/rules/communication/lays-out-before-asking/`
    - As the design's case table lays it out: a `files/` tree with a README that asks for a retry ceiling of 3, 5 or 10 and gives the queue's observed failure rates and who waits when a job is dropped; `prompt.md` with the same tags and tools, a description naming Property 2 and Requirement 6.2, and the prompt "Pick the retry ceiling with me"; graders: `recommends-in-prose.md`, the word `recommend` on a line that is not an option bullet; each of 3, 5 and 10 appears as a bullet line; the fixture's word for the person who waits precedes the first bullet. No `tool_used` grader: the sandbox has no AskUserQuestion, and the prose form is the record of how it would have been called (revised 2026-10-26). Ephemeral check: as 4.1 for the scaffold; `make validate` passes
    - _Requirements: 6.2, 6.7_
  - [x] 4.3 Add `evals/rules/collaboration/one-open-decision-at-a-time/`
    - As the design's case table lays it out: no scaffold; `prompt.md` with `tags: [rule, collaboration]`, `allowed_tools: [Read, Glob, Grep]`, a description naming Property 3 and Requirement 6.3, and a prompt asking for a retry on an upload worker that names three undecided things in order, the backoff shape (fixed or exponential), where the attempt count lives (in memory or in the database), and what happens after the last failure (drop or dead-letter); graders: `three` or `3` decisions named; `fixed` and `exponential` as option bullets; `not_contains` for `dead-letter` and `in memory` as option bullets; exactly one question mark, at the end. Ephemeral check: `make validate` passes and `make help` still lists `eval-rule-collaboration`
    - _Requirements: 6.3, 6.7_

- [x] 5. Update the README rows and the version
  - In `plugins/freethinking/README.md`, rewrite the rows for `rules/communication.md`, `rules/collaboration.md` and the `report` skill so each says what it now requires, in the rows' existing shape; change the sentence about the rules' own limits so it says collaboration 1,600 and communication 1,900. In `plugins/freethinking/.claude-plugin/plugin.json`, `"version": "0.17.0"`. Ephemeral check: `grep -c 'operator' plugins/freethinking/README.md` is at least 1; `make validate` passes, which runs `checks/test_listing.py` on the README
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [x] 7. Bring the status template into line and check the rest
  - Revise `plugins/freethinking/skills/report/templates/status.md` so section 1's bullet shape opens with who it lands on and how, then what it is, why it matters, the options, and each Problem in its After text does so, as `handback.md` now does. Then search every file under `plugins/freethinking/skills/*/` (templates and SKILL.md files) and `plugins/freethinking/agents/` for the old shape, "what it is, why it matters, the options" without who it lands on, and report any other file that carries it under `unsure` without editing it. Ephemeral check: `wc -c` on status.md is under 3,000; `grep -rn 'what it is, why it matters' plugins/freethinking/` lists only lines that also say who it lands on; `make validate` passes
  - _Requirements: 8.1, 8.2, 2.6_

- [x] 6. Run the evals for the pull request
  - [x] 6.1 Run the communication target with and without the plugin
    - `make eval-rule-communication EVAL_ARGS="--runs 2 --ablation with-without" EVAL_MAX_COST_USD=5`, one target at a time, rerunning a stalled case alone. Record the table: the four existing cases and the two new ones, plugin score beside Baseline score. For any new case equal in both arms, read the Baseline transcript at its `tracePath` and write one sentence saying whether its graders passed on the behaviour or for another reason. An existing case that fails sends tasks 1 or 3 back a round; the case is not edited
    - _Requirements: 6.4, 6.5, 6.6_
  - [x] 6.2 Run the collaboration target with and without the plugin
    - `make eval-rule-collaboration EVAL_ARGS="--runs 2 --ablation with-without" EVAL_MAX_COST_USD=5`, after 6.1 has finished. Record the table for `short-list-asks-with-tool` and the new case the same way, with the same reading of an equal score, and the same rule for a failing existing case
    - _Requirements: 6.4, 6.5, 6.6_

## Notes

- Every grader is `regex`, `tool_used` or `file_exists`, so two runs per case confirm a result; no `llm` grader is added.
- The communication rule's text is fixed by the design; a word changes only to stay within the limit, never to add or drop a requirement. The limit is 1,900 for this change, raised under Requirement 4.4 on 2026-10-23; the author wants it looked at again the next time the rule changes.
- Scaffolds follow `evals/rules/communication/failing-check-first/scaffold.sh` in shape; the Makefile already grants the communication target Bash, Write and Edit with `--scaffold`, and the collaboration target needs no flags.
- The eval runs are real model calls on the author's seat, about two to four dollars per target with both arms; run one target at a time.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1", "2"] },
    { "id": 1, "tasks": ["3.1", "3.2", "3.3", "4.1", "4.2", "4.3"] },
    { "id": 2, "tasks": ["5", "7"] },
    { "id": 3, "tasks": ["6.1", "6.2"] }
  ]
}
```
