---
name: readable-code
description: Make the source a branch changes read plainly, and prove its behaviour unchanged. Use when asked to make this branch readable, for a readability pass, or to simplify or untangle the code a branch changes. Works on the files the branch changes against its target branch, narrowed to the paths passed. Takes a baseline of the full suite, and of the synthesized output where the branch holds infrastructure code, then has the author approve groups of like files and the decisions they share, and launches one task-executor agent per group to apply the team's readability and comment rules with no behaviour change and no rename for taste. Runs both again, asks whether to revert or keep any file whose change made a difference, has the wave-reviewer agent read the pass, sends its blocker and should-fix findings back to the executors to fix, and hands back with the report skill. Not for a test cleanup, which is tighten-tests's; not for a bug, which is bugfix's; not for a new change, which is start-task's. Commits nothing.
argument-hint: "[paths]"
allowed-tools: Bash(git status *) Bash(git branch *) Bash(git rev-parse *) Bash(git config --get *) Bash(git log *) Bash(git merge-base *) Bash(git diff *) Bash(git ls-files *) Bash(cp *)
---

# Make a branch readable

Run a readability pass over the source a branch changes: one executor per group of like files, all following one list of shared decisions, applies the "Write for the reader." bullet of the `code-changes` rule and the `comments` rule to them, then the full suite, and the synthesized output where there is infrastructure code, prove that nothing behaves differently, and the reviewer reads the pass. The pass changes how the code reads, never what it does.

The author is accountable for the code. A difference from the Baseline is the author's to judge: name the file and ask, never decide it alone. Commit nothing, and change no file yourself beyond restoring one the author chose to revert.

Paths to narrow the pass to, if the author gave any: $ARGUMENTS

Terms used below:

- The **Scope** is the files the branch changes against its target branch, uncommitted and untracked work included, narrowed to the paths passed when there are any.
- A **source file** is a file in Scope that holds code the project runs or deploys. Tests, documentation, configuration, lock files and generated files are not source files; a test cleanup is `tighten-tests`'s.
- **Infrastructure code** is infrastructure-as-code that generates deployment templates. Its **synthesized output** is the templates the project's command that generates them produces.
- The **Baseline** is what step 2 records before anything changes: the full suite's result, the synthesized output where Scope holds infrastructure code, and a copy of each source file in Scope.
- A **File_Group** is the source files in Scope that share a template, role or pattern, such as several pages of one kind, worked by one executor so the issues they share are fixed the same way. A file with no peers is a group of one, and no file is in two groups.
- The **Shared_Decisions** are a short list, written before any executor starts, of how each issue that recurs across Scope is to be handled, one line each, given to every executor so their choices agree.
- An **executor** is the plugin's `task-executor` agent, launched as `freethinking:task-executor`, one per File_Group. Its own definition holds its procedure and the shape of its Summary.
- The **reviewer** is the plugin's `wave-reviewer` agent, launched as `freethinking:wave-reviewer`, once per run. Its own definition holds its procedure and the shape of its Findings.

## Working with the author

- **Stops.** Most runs stop at two points: the approval of the File_Groups and Shared_Decisions in step 3, and the hand-back of step 7.
  - Only when something is wrong: the stop in step 1 when Scope holds no source file; the question in step 2 when the project has no test suite or the suite fails at the Baseline; the revert-or-keep question in step 5 for each file whose change made a difference, and in step 6 for each file a fix left differing; the stop when the `task-executor` agent, the `wave-reviewer` agent or the `report` skill is missing.
- **How it asks.** With the AskUserQuestion tool, fixed options plus free text: whether the File_Groups and Shared_Decisions are approved (header `Groups`: approved, changes needed, with the changes as free text), whether to go on after a failing Baseline (go on, stop), whether to go on without a test suite (go on with a manual check the author names, stop), and for each differing file whether to revert or keep its change, all such files in one call.
- **Hand-backs.** The Scope line of step 1; the hand-back of step 7, written by the `report` skill, with every stopped executor, every difference kept, every finding still open after two fix attempts and every `nit` under its problems.
- **Hand-offs.** `tighten-tests` to clean up the branch's tests now that the code reads plainly; `pr` to open the pull request.

The plugin's rules on working with and writing to the author apply throughout; this skill does not restate them.

## 1. State the Scope

Find the target branch. When the repository has an `origin` remote and `git rev-parse --abbrev-ref origin/HEAD` names a branch, the target is that branch, `origin/<default>`. Otherwise the target is the local default branch, the branch `git config --get init.defaultBranch` names when it exists, else `main`. Find the base with `git merge-base <target> HEAD`.

Scope is every file `git diff --name-only <base>` lists, which compares the working tree with the base so that uncommitted edits count, with the untracked files `git ls-files --others --exclude-standard` lists, narrowed to the paths in the arguments when there are any. Keep the files that still exist. Of what is left, the source files are the work.

Say the Scope in one line before changing anything, naming the target branch and any paths passed, such as "Scope: 6 source files the branch changes against origin/main, under src/api". If Scope holds no source file, say so in that line, name what it did hold if anything, and stop without changing anything.

## 2. Take the Baseline

Before any file changes:

1. Copy each source file in Scope to the session's scratchpad, keeping its path, so that a file's change can later be reverted without touching what the branch already holds uncommitted.
2. Run the project's full test suite, the way the project runs it, and record the result: which tests pass, which fail, and the counts.
3. Where Scope holds infrastructure code, run the project's command that generates its deployment templates, with its output directed into the scratchpad, and keep that output.

If the project has no test suite, say so, and ask whether to go on with a manual check the author names, run at the Baseline and again in step 5 in place of the suite, or to stop. Do not add a test framework.

If the suite fails at the Baseline, report the failing tests with their output verbatim, and ask whether to go on, with the failing tests as the known failures the later comparison allows, or to stop. Change nothing until the author answers. On stop, delete the scratchpad copies and end there.

## 3. Group the files and agree the decisions

Read the source files in Scope. Sort them into File_Groups: files that share a template, role or pattern, such as several pages of one kind or several handlers of one shape, go in one group; a file with no peers is a group of one; no file is in two groups. Then write the Shared_Decisions: each readability issue that recurs across Scope, in a line with how it is to be handled, such as "Name the request body `payload` in every handler." When nothing recurs, say so in place of the list.

Show the File_Groups, each with its files and, in a line, why they belong together, then the Shared_Decisions, and ask with the AskUserQuestion tool, header `Groups`, whether they are approved, with the options `Approved` and `Changes needed`, the changes as free text. On changes, apply them and ask again. Change no file until the answer is a plain approval.

## 4. Launch the executors

Launch one executor per File_Group, all in one message so they run concurrently, each with the Agent tool as `subagent_type: freethinking:task-executor` and a prompt that holds:

- **Request**: "Make `<paths>` read plainly: apply the "Write for the reader." bullet of the `code-changes` rule and the `comments` rule to the code the branch added or changed in them, fix the issues they share the same way in each, and leave untouched code elsewhere in the files as it is.", with `<paths>` the group's files.
- **Lines in scope**: for each of the group's files, the lines the branch added or changed in it, from `git diff <base> -- <path>`, or the whole file when it is untracked.
- **Shared decisions**: the approved Shared_Decisions, verbatim, with the sentence, verbatim, "Follow these decisions wherever the issue they name appears in your files."
- **Constraints**: the sentence, verbatim, "No behaviour change, no rename for taste, prove it with the existing tests.", followed by the sentence, verbatim, "Renaming a one-letter, misleading or terse name to a descriptive one is what "Write for the reader." asks for; a rename for taste swaps one clear name for another clear name.", followed by the sentence, verbatim, "To see the old code, read its Baseline copy at `<copy>`; never run `git stash`, `git checkout` or `git reset`.", given once for each of the group's files, with `<copy>` the scratchpad path of that file's Baseline copy
- **In flight**: the source files of the other File_Groups being made readable in this run, with the instruction to touch only the group's own files.
- **Boundaries**: the sentence, verbatim, "Make only this change. Commit nothing. Return the Summary."

Nothing more. Never say, in any words, that the task comes from a spec: a readability pass is not a spec task, and the executor must run in its standalone mode. The constraints sentence is what keeps that mode from adding a test for a change with no new behaviour. The executor's own definition carries its procedure and the instruction to stop on drift, and the plugin's `SubagentStart` hook puts the handbook rules in its context, so the launch restates none of them.

If the Agent tool cannot find `freethinking:task-executor`, say that the plugin's `task-executor` agent is missing and stop. Do not make the readability changes yourself.

Wait until every executor has returned. Then, for each Summary:

- **`stopped`**: show the Summary verbatim. Do not relaunch it or work around it. Leave the group's files as the executor left them, name any partial edits it lists under `files changed`, and carry the group's files and its `stopped because` to the hand-back's problems. Its partial edits stay in the comparison of step 5.
- **`done`**: a Summary whose `files changed` names a file outside its group goes under the hand-back's problems with that file named. Collect its `unsure` items for the hand-back.

## 5. Prove no behaviour changed

Run the full suite again, the same way, and compare it with the Baseline: the same tests pass and the same tests fail. To see how the old code behaved, run it from its Baseline copy; never run `git stash`, `git checkout` or `git reset`, which would touch the branch's uncommitted work and the stash every worktree shares. Where Scope holds infrastructure code, run the synthesis again into the scratchpad and diff its output against the Baseline's.

If both match, say so in one line and go on to step 6.

If either differs, name the file that caused each difference: the source file the failing test exercises or the stack trace points at, or the source file that defines the resource whose synthesized output changed. When the evidence points at more than one file, name each. Report each difference with its output verbatim, then ask, for each named file, whether to revert its change or keep it, naming the file or files each answer covers. On revert, restore each named file from its Baseline copy, then run the suite, and the synthesis where it applies, once more and say whether they now match. A kept difference goes to the hand-back's problems with its output.

## 6. Review the pass

Launch the reviewer once, with the Agent tool as `subagent_type: freethinking:wave-reviewer` and a prompt that holds:

- the files the pass changed, from the Summaries' `files changed`, less any reverted in step 5;
- for each, the scratchpad path of its Baseline copy, with the instruction that the pass's own changes are `git diff --no-index <copy> <path>`, whose exit status 1 means the files differ and is expected, and that the branch's earlier changes are not under review;
- what the changes must satisfy: the "Write for the reader." bullet of the `code-changes` rule and the `comments` rule, which the hook puts in its context, and the constraints sentence the executors were given, quoted;
- the files that cite the changed ones: search the repository for each changed file's path and name.

Nothing more, and never the diff. If the Agent tool cannot find `freethinking:wave-reviewer`, say that the plugin's `wave-reviewer` agent is missing and stop. Do not review the pass yourself.

Wait for its Findings, and collect the reviewer's `unsure` items beside them. Then:

- A `blocker` or `should-fix`, and any reviewer `unsure` item that is a defect in a file the pass changed, is fixed: send it, quoted, to the executor of the group that holds the file, or to a new one launched as in step 4 for that group and given the finding, with the same Shared_Decisions and constraints sentences. A fix is still bound by them: no behaviour change, no rename for taste. Up to two attempts per finding.
- After each attempt, re-run that file's checks yourself: the full suite, compared with the Baseline as in step 5, and, where Scope holds infrastructure code, the synthesis diffed against the Baseline's output. A difference means the attempt failed. If a difference remains after the second attempt, name the file, report the difference verbatim and ask whether to revert or keep, as in step 5.
- A finding still open after two attempts, every `nit`, and every reviewer `unsure` item that is not a defect in the pass's changes go to the hand-back's problems, quoted, with the reason each was not fixed.

No second review after the fixes.

## 7. Hand back

Delete the scratchpad copies and the synthesized outputs. Then invoke the Skill tool with `skill: freethinking:report` and `args: handback`, once; its Message is the hand-back, with nothing written after it. Its problems hold every stopped executor, every difference kept, every finding still open after two fix attempts, every `nit`, every `unsure` item carried from the executors and the reviewer, and any Baseline failure the author chose to go on past. Its Next says the changes sit uncommitted on the current branch, and recommends `/freethinking:tighten-tests` to clean up the branch's tests now that the code reads plainly, or `/freethinking:pr` to open the pull request.

If the Skill tool cannot find `freethinking:report`, say that the plugin's `report` skill is missing and stop. Do not write the hand-back yourself.

Commit nothing and push nothing.
