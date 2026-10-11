---
name: implement-spec
description: Build a task whose spec already exists, wave by wave from its tasks.md, each task built by the task-executor agent and each wave read by the wave-reviewer agent before the wave ends. Use when asked to implement, build, work, continue or resume a spec, a task list, or the tasks in .claude/specs/<task>/. Reads the spec, validates its dependency graph, asks the author how often to hand back (after each task or each wave) and whether to write the optional tests, then works the waves in order with one sub-agent per leaf task, ticking each checkbox only when its tests pass or a stated manual check is done, running the full suite at the end of every wave, and handing back for review at the chosen cadence. Never edits the spec beyond checkboxes without the author's approval, and pauses with a proposal when the design cannot be followed.
argument-hint: "[task-name] [task|wave]"
allowed-tools: Bash(git status *) Bash(git branch *) Bash(git rev-parse *) Bash(git log *) Bash(git diff *) Bash(ls .claude/specs*) Bash(cat .claude/specs/*)
---

# Implement a spec

Build a task from its approved spec: read `.claude/specs/<task-name>/`, check that its task list can be executed, and then work the waves in order, each leaf task built by its own executor and each wave read by the reviewer before the wave ends, ticking each checkbox only when its tests have passed or, for a task with nothing to test, after a stated manual check. Hand back to the author as often as they chose, after every task or after every wave, with a report of what was built and tested.

The author is accountable for the code and owns the spec. The spec is the source of truth: `requirements.md` says what, `design.md` says how, and `tasks.md` says in what order. Do not change any of them, beyond ticking checkboxes, without the author's approval, and do not guess your way past a design that cannot be followed; pause and propose the change instead.

Arguments, if the author gave any: $ARGUMENTS

Terms used below:

- A **leaf task** is a checkbox task in `tasks.md` with no sub-tasks: a top-level task with no sub-tasks is a leaf; a parent with sub-tasks is not. A leaf task marked `*` is an **optional test**.
- An **ephemeral check** is a scratch script or call that exercises new code to prove a task works, is never added to the codebase, and is deleted before the task is done. It is how a code task is verified when its tests are a task of their own.
- A **wave** is one entry of the Task Dependency Graph at the end of `tasks.md`. Waves run in order. Task numbers only identify tasks; the graph decides the order of work.
- The **cadence** is the author's choice of when a run hands back: after each leaf task, or after each wave.
- A **skipped test** is an optional test the author chose not to do in this run. It stays unticked.
- An **executor** is the plugin's `task-executor` agent, launched as `freethinking:task-executor`, one per leaf task. Its own definition holds its procedure, so the launch carries only the task: it gathers the context the task needs, implements exactly what the task describes, proves it, and returns a summary with a `status` of `done` or `stopped`, the files it changed, the checks it ran, its ephemeral check's code, what it is unsure of and, when stopped, why. Tests are tasks of their own in a spec, so an executor writes a test only when its task is a test task.
- The **reviewer** is the plugin's `wave-reviewer` agent, launched as `freethinking:wave-reviewer`, one per wave. It is read-only and changes nothing; it gathers the wave's diff itself and returns Findings: a `verdict` of `holds` or `findings`, then each finding with its file, an exact quote, the problem and a severity of `blocker`, `should-fix` or `nit`, then what it is `unsure` of. Its own definition holds its procedure, so the launch carries only what to review.
- A **sub-agent**, below, means either.

## 1. Find the spec

Take the task name from the arguments: the first word that is not `task` or `wave`. The cadence is a second argument of `task` or `wave`, or an explicit phrase in the author's message such as "one task at a time" or "a wave at a time". The word "task" on its own in a sentence is not a cadence.

- With a task name, the spec is `.claude/specs/<task-name>/`.
- With no task name, run `ls .claude/specs/*/tasks.md` and look at each list for an unticked non-optional leaf task. Exactly one such spec: name it and confirm it with the author. Several: list them and ask which to work. None: say there is nothing to implement, name any spec whose only unticked tasks are optional tests, recommend `/freethinking:start-task` otherwise, and stop.

If the spec has no `tasks.md`, say so, recommend `/freethinking:start-task`, and stop without changing anything. One look at `.claude/specs/<task-name>/tasks.md` settles it; do not search elsewhere for the spec.

Read `tasks.md`, `requirements.md` and `design.md` in full before anything else. The requirements and design are read again task by task later, but the whole has to be in view first.

## 2. Validate the graph

Before going further, check that the Task Dependency Graph can be executed. Build two tables and show both to the author:

- **Leaf tasks**: every leaf task in `tasks.md`, with its id, its text, whether it is ticked, whether it is an optional test, the requirements it cites (both a `_Requirements:_` line and a `**Validates:**` line count), and the design property it names if any.
- **Graph**: every wave id and the task ids in it.

Then run three checks against the tables:

1. Every leaf task, optional tests included, appears in exactly one wave.
2. Every task id in the graph is a leaf task in the list.
3. Wave ids are unique and ascending.

If `tasks.md` has no graph, or any check fails, list each problem by task id, propose the fix as a spec edit, and wait for the author. The fix is usually a corrected `waves` block. A task list written under the old template may carry checkpoint tasks, whose text is only a pause for review with no work in it; for those, propose removing the task rather than adding it to the graph. When the author approves, apply the edit to `tasks.md`, run the three checks again, and continue to step 3. Make no code change until the graph is valid.

## 3. Find the position

Walk the waves in order and find the first wave with an unticked non-optional leaf task; that wave is the position. Ticked tasks are done; never redo one. A wave whose only unticked tasks are optional tests counts as finished for finding the position; those tests were skipped in an earlier run, and the author can ask for them at the end.

If every non-optional leaf task is already ticked, report the spec complete. If optional tests remain unticked, name them and ask whether to do them now; if yes, they are the work for this run, worked wave by wave as in step 5 with the full suite at the end of each; the earliest such wave becomes the position that step 4 states. Otherwise recommend `/freethinking:pr` and stop.

## 4. Set up the run

State where things stand: the wave found in step 3, every leaf task in it with whether it is ticked, and any that are optional tests.

Then ask the author one round of questions, batched, and only the ones that apply:

- **Cadence**, if step 1 did not settle it: hand back after each leaf task, or after each wave?
- **Optional tests**, if the wave from step 3 contains any and step 3 did not already settle it: do them in this wave, or skip them? The question is asked again for each later wave that contains one.
- **Branch**, if `git branch --show-current` is the repository's default branch (`git rev-parse --abbrev-ref origin/HEAD` with the `origin/` prefix removed, or `main` if that is unset): propose the task name as the branch name, and once the author confirms create it and switch to it with `git checkout -b <name>`. The workflow rule forbids working on the default branch.

Make no code change until the author has answered.

## 5. Work the wave

Work one wave at a time; waves run in order. Each leaf task in a wave gets its own executor, launched with the Agent tool as `subagent_type: freethinking:task-executor`, which returns at once and runs the sub-agent in the background; once every executor of the wave has returned, the wave gets one reviewer. At wave cadence, launch every task of the wave before waiting on any of them, all in one message, so they run concurrently. At task cadence, launch one and wait for its result before the next, so that the hand-back after each task still makes sense. Each agent runs on the model its own definition pins; verifying, ticking, the full suite and the report are not delegated: they are done in this session, on the session's own model.

Beyond ticking checkboxes, do not edit `tasks.md`, `requirements.md` or `design.md` in this step. A change any of them needs goes to step 6 as a proposal.

### Starting a wave

If the wave contains optional tests and the author has not yet said whether to do them in this wave, ask once now. Then check the code for every unticked task in the wave other than a skipped test: look for the behaviour, file or test the task describes, and tell the author which tasks already appear done. A task whose text is an action for the author to take by hand, such as running a session and recording what happened, gets no sub-agent either: ask the author to do it, and tick it when they report the result. It stays outside the wave review, since the reviewer has no change of it to read; if it did change files, the author names them and they join the reviewer's file list. A task that appears done gets no sub-agent. Verify it yourself: the test it names if it is a test task, otherwise an ephemeral check of the behaviour plus the existing tests for the code it touches, or a stated manual check if there is nothing to test. A pass does not tick it at once: it waits for the wave's review and is ticked with the rest, and the files its task text names, or its check touched, join the reviewer's file list. A failure means it was not done, so launch an executor for it after all. The same holds for a task that appears done when a run resumes after a hand-back.

### Launching a task

For each task that is left, other than a skipped test, state its number, its text and the requirements it cites. Then launch the agent with `subagent_type: freethinking:task-executor` and a prompt that holds:

- the mode sentence, verbatim, "This task is a leaf task from a spec; tests are tasks of their own.", which puts the agent in its spec mode;
- the task text and its cited requirements, quoted from `requirements.md`;
- the sections of `design.md` that name the component, data model, interface or property the task touches, quoted;
- the other tasks of this wave that are in flight, with the instruction to touch only the files its own task needs;
- for a property-test task, the design property the task names, to tag the test with.

Nothing more. The agent's own definition carries its procedure, the shape of its summary and the instruction to stop on drift, and the plugin's `SubagentStart` hook puts the handbook rules in its context, so the launch restates none of them. One task per sub-agent and per change. Never give a sub-agent two tasks, and never ask it to tick anything in `tasks.md`. The mode sentence is what tells the agent not to write a test for a code task, so never leave it out, and never ask for a test unless the task is a test task.

### When a task comes back

At wave cadence, wait until every executor of the wave has returned before verifying or ticking any task that had one, so that nothing is run while a sibling is still editing and a file two of them changed is judged as a whole. At task cadence handle each task as it returns. For each task:

1. Read the summary's `status` first. `stopped` is drift: the agent found that the design does not fit the code, that the task would need a new dependency, framework or tool, or that the task is unclear, and it changed nothing more. Do not let it work around that, and do not relaunch or retry the task unprompted. The task stays unticked, and its `files changed` goes under the report's Files changed as what it had already touched. Finish judging the wave's other tasks as below, through the wave review, then go to step 6 once, with its `stopped because` as the evidence, and propose the spec edit. The rest of this list is for a summary with `status: done`.
2. Read the rest of the summary. A summary whose `checks run` lists nothing and whose `ephemeral check` gives no reason why none applied goes back to the executor.
3. Run every command under `checks run` yourself, and the ephemeral check from the code given under `ephemeral check`, re-created in the scratchpad and deleted afterwards. The summary is a report, not evidence.
4. If two executors of the wave changed the same file, name that file to the reviewer as one two executors changed, so that it is judged as a whole there.
5. For a task with no testable behaviour, perform a manual check instead, say in the report what it was, and tick only after it.

Then:

- Tests pass: tick the task's checkbox in `tasks.md`, after the wave review below: at wave cadence every task waits for it, and at task cadence only the wave's last task does, the earlier ones being ticked at their hand-backs. Never tick a task whose tests, or stated manual check, you have not run yourself in this session. When every sub-task of a top-level task is ticked, tick the top-level task too.
- Tests fail: send the output to the same executor to fix, or to a new one launched as above and given its summary and the failing output, for up to two fix attempts. If they still fail, the task stays unticked; once the wave review below is done, go to step 6 with the output verbatim. Other tasks of the wave already in flight, including their fix attempts within the two allowed, are left to finish and judged as above; no further task of the wave is launched.

Skipped tests stay unticked and are listed as skipped in the report.

### Reviewing the wave

Once every executor of the wave has returned, whatever each returned, and before any tick, review the wave as a whole. The review covers the tasks that passed their own checks, together with any task that appeared already done; those are fixed and ticked after it as below, and then a task that stopped, or still fails after two fix attempts, goes to step 6. At task cadence, where the wave's earlier tasks were ticked at their hand-backs, the review runs once, when the wave's last task has passed its checks and before its tick, and covers the whole wave; a task that stops or will not pass before then goes to step 6 at once, and the review waits for the wave's last task. The file list and the `unsure` items come from this run's summaries and, after a resume, from the reports of the earlier hand-backs: their Files changed and follow-ups.

Launch the reviewer with `subagent_type: freethinking:wave-reviewer`, once, and a prompt that holds:

- the sentence, verbatim, "These changes come from a spec wave", which tells the reviewer that a code task correctly lacks a test;
- the list of files the wave changed or created, taken from the `files changed` of the wave's summaries, with the files of tasks that appeared already done or that the author did by hand, as under "Starting a wave", and with any file two executors changed named as such;
- the requirement and design excerpts the wave's tasks cite, quoted;
- the files that cite the changed ones: search the repository for each changed file's path and name.

Nothing more, and never the diff: the reviewer runs `git diff` and reads the files itself, so the diff never enters this session. Its own definition carries its procedure and the shape of its Findings, and the `SubagentStart` hook puts the handbook rules in its context, so the launch restates none of them. Wait for its Findings. One reviewer per wave: no second reviewer with another lens, no refuter after it, and no second review after the fixes.

Collect every `unsure` item from the wave's summaries, and the reviewer's own, beside its findings. Then:

- A `blocker` or `should-fix`, and any `unsure` item that is a defect, in a file a task of the wave changed, is fixed: send it to the executor that owns the file, or to a new one launched as above and given the finding, as a fix within the same two attempts the task has for failing tests, and re-run that task's checks yourself. A finding in a task ticked at an earlier hand-back is fixed the same way, and its tick stands. If it is still not fixed after those two attempts, go to step 6 with the finding.
- A finding in a file no task of the wave changed, but which the wave's changes made wrong, such as a citing file that now disagrees, gets a new executor with the finding as its whole task, within the same two attempts. This is the one case where a problem in a file outside the task is fixed in the run, because the wave caused it.
- A finding in `requirements.md`, `design.md` or `tasks.md` goes to step 6 as a proposal.
- A `nit` is fixed the same way or carried.
- The reviewer's own `unsure` items follow the same split: those about the changes are handled like findings, those outside the changes go to follow-ups.
- Anything else is outside the wave. Anything carried, whether a `nit`, an `unsure` item that is not a defect or a problem outside the wave, goes under the report's follow-ups with the reason it was not fixed.

Tick only after that: every task of the wave whose checks passed, any that appeared already done, or at task cadence the wave's last task.

### Ending a wave

With the review done and every task in the wave ticked, other than a skipped test or a task the author chose to skip under step 7, run the project's full test suite, the way the project runs it. If it passes, go to step 6 and report, with the suite's result in the report; at task cadence that is the report for the wave's last task. If it fails, go to step 6 with the failing output verbatim and ask the author how to proceed before starting the next wave. Never start a task from a later wave while a task in this wave, other than a skipped test, is unticked.

## 6. Hand back and report

Hand back here at the end of a cadence unit (after a task at task cadence, after a wave at wave cadence), after a failed full suite, after a task whose tests still fail after two fix attempts, after a review finding that is still not fixed after two attempts, or when an executor reports that the design cannot be followed or needs a new dependency. For the final wave, when its full suite passes, step 8 takes this step's place. Write the report, in this shape and order, then wait for the author:

```
## Done
- <task id> <task text> (Requirements <ids>)
## Tests
- `<command>`: <result>, per test command and ephemeral check run
- Full suite `<command>` at end of wave <n>: <result>, when a wave ended
- Wave review of wave <n>: <verdict>; carried: <each finding or `unsure` item carried, or "nothing">, when a wave was reviewed
## Files changed
- <paths>
## Skipped / follow-ups
- <optional tests skipped at the author's request; problems found outside the task, noted and not fixed>
## Next
- <next unticked task and its wave>, or the proposal below
```

Add to the report, depending on why you handed back:

- **A failing full suite or a task that will not pass**: the failing output verbatim, then which causes are confirmed and which are open. Ask the author how to proceed. Do not start the next wave.
- **A review finding that is still not fixed**: the finding quoted, then what each of the two attempts did. Ask the author how to proceed.
- **A design that cannot be followed, or a new dependency the task would need**: the evidence from the code, then a specific edit to `design.md` or `tasks.md`, quoted as it would read. Make no further code change until the author answers.

A problem found outside the current task is noted under follow-ups and left alone; do not fix it in this run. The one exception is a file the wave's changes made wrong, which the wave review in step 5 fixes. Never commit or push unless the author asks.

## 7. Continue

When the author says to continue, resume at step 5 with the same cadence and the optional-test choices already made for their waves: the next unticked task in the current wave, or the next wave if this one is done, where the optional-test question is asked afresh if it has one.

When the author approves a spec edit, apply it to the named file exactly as approved, and resume where the run handed back: at the task that raised it, or at step 3 if the edit was a graph fix made before any work.

When the author asks to skip a non-optional task or to work out of wave order, say which tasks may depend on it: the graph holds waves, not edges, so that is every task in a later wave. Proceed only after the author confirms. A skipped non-optional task stays unticked and is listed under follow-ups in every later report, and later waves start on the author's say-so despite it.

## 8. Finish

When every leaf task is ticked, apart from skipped tests and any non-optional task the author chose to skip under step 7, and the final wave's full suite passes, write the report for the final wave with its full suite result in place of step 6, note any skipped tests, and recommend `/freethinking:pr` to open the pull request. Then stop.
