---
name: start-task
description: Start a new feature or task by writing its spec before any code. Use when asked to start, plan, spec, scope or design a task, feature or piece of work, or when a request is big enough that coding straight away would be guessing. Produces requirements.md, design.md and tasks.md in .claude/specs/<task-name>/, following the team's spec template, with the author approving each document before the next is written. Does not write code.
argument-hint: "[task name or short description]"
---

# Start a task

Turn a task into an approved spec before anyone writes code: requirements first, then a design that satisfies them, then an ordered task list to build it. The author approves each document before the next one starts, and owns the result.

Task, as the author gave it: $ARGUMENTS

## Ground rules

- **No code.** This skill ends when `tasks.md` is approved. Do not create or edit source files, and do not start on the first task.
- **The template is the standard.** The three files under `${CLAUDE_SKILL_DIR}/spec-template/` are self-describing: each is a valid document whose own prose explains how that kind of document works, using a Link Shortener as the worked example. Read the matching template file before writing each document. Copy its structure and its rules; do not copy its example content or its teaching notes.
- **Ask, don't invent.** When something the spec needs is not in the request or the codebase, ask the author. Keep each round of questions short, and batch them.
- **Approval is explicit.** "Looks good" with a "but" is a change request. Make the change and ask again. Do not move to the next document until the author says the current one is approved.
- **Size to the task.** A small task gets short documents, but each document keeps its sections. For a small task, one diagram in the design is enough; for a large one, use the diagram types the template shows where they add information.

## 1. Name the task and find its spec

Derive a kebab-case task name from the request, for example `link-shortener`, and confirm it with the author along with the first questions below. The spec lives in `.claude/specs/<task-name>/` in the current repository.

If that directory already exists, read what is there and resume at the first document that is missing or that the author says is not approved. Do not overwrite an existing document without asking.

## 2. Understand the task

Before asking anything, look at the codebase for what the request touches: existing modules, patterns, naming, tests and configuration the task will have to fit. Then ask the author only what you still need, in one round:

- What the task must do, for whom, and what value it delivers.
- What is out of scope.
- Constraints: deadlines, compatibility, performance, security, systems it must work with.
- Anything the author already knows they want or do not want in the solution.

## 3. Write the requirements

Read `${CLAUDE_SKILL_DIR}/spec-template/requirements.md`, then write `.claude/specs/<task-name>/requirements.md` with:

- **Introduction**: what the feature is, who uses it, what value it delivers. A short paragraph. No implementation detail.
- **Glossary**: every domain noun the requirements use, each defined in one sentence, in `Term_Name` form. Use the terms verbatim in the criteria.
- **Requirements**: numbered, each with a user story ("As a ROLE, I want CAPABILITY, so that BENEFIT") and acceptance criteria in EARS form: ubiquitous (`THE System SHALL`), event-driven (`WHEN ..., THE System SHALL`), state-driven (`WHILE ..., THE System SHALL`), optional-feature (`WHERE ..., THE System SHALL`) and unwanted-behaviour (`IF ..., THEN THE System SHALL`). One behaviour per criterion. Quantify what can be quantified. Every requirement covers its unhappy path.

Then show the author the document and ask: do these requirements say what you want built, is anything missing, and is anything there that should not be? Iterate until approved.

## 4. Write the design

Read `${CLAUDE_SKILL_DIR}/spec-template/design.md`. Read the parts of the codebase the design will touch, so the design fits what exists rather than inventing a parallel structure. Then write `design.md` with:

- **Overview**: the solution shape in a few sentences.
- **Architecture**: components and request flow, with a Mermaid diagram. Each key decision cites the requirement it serves and names its trade-off, and each rejected alternative says why it lost.
- **Components and Interfaces**: each component's single responsibility and its operations, in a table that maps every operation to the requirements it serves.
- **Data Models**: fields, types, keys and constraints, tied to requirement bounds.
- **Correctness Properties**: statements that must hold across all valid executions, each as `### Property N: Title`, a *For any* sentence, and a `**Validates: Requirements ...**` line.
- **Error Handling**: a table of condition, category, behaviour and requirement.
- **Testing Strategy**: property-based tests for the properties, example and edge-case tests for the error rows, integration tests for the wiring.

Check traceability both ways before showing it: every requirement is satisfied somewhere in the design, and every decision traces to a requirement. Name anything that does not trace. Ask the author to approve; iterate until they do.

## 5. Write the task list

Read `${CLAUDE_SKILL_DIR}/spec-template/tasks.md`, then write `tasks.md` with:

- **Overview**: how the plan is ordered and how it will be tested.
- **Tasks**: checkbox tasks, numbered in whatever order they were thought of; the waves below put data models and shared utilities first, then the logic that uses them, then wiring, then integration. Top-level tasks group related work; sub-tasks are the concrete steps. Each leaf task is finishable in one sitting and cites the requirements it implements. Optional test sub-tasks are marked `*`; implementation sub-tasks are never optional. A property-test task names the design property it verifies.
- **Notes**: conventions the executor should follow.
- **Task Dependency Graph**: the JSON `waves` block, where each wave depends only on earlier waves. Every leaf task appears exactly once, optional test tasks included. Task numbers only identify tasks; the waves decide the order of execution.

Ask the author to approve; iterate until they do.

## 6. Hand off

When `tasks.md` is approved, tell the author where the three files are and how to proceed: run `/handbook:implement-spec <task-name>`, which builds each task in its own sub-agent in wave order, ticks each checkbox when its tests pass, runs the full suite at the end of each wave, and stops for review after each task or each wave, as the author chooses. Point at the first wave. Then stop.
