# Links Platform 2027

## Introduction and horizon

This document is a self-describing template: it is a valid tech strategy whose own
content teaches how a strategy works. The strategy it sets out is the year ahead for a
deliberately simple product, the Link Shortener that turns long URLs into short,
shareable links and counts how often each is visited, so the structure stays visible.
The high level design and low level design templates continue the same example one and
two levels down.

A strategy is the highest level view of about a year of work, spanning one or more
projects. It says where the work is going and why, and breaks it into streams that each
get a high level design of their own; it never says how a stream is built. A strategy
has no parent, so its head is the title and then this section. The introduction answers
three questions in a short paragraph: what the work is, who it serves, and the horizon,
the dates the strategy covers and when it will be looked at again.

The links platform takes the Link Shortener from an internal pilot to a product
customers rely on. It serves the marketing teams who share links today and the partners
who want to create links from their own systems. The horizon is January to December
2027, with a review at the end of each quarter.

## Goals

List the outcomes the year must deliver, each with what it is worth, so that when two
goals compete for the same people the reader can see which matters more. A goal is an
outcome someone outside the team can observe, not an activity; give each a measure the
team can check at the review. Three to five goals is usual; more than that is a sign
the strategy covers more than a year.

1. **The shortener in general availability.** Every customer can create and resolve
   Short_Links with redirects under 100 ms at the 99th percentile. Worth: the pilot's
   marketing teams move off the third-party shortener, saving its licence by Q3.
2. **Click analytics.** Customers see visits per Short_Link by day, country and
   referrer within five minutes of the visit. Worth: the reason most pilot users gave
   for wanting the product, and the feature sales asks for first.
3. **A self-serve API.** Partners create and manage Short_Links through a documented API
   with their own keys, without a ticket to the team. Worth: opens the partner channel
   the business plan counts on for the second half of the year.

## Current state

Describe where things stand today, plainly and with numbers where they exist, so the
reader can see the gap each goal closes. Name what works and is kept as well as what
falls short; a strategy that reads as a list of complaints hides what must not break.

The pilot runs as one service with one database, serving about 40 internal users and
200,000 redirects a day. Visits are counted inline on each redirect, which holds at
today's load but adds a write to every request. There are no analytics beyond a total
per link, no public API and no per-customer keys; links are created through an internal
form. The service has no on-call rota and no stated availability target.

## Principles and constraints

State the rules every design under this strategy must respect: the principles the team
chooses and the constraints it is given. Each is a sentence a high level design can be
checked against, with its reason when the reason is not obvious. Leave out what is true
of every project in the organisation; keep what this work must hold to.

- The redirect path stays fast and simple: nothing slower than one key lookup sits
  between a visitor and the destination, because a slow link reflects on the customer.
- Visit data is collected without cookies or personal data beyond country and referrer,
  to stay within the privacy policy without a consent banner.
- Everything runs on the company's existing cloud account and its managed services; no
  new vendor this year.
- The team is four engineers; any stream needing more than two at once has to be split.

## Streams of work

Break the year into streams, each a body of work one high level design can cover and a
small team can own. For each, say what it delivers, which goals it serves and roughly
when. Streams should cover every goal between them and overlap as little as possible;
where one depends on another, say so here, since that order sets the year's plan.

1. **Shortener service.** Takes the pilot to general availability: redirect latency,
   availability, per-customer links, and moving visit counting off the redirect path.
   Serves goal 1. Q1 to Q2; the other two streams build on it.
2. **Click analytics.** Collects visits as events, aggregates them by day, country and
   referrer, and shows them to customers. Serves goal 2. Q2 to Q3, starting once the
   shortener emits visit events.
3. **Self-serve API.** A public API, per-partner keys, rate limits and documentation
   over the shortener's create and manage operations. Serves goal 3. Q3 to Q4.

## Risks

Name what could stop the strategy delivering, each with how likely and how bad it is
and what the team will do about it. A risk is specific enough that someone could notice
it happening; "things take longer than planned" is not one, "the analytics store cannot
keep up with peak traffic" is.

- **Analytics volume outgrows the store.** Visits could reach tens of millions a day if
  a large partner joins. Likely in Q4, costly if it happens. The analytics design sizes
  for ten times the pilot's load and names the next store before it is needed.
- **The API stream starts late.** It depends on the shortener stream finishing on time.
  Moderate likelihood. The API design is written in Q2 so its build can start the day
  the shortener ships.
- **Abuse through public links.** Open link creation invites phishing. Likely once the
  API opens. Destination checks against a block list are part of the API stream.

## Out of scope

Say what the year will not do, especially what a reader might expect it to, so nobody
plans on it. Each entry is a sentence with the reason or the place it belongs.

- Custom domains for Short_Links: asked for by two customers, deferred to 2028.
- QR codes: a front-end feature for the marketing site, not this platform.
- Moving off the current cloud account: ruled out by the constraints above.

## High level designs

Close with the high level designs this strategy expects, one Candidate per stream of
work, none written yet. Each is a kebab-case name, which becomes the design's folder
under `.ponderly/designs/links-platform-2027/`, and a line on what it covers. The
`hld` skill takes one of these names and this document's path to write the design.

- `shortener-service`: the Short_Link service to general availability, from the
  redirect path and its latency to asynchronous visit counting and per-customer links.
- `click-analytics`: visit events, their aggregation by day, country and referrer, and
  the customer-facing reports.
- `self-serve-api`: the public API, partner keys, rate limits, abuse checks and the
  documentation partners work from.
