# Requirements Document

## Introduction

`implement-spec` is a handbook skill that builds a task whose spec already exists. An engineer who has an approved `tasks.md` from `start-task` runs it to have Claude work the task list the way the workflow rule describes: wave by wave, with each leaf task built by its own subagent and the tasks of a wave built in parallel, ticking each task only when its tests pass, and stopping for review as often as the engineer chooses. The engineer picks the cadence, and the skill never changes the spec or skips ahead on its own. It turns the "existing spec: follow it" rule into a repeatable procedure with a visible record of what was built and tested. A prerequisite change to `start-task` makes its dependency graph the single statement of execution order, so the skill never has to reconcile task numbering with the order of work.

## Glossary

- **Skill**: The `implement-spec` skill described by this document, run as `/ponderly:implement-spec`.
- **Author**: The engineer running the Skill, who is accountable for the resulting code.
- **Spec**: A directory `.claude/specs/<task>/` holding `requirements.md`, `design.md` and `tasks.md` produced by `start-task`.
- **Task_List**: The `tasks.md` file of a Spec.
- **Leaf_Task**: A checkbox task in the Task_List that has no sub-tasks; the unit of work. A top-level task with no sub-tasks is a Leaf_Task; a parent with sub-tasks is not. Optional_Tests are Leaf_Tasks.
- **Optional_Test**: A Leaf_Task marked `*` in the Task_List, which the Author may choose to skip at run time. An Optional_Test the Author chose to skip for its Wave is a Skipped_Test for that Run.
- **Skipped_Test**: An Optional_Test the Author chose to skip in the current Run. The choice lives in the conversation, not in the Task_List, so a Skipped_Test stays unticked.
- **Wave**: One entry in the Graph: a set of Leaf_Tasks that depend only on Leaf_Tasks in earlier Waves. Waves run in order, so the end of a Wave is a point where the Author can review.
- **Graph**: The Task Dependency Graph in the Task_List: the ordered list of Waves. It names every Leaf_Task, Optional_Tests included, exactly once. The Graph, not task numbering, decides execution order; task numbers only identify tasks.
- **Cadence**: The Author's choice of when a Run hands back: after each Leaf_Task, or after each Wave.
- **Sub_Agent**: An agent the Skill launches for one Leaf_Task. It gathers the context the task needs, implements exactly what the task describes, and returns a summary of what it changed, what it ran and what it is unsure of. It writes tests only when its task is a test task, because tests are their own tasks in a Spec.
- **Full_Suite**: The project's whole test suite, run the way the project runs it.
- **Ephemeral_Check**: A scratch script or call that exercises new code to prove a Leaf_Task works, kept out of the codebase and deleted before the task is done.
- **Run**: One invocation of the Skill, from reading the Spec to handing back to the Author.
- **Report**: The summary the Skill gives when it hands back: tasks completed, tests run and their results, files changed, tasks skipped and follow-ups noted, and what comes next.
- **Drift**: A point where the design or Task_List cannot be followed as written.
- **Default_Branch**: The repository's main branch, which the workflow rule forbids working on.

## Requirements

### Requirement 1: Prerequisite: start-task writes a Graph the Skill can execute

**User Story:** As an Author, I want the Graph written by `start-task` to be the single statement of execution order, with every task in it, so that the Skill can work from the Graph alone and never lose a task.

#### Acceptance Criteria

1. THE `start-task` skill's task-list step SHALL instruct that the Graph names every Leaf_Task, Optional_Tests included, exactly once.
2. THE `start-task` skill's task-list step SHALL instruct that the Graph, not task numbering, decides execution order, and SHALL NOT ask for checkpoint tasks.
3. THE `start-task` task-list template SHALL contain no checkpoint tasks, SHALL define a leaf task, SHALL state the two rules above in its Graph prose, and SHALL give an example Graph that satisfies them.
4. WHEN `start-task` writes a Task_List under the updated instructions, THE Task_List SHALL pass the Skill's Graph validation in Requirement 2.
5. THE Skill SHALL treat a Task_List written under the old template, which contained checkpoint tasks, whose Graph omits a Leaf_Task, as failing validation and handle it under Requirement 2.

### Requirement 2: Find, load and validate the Spec

**User Story:** As an Author, I want the Skill to pick up the right Spec, check its Graph, and know where it left off, so that I can resume work across sessions without re-explaining it.

#### Acceptance Criteria

1. WHEN the Author gives a task name as the argument, THE Skill SHALL read that Spec's `tasks.md`, `requirements.md` and `design.md` before doing anything else.
2. WHEN the Author gives no argument and exactly one Spec has an unticked non-optional Leaf_Task, THE Skill SHALL name that Spec and confirm it with the Author.
3. WHEN the Author gives no argument and more than one Spec has an unticked non-optional Leaf_Task, THE Skill SHALL list them and ask the Author which to work.
4. IF the named Spec has no `tasks.md`, THEN THE Skill SHALL say so, recommend `/ponderly:start-task`, and make no code change.
5. WHEN the Skill loads the Task_List, THE Skill SHALL validate the Graph before any other step, checking that: every Leaf_Task, Optional_Tests included, appears in exactly one Wave; every task id in the Graph is a Leaf_Task in the Task_List; and Wave ids are unique and ascending.
6. IF the Task_List has no Graph or the Graph fails validation, THEN THE Skill SHALL list each problem by task id, propose a corrected Graph, or the removal of a task that has no work in it, as a spec edit under Requirement 6, and make no code change until the Author approves it.
7. WHEN the Spec has ticked Leaf_Tasks, THE Skill SHALL resume at the first unticked Leaf_Task in Wave order and SHALL NOT redo a ticked task.
8. WHEN every non-optional Leaf_Task in the Task_List is already ticked at load, THE Skill SHALL report the Spec complete, name any unticked Optional_Tests and ask whether to do them, and otherwise recommend `/ponderly:pr` and stop.
9. WHEN the Author gives no argument and no Spec has an unticked non-optional Leaf_Task, THE Skill SHALL say there is nothing to implement, recommend `/ponderly:start-task`, and stop.

### Requirement 3: Set up the Run

**User Story:** As an Author, I want to say how often the Skill hands back and whether to write the optional tests, so that I control how much it does unattended.

#### Acceptance Criteria

1. WHEN a Run starts, THE Skill SHALL state the next unticked Wave and the Leaf_Tasks in it.
2. WHEN a Run starts and the Author has not stated a Cadence in the argument or the message, THE Skill SHALL ask the Author to choose a Cadence of one Leaf_Task or one Wave.
3. WHEN the Skill starts a Wave that contains an Optional_Test, THE Skill SHALL ask the Author once, for that Wave, whether to do the Optional_Tests in it.
4. THE Skill SHALL batch the Cadence question, the Optional_Test question for the first Wave, and the branch question into a single round of questions.
5. IF the current branch is the Default_Branch, THEN THE Skill SHALL propose a branch name derived from the task name and create it after the Author confirms, before the first code change.
6. WHILE the Author has not answered the start questions, THE Skill SHALL make no code change.

### Requirement 4: Work a Leaf_Task

**User Story:** As an Author, I want each task built in wave order by a subagent that starts from its cited requirements and design, with its checkbox ticked only on passing tests, so that the Task_List is a trustworthy record of what is done and a wave's tasks can proceed in parallel.

#### Acceptance Criteria

1. THE Skill SHALL work Waves in order, and MAY run the Leaf_Tasks of one Wave in parallel, each in its own Sub_Agent.
2. THE Skill SHALL NOT start a Leaf_Task from a later Wave while any Leaf_Task in the current Wave other than a Skipped_Test is unticked.
3. THE Skill SHALL NOT combine two Leaf_Tasks into one change or one Sub_Agent.
4. WHEN the Skill starts a Leaf_Task, THE Skill SHALL state its number, its text and the requirements it cites, and SHALL give the Sub_Agent the task text, the cited requirements, the design sections they map to, the handbook code-changes rules with their spec exception to the test rule (tests are their own Leaf_Tasks, so a code task is proved by an Ephemeral_Check), the other Leaf_Tasks in flight in the same Wave with the instruction to touch only the files its own task needs, and the instruction to stop and report rather than work around a design that cannot be followed or add a dependency.
5. WHEN a Sub_Agent implements a Leaf_Task, THE Sub_Agent SHALL gather context first (the cited requirements and design, the surrounding code, the project's tests and configuration), then implement only what the task describes, as the smallest change that does the job in the project's style, then prove it (the test it wrote if its Leaf_Task is a test task, otherwise an Ephemeral_Check plus the existing tests for the code it touched), then return a summary listing files changed, every test and Ephemeral_Check run with its result and the check's code, and anything it is unsure of.
6. THE Sub_Agent SHALL NOT write a test unless its Leaf_Task is a test task, and SHALL NOT produce code for any other Leaf_Task.
7. WHEN a Wave starts, THE Skill SHALL check the code for each unticked Leaf_Task in it and tell the Author which already appear done; for such a task it SHALL skip the Sub_Agent, run the task's tests (an Ephemeral_Check and the existing tests for a code task), tick on a pass, and launch a Sub_Agent after all if they fail.
8. WHILE the Cadence is one Leaf_Task, THE Skill SHALL run one Sub_Agent at a time.
9. WHILE Sub_Agents of a Wave run in parallel, THE Skill SHALL tick none of the tasks that have a Sub_Agent until every Sub_Agent of the Wave has returned, and IF two of them changed the same file, THEN THE Skill SHALL read the combined diff of that file before ticking either task.
10. WHEN a Sub_Agent returns, THE Skill SHALL run the task's tests itself before ticking, and SHALL NOT rely on the Sub_Agent's report alone.
11. WHEN a Leaf_Task's tests pass, THE Skill SHALL tick that task's checkbox in the Task_List. A Leaf_Task's tests are the tests the task itself writes if it is a test task, and otherwise its Ephemeral_Check plus the existing tests for the code it touched.
12. THE Skill SHALL NOT tick a checkbox for a task whose tests it has not run and seen pass in the current session.
13. IF a Leaf_Task has no testable behaviour, THEN THE Skill SHALL state the manual check it performed in the Report and tick the task only after that check.
14. WHEN a Leaf_Task is a property-test task, THE Skill SHALL tag the test with the design property it names.
15. WHEN every sub-task of a top-level task is ticked, THE Skill SHALL tick the top-level task.
16. WHEN the Author chose to skip the Optional_Tests in a Wave, THE Skill SHALL leave them unticked and list them as skipped in the Report.
17. THE Skill SHALL NOT edit `requirements.md`, `design.md`, or any part of `tasks.md` other than checkboxes without the Author's approval.

### Requirement 5: Stop and report

**User Story:** As an Author, I want the Skill to stop where I told it to, with the whole suite run at the end of every Wave and a clear Report, so that I can review before more is built.

#### Acceptance Criteria

1. WHEN the Cadence unit is complete, THE Skill SHALL stop and give the Report.
2. WHEN the last Leaf_Task of a Wave other than a Skipped_Test is ticked, THE Skill SHALL run the Full_Suite and include its result in the Report.
3. IF the Full_Suite fails at the end of a Wave, THEN THE Skill SHALL report the failing output verbatim and ask the Author how to proceed before starting the next Wave.
4. THE Report SHALL list each Leaf_Task completed, each test command run with its result, each file changed, and the next unticked Leaf_Task.
5. THE Skill SHALL NOT commit or push unless the Author asks.
6. WHEN every Leaf_Task other than a Skipped_Test is ticked, THE Skill SHALL give the Report with the final Wave's Full_Suite result, recommend `/ponderly:pr`, and stop.
7. WHEN the Author says to continue after a Report, THE Skill SHALL resume at the next unticked Leaf_Task under the same Cadence and Optional_Test choices.

### Requirement 6: Handle Drift and failure

**User Story:** As an Author, I want the Skill to stop and show me when the spec cannot be followed or a task will not pass, so that the spec stays the source of truth and I decide how it changes.

#### Acceptance Criteria

1. IF a Leaf_Task cannot be implemented as the design describes, THEN THE Skill SHALL stop before further code change, explain what it found with evidence from the code, propose a specific edit to `design.md` or `tasks.md`, and wait for the Author.
2. IF a Leaf_Task's tests still fail after 2 attempts to fix the implementation, THEN THE Skill SHALL stop, report the failing output verbatim, state which causes are confirmed and which are open, and ask the Author.
3. IF the Author asks the Skill to skip a Leaf_Task or work out of Wave order, THEN THE Skill SHALL name the Leaf_Tasks in later Waves that may depend on it according to the Graph and proceed only after the Author confirms.
4. WHEN the Author approves a spec edit, THE Skill SHALL apply it to the named file and then resume where it stopped: at the current Leaf_Task, or at finding the position if the edit was a Graph fix made before any work.
5. IF the Skill finds a problem outside the current Leaf_Task, THEN THE Skill SHALL note it in the Report as a follow-up and SHALL NOT fix it in the current Run.

### Requirement 7: Ship in the handbook

**User Story:** As an engineer, I want the Skill installed with the handbook plugin and reachable from the workflow rule, so that it is used the same way as the other skills.

#### Acceptance Criteria

1. THE Skill SHALL be invokable as `/ponderly:implement-spec [task-name] [cadence]` and SHALL trigger when the Author asks to implement, build, work, continue or resume a spec or its tasks.
2. THE handbook's workflow rule SHALL direct Claude to `/ponderly:implement-spec` when a `tasks.md` exists for the work in hand.
3. THE handbook README SHALL list the Skill in the skills table.
4. THE handbook SHALL include at least one eval case under `evals/skills/implement-spec/` that passes when run twice.
5. THE `start-task` hand-off SHALL point the Author at `/ponderly:implement-spec` for the first Wave.
6. THE plugin version SHALL be bumped for the release that adds the Skill.
7. THE workflow rule and the README SHALL describe stops as the Author's Cadence, after each Leaf_Task or each Wave, and SHALL NOT refer to checkpoints.
