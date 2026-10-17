# Implementation Plan

## Overview

The move comes first, because every other task writes paths under `plugins/freethinking/`. Then, in one wave, the manifest, the hook scripts, the re-rooted checks, the Makefile and the four guides, which touch disjoint files. The two checks that depend on new content, the encoder check on the rewritten hooks and the listing check on the new manifest, follow. The last wave is the author's: the eval runs that cost tokens and the local install. Every task is proved by `make validate` plus the ephemeral check its text names; the eval runs are the integration proof. Requirement 7, the portal's validation, happens after the merge and is recorded on issue #43, so it is not a task here.

## Tasks

- [x] 1. Move the plugin into `plugins/freethinking/`
  - `git mv` `.claude-plugin/plugin.json`, `skills/`, `agents/`, `rules/`, `hooks/` and `README.md` under `plugins/freethinking/`, and move the untracked `.claude-plugin/icon.png` to `plugins/freethinking/.claude-plugin/icon.png`; leave `.claude-plugin/marketplace.json` at the root and set its entry's `source` to `./plugins/freethinking`. Ephemeral check for Property 1: list the skill, agent, rule and hook names at the old and new paths and diff them; `claude plugin validate . --strict` passes
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 2. Fill the manifest's listing fields
  - In `plugins/freethinking/.claude-plugin/plugin.json`, set `displayName`, `version` 0.13.0, `author`, `homepage`, `repository`, `license`, `icon` and `keywords` to the values of Requirement 2, in the field order the design gives; `claude plugin validate ./plugins/freethinking --strict` passes with no warning
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 3. Rewrite the hook scripts to the validator's shape
  - Rewrite `plugins/freethinking/hooks/load-rules.sh` and `load-rules-subagent.sh` as the design's table says: one `awk` program each over `"${CLAUDE_PLUGIN_ROOT}"/rules/*.md`, no other variable, no command substitution, no call between them, the header written in both with a comment naming the other, and the no-rules branches of Requirement 4.4. Ephemeral check: run the old scripts from `git show HEAD:` and the new ones on the real rules folder and diff the session output and the decoded subagent context, byte for byte
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 4. Re-point the free checks
  - [x] 4.1 Re-root the existing checks on the plugin folder
    - In `test_agents.py`, `test_descriptions.py`, `test_report_skill.py`, `test_rules_size.py` and `test_issue_forms.py`, add one `PLUGIN` constant at the top and read `skills/`, `agents/`, `rules/`, `hooks/` under it; `test_rules_size.py` sets `CLAUDE_PLUGIN_ROOT` to it; `test_eval_cases.py` is untouched; `make check` passes
    - _Requirements: 4.6, 6.1, 6.5_
  - [x] 4.2 Rewrite the encoder check around a fixture rules folder
    - In `test_hook_encoder.py`, make `roundtrip` write a temp folder with `rules/a.md`, run both scripts with `CLAUDE_PLUGIN_ROOT` set to it and compare byte for byte; keep the fixed table and the seeded fuzz, add a file with no trailing newline to the fixed table, make `test_real_run` compare both scripts on the plugin folder, and add the no-rules test of Requirement 4.4; `make check` passes
    - _Requirements: 4.4, 4.5_
  - [x] 4.3 Add the listing check
    - Write `checks/test_listing.py` as the design's Checks row says: README of at least 40 words outside fenced blocks, `LICENSE` or a `license` field, and the icon a square PNG of 512 to 2048 px read from the IHDR chunk with `struct`. Ephemeral negative check: a temp folder with a 300 px PNG and a 10-word README fails each assertion; `make check` passes on the real folder
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 5. Teach the Makefile the layout and the Run_Tree
  - Add `PLUGIN := plugins/freethinking`; make `validate` run `check`, then the three strict validate commands; add the `RUN_EVAL` define of the design, with a per-recipe results folder, `mktemp`, the traps, `cp -R` of the plugin, `tar` of `evals/` without `results/` and no pipeline, the pull request template, `git init`, `mkdir -p` of the results folder and `claude plugin eval` with `--output-dir`; expand it in every eval recipe with the same tags; keep the per-target flags, `help` and the `PATH` exports. Ephemeral check: `make -n eval-skill-pr` shows the recipe, and `make validate` passes
  - _Requirements: 5.1, 5.2, 5.4, 5.5, 6.2, 6.3, 6.5_

- [x] 6. Update the guides
  - [x] 6.1 The plugin README
    - In `plugins/freethinking/README.md`, drop the read-access sentence and the `gh auth` paragraph from Install, cut the "Add or change a skill or rule" and Testing sections, and add the Disclosure_Section last with the sentences of Requirement 3.2; every backticked path in the file exists
    - _Requirements: 3.1, 3.2, 3.3, 3.5_
  - [x] 6.2 The root README
    - Write a new `README.md` at the root: the title, what the repository is, the layout list, links to `plugins/freethinking/README.md` and `.github/CONTRIBUTING.md`, then the "Add or change a skill or rule" and Testing sections moved from the plugin README, with the Validator subsection naming the three validate commands and the Evals subsection saying how an Eval_Target copies the plugin and `evals/` into a temporary tree; every backticked path in the file exists
    - _Requirements: 3.4, 6.4_
  - [x] 6.3 The contributing guide and the evals README
    - In `.github/CONTRIBUTING.md`, `claude --plugin-dir ./plugins/freethinking` and one sentence on `evals/` sitting outside the plugin; in `evals/README.md`, the Makefile's copy in place of `claude plugin eval . --tag <name>` and the note that `git rev-parse --show-toplevel` resolves to the copy; every backticked path in both files exists
    - _Requirements: 6.4_

- [x] 7. Prove the run tree and the install by hand
  - [x] 7.1 Run two eval targets and keep the tables
    - The author runs `make eval-skill-pr EVAL_ARGS="--runs 1 --case opens-pr-with-stub-gh"` and `make eval-hook EVAL_ARGS="--runs 1"`, confirms the results folder appeared under `evals/results/`, that nothing was left under `$TMPDIR`, and pastes both tables into the PR's Testing section
    - **Property 3: An eval run leaves only results behind**
    - **Validates: Requirements 5.1, 5.2, 5.3**
  - [x] 7.2 Install from the checkout
    - The author registers the checkout as a local marketplace from another folder, installs `freethinking@freethinkingit`, runs `claude plugin details freethinking` and records that it lists five skills, two agents and two hooks, then removes the probe marketplace
    - _Requirements: 1.6_

## Notes

- Every task runs `make validate` before it is done; a task's ephemeral check is created in a scratch location and deleted afterwards.
- Task 7's two leaves are actions for the author, since the eval runs cost tokens and the install touches the author's own Claude settings; they get no sub-agent.
- The spec records (`.claude/specs/`) are not edited to match the move; they stay as written.
- Requirement 7, the portal's validation after merge, is recorded on issue #43 and is not a task.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2", "3", "4.1", "5", "6.1", "6.2", "6.3"] },
    { "id": 2, "tasks": ["4.2", "4.3"] },
    { "id": 3, "tasks": ["7.1", "7.2"] }
  ]
}
```
