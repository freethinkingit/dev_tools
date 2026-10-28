# Implementation Plan

## Overview

The plan builds the substitution script first, applies it to the working tree and then to the Records, makes the hand edits, and moves the two folders last, so that the session running this plan keeps reading its spec at `.freethinking/specs/ponderly-rename/` until the final build wave. The few Judgment_Lines the script would get wrong are corrected by hand in wave 2. The proof wave runs the Name_Search, the Validation, a word-diff review for Property 2 and scratch checks for Properties 3 and 4. No eval target runs. The Draft_PR waves come after the owner has committed, pushed and merged this branch, and each waits for the owner's go. Nothing is committed or pushed by any task.

## Tasks

- [x] 1. Build the substitution script
  - [x] 1.1 Write the scratch substitution script outside the Repository, in the session's scratchpad
    - Encode the design's Substitution Table, rows 1 to 9 in order, and its one Exception: the files of this spec, `ponderly-rename/requirements.md`, `design.md` and `tasks.md`, which describe the rename and must keep the Old_Names
    - `apply` rewrites text files in place, skips `.git/`, binary files and the Exceptions, and prints the files it changed; usage is `python3 rename.py apply <paths>... --exclude <prefix>...`, paths first
    - _Requirements: 4.2, 4.3, 8.2_

- [x] 2. Substitute the Old_Names
  - [x] 2.1 Apply the script to every file outside `.freethinking/`
    - Covers `plugins/freethinking/` (skills, agents, rules, hooks, READMEs, templates, `plugin.json`), `.claude-plugin/marketplace.json`, `evals/`, `checks/`, `Makefile`, `.github/`, `README.md`, `LICENSE`
    - Review the diff: every `freethinking:` became `ponderly:`, every `.freethinking/` became `.ponderly/`, the Makefile's temporary folder reads `ponderly-eval`, and no line changed for another reason
    - _Requirements: 1.2, 2.1, 2.2, 3.1, 3.4, 4.4, 5.1, 5.2, 5.3, 6.1, 6.4_
  - [x] 2.2 Apply the script to the Records under `.freethinking/specs/` and `.freethinking/strategies/`, skipping this spec's folder
    - `@freethinkingit/gherkin-harness` in the strategy becomes `@sabind/gherkin-harness` through row 6
    - _Requirements: 4.1, 4.3_
  - [x] 2.3 Correct the Judgment_Lines in the Records by hand
    - Read each line in the design's Judgment_Lines table in context and apply its correction, rewording as little as keeps the sentence true without an Old_Name; read every other line the script changed in `specs/contributing-guide/` and `specs/directory-listing/` for the same problem, and list each line corrected
    - _Requirements: 4.2, 7.1_

- [x] 3. Make the hand edits
  - [x] 3.1 Set the Identity
    - `plugin.json` author: name Dan Sabin, email `dan.sabin@gmail.com`, URL `https://dansabin.com`; `LICENSE`: "Copyright (c) 2026 Dan Sabin"; `.github/CODE_OF_CONDUCT.md` contact `dan.sabin@gmail.com`; `marketplace.json` owner name Dan Sabin
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [x] 3.2 Replace each Issue_Form's `type:` line with its Type_Label in `labels:`
    - Per the design's label mapping: bug, feature, task, spike, each beside `triage`
    - Reword `.github/CONTRIBUTING.md` for a personal account: each form applies its `type:` label rather than setting an Issue_Type, and no line calls Issue_Types a repository or organisation setting
    - _Requirements: 6.2, 6.3_
  - [x] 3.3 Set the Plugin version to `1.0.0` in `plugin.json`
    - _Requirements: 1.4_
  - [x] 3.4 Update the READMEs' install and Work_Folder text
    - In the Plugin README, remove the 0.14.0 note about moving specs from `.claude/specs/`; check that the install, update and marketplace-selection steps read `sabind/ponderly`, `ponderly@sabind` and `sabind`, and the Work_Folder section reads `.ponderly/`
    - _Requirements: 2.2, 3.3_

- [x] 4. Move the folders
  - [x] 4.1 `git mv plugins/freethinking plugins/ponderly`
    - _Requirements: 1.1_
  - [x] 4.2 `git mv .freethinking .ponderly`
    - This moves this spec too: from here on, tick boxes in `.ponderly/specs/ponderly-rename/tasks.md`
    - _Requirements: 3.2_

- [x] 5. Prove the rename
  - [x] 5.1 Run the Name_Search and confirm the only matches are the Exceptions
    - List any other match with its file and line, and fix it before going on
    - **Property 1: No Old_Name is left**
    - **Validates: Requirements 1.3, 3.1, 4.1, 5.3, 6.1, 9.1, 9.2**
  - [x] 5.2 Run `make validate` and `make check`, and report the result as it is
    - _Requirements: 2.3, 5.4_
  - [x] 5.3 Review the word diff against `main`
    - Run `git diff --word-diff=porcelain -M origin/main`, check each changed word is an Old form becoming its New form under the Substitution Table, and read the Judgment_Lines and the hand edits of wave 2 by eye; list anything else as a non-name change
    - **Property 2: Every other change is a name**
    - **Validates: Requirements 4.1, 4.2, 4.4**
  - [x] 5.4 Check that every `ponderly:<name>` outside the Records names a skill folder or agent file under `plugins/ponderly/`
    - **Property 3: Every Namespace reference resolves**
    - **Validates: Requirements 1.2, 5.3**
  - [x] 5.5 Check that moved files keep their history
    - `git status` shows the moves as renames, and `git log --follow` on a sample from `plugins/ponderly/` and `.ponderly/` reaches commits from before the move
    - **Property 4: Moved files keep their history**
    - **Validates: Requirements 1.1, 3.2**

- [x] 6. Carry the Draft_PRs onto the new names, after the owner has merged this branch and says go
  - [x] 6.1 Rebase #73 (`56-experience-first-explanations`) onto `origin/main` in its own worktree, apply the script to the files it adds or changes, then run the Name_Search and the Validation on it
    - Stop and show any conflict that is not a name change; commit and force-push only when the owner says so
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  - [x] 6.2 Do the same for #71 (`63-canonical-source-hld`)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  - [x] 6.3 Delete the scratch scripts and report the remaining Exceptions to the owner
    - The only Exception left is this spec's own folder
    - _Requirements: 4.3, 9.1_

## Notes

- Commit nothing and push nothing, on any branch, until the owner says so. Do not touch the `newcomer-docs` branch or PR #72, and do not transfer or rename the GitHub repository.
- The proof tasks in wave 5 are required, not optional: they are the only proof this task has, and no eval target runs.
- The scratch scripts stay in the scratchpad, never in the Repository, and are deleted in task 6.3, after the Draft_PRs have used them.
- After wave 4, this spec lives at `.ponderly/specs/ponderly-rename/`.
- Wave 6 starts only after the owner has merged this branch; implement-spec hands back at the end of wave 5 and waits.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1", "2.2"] },
    { "id": 2, "tasks": ["4.1"] },
    { "id": 3, "tasks": ["2.3", "3.1", "3.2", "3.3", "3.4"] },
    { "id": 4, "tasks": ["4.2"] },
    { "id": 5, "tasks": ["5.1", "5.2", "5.3", "5.4", "5.5"] },
    { "id": 6, "tasks": ["6.1"] },
    { "id": 7, "tasks": ["6.2"] },
    { "id": 8, "tasks": ["6.3"] }
  ]
}
```
