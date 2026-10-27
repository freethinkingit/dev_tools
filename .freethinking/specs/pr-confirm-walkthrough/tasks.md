# Implementation Plan

## Overview

The skill file is rewritten in two sittings on two waves, the parts that frame the walkthrough first, then the walkthrough itself, so that the second task reads the first's text on disk. The eval cases and the check of the existing cases' wording run in the second wave beside it, on disjoint files, and the README row and version follow once the skill's words are final. The last wave is the paid one: the pr target with both arms, whose table goes to the pull request. Every task is proved by `make validate`, which runs the description, listing and eval-case checks, plus the ephemeral check its text names; the eval run is the integration proof. GitHub issues #69, #45 and #55 are the tickets; the branch is `69-pr-explains-each-change`.

## Tasks

- [x] 1. Rewrite the pr skill
  - [x] 1.1 Frame the walkthrough: description, "Working with the author", step 1 and step 4
    - In `plugins/freethinking/skills/pr/SKILL.md`: rewrite the `description` so it says the skill explains each change as the user and the owner experience it and asks the author to confirm or correct, drafts a branch built from a ticked spec from the spec and its reports, gives a mechanical change one question, never re-asks an answered question, and puts the branch, commit, Closes and draft questions in one call; under 1,024 characters. Rewrite the "Working with the author" block's Stops and How it asks to the design's components row for it. In step 1, keep every stop and the facts, and change the `current branch` and `uncommitted changes` bullets so they note what they found for the fixed-choice call instead of asking; the sentence that nothing is committed, branched or pushed without the author's yes stays. In step 4, after the three groups, add the Ticked_Spec test and the Mechanical_Group sort, in the words of the design's Data Models. Leave steps 5 to 9 as they are for task 1.2. Ephemeral check: `checks/test_descriptions.py` passes under `make validate`; `grep -c 'take no pre-filled answers'` on the file is unchanged from today (that sentence is task 1.2's); the two step 1 bullets no longer say "Ask with the AskUserQuestion tool"
    - _Requirements: 1.1, 1.2, 1.4, 1.5, 4.1, 5.1, 5.3, 8.1_
  - [x] 1.2 Rewrite the walkthrough: steps 5 to 9
    - In the same file: replace step 5 with the Confirm_Form and the Spec_Form as the design's Architecture and Data Models give them, the form named in one line before the first group; the Confirm_Form's Explanation per group with its five parts, every group in one message or two or three messages past five groups, the confirmation question naming each group, the Review_Prompts on request, the why asked alone when it cannot be inferred and the Marker when declined, the Mechanical_Group's one question, answers taken from the session or the request and named, the self-explanatory bullet; the Spec_Form's one message of groups by task with drafted why, and the fallback when no reports are in the conversation. Replace step 6 with the one prose round for both forms and the ticket-in-prose Closes exception. Add a step after it, "The fixed choices", with the one AskUserQuestion call of the design's Data Models. In steps 7 to 9, change the Changes-bullet rules to the design's Changes bullet, remove "take no pre-filled answers" and "Do not propose an answer to any prompt", keep the title, template, name-once, approval and `gh` rules. Renumber the steps. Ephemeral check: `grep -c 'take no pre-filled answers\|Do not propose an answer'` on the file prints 0; `grep -c 'anything a reviewer should know'` prints at least 1; the step headings are numbered in order by `grep -n '^## '`; `make validate` passes
    - _Requirements: 1.3, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.4, 6.1, 6.2, 6.3, 6.4_

- [x] 2. Prove both forms with eval cases
  - [x] 2.1 Rewrite `evals/skills/pr/opens-pr-with-ticket/`
    - Change the prompt's advance text to a Confirmation: the author cannot answer during the run, confirms every explanation as written with one correction, that the why is that the CLI needed a greeting helper, says merging finishes the ticket, not a draft, and treats the draft as approved; rewrite `description` and `expected_outcome` to match and to name Requirement 7.1. Rename `graders/carries-authors-words.md` to `carries-confirmed-words.md` with an `input_match` that the `## Changes` section holds "greeting helper". Keep the other graders and the scaffold. Ephemeral check: `make validate` passes; the scaffold still runs by hand in an empty directory
    - _Requirements: 7.1, 7.7_
  - [x] 2.2 Add `evals/skills/pr/explains-and-asks-to-confirm/`
    - Copy the `opens-pr-with-ticket` scaffold; a prompt of `/freethinking:pr` with nothing in advance; `description` naming Property 1 and Requirement 7.2; graders as the design's case table: the user's or the owner's experience named after the first group's heading line and before the mechanism (`greet`, `return` or `Hello`); "confirm" and "correct" in a question; both groups named in the first message; `not_contains` "What would break it"; `tool_used` Bash `max: 0` with `input_match` on `gh pr create`. Ephemeral check: the scaffold runs by hand; a node scratch check of each regex against a sample message that follows the design and one that lists the five prompts; `make validate` passes
    - _Requirements: 7.2, 7.7_
  - [x] 2.3 Add `evals/skills/pr/drafts-from-ticked-spec/`
    - Copy the scaffold and, on the `add-greeting` branch, commit `.freethinking/specs/add-greeting/requirements.md`, `design.md` and `tasks.md`, the task list with two ticked tasks naming `demo/greeting.py` and `tests/test_greeting.py` and a valid waves block; a prompt of `/freethinking:pr #7` with nothing in advance; `description` naming Property 3 and Requirement 7.3; graders: names the spec and the Spec_Form in the first walkthrough message; a group named by task 1 or its title; `not_contains` "What would break it"; asks about risk or review focus; `tool_used` Bash `max: 0` on `gh pr create`. Ephemeral check: as 2.2
    - _Requirements: 7.3, 7.7_
  - [x] 2.4 Add `evals/skills/pr/one-question-for-a-version-bump/`
    - Copy the scaffold and add a third commit on the branch that bumps a version line in `demo/__init__.py`; a prompt of `/freethinking:pr #7` with the advance text of the design's case table; `description` naming Property 2 and Requirement 7.4; graders: the version-bump group gets "anything a reviewer should know" or its answer taken; "reviewer should know" occurs at most once; `tool_used` Bash on `gh pr create` with `input_match` on a Changes bullet naming the version. Ephemeral check: as 2.2
    - _Requirements: 7.4, 7.7_
  - [x] 2.5 Read the existing pr cases for wording the move of the offers breaks
    - Read the prompts and graders of `offers-branch-on-default`, `offers-commit-on-dirty-tree`, `opens-pr-with-stub-gh`, `follows-repo-template` and `stops-at-starting-checks`; change only a `description` or `expected_outcome` sentence that says the offer is made at the start or before the walkthrough, so it says the offer comes in the one call after the walkthrough; change no grader. Report any grader that would fail under the new order under `unsure`. Ephemeral check: `make validate` passes; `git diff --stat` touches only `prompt.md` files
    - _Requirements: 7.5, 7.7_
  - [x] 2.6 Let the two offer cases reach the offer
    - In `evals/skills/pr/offers-branch-on-default/prompt.md` and `evals/skills/pr/offers-commit-on-dirty-tree/prompt.md`, change the prompt body so the run reaches the fixed-choice call where the offer now lives: give in advance that the author cannot answer during the run, a confirmation of every group as explained, and the prose round's answers (no ticket, testing not seen, no risk, no review focus); replace "stop at the first question you ask and wait for me" with "stop at the branch, commit, Closes and draft questions and wait for me"; raise `max_turns` to 20. Change no grader. Ephemeral check: `make validate` passes; `git diff --stat` touches only the two `prompt.md` files
    - _Requirements: 7.5, 7.7_

- [x] 3. Update the README row and the version
  - In `plugins/freethinking/README.md`, rewrite the `pr` row so it says what the skill now does, in the row's existing shape. In `plugins/freethinking/.claude-plugin/plugin.json`, set the version to the next minor above `main`'s at the time of the task: 0.18.0 if `main` holds 0.17.0, else 0.17.0, and say which in the Summary. Ephemeral check: `grep -c 'confirm' plugins/freethinking/README.md` is at least 1; `make validate` passes
  - _Requirements: 8.2, 8.3, 8.4_

- [x] 4. Run the pr target for the pull request
  - `make eval-skill-pr EVAL_ARGS="--runs 2 --ablation with-without --keep-temp" EVAL_MAX_COST_USD=12`, one target, after every other task is ticked. Record the table of all nine cases, plugin beside Baseline. For any case equal in both arms, read the Baseline's `trace.jsonl` and write one sentence saying whether its graders passed on the behaviour or for another reason. An existing case that fails sends task 1 or 2.5 back a round; the case is not edited to pass. Remove the kept sandboxes afterwards
  - _Requirements: 7.5, 7.6_

## Notes

- Every grader is `regex` or `tool_used`, so two runs per case confirm a result; no `llm` grader is added.
- The eval sandbox has no AskUserQuestion: the fixed-choice call and the confirmation question appear in prose with the options on separate lines, which is what the graders read. A bullet regex must require whitespace after the marker so a bold line is not taken for a bullet.
- Scaffolds copy `evals/skills/pr/opens-pr-with-ticket/scaffold.sh`; the Makefile's pr target already grants Bash, runs the scaffold and puts `bin` on the PATH.
- The pr target costs about one dollar per case with both arms and two runs; the run in task 4 is on the author's seat.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6"] },
    { "id": 2, "tasks": ["3"] },
    { "id": 3, "tasks": ["4"] }
  ]
}
```
