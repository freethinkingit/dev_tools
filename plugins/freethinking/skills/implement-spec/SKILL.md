---
name: implement-spec
description: Build a task whose spec already exists, wave by wave from its tasks.md, with the task-executor agent building each task and the wave-reviewer agent reading each wave. Use when asked to implement, build, work, continue or resume a spec, a task list, or the tasks in .freethinking/specs/<task>/. Reads the spec and validates its dependency graph, then asks once how often to hand back (after each task, each wave, or only at the end) and how to treat optional tests (ask, always, never). Runs one sub-agent per leaf task, ticks a checkbox only when its tests pass or a stated manual check is done, and runs the full suite at the end of every wave. Never edits the spec beyond checkboxes without the author's approval, and pauses with a proposal when the design cannot be followed.
argument-hint: "[task-name] [task|wave|spec]"
allowed-tools: Bash(git status *) Bash(git branch *) Bash(git rev-parse *) Bash(git log *) Bash(git diff *) Bash(ls .freethinking/specs*) Bash(cat .freethinking/specs/*)
---

# Implement a spec

Build a task from its approved spec: read `.freethinking/specs/<task-name>/`, check that its task list can be executed, and then work the waves in order, each leaf task built by its own executor and each wave read by the reviewer before the wave ends, ticking each checkbox only when its tests have passed or, for a task with nothing to test, after a stated manual check. Hand back to the author as often as they chose, after every task, after every wave, or only once every wave is done, with a report of what was built and tested.

The author is accountable for the code and owns the spec. The spec is the source of truth: `requirements.md` says what, `design.md` says how, and `tasks.md` says in what order. Do not change any of them, beyond ticking checkboxes, without the author's approval, and do not guess your way past a design that cannot be followed; pause and propose the change instead.

Arguments, if the author gave any: $ARGUMENTS

Terms used below:

- A **leaf task** is a checkbox task in `tasks.md` with no sub-tasks: a top-level task with no sub-tasks is a leaf; a parent with sub-tasks is not. A leaf task marked `*` is an **optional test**.
- An **ephemeral check** is a scratch script or call that exercises new code to prove a task works, is never added to the codebase, and is deleted before the task is done. It is how a code task is verified when its tests are a task of their own.
- A **wave** is one entry of the Task Dependency Graph at the end of `tasks.md`. Waves run in order. Task numbers only identify tasks; the graph decides the order of work.
- The **cadence** is the author's choice of when a run hands back: after each leaf task (task cadence), after each wave (wave cadence), or only at the end of the run (spec cadence). At spec cadence every wave still ends with its review, its full suite and its report, but the report is written into the conversation without waiting for the author, and the next wave starts at once, in the same turn, so the session holds one short report per wave and never the diff; once the last wave is done, the reviewer reads the whole run once more, in a final review, and the run hands back with the final report. Before the end it hands back only for a failure, an unfixed finding or a proposal.
- The **optional-tests choice** is the author's choice of what to do with optional tests: ask about them (at the start of each wave that has one, or at spec cadence once at the end of the run), always do them, or never do them.
- A **skipped test** is an optional test the author chose not to do in this run. It stays unticked.
- An **executor** is the plugin's `task-executor` agent, launched as `freethinking:task-executor`, one per leaf task. Its own definition holds its procedure, so the launch carries only the task: it gathers the context the task needs, implements exactly what the task describes, proves it, and returns a summary with a `status` of `done` or `stopped`, the files it changed, the checks it ran, its ephemeral check's code, what it is unsure of and, when stopped, why. Tests are tasks of their own in a spec, so an executor writes a test only when its task is a test task.
- The **reviewer** is the plugin's `wave-reviewer` agent, launched as `freethinking:wave-reviewer`, one per wave, and at spec cadence once more over the whole run. It is read-only and changes nothing; it gathers the wave's diff itself and returns Findings: a `verdict` of `holds` or `findings`, then each finding with its file, an exact quote, the problem and a severity of `blocker`, `should-fix` or `nit`, then what it is `unsure` of. Its own definition holds its procedure, so the launch carries only what to review.
- A **sub-agent**, below, means either.

## Working with the author

- **Stops.** Most stops happen only in some runs; a run with a valid graph in which nothing goes wrong stops only at the first group.
  - Every run: the set-up round of step 4, with whichever of its questions apply; the hand-back of step 6 at the chosen cadence. At spec cadence that is the report of step 6 written at the end of each wave, which does not wait for the author, and the final report of step 8, which does.
  - Only when the author left something out: the choice among several specs in step 1, when no task name was given.
  - Only when something is wrong: the approval of a graph fix in step 2; the question in step 6 of how to proceed after a failing suite, a task that will not pass or an unfixed finding; the proposal in step 6 when the design cannot be followed or a task needs a new dependency.
  - Only when the author asks for it: the question in step 3 whether to do the remaining optional tests of an otherwise complete spec; the optional-tests question at the start of each wave that has one, in step 5, when the author chose to be asked, or at spec cadence the one offer of every skipped optional test at the end of the run, in step 8; the confirmation in step 7 before skipping a non-optional task or working out of wave order; the request in step 5 for a task done by hand, when the spec has one.
- **How it asks.** With the AskUserQuestion tool, fixed options plus free text. The set-up round of step 4 is one call holding the cadence (after each task; after each wave; run every wave and hand back only at the end), the optional tests (ask about them, at each wave that has one or at spec cadence once at the end; always do them; never do them) and the branch (create it under the proposed name). The tool also asks the per-wave optional-tests question (do them in this wave, skip them), the end-of-run optional-tests offer at spec cadence (do them now, leave them), the choice of spec in step 1, the confirmations of steps 3 and 7, and the approval of a graph fix or spec edit once the edit is shown in full. The question of how to proceed after a hand-back, and the request for a task done by hand, are prose, since the answer is the author's own words.
- **Hand-backs.** The two tables of step 2; the report of step 6, written by the plugin's `report` skill, with the failing output verbatim or the proposed edit quoted as it would read when the hand-back is for one; at spec cadence, the report of step 6 for each wave, written without waiting, and the report of step 8, covering the run with a line for the final review.
- **Hand-offs.** `start-task` when there is no spec or no `tasks.md`; `pr` when every non-optional task is ticked, at step 3 or step 8.

## 1. Find the spec

Take the task name from the arguments: the first word that is not `task`, `wave` or `spec`. The cadence is a second argument of `task`, `wave` or `spec`, or an explicit phrase in the author's message such as "one task at a time", "a wave at a time" or "run all the waves". The word "task" or "spec" on its own in a sentence is not a cadence. The optional-tests choice is settled here only by an explicit phrase in the author's message, such as "skip the optional tests".

- With a task name, the spec is `.freethinking/specs/<task-name>/`.
- With no task name, run `ls .freethinking/specs/*/tasks.md` and look at each list for an unticked non-optional leaf task. Exactly one such spec: name it and proceed. Several: list them and ask which to work. None: say there is nothing to implement, name any spec whose only unticked tasks are optional tests, recommend `/freethinking:start-task` otherwise, and stop.

If the spec has no `tasks.md`, say so, recommend `/freethinking:start-task`, and stop without changing anything. One look at `.freethinking/specs/<task-name>/tasks.md` settles it; do not search elsewhere for the spec.

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

- **Cadence**, if step 1 did not settle it: hand back after each leaf task, after each wave, or run every wave and hand back only at the end?
- **Optional tests**, if the wave from step 3 or a later one contains an unticked optional test and neither step 1 nor step 3 already settled it: ask about them (at the start of each wave that has one, or at spec cadence once at the end of the run), always do them, or never do them?
- **Branch**, if `git branch --show-current` is the repository's default branch (`git rev-parse --abbrev-ref origin/HEAD` with the `origin/` prefix removed, or `main` when that command fails because it is unset): propose the task name as the branch name, and once the author confirms create it and switch to it with `git checkout -b <name>`. The workflow rule forbids working on the default branch.

Ask the cadence and optional-tests questions in one AskUserQuestion call, with the branch question when it applies. They are asked only here: both answers hold for the whole run, through every resume in step 7.

Make no code change until the author has answered.

## 5. Work the wave

Work one wave at a time; waves run in order. Each leaf task in a wave gets its own executor, launched with the Agent tool as `subagent_type: freethinking:task-executor`, which returns at once and runs the sub-agent in the background; once every executor of the wave has returned, the wave gets one reviewer. At wave or spec cadence, launch every task of the wave before waiting on any of them, all in one message, so they run concurrently. At task cadence, launch one and wait for its result before the next, so that the hand-back after each task still makes sense. Each agent runs on the model its own definition pins; verifying, ticking, the full suite and the report are not delegated: they are done in this session, on the session's own model.

Beyond ticking checkboxes, do not edit `tasks.md`, `requirements.md` or `design.md` in this step. A change any of them needs goes to step 6 as a proposal.

### Starting a wave

If the wave contains optional tests: when the author chose to be asked, ask once now whether to do them in this wave, except at spec cadence, where they are skipped tests for now and offered once at the end of the run in step 8; when they chose always, they are worked like any other task; when they chose never, they are skipped tests. Then check the code for every unticked task in the wave other than a skipped test: look for the behaviour, file or test the task describes, and tell the author which tasks already appear done. A task whose text is an action for the author to take by hand, such as running a session and recording what happened, gets no sub-agent either: ask the author to do it, and tick it when they report the result. It stays outside the wave review, since the reviewer has no change of it to read; if it did change files, the author names them and they join the reviewer's file list. A task that appears done gets no sub-agent. Verify it yourself: the test it names if it is a test task, otherwise an ephemeral check of the behaviour plus the existing tests for the code it touches, or a stated manual check if there is nothing to test. A pass does not tick it at once: it waits for the wave's review and is ticked with the rest, and the files its task text names, or its check touched, join the reviewer's file list. A failure means it was not done, so launch an executor for it after all. The same holds for a task that appears done when a run resumes after a hand-back.

### Launching a task

For each task that is left, other than a skipped test, state its number, its text and the requirements it cites. Then launch the agent with `subagent_type: freethinking:task-executor` and a prompt that holds:

- the mode sentence, verbatim, "This task is a leaf task from a spec; tests are tasks of their own.", which puts the agent in its spec mode;
- the task text and its cited requirements, quoted from `requirements.md`;
- the sections of `design.md` that name the component, data model, interface or property the task touches, quoted;
- the other tasks of this wave that are in flight, with the instruction to touch only the files its own task needs;
- for a property-test task, the design property the task names, to tag the test with.

Nothing more. The agent's own definition carries its procedure, the shape of its summary and the instruction to stop on drift, and the plugin's `SubagentStart` hook puts the handbook rules in its context, so the launch restates none of them. One task per sub-agent and per change. Never give a sub-agent two tasks, and never ask it to tick anything in `tasks.md`. The mode sentence is what tells the agent not to write a test for a code task, so never leave it out, and never ask for a test unless the task is a test task.

### When a task comes back

At wave or spec cadence, wait until every executor of the wave has returned before verifying or ticking any task that had one, so that nothing is run while a sibling is still editing and a file two of them changed is judged as a whole. At task cadence handle each task as it returns. For each task:

1. Read the summary's `status` first. `stopped` is drift: the agent found that the design does not fit the code, that the task would need a new dependency, framework or tool, or that the task is unclear, and it changed nothing more. Do not let it work around that, and do not relaunch or retry the task unprompted. The task stays unticked, and its `files changed` goes under the report's files (its Files section in the plugin's template) as what it had already touched. Finish judging the wave's other tasks as below, through the wave review, then go to step 6 once, with its `stopped because` as the evidence, and propose the spec edit. The rest of this list is for a summary with `status: done`.
2. Read the rest of the summary. A summary whose `checks run` lists nothing and whose `ephemeral check` gives no reason why none applied goes back to the executor.
3. Run every command under `checks run` yourself, and the ephemeral check from the code given under `ephemeral check`, re-created in the scratchpad and deleted afterwards. The summary is a report, not evidence.
4. If two executors of the wave changed the same file, name that file to the reviewer as one two executors changed, so that it is judged as a whole there.
5. For a task with no testable behaviour, perform a manual check instead, say in the report what it was, and tick only after it.

Then:

- Tests pass: tick the task's checkbox in `tasks.md`, after the wave review below: at wave or spec cadence every task waits for it, and at task cadence only the wave's last task does, the earlier ones being ticked at their hand-backs. Never tick a task whose tests, or stated manual check, you have not run yourself in this session. When every sub-task of a top-level task is ticked, tick the top-level task too.
- Tests fail: send the output to the same executor to fix, or to a new one launched as above and given its summary and the failing output, for up to two fix attempts. If they still fail, the task stays unticked; once the wave review below is done, go to step 6 with the output verbatim. Other tasks of the wave already in flight, including their fix attempts within the two allowed, are left to finish and judged as above; no further task of the wave is launched.

Skipped tests stay unticked and are listed as skipped in the report.

### Reviewing the wave

Once every executor of the wave has returned, whatever each returned, and before any tick, review the wave as a whole. The review covers the tasks that passed their own checks, together with any task that appeared already done; those are fixed and ticked after it as below, and then a task that stopped, or still fails after two fix attempts, goes to step 6. At task cadence, where the wave's earlier tasks were ticked at their hand-backs, the review runs once, when the wave's last task has passed its checks and before its tick, and covers the whole wave; a task that stops or will not pass before then goes to step 6 at once, and the review waits for the wave's last task. The file list and the `unsure` items come from this run's summaries and, after a resume, from the reports of the earlier hand-backs: the files and the problems each one lists (its Files and Problems sections in the plugin's template).

Launch the reviewer with `subagent_type: freethinking:wave-reviewer`, once, and a prompt that holds:

- the sentence, verbatim, "These changes come from a spec wave", which tells the reviewer that a code task correctly lacks a test;
- the list of files the wave changed or created, taken from the `files changed` of the wave's summaries, with the files of tasks that appeared already done or that the author did by hand, as under "Starting a wave", and with any file two executors changed named as such;
- the requirement and design excerpts the wave's tasks cite, quoted;
- the files that cite the changed ones: search the repository for each changed file's path and name.

Nothing more, and never the diff: the reviewer runs `git diff` and reads the files itself, so the diff never enters this session. Its own definition carries its procedure and the shape of its Findings, and the `SubagentStart` hook puts the handbook rules in its context, so the launch restates none of them. Wait for its Findings. One reviewer per wave: no second reviewer with another lens, no refuter after it, and no second review after the fixes. The one other review is the final review of the whole run at spec cadence, in step 8.

Collect every `unsure` item from the wave's summaries, and the reviewer's own, beside its findings. Then:

- A `blocker` or `should-fix`, and any `unsure` item that is a defect, in a file a task of the wave changed, is fixed: send it to the executor that owns the file, or to a new one launched as above and given the finding, as a fix within the same two attempts the task has for failing tests, and re-run that task's checks yourself. A finding in a task ticked at an earlier hand-back is fixed the same way, and its tick stands. If it is still not fixed after those two attempts, go to step 6 with the finding.
- A finding in a file no task of the wave changed, but which the wave's changes made wrong, such as a citing file that now disagrees, gets a new executor with the finding as its whole task, within the same two attempts. This is the one case where a problem in a file outside the task is fixed in the run, because the wave caused it.
- A finding in `requirements.md`, `design.md` or `tasks.md` goes to step 6 as a proposal.
- A `nit` is fixed the same way or carried.
- The reviewer's own `unsure` items follow the same split: those about the changes are handled like findings, those outside the changes go under the report's problems (its Problems section in the plugin's template), with the reason they were not fixed, and not under its next step (its Next section in the plugin's template).
- Anything else is outside the wave. Anything carried, whether a `nit`, an `unsure` item that is not a defect or a problem outside the wave, goes under the report's problems, with the reason it was not fixed, and not under its next step.

Tick only after that: every task of the wave whose checks passed, any that appeared already done, or at task cadence the wave's last task.

### Ending a wave

With the review done and every task in the wave ticked, other than a skipped test or a task the author chose to skip under step 7, run the project's full test suite, the way the project runs it. If it passes, go to step 6 and report, with the suite's result in the report; at task cadence that is the report for the wave's last task. At spec cadence a pass goes to step 6 too, for the wave's report, but does not wait: write the report in full, as step 6 writes it, then launch the next wave's executors in the same turn, straight after it, with nothing written between. The report ends the message, not the turn. A line saying the wave is done is not the report; the report is what the final review reads back. If it fails, go to step 6 with the failing output verbatim and ask the author how to proceed before starting the next wave. Never start a task from a later wave while a task in this wave, other than a skipped test, is unticked.

## 6. Hand back and report

Hand back here at the end of a cadence unit (after a task at task cadence, after a wave at wave or spec cadence), after a failed full suite, after a task whose tests still fail after two fix attempts, after a review finding that is still not fixed after two attempts, or when an executor reports that the design cannot be followed or needs a new dependency. For the final wave, when its full suite passes, step 8 takes this step's place; at spec cadence, write that wave's report first, without waiting, as for any other wave, so that every wave's report is in the conversation for step 8. The report ends the message, with nothing written after it in that message. A hand-back that waits for the author is the only place the turn ends: at task or wave cadence that is every report, and at spec cadence it is the final report of step 8 or a stop for a failure, an unfixed finding or a proposal. At spec cadence, after a wave whose full suite passed, the report is written without waiting, and the next wave's executors are launched in the same turn, straight after it, as the next tool calls.

To write the report, invoke the Skill tool with `skill: freethinking:report` and `args: handback`, once, in this session; its Message is the report, with nothing written before or after it in that message. If the Skill tool cannot find `freethinking:report`, say the plugin's `report` skill is missing and write the hand-back by the communication rule, Problems first.

At spec cadence each report covers its own wave, and the reports stack up in the conversation, one per wave, for the final review and the final report of step 8 to read back. A hand-back that waits, for a failure, an unfixed finding or a proposal, covers the wave it stops in, with the earlier waves' reports already above it.

The failing output, the finding, the proposed edit and the question are already in the conversation the report skill reads. Each goes under the report's problems or its next step (the Problems and Next sections in the plugin's template), by the cause of the hand-back:

- **A failing full suite or a task that will not pass**: the failing output verbatim, then which causes are confirmed and which are open; next, the question of how to proceed. Do not start the next wave.
- **A review finding that is still not fixed**: the finding quoted, then what each of the two attempts did; next, the question of how to proceed.
- **A design that cannot be followed, or a new dependency the task would need**: the evidence from the code; next, a specific edit to `design.md` or `tasks.md`, quoted as it would read. Make no further code change until the author answers.

A problem found outside the current task is a discovery: it goes under the report's problems with where it is, roughly how much work it would add to the branch, and its two options, a task in `tasks.md` or an issue, and is left alone; do not fix it in this run. The one exception is a file the wave's changes made wrong, which the wave review in step 5 fixes. At spec cadence, where a wave's report does not wait, each discovery reappears in the final report of step 8 for the author to answer. Never commit or push unless the author asks.

## 7. Continue

When the author says to continue, resume at step 5 with the same cadence and the same optional-tests choice: the next unticked task in the current wave, or the next wave if this one is done, whose optional tests are asked about at its start only when the author chose to be asked and the cadence is not spec. At spec cadence, when the hand-back came from the final review or the end-of-run optional tests of step 8, resume there.

When the author approves a spec edit, apply it to the named file exactly as approved, and resume where the run handed back: at the task that raised it, or at step 3 if the edit was a graph fix made before any work.

When the author answers a discovery from the report's problems: for a task, write a proposal for `tasks.md`, the task and its wave quoted as they would read, and apply it as a spec edit on the author's approval; for an issue, draft its title and body in the next message and leave filing it to the author. A discovery the author has answered is not listed in later reports.

When the author asks to skip a non-optional task or to work out of wave order, say which tasks may depend on it: the graph holds waves, not edges, so that is every task in a later wave. Proceed only after the author confirms. A skipped non-optional task stays unticked and is listed under the report's problems in every later report, and later waves start on the author's say-so despite it.

## 8. Finish

When every leaf task is ticked, apart from skipped tests and any non-optional task the author chose to skip under step 7, and the final wave's full suite passes, finish.

At task or wave cadence, write the report for the final wave with its full suite result, by the same invocation as step 6, in place of step 6. The Message's next step (its Next section in the plugin's template) names any skipped tests as left unticked and recommends `/freethinking:pr` to open the pull request, which the report skill writes because this step's text is in the conversation; add nothing after it. Then stop.

At spec cadence, finish in three parts:

1. **Optional tests.** When the author chose to be asked and the run skipped optional tests, offer them once, all together, with the AskUserQuestion tool: do them now, or leave them. If the author says do them, work them as one final set as in step 5: an executor each, launched together, their checks run here, their own wave review, their ticks, and the full suite. A failure there goes to step 6 as for any wave. Left, they stay unticked as skipped tests. When the author chose always or never, there is nothing to offer.
2. **Final review.** Launch the reviewer once more, with `subagent_type: freethinking:wave-reviewer`, over the whole run, and a prompt that holds:
   - the sentence, verbatim, "These changes come from a spec wave", which tells the reviewer that a code task correctly lacks a test;
   - the full list of files the run changed or created, taken from the files every wave's report lists;
   - each wave's report as written: its problems, what was done, its checks with the full-suite result and the wave-review verdict, its files and its next step;
   - the requirement and design excerpts the run's tasks cite, quoted;
   - the files that cite the changed ones, found as for a wave review.

   Nothing more, and never the diff, which the reviewer gathers itself. Its job is the whole: consistency across waves, nits and other items carried from wave to wave that have piled up, and anything one wave's review could not see. Handle its Findings and `unsure` items by the rules of "Reviewing the wave" in step 5: a `blocker`, a `should-fix` or an `unsure` item that is a defect is fixed by an executor within two attempts, with the owning task's checks re-run here; a `nit` is fixed or carried; a finding in the spec goes to step 6 as a proposal; and a finding still not fixed after two attempts goes to step 6. If anything was fixed, run the full suite once more; a failure goes to step 6. There is no second final review.
3. **Final report.** Write the report by the same invocation as step 6, covering the whole run: every task ticked in it, the full suite result and the wave-review verdict of each wave, the final review's verdict and whether anything was carried, and the files the run changed. The plugin's template writes the verdicts as the lines `Wave review of wave <n>: <verdict>` and `Final review of the run: <verdict>`, each followed by `carried: see Problems` or `nothing carried`; with a repository's own template, the final review reads the wave verdicts, and the final report writes the run's verdict, wherever that template puts them. The Message's next step names any skipped tests as left unticked and recommends `/freethinking:pr` to open the pull request, which the report skill writes because this step's text is in the conversation; add nothing after it. Then stop.
