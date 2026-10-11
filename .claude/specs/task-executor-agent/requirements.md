# Requirements Document

## Introduction

`task-executor` is a plugin agent that builds one well-specified change: a leaf task from a spec, or any single task an engineer hands it directly. Today `implement-spec` launches a general-purpose sub-agent for each task and restates the whole working procedure and the team rules in every launch prompt, and those sub-agents start without the handbook rules in their context. Moving the procedure into an agent definition makes it one source of truth, lets `implement-spec` launch with just the task, and gives engineers the same disciplined executor on demand. A prerequisite change to the plugin's hooks delivers the team rules to every sub-agent, not only to sessions.

## Glossary

- **Agent**: The `task-executor` plugin agent described by this document, defined in `agents/task-executor.md` and addressed as `handbook:task-executor`.
- **Reviewer**: The `wave-reviewer` plugin agent, defined in `agents/wave-reviewer.md` and addressed as `handbook:wave-reviewer`, which reviews one set of changes against the requirements and design they implement.
- **Findings**: The fixed-shape report the Reviewer returns: a verdict, then each finding with its file, an exact quote, the problem and a severity, then anything the Reviewer is unsure of.
- **Author**: The engineer whose session launches the Agent, directly or through `implement-spec`.
- **Launcher**: Whatever launches the Agent: the `implement-spec` skill, or the Author by name.
- **Spec_Mode**: The Agent's behaviour when its launch prompt says the Task is a Leaf_Task from a Spec: tests are tasks of their own, so a code Task gets no test.
- **Standalone_Mode**: The Agent's behaviour when the launch prompt does not say that: the ordinary code-changes rule applies, and a behaviour change comes with its test.
- **Task**: The one change the Agent is launched to make: a Leaf_Task from a Spec, or a single change the Author describes.
- **Leaf_Task**: A checkbox task with no sub-tasks in a Spec's `tasks.md`, as `implement-spec` defines it.
- **Spec**: A directory `.claude/specs/<task>/` with `requirements.md`, `design.md` and `tasks.md`.
- **Test_Task**: A Leaf_Task whose text asks for a test to be written.
- **Ephemeral_Check**: A scratch script or call that exercises new code to prove a Task works, kept outside the codebase and deleted before the Agent finishes.
- **Summary**: The fixed-shape report the Agent returns: status, files changed, checks run with results and code, things unsure of, and a reason when stopped.
- **Rules**: The handbook rules under `rules/`, which the SessionStart hook prints into every session.
- **Rules_Hook**: The plugin hook that delivers the Rules to a sub-agent when it starts.
- **Drift**: A point where the Task cannot be done as described: the design does not fit the code, the Task would need a new dependency or tool, or the Task is unclear.

## Requirements

### Requirement 1: Prerequisite: every sub-agent gets the Rules

**User Story:** As an Author, I want every sub-agent my session launches to work under the team rules, so that delegated work is held to the same standard as my own.

#### Acceptance Criteria

1. THE plugin SHALL register a `SubagentStart` hook in `hooks/hooks.json`, with no agent-type matcher, that runs a script printing the Rules.
2. THE Rules_Hook SHALL output the Rules as JSON `hookSpecificOutput.additionalContext` with `hookEventName` `SubagentStart`, since plain stdout is not added to a sub-agent's context for that event.
3. THE Rules_Hook SHALL print the same text as the SessionStart hook, from the same `rules/` files, so there is one source.
4. WHEN a sub-agent of any type starts in a session with the plugin enabled, THE sub-agent SHALL have the Rules in its context before its first prompt.
5. IF the Rules_Hook fails, THEN THE sub-agent SHALL still start, and the failure SHALL be visible in the sub-agent's transcript.

### Requirement 2: The Agent definition

**User Story:** As an Author, I want the executor's procedure to live in one agent definition, so that `implement-spec` and I launch the same executor and a change to the procedure is made once.

#### Acceptance Criteria

1. THE plugin SHALL ship `agents/task-executor.md` with frontmatter `name: task-executor`, a `description` that says it builds one well-specified change and invites direct use for a single task, `model: opus` and `effort: medium`, so that every executor runs on Opus at medium effort while the orchestrating session keeps its own model.
2. THE Agent's `tools` SHALL be the tools needed to read, edit, write and run code and tests: `Read`, `Glob`, `Grep`, `Edit`, `Write`, `Bash`.
3. THE Agent's body SHALL hold the procedure: gather context first (the Task, its cited requirements and design, the surrounding code, the project's tests and configuration), implement only what the Task describes as the smallest change in the project's style, prove it, then return the Summary.
4. THE Agent SHALL prove a Test_Task by running the test it wrote, a Standalone_Mode change by running the test it wrote with it, and a Spec_Mode code Task by an Ephemeral_Check, in every case together with the existing tests for the code it touched, or by a stated manual check when there is nothing to exercise.
5. WHILE in Spec_Mode, THE Agent SHALL NOT write a test unless its Task is a Test_Task, and SHALL NOT produce code for any Task other than its own.
6. WHILE in Standalone_Mode, THE Agent SHALL write a test with every behaviour change in the project's test framework, the way the project writes tests, and SHALL say so when the project has no test framework and record a manual check instead.
7. THE Agent SHALL decide between Spec_Mode and Standalone_Mode from the launch prompt alone, and SHALL be in Standalone_Mode when the prompt does not say the Task comes from a Spec.
8. THE Agent SHALL NOT edit a Spec's `requirements.md`, `design.md` or `tasks.md`, and SHALL NOT tick a checkbox.
9. THE Agent SHALL NOT commit, push, create a branch, or add a dependency, framework or tool.
10. THE Agent SHALL delete every Ephemeral_Check and scratch file before it finishes, and SHALL include the check's code in the Summary so the Launcher can re-run it.
11. IF the Agent meets Drift, or is unsure what the Task asks, THEN THE Agent SHALL stop without assuming, make no further change, and return a Summary with status `stopped` and the question or evidence the Launcher needs, rather than guess or work around it.
12. THE Agent's body SHALL NOT restate the Rules, since the Rules_Hook delivers them; it MAY name the ones the procedure depends on.

### Requirement 3: The Summary

**User Story:** As a Launcher, I want every executor to report the same way, so that `implement-spec` can verify and tick from it and an Author can read it at a glance.

#### Acceptance Criteria

1. THE Summary SHALL have, in order: `status` (`done` or `stopped`), the files changed, every test command and Ephemeral_Check run with its result, the Ephemeral_Check's code, anything the Agent is unsure of, and when stopped, the reason.
2. WHEN the Agent ran no test and no Ephemeral_Check, THE Summary SHALL say why none applied.
3. THE Summary SHALL state facts the Agent observed, and SHALL mark anything inferred as inferred.

### Requirement 4: implement-spec launches the Agent

**User Story:** As an Author running `implement-spec`, I want each task built by the Agent, so that the skill's launch carries only the task and the executor's behaviour is the one place it is defined.

#### Acceptance Criteria

1. WHEN `implement-spec` launches a sub-agent for a Leaf_Task, THE skill SHALL launch the Agent by its scoped name `handbook:task-executor`.
2. THE launch prompt SHALL say that the Task is a Leaf_Task from a Spec, so the Agent is in Spec_Mode, and SHALL carry the Task text, its cited requirements quoted from `requirements.md`, the design sections the Task touches quoted from `design.md`, the other tasks of the wave in flight with the instruction to touch only the Task's own files, and for a property-test Task the design property to tag.
3. THE launch prompt SHALL NOT restate the Agent's procedure, the Rules, or the Summary shape.
4. WHEN the Agent returns `stopped`, THE skill SHALL treat it as Drift under its own step 6 and SHALL NOT retry the Task unprompted.
5. THE skill's verification, ticking, full-suite and reporting steps SHALL be unchanged, and SHALL run in the session's own model, so the orchestrator is the model the Author chose for the session.
6. WHEN every Sub_Agent of a Wave has returned and their checks have passed, THE skill SHALL review the Wave as a whole before ticking anything: it SHALL launch the Reviewer as a sub-agent, giving it the list of files the Wave changed or created, the requirements and design sections the Wave's tasks cite, and the files the changes must agree with; the Reviewer gathers the Wave's diff itself so that the diff never enters the orchestrating session, and returns Findings. THE skill SHALL also collect every `unsure` item from the Wave's Summaries. Each finding and each `unsure` item SHALL be either fixed before the tick or carried into the report's follow-ups with the reason. One reader per Wave; no repeated lenses, no refuters.
7. THE skill SHALL define both agents in its Terms by scoped name, the executor `handbook:task-executor` for one Leaf_Task and the Reviewer `handbook:wave-reviewer` for one Wave, and SHALL name the Reviewer in the wave step at the point it is launched, with what it is given and what it returns.

### Requirement 5: Ship in the handbook

**User Story:** As an engineer, I want the Agent installed with the plugin, documented, and covered by evals, so that it is used the same way as the skills.

#### Acceptance Criteria

1. THE README SHALL gain an Agents section naming `task-executor` and `wave-reviewer`, how to launch each directly, and what each returns.
2. THE handbook SHALL include two eval cases under `evals/agents/task-executor/` on a scaffolded project: one launching the Agent in Spec_Mode, grading that the code landed, no test was written, and the Summary has the required shape; one launching it in Standalone_Mode, grading that the code landed with a test in the project's test file.
3. THE handbook SHALL include an eval case under `evals/hook/` that launches a sub-agent and grades that it reports the Rules present.
4. THE `implement-spec` work-loop eval SHALL still pass after the skill launches the Agent.
5. THE plugin version SHALL be bumped for the release that adds the Agent.
6. THE handbook SHALL include two eval cases under `evals/agents/wave-reviewer/` on a scaffolded project: one whose diff carries a planted contradiction with a cited requirement, grading that the Findings name the file and the problem with `verdict: findings`; and one whose diff is clean, grading `verdict: holds`, so the Reviewer is not rewarded for always finding something.
7. THE README SHALL describe the free checks and the evals under one Testing heading, and SHALL state that using the plugin needs only Claude Code while developing it needs make and python3.

### Requirement 6: The Reviewer agent

**User Story:** As an Author, I want the review of a wave done by a reviewer whose procedure is defined once, so that every wave is read the same way and the reviewing rules can be changed without touching the coding ones.

#### Acceptance Criteria

1. THE plugin SHALL ship `agents/wave-reviewer.md` with frontmatter `name: wave-reviewer`, a `description` that says it reviews one set of changes against the requirements and design they implement and the files they must agree with, and invites direct use on any diff, `tools: Read, Glob, Grep, Bash`, `model: opus` and `effort: high`.
2. THE Reviewer SHALL NOT edit, write, create or delete any file, commit, or run anything that changes the working tree; its body SHALL say so, and `Bash` is for `git diff`, `git status` and reading.
3. WHEN launched, THE Reviewer SHALL gather the diff itself from the file list it is given (`git diff` for tracked files, the full content of new files) and read the requirement and design excerpts and the citing files it is given.
4. THE Reviewer SHALL judge each change by what it is: text that instructs (a skill, an agent, a rule, a prompt, a README) is dry-run in its head against a concrete case and every point of doubt reported; code the suite cannot exercise on this machine is reasoned through; a changed file is checked against the files that cite it.
5. THE Reviewer SHALL apply the team rules in its context as the standard it reviews against, and SHALL treat a code task in a spec wave as correctly lacking a test, since tests are tasks of their own there.
6. THE Findings SHALL have, in order: `verdict` (`holds` or `findings`), each finding with `file`, `quote` (exact text from the diff or a cited file), `problem` (one sentence) and `severity` (`blocker`, `should-fix` or `nit`), then `unsure`.
7. IF the Reviewer cannot gather the diff or a cited file is missing, THEN THE Reviewer SHALL return `verdict: findings` with one blocker that names what is missing, rather than review what it has as if it were complete.
8. THE Reviewer's body SHALL NOT restate the team rules; the Rules_Hook delivers them.
