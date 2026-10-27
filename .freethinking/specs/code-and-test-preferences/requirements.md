# Requirements Document

## Introduction

Agents tend to write too many unit tests: they encode every value and feature rather than proving each code path once, and they write terse code that then needs comments to explain its algorithm. This change gives every repository the handbook applies to two always-on preferences, tests that prove paths rather than values and code that reads plainly without algorithm comments, and two skills for a branch that has already grown: `readable-code`, a readability pass over the branch's source, and `tighten-tests`, a cleanup of the branch's tests that cuts what adds nothing without losing a covered line or a proof a requirement needs. GitHub issue #68 is the ticket.

## Glossary

- **Test_Rule**: The new rule file `plugins/freethinking/rules/tests.md`, loaded into every session and sub-agent by the plugin's hooks.
- **Readability_Bullet**: The bullet added to `plugins/freethinking/rules/code-changes.md` that prefers readable code to terse code.
- **Comment_Sentence**: The sentence added to `plugins/freethinking/rules/comments.md` saying that a comment describing an algorithm is fixed by making the code readable.
- **Readable_Code**: The new skill at `plugins/freethinking/skills/readable-code/SKILL.md`.
- **Tighten_Tests**: The new skill at `plugins/freethinking/skills/tighten-tests/SKILL.md`.
- **Skill**: Readable_Code or Tighten_Tests.
- **Author**: The person running a Skill, who answers its questions and decides its verdicts.
- **Scope**: The files a Skill works on: the files the branch changes against its target branch, narrowed to the paths the Author passes as arguments when there are any.
- **Baseline**: What a Skill records before it changes anything, to compare against afterwards: the full suite's result, and for Tighten_Tests the test counts and per-module coverage, and for infrastructure code the synthesized output.
- **Synthesized_Output**: What infrastructure-as-code produces from the source, such as generated deployment templates, compared before and after a change to prove the change altered no behaviour.
- **Executor**: The plugin's `task-executor` agent, launched once per File_Group.
- **File_Group**: Files in Scope that share a template, role or pattern, such as several pages of one kind, worked by one Executor so the issues they share are fixed the same way; a file with no peers is a group of one.
- **Shared_Decisions**: A short list, written before any Executor starts, of how each issue that recurs across Scope is to be handled, given to every Executor so their choices agree.
- **Reviewer**: The plugin's `wave-reviewer` agent.
- **Keep_List**: The tests Tighten_Tests keeps whatever the Audit says: checks the Author asked for, checks a requirement names, deployed end-to-end proofs, and seeded property tests a spec names.
- **Audit**: Tighten_Tests' read-only pass that names, for every test in Scope, the path or gotcha it proves and gives a Verdict.
- **Verdict**: One of `keep`, `merge` (naming the test it merges into) or `drop` (saying why it adds nothing).
- **Gap**: A code path, corner case or gotcha in Scope that no test proves, found by the Audit.
- **Mutation_Check**: A check that backs up one source file, breaks or removes in it the behaviour a test covers, shows that a test fails, and restores the file at once, leaving the real source as it was.
- **Vacuous_Test**: A test that still passes when the behaviour it claims to test is removed or inverted.
- **Expected_Failure**: A test marked, in the project's test framework, as known to fail, such as node:test `todo` or Python's `expectedFailure`.
- **System**: The handbook plugin: the rules, the Skills, the README, the issue forms, the manifest, the checks and the eval cases this change touches.

## Requirements

### Requirement 1: Tests prove paths, not values

**User Story:** As a developer, I want every test an agent writes to prove one code path, corner case or gotcha, so that the suite pressure-tests the code without codifying every value.

#### Acceptance Criteria

1. THE System SHALL add the Test_Rule, with a heading and an opening line in the shape of the existing rules.
2. THE Test_Rule SHALL say to write one test per code path, corner case or gotcha.
3. THE Test_Rule SHALL say to test boundary values, such as zero, one, the limit, the limit plus one, empty, NaN and negative, and not exhaustive tables or cross products. It SHALL say each test takes one input, with no loop, `subTest` or `parametrize`, except a seeded property test.
4. THE Test_Rule SHALL say not to write a test that restates an implementation constant, checks its own input or checks a library's behaviour.
5. THE Test_Rule SHALL say that code parsing input gets a small fixed set of awkward inputs, naming joined emoji, non-Latin scripts, a very long string, whitespace only, zero-width and control characters and a byte-order mark, and that each gets the outcome the input's contract defines, accepted or refused with a clear error, and none throws.
6. THE Test_Rule SHALL say that a test's name reads as a behaviour sentence and that the test asserts everything its name promises.
7. THE Test_Rule SHALL say to mock at the boundary with small in-memory fakes that enforce the real contract, shared in one place.
8. THE Test_Rule SHALL say that a seeded property test a spec names stays a property test.
9. THE Test_Rule SHALL not restate the test-with-every-change bullet of `code-changes.md` or name any skill's steps.

### Requirement 2: Readable code over comments

**User Story:** As a developer, I want code written to be read, so that its algorithm needs no comment to be understood.

#### Acceptance Criteria

1. THE System SHALL add the Readability_Bullet to `code-changes.md`, saying to prefer descriptive names and plain control flow over dense ternaries, chained optional operators, clever destructuring and one-letter names.
2. THE Readability_Bullet SHALL say that a hidden side effect, such as a function that mutates the state it is passed, is justified or removed.
3. THE System SHALL add the Comment_Sentence to `comments.md`, saying that a docstring or comment that describes the algorithm is fixed by making the code readable, not by rewording the comment.
4. THE Readability_Bullet and the Comment_Sentence SHALL not repeat what `comments.md` already says about docstrings on public contracts and about comments on what or how.

### Requirement 3: The rules still fit the hooks

**User Story:** As a maintainer, I want the rules kept within their limits, so that Claude Code never truncates them.

#### Acceptance Criteria

1. THE System SHALL keep the output of `hooks/load-rules.sh`, and the decoded `additionalContext` of `hooks/load-rules-subagent.sh`, under 10,000 characters each.
2. THE System SHALL set a character limit in `checks/test_rules_size.py` for `tests`, `code-changes` and `comments`, each at or under the room the hook limit leaves.
3. WHEN `make validate` runs, THE System SHALL pass.

### Requirement 4: A readability pass over a branch

**User Story:** As the owner of a branch, I want to run a readability pass over its source on its own or before a test cleanup, so that the code reads plainly and its behaviour is proved unchanged.

#### Acceptance Criteria

1. WHEN the Author runs Readable_Code, THE Skill SHALL say its Scope in one line, naming the target branch and any paths passed, before changing anything.
2. IF the Scope holds no source file, THEN THE Skill SHALL say so and stop without changing anything.
3. THE Skill SHALL take the Baseline before changing anything.
4. IF the full suite fails at the Baseline, THEN THE Skill SHALL report the failures and ask the Author whether to go on before changing anything.
5. THE Skill SHALL read the source files in Scope, sort them into File_Groups, write the Shared_Decisions, and show both to the Author for approval before any change; THEN it SHALL launch one Executor per File_Group, with the Shared_Decisions, to apply the Readability_Bullet and the Comment_Sentence, with no behaviour change and no rename for taste.
6. THE Skill SHALL prove no behaviour change by running the full suite after the pass and comparing it with the Baseline, and WHERE the Scope holds infrastructure code, by diffing the Synthesized_Output before and after.
7. IF the suite result or the Synthesized_Output differs from the Baseline, THEN THE Skill SHALL report the difference with the file that caused it and ask the Author whether to revert that file's change or keep it.
8. WHEN the pass is done, THE Skill SHALL launch the Reviewer over the pass's changes against the Readability_Bullet and `comments.md`; WHEN the Reviewer returns a `blocker` or `should-fix` Finding, THE Skill SHALL send it to the Executor that owns the file for up to two fix attempts and re-run that file's checks, and SHALL carry to the hand-back every Finding still open after them and every `nit`.
9. THE Skill SHALL hand back with the plugin's `report` skill, problems first, and SHALL commit nothing.
10. THE Skill SHALL compare against its Baseline copies and SHALL not run `git stash`, `git checkout` or `git reset`, so the branch's uncommitted work and the shared stash stay as they were.

### Requirement 5: A test cleanup prepared before any test changes

**User Story:** As the owner of a branch whose tests have grown, I want the cleanup to know what must stay and what it is measured against before it touches a test, so that nothing a requirement needs is cut by accident.

#### Acceptance Criteria

1. WHEN the Author runs Tighten_Tests, THE Skill SHALL say its Scope in one line before doing anything else.
2. THE Skill SHALL ask the Author whether Readable_Code has run on the final code, and SHALL offer to run it first, so that coverage is measured once on the final code.
3. THE Skill SHALL take the Baseline, with test counts and per-module coverage, before any test changes.
4. IF the project has no coverage tool, THEN THE Skill SHALL say so and ask the Author whether to add one or to go on with the Mutation_Checks alone, and SHALL not add a tool unasked.
5. THE Skill SHALL gather the Keep_List before the Audit, from the Author, the spec or ticket the branch serves, and the tests of the branch.

### Requirement 6: Audit and verdicts

**User Story:** As the owner of a branch, I want every test named for what it proves and given a verdict I decide, so that I choose what goes and why.

#### Acceptance Criteria

1. THE Skill SHALL run the Audit without changing any file.
2. THE Audit SHALL give, for every test the branch adds or changes in Scope, the path or gotcha it proves and a Verdict.
3. THE Audit SHALL give the test counts before and after its Verdicts, and every Gap it found.
4. THE Audit SHALL give a test on the Keep_List the Verdict `keep`.
5. THE Skill SHALL show the Audit to the Author and SHALL apply no Verdict until the Author approves it, a Verdict the Author changes taking the Author's value.

### Requirement 7: Slimming with proof

**User Story:** As the owner of a branch, I want the approved verdicts applied with proof that no covered line lost its test and no kept test is vacuous, so that a smaller suite is no weaker.

#### Acceptance Criteria

1. WHEN the Author approves the Verdicts, THE Skill SHALL sort the test files to change into File_Groups, write the Shared_Decisions for applying the Verdicts, show both to the Author with the Audit, and launch one Executor per File_Group with the Shared_Decisions.
2. THE Skill SHALL change no source file while applying the Verdicts.
3. IF a test exposes a defect in the source, THEN THE Skill SHALL mark the test an Expected_Failure and report the defect, not fix it.
4. THE Skill SHALL measure per-module coverage after the slimming and compare it with the Baseline, reporting both, and SHALL set no coverage threshold.
5. IF a line covered at the Baseline is not covered after the slimming, THEN THE Skill SHALL restore a test that covers it and report which.
6. THE Skill SHALL run a Mutation_Check for each dropped test, breaking the behaviour it covered, and show that a kept test fails.
7. IF no kept test fails under a dropped test's Mutation_Check, THEN THE Skill SHALL restore the dropped test and report it.
8. THE Skill SHALL run a Mutation_Check for each kept or new test, removing or inverting the behaviour it claims to test, and show that the test fails.
9. IF a test is a Vacuous_Test, THEN THE Skill SHALL fix it so it fails under its Mutation_Check, or report it to the Author when it cannot.
10. THE Skill SHALL leave the source exactly as before the Mutation_Checks, shown by a diff.
11. THE Skill SHALL compare against its backups and Baseline and SHALL not run `git stash`, `git checkout` or `git reset`.

### Requirement 8: Final review and gaps

**User Story:** As the owner of a branch, I want the cleanup reviewed against what the branch must prove, and the gaps it found turned into separate work, so that the cleanup does not grow into new features.

#### Acceptance Criteria

1. WHEN the slimming is done, THE Skill SHALL launch the Reviewer over the test changes against the requirements the branch serves, or against the Keep_List when there are none; WHEN the Reviewer returns a `blocker` or `should-fix` Finding, THE Skill SHALL send it to the Executor that owns the file, or to a new Executor when the file is one the slimming made wrong without changing it, for up to two fix attempts, SHALL re-run that file's tests and the Mutation_Check of every test the fix changed, and SHALL carry to the hand-back every Finding still open after them, every Finding that needs a source change, and every `nit`.
2. IF the review finds a requirement left with no proof, THEN THE Skill SHALL report it and offer to restore the test that proved it.
3. THE Skill SHALL hand off each Gap as a separate task for the Author, and SHALL not fill a Gap inside the cleanup.
4. THE Skill SHALL hand back with the plugin's `report` skill, problems first, with the test counts and coverage before and after, and SHALL commit nothing.

### Requirement 9: The skills ship with the plugin

**User Story:** As a team member, I want the new skills and rule listed, proposable and released like the rest, so that I can find them and report problems with them.

#### Acceptance Criteria

1. THE System SHALL list Readable_Code and Tighten_Tests in the plugin README's skills table and the Test_Rule in its rules table, and SHALL update the `code-changes.md` and `comments.md` rows.
2. THE System SHALL add Readable_Code, Tighten_Tests and the Test_Rule to the component dropdown of every issue form that has one.
3. THE System SHALL bump the plugin version in `plugins/freethinking/.claude-plugin/plugin.json` from 0.16.0 to 0.17.0.
4. THE System SHALL add at least one eval case under `evals/skills/readable-code/`, one under `evals/skills/tighten-tests/` and one under `evals/rules/` for the Test_Rule, each case's behaviour decided while the Skill is built.
5. THE System SHALL not change `implement-spec`, `pr` or any agent, and SHALL add no hook.
