#!/usr/bin/env bash
# Fixture for the invalid-graph-stops case: a link-shortener spec whose
# Task Dependency Graph omits leaf task 4.2. Runs in the empty eval workspace.
set -euo pipefail

mkdir -p .ponderly/specs/link-shortener

cat > .ponderly/specs/link-shortener/requirements.md <<'MD'
# Requirements Document

## Introduction

A link shortener: users submit a long URL and get a short code; visiting the code redirects and counts the click.

## Requirements

### Requirement 1: Create a short link

1. WHEN a user submits a valid URL, THE Service SHALL return a short code.
2. IF the URL is empty or malformed, THEN THE Service SHALL reject it.

### Requirement 2: Resolve a short link

1. WHEN a short code is visited, THE Service SHALL redirect to its URL.
2. WHEN a short code is visited, THE Service SHALL record exactly one visit.
3. IF the short code is unknown, THEN THE Service SHALL return not found.

### Requirement 3: Report visits

1. THE Service SHALL report the total visits for a short code.
2. WHEN a short code has no visits, THE Service SHALL report 0.
MD

cat > .ponderly/specs/link-shortener/design.md <<'MD'
# Design Document

## Overview

A small HTTP service with an injectable link store, a resolve handler that enqueues visits, and a worker that drains the queue into visit counts.

## Components and Interfaces

| Component | Responsibility | Requirements |
|-----------|----------------|--------------|
| Link store | Create, get and increment link records | 1.1, 3.2 |
| Create handler | Validate the URL and issue a short code | 1.1, 1.2 |
| Resolve handler | Redirect, not-found, enqueue one visit | 2.1, 2.2, 2.3 |
| Visit counter worker | Drain the queue and increment counts | 2.2, 3.1 |
| Metrics | Return the total, 0 when none | 3.1, 3.2 |

## Correctness Properties

### Property 1: Round-trip resolution

Any created short code resolves to the URL it was created with.

### Property 2: Visit count is non-decreasing and accurate

The count never decreases and equals the number of visits recorded.

## Testing Strategy

Unit tests with the link store mocked; property tests with at least 100 iterations per property.
MD

cat > .ponderly/specs/link-shortener/tasks.md <<'MD'
# Implementation Plan

## Overview

Build the link shortener in the design's order: scaffold, data model, create and resolve, then visit counting and metrics.

## Tasks

- [ ] 1. Scaffold the project
  - Create the service project layout, pin dependencies, and confirm an empty build and test run passes
  - _Requirements: foundational; supports all_

- [ ] 2. Implement the Link data model and store interface
  - [ ] 2.1 Define the Link record and an injectable store interface
    - _Requirements: 1.1, 3.2_
  - [ ]* 2.2 Write unit tests for the store interface against an in-memory fake
    - _Requirements: 1.1, 3.2_

- [ ] 3. Implement create and resolve
  - [ ] 3.1 Implement create with validation
    - _Requirements: 1.1, 1.2_
  - [ ] 3.2 Implement resolve with not-found handling and visit enqueue
    - _Requirements: 2.1, 2.2, 2.3_
  - [ ]* 3.3 Write the property test for round-trip resolution
    - **Property 1: Round-trip resolution**
    - **Validates: Requirements 1.1, 2.1**

- [ ] 4. Implement visit counting and metrics
  - [ ] 4.1 Implement the visit counter worker that drains the queue and increments counts
    - _Requirements: 2.2, 3.1_
  - [ ] 4.2 Implement metrics returning the total, reporting 0 when there are no visits
    - _Requirements: 3.1, 3.2_
  - [ ]* 4.3 Write the property test for a non-decreasing, accurate visit count
    - **Property 2: Visit count is non-decreasing and accurate**
    - **Validates: Requirements 2.2, 3.1**

## Notes

- Sub-tasks marked `*` are optional tests; implementation sub-tasks are never optional.
- Task numbers identify tasks; the graph below decides the order.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2", "3.1", "3.2"] },
    { "id": 3, "tasks": ["3.3", "4.1"] },
    { "id": 4, "tasks": ["4.3"] }
  ]
}
```
MD
