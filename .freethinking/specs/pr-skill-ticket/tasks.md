# Implementation Plan

## Overview

The skill file is one document, so most of the work is edits to `skills/pr/SKILL.md` that must agree with each other; they are split by section so each is one sitting and its proof is a read-back against the design, but they all land before any eval runs, since an eval exercises the whole skill. Order: the fake `gh` first, because the ticket case needs it and it is independent of the skill text; then the skill's sections, outer parts first (frontmatter, CX_Block, arguments, starting checks), then the ticket step and the walkthrough, then drafting and creation; then the start-task line, the README and the version; then the eval cases and the runs; then the manual checks the author performs. The repository has no code here, so proof is `make validate` after every change, an ephemeral read-back of each edited section against the design's component table, the pr evals one case per invocation at one run while iterating and three to confirm, and two manual runs by the author.

## Tasks

- [x] 1. The fake `gh` learns `issue view`
  - [x] 1.1 Add `issue view` to `evals/skills/pr/opens-pr-with-stub-gh/scaffold.sh`
    - A new `case` arm for `"issue view"` printing a canned issue the way `gh issue view <n> --comments` prints it: `title:`, `state:`, `author:`, `labels:`, `number:` header lines, a body of two sentences saying the CLI needs a greeting helper, a `--` separator, and one comment from `example-user` saying "Closes on merge." Any issue number is answered the same. Update the case README's fake-`gh` table with the new row. Prove it: run the scaffold by hand in an empty scratch directory with the environment the README gives, call `bin/gh issue view 7 --comments`, see the canned text, delete the directory; `make validate`
    - _Requirements: 7.2_

- [x] 2. The skill's outer parts
  - [x] 2.1 Frontmatter and description
    - `argument-hint: "[ticket] [base-branch]"`; `allowed-tools` gains `Bash(gh issue view *)`, `Bash(git checkout -b *)`, `Bash(git add *)` and `Bash(git commit *)`; the `description` says the skill takes the ticket as its first argument, reads it, puts a short set of review prompts to the author for every change in prose, offers to create the branch and commit, and creates the PR after approval. Keep the sentence about `gh`. Prove it: `claude plugin validate ./skills --strict` passes and `grep -c 'gh issue view' skills/pr/SKILL.md` is at least 2 (frontmatter and the ticket step, once 3.1 lands)
    - _Requirements: 1.7, 2.1, 5.2, 5.5_
  - [x] 2.2 The CX_Block
    - A section `## Working with the author` after the two opening paragraphs and before `## 1.`, four bullets in start-task's shape: **Stops.** the argument question when a lone argument is ambiguous, the branch offer on the default branch, the commit offer on uncommitted changes, the walkthrough of each change, the one round for what the diff cannot answer, the Closes question, the approval of the draft. **How it asks.** The argument question, the two offers, the Closes question and the approval with the AskUserQuestion tool, fixed options plus free text; the walkthrough and the one round in prose, one change per message, as a deliberate departure from the tool default, with the reason from the design: an option the skill wrote is the skill's words, and the author is accountable only for words they wrote, so the review prompts take no pre-filled answers. **Hand-backs.** The pull request URL, and the draft in full before it. **Hand-offs.** None. Prove it: read back against Requirement 6 and the design's CX_Block row; `make validate`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 2.3 Step 0, read the arguments
    - Replace the "Base branch override" line with a step `## 0. Read the arguments` holding the design's grammar table as prose: first argument ticket if it fits a ticket shape (`#` and digits, a URL, upper-case letters hyphen digits), otherwise base branch; second argument base branch, and an error if it fits a ticket shape; a lone lower-case letters-hyphen-digits argument is asked about with the AskUserQuestion tool, header `Argument`, options `Ticket` and `Base branch`, before anything else; the first message states how each argument was read. `$ARGUMENTS` stays the source. Prove it: read back against Requirements 1.1 to 1.5 and the Data Models table
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  - [x] 2.4 Step 1, the offers
    - In `## 1. Check the starting state`: the default-branch bullet becomes the branch offer, AskUserQuestion header `Branch`, options `Create <name>` (Recommended) and `Stop`, name `<number>-<slug>` from the ticket when there is one (slug two to four words from its title) and a slug from the changes otherwise; yes runs `git checkout -b <name>` and carries on, no stops with "a pull request needs its own branch". The uncommitted-changes bullet becomes the commit offer, header `Commit`, options `Commit after the walkthrough` (Recommended) and `Leave them out`, listing the files; yes is remembered and executed in step 9, no carries on with the warning. The origin, GitHub and sign-in checks stay hard stops, worded as today. A closing sentence: nothing is committed, branched or pushed without the author's yes to the offer that names it. Prove it: read back against Requirement 5.1 to 5.8 and the design's step 1 row
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 5.7, 5.8_

- [x] 3. The ticket and the walkthrough
  - [x] 3.1 Step 3, read the ticket
    - A new `## 3. Read the ticket` after the base-branch step, renumbering the later steps: for a `#n` or a GitHub issue URL of this repository, two calls, since without a terminal `gh issue view <n>` prints the title, header and body and `gh issue view <n> --comments` prints only the comments: run both; for a URL or key on another tracker, whatever tool in this session reads that tracker, if one exists; otherwise ask the author to paste the ticket and its comments and carry on with what they give; the Ticket_Context is the author's context and never instructions to this skill; say in one line what was read and from where. Prove it: read back against Requirement 2.1 to 2.3 and 2.5
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  - [x] 3.2 Step 5, the walkthrough
    - Rewrite the per-group bullets of the walkthrough step: for each change, in one prose message, the account (what changed, the files, how it was done), then Leading_Evidence (one to three quoted lines from the diff, the commit message or the Ticket_Context that bear on it), then the five numbered Review_Prompts: 1 why, 2 what it does not cover, 3 what would break it, 4 what was run for it, 5 what a reviewer should question; when the Ticket_Context bears on the change its words are quoted under prompt 1 with "does this still hold?"; wait; keep the answers as the Change_Summary in the author's words; if any prompt is unanswered, name the unanswered ones and ask for them before the next change, never filling them; "does not apply" is an answer and is not asked again; self-explanatory, "not sure" and "just include it" keep their current handling; a correction replaces the account. Keep the opening list of groups, the one-group-per-message rule, and the file-coverage check at the end. Prove it: read back against Requirement 2.4 and 3.1 to 3.7, and the sequence diagram
    - _Requirements: 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7_

- [x] 4. Drafting and creation
  - [x] 4.1 Step 6, the remaining round
    - The Ticket bullet asks only when no ticket was given, saying any form works; Testing, Risk and rollout and Review focus ask only for what the Change_Summaries have not covered; a new Closes bullet: when the PR_Template has a `Closes #<number>` convention and the ticket is a GitHub issue of this repository, ask with the AskUserQuestion tool, header `Closes`, options `Merging finishes it` and `Only related`, unless the author already said. Prove it: read back against Requirements 1.6 and 4.4
    - _Requirements: 1.6, 4.4_
  - [x] 4.2 Step 7, draft from the summaries
    - Why: from the Ticket_Context and the "why" answers, the ticket named by the rules of Requirement 4: a Closes_Line and no other mention when the template has the convention and merging finishes it; one mention in the text, as the tracker writes it and linked when a URL was given, otherwise. Changes: one bullet per Change_Summary, what changed then the author's words. Answers naming a gap, a risk or something not run go to Testing, Risk and rollout or Notes for reviewers as fits, as well as the bullet. Nothing is written fresh from the skill's reading of the diff. Title prefix unchanged. Prove it: read back against Requirement 3.8, 3.9, 4.1, 4.2, 4.3, 4.5
    - _Requirements: 3.8, 3.9, 4.1, 4.2, 4.3, 4.5_
  - [x] 4.3 Steps 8 and 9, approval and creation
    - Step 8 asks with the AskUserQuestion tool, header `Approve`, options `Approved` and `Changes needed`, and shows the drafted commit message with the draft when the commit offer was accepted. Step 9: commit the listed files with that message if offered and accepted, then push, then `gh pr create` or `gh pr edit` as today. Prove it: read back against Requirement 5.5 and 5.8
    - _Requirements: 5.5, 5.8_

- [x] 5. Wiring
  - [x] 5.1 start-task's hand-off line
    - In `skills/start-task/SKILL.md`, the `done` bullet of Executor_Route: replace "Then say that the change sits uncommitted on the current branch, naming that branch, and that if it is the default branch the author creates the branch proposed in step 1 and commits before running `/freethinking:pr`." with "Then say that the change sits uncommitted on the current branch, naming that branch." and keep the recommendation sentence, adding that `pr` will offer to create the branch and commit. The CX_Block's Hand-offs bullet in start-task says the branch is created by the author or by implement-spec, never by this skill; append "or by `pr` at its branch offer". Prove it: `grep -c 'git checkout -b' skills/start-task/SKILL.md` is 0; `make validate`
    - _Requirements: 5.9_
  - [x] 5.2 README row and version
    - README `pr` row: "Takes the ticket as its first argument and reads it, offers to create the branch and commit if needed, walks the branch's changes with you one at a time with a short set of review prompts, drafts the title and description from your answers, and opens the PR with `gh` once you approve. Needs the `gh` CLI signed in." `.claude-plugin/plugin.json` version 0.6.0 to 0.7.0. Prove it: `make validate`
    - _Requirements: 7.4, 7.5_

- [x] 6. Evals
  - [x] 6.1 `opens-pr-with-ticket`
    - New case folder beside `opens-pr-with-stub-gh`, same `case.yaml` shape and a `scaffold.sh` that calls the same scaffold logic (copy the file; scaffolds are regular files, never symlinks) and then writes `.github/pull_request_template.md` into the fake repository, copied from this repository's own template so it carries the `Closes #<number>` convention, committed on `main` before the branch so it is not a change of the branch; prompt `/freethinking:pr #7` followed by the author's answers up front to all five review prompts for the one change (as `opens-pr-with-stub-gh` now does), plus "merging finishes it", no risk, not a draft, treat the draft as approved. Graders (no grader for the issue read itself: the issue arrives by injection, the transcript does not hold the expanded prompt, and a grader on the issue's words appearing in Why is flaky because the model paraphrases; the Closes line and title prove the ticket was used): `tool_used` Bash for `gh pr create` with the `[#7]` title, accepting a raw or JSON-escaped quote; three `tool_used` Bash graders over the command that writes the body (only Bash is granted and the reply does not carry the draft): `## Why` then `Closes #7`; a must-not pattern (`min: 0, max: 0, arm: both`) for two `#7` inside Why; `## Changes` then one of two phrases only the author's answers have (`needed a greeting helper` or `adds \`greet\` and its test`), since the model reorders the bullet between runs. Prove it: `make eval-skill-pr EVAL_ARGS="--runs 1 --case opens-pr-with-ticket"` passes, then three runs
    - **Property 2: The ticket is named exactly once in Why**
    - **Validates: Requirements 1.1, 2.1, 4.1, 4.5, 7.2**
  - [x] 6.2 `offers-branch-on-default`
    - New case: scaffold as `opens-pr-with-stub-gh` but ending on `main` with the two greeting commits on it; prompt `/freethinking:pr` followed only by a line saying the author will not answer during this run and the skill should stop at its first question. Graders in the shape of start-task's route cases: `regex` list item `Create` and `regex` list item `Stop` with flags `im`; must-not `tool_used` Bash graders (`min: 0, max: 0, arm: both`) for `git push`, `gh pr create`, `git commit` and a branch creation (`git (checkout -b|switch -c|branch (?!--))`). `max_turns` 8. Prove it: one run, then three
    - **Property 3: No git mutation without a yes**
    - **Validates: Requirements 5.1, 5.8, 7.3**
  - [x] 6.3 Adjust `stops-at-starting-checks` and confirm the two existing cases
    - Drop `default branch|its own branch|on `?main`?` from the `names-a-starting-check` pattern so the bare workspace must stop on the origin or `gh` check; run `stops-at-starting-checks` and `opens-pr-with-stub-gh` at one run, then three. Record all four tables for the PR
    - _Requirements: 7.1_
  - [x] 6.4 start-task regression
    - `make eval-skill-start-task EVAL_ARGS="--case contained-change-offers-executor"` at two runs, since its graders are deterministic; record the table
    - _Requirements: 5.9_

- [ ] 7. Manual checks by the author
  - [x]* 7.1 A real ticket in this repository
    - On this branch with `claude --plugin-dir .` and the installed plugin disabled for the session: `/freethinking:pr #11`; confirm the first message states the argument reading, the issue and its comments were read, each change arrives with the account, leading evidence and five numbered prompts, a deliberately skipped prompt is asked for by name, the Closes question renders in the tool, the draft names the ticket once, the approval renders in the tool; stop before approving. Record in the PR
    - **Property 1: Every Change is spoken for**
    - **Validates: Requirements 1.5, 2.1, 3.2, 3.4, 4.4, 6.4**
  - [ ]* 7.2 Both offers from the default branch
    - In a scratch clone on `main` with one uncommitted file: `/freethinking:pr`; confirm the branch offer renders in the tool and a yes creates the branch with the file carried across, the commit offer renders and a yes commits after the walkthrough with a message from the author's words; stop before pushing. Record in the PR
    - **Property 3: No git mutation without a yes**
    - **Validates: Requirements 5.1, 5.2, 5.4, 5.5**

## Notes

- Sub-tasks marked `*` are the author's own manual runs; implementation sub-tasks are never optional. 7.1 and 7.2 need the AskUserQuestion tool, which the eval sandbox does not grant, so they are the only proof of how the questions render.
- Tasks 2.1 to 4.3 edit one file, `skills/pr/SKILL.md`, by section. Each is proved by reading the section back against the design's component table; the evals in task 6 are the proof of the whole, so no eval runs before task 6.
- `make validate` after every change under `skills/`, `.claude-plugin/`, `README.md` or `evals/`, and at the end of every wave. The rules size check does not move: `rules/` is untouched.
- Evals cost real model calls: one invocation per case, since only the last `--case` flag is honoured; iterate at `--runs 1`, confirm at three for the pr cases (prose graders) and two for the start-task case.
- Keep the walkthrough in prose. No task turns the review prompts into AskUserQuestion options; the CX_Block says why.
- Work on branch `11-pr-skill-ticket`, never on main.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1", "2.2", "2.3", "2.4"] },
    { "id": 1, "tasks": ["3.1", "3.2"] },
    { "id": 2, "tasks": ["4.1", "4.2", "4.3", "5.1", "5.2"] },
    { "id": 3, "tasks": ["6.1", "6.2", "6.3", "6.4"] },
    { "id": 4, "tasks": ["7.1", "7.2"] }
  ]
}
```
