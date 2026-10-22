# Links 2027

## Introduction and horizon

Links 2027 turns the internal link shortener into a product the company's customers use
to share links and see who visits them. It serves the marketing teams who share links
today and the partners who want to create links from their own tools. The horizon is
January to December 2027, reviewed at the end of each half.

## Goals

1. **Redirects customers can rely on.** Every customer creates short links and every
   redirect answers in under 50 ms at the 99th percentile. Worth: lets marketing drop
   the paid shortener it uses for campaigns.
2. **Visit reports.** Customers see visits per link by day and country within an hour.
   Worth: the feature customers ask for most.
3. **Partner access.** Partners create links through an API with their own keys. Worth:
   the partner deals planned for the second half.

## Current state

One service and one relational database serve about 30 internal users and 150,000
redirects a day. Each redirect also writes a visit count, which holds at today's load.
There are no reports, no API and no availability target.

## Principles and constraints

- A redirect does one lookup and nothing else on its path, because a slow link reflects
  on the customer.
- Visit data holds country and referrer only, so no consent banner is needed.
- Everything runs on the existing cloud account and its managed services.
- The team is three engineers.

## Streams of work

1. **Shortener service.** Redirect latency, per-customer links, and visit counting
   moved off the redirect path. Serves goal 1. First half; the others build on it.
2. **Visit analytics.** Visit events aggregated by day and country, and the customer
   report. Serves goal 2. Second half, once the shortener emits visit events.
3. **Partner API.** Keys, rate limits and documentation over link creation. Serves
   goal 3. Second half.

## Risks

- **A popular link overloads the store.** Likely once a large customer joins; the
  shortener design caches the hottest links.
- **The partner API starts late.** It waits on the shortener; its design is written in
  the first half so its build can start on time.

## Out of scope

- Custom domains: two customers asked; deferred to 2028.
- QR codes: a marketing site feature, not this platform.

## High level designs

- `shortener-service`: link creation and the redirect path to general availability,
  with visits handed off as events.
- `visit-analytics`: visit events, their aggregation by day and country, and the
  customer report.
- `partner-api`: partner keys, rate limits and the documentation partners work from.
