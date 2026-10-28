# Implementation Plan

## Overview

The rules and both skills are written first, in parallel, since none reads another's text. The size limits, the README, the issue forms and the version follow once the files they describe are on disk. The eval cases come last, each case's behaviour chosen with the Author while it is written, as agreed. A manual run of each skill on a small real branch closes the plan. Proof is `make validate` after every task, the eval targets run by hand one at a time, and the manual runs.

## Tasks

- [x] 1. The rules
  - [x] 1.1 Write `plugins/freethinking/rules/tests.md`
    - A `# Tests` heading, an opening line in the shape of the other rules ("How tests are written in any repository this handbook applies to."), and bold-lead bullets for each criterion of Requirement 1: one test per path, corner case or gotcha; boundary values, not tables or cross products; no test restating a constant, checking its own input or checking a library; the fixed awkward-input set for parsers, refused cleanly, never thrown; names as behaviour sentences that the assertions keep; in-memory fakes at the boundary enforcing the real contract, shared in one place; a seeded property test a spec names stays. At most 1,000 characters; no skill named; nothing from `code-changes.md` restated. Ephemeral check: `wc -m` is at most 1,000; `make validate` passes
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_
  - [x] 1.2 Add the readability bullet and the comment sentence
    - In `plugins/freethinking/rules/code-changes.md`, after "Match the project.", a bullet "**Write for the reader.**" preferring descriptive names and plain control flow over dense ternaries, chained optional operators, clever destructuring and one-letter names, and saying a hidden side effect, such as a function that mutates the state it is passed, is justified or removed. In `plugins/freethinking/rules/comments.md`, in the docstring bullet, the sentence that a docstring or comment describing the algorithm is fixed by making the code readable, not by rewording it; and the adjacent fixes "One write inline comments" to "Only write inline comments" and "return types ," to "return types,". Nothing else in either file changes. Ephemeral check: `git diff --stat` shows the two files; `code-changes.md` is at most 2,450 characters and `comments.md` at most 1,450; `make validate` passes
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 1.3 Set the size limits
    - In `checks/test_rules_size.py`, add `"tests": 1000`, `"code-changes": 2450` and `"comments": 1450` to `RULE_LIMITS`. Ephemeral check: `python3 -m unittest discover -s checks -p test_rules_size.py` passes, and fails when a limit is lowered below the file's size in a scratch copy; the hook output's `wc -m` is under 10,000 for both `load-rules.sh` and `load-rules-subagent.sh`
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 2. The skills
  - [x] 2.1 Write `plugins/freethinking/skills/readable-code/SKILL.md`
    - Frontmatter as the design's data model gives it, with a description under 1,024 characters that names the requests it takes ("make this branch readable", "readability pass") and says a test cleanup is `tighten-tests`'s. A "Working with the author" section in the other skills' shape (Stops, How it asks, Hand-backs, Hand-offs). Steps for each operation of the design's `readable-code` table: Scope from `git diff --name-only <base>`, where the base is the merge base with the target, plus the untracked files, narrowed by the paths in `$ARGUMENTS`; Baseline; one `freethinking:task-executor` per source file with the launch prompt of key decision 4; the suite and synthesized output compared; the `freethinking:wave-reviewer` launch; the `report` handback naming `tighten-tests` and `pr` as next. Every error row of the design that applies, including the missing-agent stops. It names the rules it applies and does not restate them. Ephemeral check: `make validate` passes, which runs the skills validator and `checks/test_descriptions.py`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9_
  - [x] 2.2 Write `plugins/freethinking/skills/tighten-tests/SKILL.md`
    - Frontmatter as the design's data model gives it, with a description under 1,024 characters that names the requests it takes ("slim the tests", "too many tests", "audit the tests") and says readability is `readable-code`'s. The same "Working with the author" shape. Steps for each operation of the design's `tighten-tests` table, in order: Scope and the readability question; Baseline with per-line coverage and the no-tool question; Keep_List; the read-only Audit with the Verdict record of the data model, shown as key decision 8 says; approval; one `freethinking:task-executor` per test file with its Verdicts and "change no source file"; Expected_Failure for exposed defects; line-by-line coverage comparison with no threshold; Mutation_Checks in place with a backup, as key decision 6 says, for dropped, kept and new tests, with the real tree's diff before and after; the `freethinking:wave-reviewer` launch against the requirements or Keep_List; the `report` handback with counts, coverage and Gaps, and the offer to file Gaps with `gh issue create`. Every error row of the design that applies. Ephemeral check: `make validate` passes
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 8.1, 8.2, 8.3, 8.4_

- [x] 3. Ship them
  - [x] 3.1 Document the skills and rules in the README
    - In `plugins/freethinking/README.md`: rows for `readable-code` and `tighten-tests` in the Skills table, in the order `checks/test_listing.py` requires; a `rules/tests.md` row in the Rules table; the `code-changes.md` row gains the readability preference and the `comments.md` row the algorithm-comment sentence; the size-limit sentence below the Rules table names the new limits. Ephemeral check: `make validate` passes, which runs `checks/test_listing.py`
    - _Requirements: 9.1_
  - [x] 3.2 Add the components to the issue forms
    - In the four forms under `.github/ISSUE_TEMPLATE/` with a `component` dropdown, add `readable-code (skill)`, `tighten-tests (skill)` and `tests (rule)` at the positions `checks/test_issue_forms.py` requires. Ephemeral check: `python3 -m unittest discover -s checks -p test_issue_forms.py` passes; `make validate` passes
    - _Requirements: 9.2_
  - [x] 3.3 Raise the version
    - In `plugins/freethinking/.claude-plugin/plugin.json`, `"version": "0.17.0"`. Ephemeral check: `make validate` passes
    - _Requirements: 9.3_

- [x] 4. Eval cases
  - [x] 4.1 Add the Test_Rule case
    - Agree with the Author which behaviour the case guards, then add `evals/rules/tests/<case>/` in the shape of `evals/rules/code-changes/test-with-change/`: `case.yaml`, `prompt.md` with `tags: [rule, tests]`, a `scaffold.sh` on a fixture under `evals/fixtures/`, and graders. Run `make eval-rule-tests EVAL_ARGS="--runs 1 --ablation with-without"` once and paste the table into the conversation. Ephemeral check: `checks/test_eval_cases.py` passes under `make validate`; `make help` lists `eval-rule-tests`
    - _Requirements: 9.4_
  - [x] 4.2 Add the `readable-code` case
    - Agree with the Author which behaviour the case guards, then add `evals/skills/readable-code/<case>/` with `tags: [skill, readable-code]`, a fixture under `evals/fixtures/` when the existing `calc-smells` does not serve, and the `Makefile` per-target line `eval-skill-readable-code: CASE_ARGS += --allow-tools Bash Write Edit Agent --scaffold` with `bin` on the PATH. Run the target once at `--runs 1` and paste the table. Ephemeral check: `checks/test_eval_cases.py` passes; `make -n eval-skill-readable-code` shows the flags
    - _Requirements: 9.4_
  - [x] 4.3 Add the `tighten-tests` case
    - Agree with the Author which behaviour the case guards, then add `evals/skills/tighten-tests/<case>/` with `tags: [skill, tighten-tests]`, an over-tested fixture under `evals/fixtures/`, and the `Makefile` per-target line as 4.2 with the target `eval-skill-tighten-tests`. Run the target once at `--runs 1` and paste the table. Ephemeral check: as 4.2
    - _Requirements: 9.4_

- [x] 5. Run each skill on a real branch
  - The Author runs `/freethinking:readable-code` and then `/freethinking:tighten-tests` on a small branch of a real project and pastes each hand-back into the conversation, for the pull request's Testing section. This is done by hand
  - _Requirements: 4.9, 8.4_

## Notes

- `make validate` runs after every task; a task is not done while it fails.
- A skill names the rules and the other skills it uses and hands off to them; it never restates their text or steps.
- Skill and rule text follows the handbook's voice: plain words, one idea per sentence, things named by what they are.
- No change to `implement-spec`, `pr`, any agent or any hook. A hook-up from those skills is a later proposal.
- Eval targets run one at a time, never in parallel, and a stalled target is rerun alone.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "2.1", "2.2"] },
    { "id": 1, "tasks": ["1.3", "3.1", "3.2", "3.3"] },
    { "id": 2, "tasks": ["4.1", "4.2", "4.3"] },
    { "id": 3, "tasks": ["5"] }
  ]
}
```
