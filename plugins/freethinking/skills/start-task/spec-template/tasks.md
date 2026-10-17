# Implementation Plan

## Overview

This document is a self-describing template: it is a valid implementation plan whose own
content teaches how a task list works, while actually planning the example Link
Shortener feature from the requirements and design documents.

A task list turns the design into an ordered sequence of small, verifiable coding steps
— the hand-off from "we have a plan" to "we are building." A good task is actionable
(concrete work, not a vague goal), scoped (finishable and verifiable in one sitting),
traceable (it cites the requirements and/or design properties it implements),
test-driven (implementation and its verifying tests are planned together), and
incremental (it builds on earlier tasks, with no big-bang integration at the end). Tasks
are numbered as they are thought of; the waves at the end of the plan decide the order,
putting data models and shared utilities first, then the logic that uses them, then the
wiring, then integration.

This plan builds the Link Shortener service in that order. Tests use a property-based
testing library (minimum 100 iterations per property) with the Link Store mocked so
unit tests need no live infrastructure. Each leaf task cites the requirements it
implements; property-test tasks also name the design property they verify.

## Tasks

Tasks use checkboxes. Top-level tasks group related work; sub-tasks are the concrete
steps. By convention, optional test sub-tasks are marked with `*` so an MVP run can skip
them, while core implementation sub-tasks are never optional. Each example task below is
a real step for the example feature; the pattern it demonstrates is noted in prose where
helpful (you would omit such notes in a production plan).

- [ ] 1. Scaffold the project
  - Create the service project layout, pin dependencies at exact versions, and confirm an empty build and test run passes before any logic exists
  - _Requirements: foundational; supports all_

- [ ] 2. Implement the Link data model and store interface
  - [ ] 2.1 Define the Link record and an injectable store interface
    - Implement the typed Link record (shortLink, destinationUrl, visitCount, createdAt) and a store interface with create, get, and increment operations, kept injectable so tests can supply a fake
    - _Requirements: 1.1, 3.2_
  - [ ]* 2.2 Write unit tests for the store interface against an in-memory fake
    - _Requirements: 1.1, 3.2_

- [ ] 3. Implement create and resolve
  - [ ] 3.1 Implement create with validation and Alias handling
    - Validate the Destination_URL, accept or generate the identifier, and reject empty/malformed URLs and already-used Aliases
    - _Requirements: 1.1, 1.2, 1.3, 1.4_
  - [ ] 3.2 Implement resolve with not-found handling and Visit enqueue
    - Redirect to the Destination_URL, return not-found for unknown links, and enqueue exactly one Visit per resolution
    - _Requirements: 2.1, 2.2, 2.3_
  - [ ]* 3.3 Write the property test for round-trip resolution
    - **Property 1: Round-trip resolution**
    - **Validates: Requirements 1.1, 2.1**

- [ ] 4. Implement Visit counting and metrics
  - [ ] 4.1 Implement the Visit Counter Worker that drains the queue and increments counts
    - _Requirements: 2.2, 3.1_
  - [ ] 4.2 Implement metrics returning the total, reporting 0 when there are no Visits
    - _Requirements: 3.1, 3.2_
  - [ ]* 4.3 Write the property test for a non-decreasing, accurate Visit count
    - **Property 2: Visit count is non-decreasing and accurate**
    - **Validates: Requirements 2.2, 3.1**

## Notes

These conventions are worth copying into a real plan:

- Sub-tasks marked `*` are optional tests; core implementation sub-tasks are never optional.
- Each property test maps to exactly one design property and is tagged in code so it is traceable back to the design.
- Every leaf task cites the requirements it implements, so any line of code can be traced back to a stakeholder-approved need.

## Task Dependency Graph

The dependency graph expresses ordering as data: "waves" of tasks that can run in
parallel, where each wave depends only on tasks in earlier waves. It lets a human or an
agent parallelize safely without building on something that does not yet exist. Every
leaf task appears exactly once. A leaf task is a checkbox task with no sub-tasks: a
top-level task with no sub-tasks is a leaf, and a parent with sub-tasks never appears
in the graph. Optional test tasks are leaves too and are included, so they are never
lost; the executor decides at run time whether to skip them. Task numbers only identify
tasks; the waves decide the order of execution. In this example, wave 0 is the scaffold
everything needs; the data model (2.1) precedes the logic that uses it; and tests that
read finished code fall into later waves than the code they verify.

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2", "3.1", "3.2"] },
    { "id": 3, "tasks": ["3.3", "4.1", "4.2"] },
    { "id": 4, "tasks": ["4.3"] }
  ]
}
```
