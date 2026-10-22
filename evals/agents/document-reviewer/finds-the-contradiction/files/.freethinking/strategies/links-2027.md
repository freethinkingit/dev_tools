# Links 2027

## Introduction and horizon

The links platform takes the Link Shortener from an internal pilot to a product
customers rely on. It serves the marketing teams who share links today. The horizon is
January to December 2027, with a review at the end of each quarter.

## Goals

1. **The shortener in general availability.** Every customer can create and resolve
   Short_Links with redirects under 100 ms at the 99th percentile. Worth: the marketing
   teams move off the third-party shortener, saving its licence by Q3.
2. **Visit counts owners can trust.** Each owner sees the total visits of every
   Short_Link, at most five minutes behind. Worth: the figure the pilot's users check
   first.

## Current state

The pilot runs as one service with one database, serving about 40 internal users and
200,000 redirects a day. Visits are counted inline on each redirect, which holds at
today's load but adds a write to every request.

## Principles and constraints

- The redirect path stays fast: nothing slower than one key lookup sits between a
  visitor and the destination.
- Everything runs on the company's existing cloud account and its managed services; no
  new vendor this year.

## Streams of work

1. **Shortener service.** Takes the pilot to general availability, moving visit counting
   off the redirect path. Serves goals 1 and 2. Q1 to Q2.

## Risks

- **Traffic spikes delay counts.** Likely at launch. The shortener design sizes for ten
  times the pilot's load and reports how far counts lag.

## Out of scope

- Custom domains for Short_Links: deferred to 2028.

## High level designs

- `shortener-service`: the Short_Link service to general availability, from the redirect
  path to asynchronous visit counting.
