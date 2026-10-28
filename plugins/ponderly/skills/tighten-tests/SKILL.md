---
name: tighten-tests
description: Slim a branch's tests without losing a covered line or a proof a requirement needs. Use when asked to slim the tests, tighten, trim or prune them, audit the tests, or when a branch has too many tests. Readability of the source is readable-code's, not this skill's; it asks first whether readable-code has run on the final code and offers to run it. Audits every test the branch adds or changes with a keep, merge or drop verdict the author approves, applies the verdicts without changing a source file, proves the smaller suite no weaker by line coverage and mutation checks, has the changes reviewed and fixed, and hands back with the report skill, offering to file each gap it found as an issue. Commits nothing.
argument-hint: "[paths]"
allowed-tools: Bash(git status *) Bash(git branch *) Bash(git rev-parse *) Bash(git config --get *) Bash(git log *) Bash(git diff *) Bash(git merge-base *) Bash(git ls-files *) Bash(git show *) Bash(cp *) Bash(mkdir *) Bash(gh issue create *)
---

# Tighten the tests

Cut the tests a branch adds or changes down to the ones that prove something, without losing a covered line, a proof a requirement needs or a test the author wants kept. Measure first, decide with the author, apply the decisions, then prove that the smaller suite is no weaker: coverage line by line against the Baseline, and a Mutation_Check for every dropped, kept and new test. The source is never changed; a defect a test exposes is reported, not fixed, and a missing test is handed back as a Gap, not written here.

The author is accountable for the tests and decides every Verdict. What a good test is comes from the `tests` rule; this skill applies it and does not restate it.

Paths, if the author gave any: $ARGUMENTS

Terms used below:

- **Scope** is the files the branch changes against its target branch, uncommitted and untracked work included, narrowed to the paths in the arguments when there are any.
- The **Baseline** is what is recorded before any test changes: the full suite's result, the test counts, the covered lines per module and the source state.
- The **source state** is `git status --porcelain` and `git diff HEAD`, each over every file of the repository that is not a test file, and the contents of the untracked source files, kept in the session's scratchpad.
- The **source check** records the source state again and compares it with the Baseline's. If any part differs, stop and report the diff. No step of this skill changes a source file, so every step that ends with the source check stops on a difference. To see the old code, use the backup or the Baseline's source state; never run `git stash`, `git checkout` or `git reset`, which would touch the branch's uncommitted work and the stash every worktree shares.
- The **Keep_List** is the tests kept whatever the Audit says: checks the author asked for, checks a requirement names, deployed end-to-end proofs, and seeded property tests a spec names.
- The **Audit** is the read-only pass that names, for every test in Scope, the path or gotcha it proves and gives it a Verdict.
- A **Verdict** is `keep`, `merge` (naming the test it merges into) or `drop` (saying why the test adds nothing).
- A **File_Group** is the test files with Verdicts to apply that share a template, role or pattern, such as several test files of one kind, worked by one executor so the issues they share are handled the same way; a file with no peers is a group of one.
- The **Shared_Decisions** are a short list, written before any executor starts, of how each issue that recurs across the Verdicts is to be handled, given to every executor so their choices agree.
- A **Gap** is a code path, corner case or gotcha in Scope that no test proves.
- A **Mutation_Check** breaks, in one source file, the behaviour a test covers, shows that a test fails, and restores the file at once; step 8 says how.
- A **Vacuous_Test** is a test that still passes when the behaviour it claims to test is removed or inverted.
- An **Expected_Failure** is a test marked in the project's test framework as known to fail, such as node:test `todo` or Python's `expectedFailure`.
- The **backup folder** is a folder in the system's temporary directory, outside the repository, named `ponderly-tighten-tests-` followed by the repository's top-level path (`git rev-parse --show-toplevel`) with each `/` replaced by `-`, so that a later run finds it. It holds the backup of the one source file a Mutation_Check has broken, at that file's path relative to the repository's top level.
- An **executor** is the plugin's `task-executor` agent, launched as `ponderly:task-executor`. The **reviewer** is the plugin's `wave-reviewer` agent, launched as `ponderly:wave-reviewer`. Each agent's own definition holds its procedure, so a launch carries only its job.

## Working with the author

- **Stops.** Every run: the readability question in step 1; the Keep_List question in step 3; the approval of the Audit in step 5, repeated until approved. Only when something is wrong: the stop in step 1 when Scope holds no test file; the question in step 2 when the suite fails at the Baseline, and the one when the project has no coverage tool; the stop in step 6 when an executor changed a file outside its File_Group; the source check's stop in steps 6, 8 and 9; the restore offer in step 9 when the review finds a requirement left with no proof; the stop when the `task-executor` agent, the `wave-reviewer` agent or the `report` skill is missing. At the end: the Gap offer in step 10, when there are Gaps.
- **How it asks.** With the AskUserQuestion tool, fixed options plus free text, at the readability question, the suite and coverage-tool questions, the approval, the restore offer and the Gap offer. The Keep_List question is prose, since the answer is the author's own words.
- **Hand-backs.** The Audit, the File_Groups and the Shared_Decisions in step 5, as the approval question's text; the hand-back in step 10, written by the plugin's `report` skill.
- **Hand-offs.** `readable-code` when the author chooses to run it first; `start-task` for each Gap, or the issue it is filed as; `pr` once the hand-back is accepted. This skill never commits, branches or pushes.

If the Agent tool cannot find `ponderly:task-executor` or `ponderly:wave-reviewer`, or the Skill tool cannot find `ponderly:report`, say which is missing and stop. Do not do its work another way.

## 1. State the Scope and check readability

First, restore any backup an interrupted run left behind. If the backup folder exists and holds files, copy each one back over the file at the same path in the repository, delete it, and name each file restored; then delete the folder. Say nothing when there is none.

Find the target branch. When the repository has an `origin` remote and `git rev-parse --abbrev-ref origin/HEAD` names a branch, the target is that branch, `origin/<default>`. Otherwise the target is the local default branch, the branch `git config --get init.defaultBranch` names when it exists, else `main`. Find the base with `git merge-base <target> HEAD`.

Scope is every file `git diff --name-only <base>` lists, which compares the working tree with the base so uncommitted edits count, with the untracked files `git ls-files --others --exclude-standard` lists, narrowed to the files at or under the paths in the arguments when there are any. Sort Scope into test files and source files by the project's own test layout and naming. Outside Scope, the same layout and naming decide which files of the repository are test files; every other file is a source file for the source state.

Before anything else, say the Scope in one line: the target branch, the paths passed if any, and how many test and source files it holds. If Scope holds no test file, say so and stop, changing nothing.

Then ask, header `Readability`, whether `readable-code` has run on the final code, since renames and restructures change what the tests should assert and coverage is measured once, on the final code. Options:

- **It has run**: go on to step 2.
- **Run readable-code first (Recommended)**: invoke the Skill tool with `skill: ponderly:readable-code` and the same paths as `args`, and end this run.
- **Go on without it**: go on to step 2, and say in the hand-back that coverage was measured on code that may still change.

## 2. Take the Baseline

Find how the project runs its tests and its coverage, from its configuration and scripts. Run the full suite once with coverage, and record:

- the suite's result: passed, failed and skipped;
- the number of tests in each test file in Scope, and in total;
- for each module, the set of covered lines, read from the coverage tool's machine-readable report and kept in a file in the session's scratchpad;
- the source state.

If the suite fails, report the failing tests verbatim and ask, header `Baseline`, whether to go on (`Go on`, `Stop`). On `Go on`, record each failing test in Scope that fails because the source is wrong, with its failure output quoted; step 6 marks it an Expected_Failure.

If the project has no coverage tool, say so, and ask, header `Coverage`, with options `Add one` and `Mutation_Checks alone`. On `Add one`, name the tool that fits the project and add it as a development dependency, the way the project adds dependencies, then take the Baseline again; the hand-back lists the change. On `Mutation_Checks alone`, step 7 is skipped and the hand-back lists it as a check not run. Never add a tool unasked.

## 3. Gather the Keep_List

Before the Audit, gather the Keep_List from three places:

- the spec or ticket the branch serves: the `.ponderly/specs/<task>/requirements.md` the branch implements, or the issue the branch name or its commits cite; take every test a requirement or acceptance criterion names, and every seeded property test a spec names. Keep the requirements themselves for step 9;
- the tests of the branch: deployed end-to-end proofs, and seeded property tests;
- the author.

Show the list, each test quoted with its file and where it came from, and ask in prose which other tests must stay. Add the author's answer to the list.

## 4. Audit

Run the Audit in this session, and change no file while it runs. Find the tests the branch adds or changes from `git diff <base> -- <test files>` and the untracked test files. Read them side by side, with the source they exercise, so that duplicates across files show.

For every such test, write a Verdict record:

| Field | Notes |
|-------|-------|
| test | file and test name, quoted |
| proves | the path, corner case or gotcha, in a phrase |
| verdict | `keep`, `merge` or `drop` |
| into / why | the test it merges into, or why it adds nothing |
| on Keep_List | yes or no; a yes forces `keep` |

Judge each test by the `tests` rule. Then, reading the source in Scope against the tests, list every Gap: the path, corner case or gotcha, and the file and lines it lives in. Count the tests in Scope before the Verdicts and after them.

## 5. Get approval

Show the Audit as the approval question's text:

- every `drop` and every `merge` in full, with every field of its record;
- the `keep`s counted per file, not listed; the author can ask to see them;
- the test counts before and after the Verdicts;
- every Gap;
- the File_Groups: the test files that hold a `merge` or a `drop`, or a test that failed at the Baseline because the source is wrong, sorted into groups, each with its files and why they belong together;
- the Shared_Decisions for applying the Verdicts, such as how a merged test is named, where a shared fake goes, and how an Expected_Failure is marked in this project's test framework.

Ask, header `Approve`, options `Approved` and `Changes needed`, whether to apply these Verdicts with these File_Groups and Shared_Decisions. If the dialog cannot hold them, write them as a message immediately followed by the question. A Verdict, group or decision the author changes takes the author's value; a change that drops or merges a test on the Keep_List takes it off the Keep_List, and say so. Show the changed records and ask again. Apply no Verdict until the answer is a plain yes.

## 6. Apply the Verdicts

Launch one executor per approved File_Group, with `subagent_type: ponderly:task-executor`, all in one message so they run concurrently. Never say to an executor, in any words, that its task comes from a spec. Each prompt holds:

- the group's file paths, and that they are the only files to change;
- each file's approved Verdicts, each test quoted with its Verdict and the test it merges into or why it goes;
- the Shared_Decisions, verbatim, and that issues its files share are handled the same way in each;
- each test of the group that failed at the Baseline because the source is wrong, named, with its Baseline failure quoted, to be marked an Expected_Failure;
- the sentence, verbatim, "Change no source file.";
- the sentence, verbatim, "Never run `git stash`, `git checkout` or `git reset`.";
- the sentence "To see a file as it was before the branch changed it, use `git show <base>:<path>`, which is read-only.", with `<base>` replaced by the base found in step 1;
- that a test which fails because the source is wrong is marked an Expected_Failure in the project's test framework and the defect is reported under `unsure`, not fixed;
- that it proves the change by running its files' tests;
- the other File_Groups in flight.

When every executor has returned:

- A `stopped` Summary is shown to the author as it is. That group's files are left as they are and carried to the hand-back.
- For a `done` Summary, check that its `files changed` lists only its own group's test files. Any other file is treated as a changed source file: stop and report it. Then run the commands under its `checks run` yourself.
- Each Expected_Failure an executor marked, and each defect it reported, goes to the hand-back's problems, with the test and the defect.
- Run the source check.

Later steps relaunch a file's executor "as in step 6": a new executor for the File_Group that owns the file, with the same prompt, its job replaced by the one that step gives.

## 7. Compare coverage

Run the full suite with coverage again and read the covered lines per module. Report, for each module, the lines covered at the Baseline and after, both as counts. Set no threshold and judge no percentage.

Compare the covered lines line by line. For each line covered at the Baseline and not after, find the dropped or merged test whose path reached it, and relaunch that file's executor, as in step 6, to restore that test. Run coverage again to confirm the line is covered, and report the line and the test restored.

## 8. Run the Mutation_Checks

Record the source state again, to compare with at the end of this step.

Run the checks one at a time, never in parallel, so that only one source file is ever broken. Each check:

1. copies the one source file it changes to the backup folder;
2. changes one place in that file in the real tree;
3. runs only the tests named below;
4. restores the file from its backup at once, whatever the result, and deletes the backup.

Here a kept test is one whose Verdict is `keep`, and a new test is one the slimming added or merged another into.

- **Each dropped test**: break the behaviour it covered, and run the remaining tests of the module. Any remaining test must fail. If none fails, relaunch the file's executor, as in step 6, to restore the dropped test, and report it.
- **Each kept or new test**: remove or invert the behaviour it claims to test, and run that test. It must fail. A test that still passes is a Vacuous_Test: relaunch its file's executor, as in step 6, with the mutation that left it passing, to fix the test so it fails under it. Run the check again, with a new backup. If it still passes, report it to the author as vacuous. Skip a test marked Expected_Failure, and say so.

When the checks are done, delete the backup folder. Then compare the source state with the record taken at the start of this step, stopping and reporting the diff if it differs, and run the source check. Keep the empty diff for the hand-back as the proof that the source is as it was.

## 9. Review

Launch the reviewer once, with `subagent_type: ponderly:wave-reviewer`, and a prompt that holds:

- the list of test files this run changed, from the executors' Summaries and the restorations of steps 7 and 8;
- the requirements the branch serves, quoted, from step 3; or, when there are none, the Keep_List, quoted;
- the approved Verdicts for every `drop` and `merge`;
- the job: report any requirement, or test on the Keep_List, left with no test that proves it;
- the files that cite the changed ones: search the repository for each changed file's path and name.

Nothing more, and never the diff, which the reviewer gathers itself.

Wait for its Findings. Then:

- For each requirement the Findings name as left with no proof, report it and ask, header `Restore`, options `Restore it` and `Leave it`, whether to restore the test that proved it. On `Restore it`, relaunch that file's executor, as in step 6, and run its tests.
- A `blocker` or `should-fix` that needs a source change is not fixed; it goes to the hand-back's problems, quoted.
- Every other `blocker` or `should-fix` is fixed, for up to two fix attempts. One in a test file this run changed goes to the executor of the File_Group that owns the file, relaunched as in step 6. One in a file the slimming made wrong without changing it, such as a shared fake that only dropped tests used and that is now dead, or a document that counts the tests, goes to a new executor, launched as in step 6 with that file as a group of one and the finding as its whole task; never a source file. After each attempt, run that file's tests, run the Mutation_Check of step 8 for every test the fix changed, handling a Vacuous_Test as step 8 does, and run the source check. A finding still open after the two attempts goes to the hand-back's problems, quoted.
- Every `nit`, and every finding in a file the slimming neither changed nor made wrong, goes to the hand-back's problems, quoted.

There is no second review after the fixes.

## 10. Hand back

Invoke the Skill tool with `skill: ponderly:report` and `args: handback`, inline, to write the hand-back Message. It carries:

- the problems, first: each executor that stopped; each Expected_Failure with its defect; each line that lost its test and the test restored; each dropped test restored by a Mutation_Check; each Vacuous_Test left unfixed; each review finding still open after two fix attempts, each that needs a source change, and each `nit`; each check not run, such as coverage when there is no tool, and readability when the author went on without it;
- the test counts before and after, per file and in total;
- the coverage per module at the Baseline and after;
- the empty source diff of step 8;
- the files changed;
- each Gap as a separate task one `start-task` run could take, saying what is unproved and where; none is filled here;
- the next step: `/ponderly:pr`. Nothing is committed.

When there are Gaps, put the Message as the text of a question, header `Gaps`, options `File them` and `Leave them`, asking whether to file each Gap as an issue; when the dialog cannot hold the Message, write it as a message immediately followed by the question. When there are none, the Message is the hand-back and the run ends.

On `File them`, file each Gap as its own issue with `gh issue create --title <title> --body-file - <<'EOF'`, then the body, then `EOF`, on one command. Write the body for the issue's reader, who has none of the author's local state: what is unproved, the file and lines, and why it matters; no branch name, no uncommitted files and no command to run. Show each issue's URL, or the error verbatim if the command fails. On `Leave them`, the Gaps stay in the Message.
