# Requirements Document

## Introduction

This document is a self-describing template: it is a valid requirements document whose
own content teaches you how a requirements document works. The feature it specifies is
deliberately simple — a Link Shortener that turns long URLs into short, shareable links
and counts how often each is visited — so the structure stays visible.

An Introduction answers three questions in a short paragraph: what is this feature, who
uses it, and what value does it deliver. It never describes *how* the feature is built;
technology and implementation belong in the design document. The paragraph above is
written to double as both the real introduction for the example feature and a
demonstration of that rule. Keep this section to a few sentences — its job is framing,
not detail.

The sections that follow are the ones every requirements document should contain: a
Glossary that defines domain terms so each requirement reads unambiguously, and a
Requirements section containing numbered requirements. Each requirement pairs a user
story ("As a ROLE, I want CAPABILITY, so that BENEFIT") with acceptance criteria
written in the EARS format. EARS (Easy Approach to Requirements Syntax) gives each
criterion one of a few predictable shapes so it is unambiguous and testable: ubiquitous
("THE System SHALL ..."), event-driven ("WHEN ..., THE System SHALL ..."), state-driven
("WHILE ..., THE System SHALL ..."), optional-feature ("WHERE ..., THE System SHALL
..."), and unwanted-behavior ("IF ..., THEN THE System SHALL ..."). Good criteria state
one behavior each, quantify what they can (times, sizes, counts), always cover the
unhappy path, and reuse glossary terms verbatim. The example requirements below are
chosen so that, between them, they exercise every one of these EARS patterns.

## Glossary

Define every domain noun your requirements rely on, each with a single unambiguous
sentence. This prevents two readers from interpreting the same word differently, and it
lets acceptance criteria stay short because the meaning is pinned here. Use the exact
term, verbatim, in the criteria.

- **Short_Link**: A system-generated short identifier that redirects to a user-supplied destination URL.
- **Destination_URL**: The original long URL that a Short_Link points to.
- **Visit**: A single resolution of a Short_Link that redirects a visitor to its Destination_URL.
- **Alias**: An optional user-supplied identifier used in place of a system-generated one for a Short_Link.
- **System**: The complete Link Shortener solution described by this document.

## Requirements

Each requirement below is a real, well-formed requirement for the example feature, and
its selection also illustrates a teaching point noted in the final sentence of its user
story. In a production document you would omit those teaching notes; here they show why
each requirement is shaped the way it is.

### Requirement 1: Create a Short Link

**User Story:** As a marketer, I want to turn a long URL into a Short_Link, so that I can share a tidy link. This requirement shows the event-driven, optional-feature, and unwanted-behavior EARS patterns side by side.

#### Acceptance Criteria

1. WHEN a user submits a valid Destination_URL, THE System SHALL create a Short_Link and return it within 2 seconds.
2. WHERE a user supplies an Alias, THE System SHALL use that Alias as the Short_Link identifier when the Alias is not already in use.
3. IF a user submits a Destination_URL that is empty or not a well-formed URL, THEN THE System SHALL reject the request and return a validation error identifying the problem.
4. IF a user requests an Alias that is already in use, THEN THE System SHALL reject the request and return an error indicating that the Alias is taken.

### Requirement 2: Resolve a Short Link

**User Story:** As a visitor, I want a Short_Link to send me to the original page, so that the link simply works. This requirement shows how a quantified count ("one Visit") removes ambiguity a test would otherwise trip over.

#### Acceptance Criteria

1. WHEN a visitor requests an existing Short_Link, THE System SHALL redirect the visitor to the matching Destination_URL.
2. WHEN a Short_Link is resolved, THE System SHALL record exactly one Visit for that Short_Link.
3. IF a visitor requests a Short_Link that does not exist, THEN THE System SHALL return a not-found response.

### Requirement 3: Report Visit Counts

**User Story:** As a marketer, I want to see how many times my Short_Link was visited, so that I can measure reach. This requirement shows the state-driven pattern defending an empty base case.

#### Acceptance Criteria

1. WHEN a marketer requests the metrics for a Short_Link, THE System SHALL return the total number of Visits recorded for that Short_Link.
2. WHILE a Short_Link has zero recorded Visits, THE System SHALL report a count of 0 rather than an error.
