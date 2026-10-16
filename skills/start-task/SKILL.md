---
name: start-task
description: Front door for any request to change code. Reads the code the request touches, then decides whether it goes to the task executor, to the bugfix skill or to a spec, and asks the author when the answer is not a spec. Start a new feature or task by writing its spec before any code. Use for any request to change code that the workflow rule does not route elsewhere (a named bug, an existing spec, a pull request, a typo-sized change), and when asked to start, plan, spec, scope or design a task, feature or piece of work, or when a request is big enough that coding straight away would be guessing. Produces requirements.md, design.md and tasks.md in .claude/specs/<task-name>/, following the team's spec template, with the author approving each document before the next is written. Does not write code.
argument-hint: "[task name or short description]"
---

# Start a task

The front door for a change: read the code the request touches, then route the request to `bugfix`, to the executor, or to a spec. On the spec route, turn the task into an approved spec before anyone writes code: requirements first, then a design that satisfies them, then an ordered task list to build it. The author approves each document before the next one starts, and owns the result.

Task, as the author gave it: $ARGUMENTS

## Ground rules

- **No code of your own.** Do not create or edit source files. On Spec_Route the skill ends when `tasks.md` is approved; on Bug_Route it ends at the hand-off; on Executor_Route the executor writes the code and the skill ends after reporting its Summary.
- **The template is the standard.** The three files under `${CLAUDE_SKILL_DIR}/spec-template/` are self-describing: each is a valid document whose own prose explains how that kind of document works, using a Link Shortener as the worked example. Read the matching template file before writing each document. Copy its structure and its rules; do not copy its example content or its teaching notes.
- **Ask, don't invent.** When something the spec needs is not in the request or the codebase, ask the author. Keep each round of questions short, and batch them.
- **Approval is explicit.** "Looks good" with a "but" is a change request. Make the change and ask again. Do not move to the next document until the author says the current one is approved.
- **Size to the task.** A small task gets short documents, but each document keeps its sections. For a small task, one diagram in the design is enough; for a large one, use the diagram types the template shows where they add information.

## Working with the author

- **Stops.** The route question at triage, when the route is Bug_Route or Executor_Route; the fit question at triage, when the request extends nothing in the codebase; the approval of each of the three documents on Spec_Route; the relaunch question after a `stopped` Summary on Executor_Route.
- **How it asks.** With the AskUserQuestion tool, fixed options plus free text, at every stop. The spec questions at the head of the requirements step are the exception: ask them in prose, because the answers are the author's own words.
- **Hand-backs.** On Executor_Route, the executor's Summary verbatim and the diff, failures first, then the closing Message written with `report`. On Spec_Route, each document in full.
- **Hand-offs.** `bugfix` on Bug_Route; `pr` after a `done` Summary; `implement-spec` after `tasks.md` is approved. The branch name proposed in step 1 is created by the author before the first commit, or by `implement-spec` at its set-up when the author gives it that name, or by `pr` at its branch offer, under the name `pr` proposes from the ticket, which is the same shape when the author passes the ticket to it; never by this skill.

## 1. Name the task and find its spec

Derive a kebab-case task name from the request, for example `link-shortener`. Beside it, propose a branch name: the issue number and the task name, such as `12-link-shortener`, when the request names or links an issue, and the task name alone otherwise. Do not create the branch. Say both in the route statement of step 3, so the author can correct them in the same breath. The spec lives in `.claude/specs/<task-name>/` in the current repository.

If that directory already exists, the request takes Spec_Route without triage, since its size was already decided. Read what is there and resume at the first document that is missing or that the author says is not approved. Do not overwrite an existing document without asking.

## 2. Read the code

Before asking anything, look at the codebase for what the request touches: existing modules, patterns, naming, tests and configuration the task will have to fit.

## 3. Triage

Before asking any spec question or writing any document, decide which route the request takes:

- **Bug_Route** when the request describes a defect: observed behaviour that differs from intended behaviour in code that already exists.
- **Executor_Route** when the request is a contained change: one change, describable in a sentence or two, touching a place in the code you can name after reading it, needing no design decision and no new dependency, framework or tool.
- **Spec_Route** for every other request.

State the route you chose and the reason for it in two or three sentences that name the code you read; on Spec_Route, one sentence that names the route is enough.

If step 2 found nothing the request would extend, no module, pattern or test it builds on, say so in the route statement, then, before any other question, put one question with the AskUserQuestion tool, header `Fit`, with two options in this order: `Spec it here`, to write the spec in this repository anyway, and `Wrong repository`, to stop, each with a one-sentence description. Act only on the author's answer. On `Wrong repository`, say where the work belongs if the request or the code says, then stop and write nothing. On `Spec it here`, go on with the route, asking the route question after this one when the route has one, since there is no point sizing work that does not belong here.

On Bug_Route or Executor_Route, put one question to the author with the AskUserQuestion tool, header `Route`, with two options in this order: the route you chose, marked "(Recommended)", then `Spec_Route`, each with a one-sentence description. The tool adds the free-text answer itself. Act only on the author's answer. If the author picks the other route, take it without arguing for yours. If the free-text answer is neither route, restate the two routes in one sentence and ask once more.

On Spec_Route, go on to step 4 without a question.

On Bug_Route or Executor_Route, once the author has accepted it, the route's own section below takes over.

### Bug_Route

Invoke the Skill tool with `skill: freethinking:bugfix` and `args:` the request, in the author's words. This skill's own steps end at that hand-off, and `bugfix`'s procedure takes over from its first step. Do not reproduce, diagnose or fix the defect under this skill's steps: `bugfix` holds that discipline, and the hand-off keeps it in one place.

If the Skill tool cannot find `freethinking:bugfix`, say that the plugin's `bugfix` skill is missing and stop. Do not do its work in its place.

### Executor_Route

Launch the agent once, with the Agent tool as `subagent_type: freethinking:task-executor` and a prompt that holds, in this order:

- **Request**: the author's words, verbatim, from the task above and their message.
- **Context found**: the files and symbols step 2 read that the change touches, each as `path: what is there`.
- **Author's additions**: the free-text answer to the route question, verbatim, if there was one.
- **Boundaries**: the sentence, verbatim, "Make only this change. Commit nothing. Return the Summary."

Nothing more. Never say, in any words, that the task comes from a spec: that sentence puts the agent in its spec mode, and here it must be in its standalone mode, where the change comes with its test. The agent's own definition carries its procedure, the shape of its Summary and the instruction to stop on drift, so the launch restates none of them.

If the Agent tool cannot find `freethinking:task-executor`, say that the plugin's `task-executor` agent is missing and stop. Do not make the change yourself.

On this route, edit, create or delete no source file yourself, commit nothing, push nothing and create no branch. The executor writes the change; the author commits it.

To show the change, run `git status --short -- <files changed>` with every path the Summary lists under `files changed`, and show the output; then run `git diff HEAD -- <files changed>` for the tracked paths and show it; then, for each path `git status` marks `??`, run `git diff --no-index -- /dev/null <path>` and show it (its exit status 1 is normal). Never run `git add`, not even with `-N`: committing is the author's. If `files changed` is empty, show nothing and say so.

When the Summary comes back, read its `status` first.

- **`done`**: if any check under `checks run` failed, say so plainly before anything else, naming the check and its result. Then show the Summary verbatim and show the change. Then invoke the Skill tool with `skill: freethinking:report` and `args: handback`, nothing more in `args`; the report skill reads what its Next carries from this step's text in the conversation. The Message's Next names the branch the change sits on uncommitted, recommends `/freethinking:pr <ticket>` to open the pull request, with the issue when the request named one, says that on the default branch `pr` offers to create the branch and that it offers to commit, and names any failed check. If the Skill tool cannot find `freethinking:report`, say that the plugin's `report` skill is missing and write that closing message yourself, problems first, then the branch and the recommendation.
- **`stopped`**: show the Summary verbatim, then show the change for anything it lists under `files changed`, and say plainly that those partial edits are in the working tree. Then put one question with the AskUserQuestion tool, header `Relaunch`, with two options in this order: `Answer and relaunch`, to answer the question under `stopped because` and launch the executor again, and `Spec_Route`, to write a spec for the change instead. A free-text answer counts as `Answer and relaunch`, with that text as the answer; if the author picks `Answer and relaunch` with no text, ask for the answer in prose, once, before relaunching. Act only on the author's answer. On `Answer and relaunch`, launch once more with the same prompt, adding under Author's additions the executor's `stopped because` text, quoted, then the author's answer, then the files that already hold partial edits, if any; the launch still never says that the task comes from a spec. Handle that Summary the same way. On `Spec_Route`, say again in one sentence that any partial edits are still in the working tree, then go on to step 4. Never relaunch unprompted.

## 4. Write the requirements

Ask the author only what you still need, in one round, in prose:

- What the task must do, for whom, and what value it delivers.
- What is out of scope.
- Constraints: deadlines, compatibility, performance, security, systems it must work with.
- Anything the author already knows they want or do not want in the solution.

Then read `${CLAUDE_SKILL_DIR}/spec-template/requirements.md` and write `.claude/specs/<task-name>/requirements.md` with:

- **Introduction**: what the feature is, who uses it, what value it delivers. A short paragraph. No implementation detail.
- **Glossary**: every domain noun the requirements use, each defined in one sentence, in `Term_Name` form. Use the terms verbatim in the criteria.
- **Requirements**: numbered, each with a user story ("As a ROLE, I want CAPABILITY, so that BENEFIT") and acceptance criteria in EARS form: ubiquitous (`THE System SHALL`), event-driven (`WHEN ..., THE System SHALL`), state-driven (`WHILE ..., THE System SHALL`), optional-feature (`WHERE ..., THE System SHALL`) and unwanted-behaviour (`IF ..., THEN THE System SHALL`). One behaviour per criterion. Quantify what can be quantified. Every requirement covers its unhappy path.

Then show the author the document and ask with the AskUserQuestion tool, header `Approve`, options `Approved` and `Changes needed`, whether these requirements say what they want built, with anything missing or wrong in the free text. Iterate until approved.

## 5. Write the design

Read `${CLAUDE_SKILL_DIR}/spec-template/design.md`. Read the parts of the codebase the design will touch, so the design fits what exists rather than inventing a parallel structure. Then write `design.md` with:

- **Overview**: the solution shape in a few sentences.
- **Architecture**: components and request flow, with a Mermaid diagram. Each key decision cites the requirement it serves and names its trade-off, and each rejected alternative says why it lost.
- **Components and Interfaces**: each component's single responsibility and its operations, in a table that maps every operation to the requirements it serves.
- **Data Models**: fields, types, keys and constraints, tied to requirement bounds.
- **Correctness Properties**: statements that must hold across all valid executions, each as `### Property N: Title`, a *For any* sentence, and a `**Validates: Requirements ...**` line.
- **Error Handling**: a table of condition, category, behaviour and requirement.
- **Testing Strategy**: property-based tests for the properties, example and edge-case tests for the error rows, integration tests for the wiring.

Check traceability both ways before showing it: every requirement is satisfied somewhere in the design, and every decision traces to a requirement. Name anything that does not trace. Then show the author the document and ask with the AskUserQuestion tool, header `Approve`, options `Approved` and `Changes needed`, whether this design is how they want the requirements met, with anything missing or wrong in the free text. Iterate until approved.

## 6. Write the task list

Read `${CLAUDE_SKILL_DIR}/spec-template/tasks.md`, then write `tasks.md` with:

- **Overview**: how the plan is ordered and how it will be tested.
- **Tasks**: checkbox tasks, numbered in whatever order they were thought of; the waves below put data models and shared utilities first, then the logic that uses them, then wiring, then integration. Top-level tasks group related work; sub-tasks are the concrete steps. Each leaf task is finishable in one sitting and cites the requirements it implements. Optional test sub-tasks are marked `*`; implementation sub-tasks are never optional. A property-test task names the design property it verifies.
- **Notes**: conventions the executor should follow.
- **Task Dependency Graph**: the JSON `waves` block, where each wave depends only on earlier waves. Every leaf task appears exactly once, optional test tasks included. Task numbers only identify tasks; the waves decide the order of execution.

Then show the author the document and ask with the AskUserQuestion tool, header `Approve`, options `Approved` and `Changes needed`, whether these tasks build the design in an order they accept, with anything missing or wrong in the free text. Iterate until approved.

## 7. Hand off

When `tasks.md` is approved, tell the author where the three files are and how to proceed: run `/freethinking:implement-spec <task-name>`. Point at the first wave. Then stop.
