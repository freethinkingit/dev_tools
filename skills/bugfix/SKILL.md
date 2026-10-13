---
name: bugfix
description: Fix a bug the disciplined way, starting from a ticket. Use when asked to fix, debug, investigate, or resolve a bug, issue, or defect. Reads the ticket, reproduces the bug before touching code (by a test or script when possible, by guiding the author through manual steps when the bug involves a UI flow, an external service or generated output), keeps the steps, observations, evidence and hypotheses in the conversation so the fix is informed by what was seen, drives to the real root cause, fixes the cause and adds a regression test, verifies the repro no longer triggers and nothing else broke, then hands off to the pr skill, which walks the changes with the author before anything is opened. Confirms the diagnosis with the author before changing any code.
argument-hint: "[ticket-key-url-or-description]"
allowed-tools: Bash(git status *) Bash(git branch *) Bash(git remote *) Bash(git rev-parse *) Bash(git log *) Bash(git diff *) Bash(gh issue view *) Bash(gh auth status *)
---

# Fix a bug

Fix a bug by driving from the ticket to a reproduction, then to the root cause, then to a fix that is guarded by a regression test. Confirm the diagnosis with the author before changing any code, and once the fix is verified hand off to the pr skill so the author walks the changes before the PR is opened.

The author is accountable for the fix. The root cause and the fix must be understood, not guessed. A bug that merely stopped reproducing is not the same as a bug whose cause is known and prevented; do not treat "it works now" as a fix. Help the author understand the cause; do not assert one you cannot support from evidence.

Ticket, if the author gave one: $ARGUMENTS

## 1. Read the ticket

Get the ticket in front of you before anything else.

- If the argument is a GitHub issue URL or number and `gh` is signed in, read it with `gh issue view <ref>`.
- If the argument is a key for another tracker (for example `ENG-1234`) or a short description, ask the author to paste the ticket text if it is not already in the session.
- If there is no ticket at all, ask the author for the symptom and the expected behaviour, and record that there is no ticket.

From the ticket, pull out and state back to the author:

- **Symptom**: what actually happens, with the exact error, wrong output, or failure if given.
- **Expected**: what should happen instead.
- **Context**: environment, version, affected area, and any steps to reproduce the ticket already provides.

Ask only what the ticket cannot answer, and only what you need to reproduce the bug. Do not start searching the code yet.

### Keep the record in the conversation

The conversation is the investigation's record; there is no separate notes file. What matters is that the context is there when it is needed: the root cause is argued from the evidence gathered, the regression test is shaped by the reproduction, and the PR's Testing section is written from what was run. So, as you go:

- State observations back in the author's words and keep exact error text, log lines, request ids and values verbatim rather than paraphrased.
- After each reproduction attempt and each hypothesis, give a short running summary: what has been tried, what was observed, which causes are open, confirmed or ruled out.
- Ask the author to paste or attach evidence into the conversation (screenshots, recordings, log excerpts, the generated output) rather than describing it from memory.

## 2. Reproduce the bug

Establish a reliable, repeatable way to trigger the bug before changing any code. **This is a hard gate: do not move to a fix until the bug is reproduced, or until the author explicitly waives reproduction.**

Choose the mode by what the bug involves:

- **Automated**: the failing path is code you can drive from here. Prefer a reproduction that runs on demand: a failing test, a script, or a command. Use the ticket's steps first, and work with the author to fill gaps.
- **Manual**: the bug lives in something you cannot drive yourself, such as a UI flow, an external service integration, a generated image or file, a specific device or environment, or timing. The author performs the steps; you run the process and keep the record.

In both modes, capture the exact observed failure (error text, stack trace, wrong output, the artifact itself) so you can tell later whether the fix actually changed it, and account for every attempt in the running summary.

### Manual reproduction

- Write the procedure as numbered steps, each with the expected result and a place for the observed result. Start from the ticket's steps and the code path you expect them to exercise.
- Tell the author what evidence to collect while they run it: console or server log lines, network requests and responses, request ids, timestamps, screenshots or a recording, the generated output. Say where each piece can be found when you know.
- Ask the author to run the steps and report back. Restate the observed result of every step, with the evidence they provided, verbatim.
- When a run does not trigger the bug, keep that result too, ask what differed from the ticket (account, data, environment, timing, order), adjust the steps, and try again.
- When the code offers a way to shrink the manual loop, use it: a feature flag, a stubbed service response, a fixture that reproduces the input, a log line added for the investigation. Note anything you add so it is removed in step 5.

The bug counts as reproduced when the steps trigger it reliably, or when the conditions that trigger it are understood well enough to name them. State those conditions explicitly.

If the bug cannot be reproduced in either mode:

- Say what was tried and what happened instead.
- Ask the author for the missing conditions: version, data, configuration, timing, environment.
- Do not proceed to a speculative fix. If the author chooses to waive reproduction, say plainly that the fix cannot be verified against a repro, note the waiver in the running summary, and treat every later claim of "fixed" as unverified.

## 3. Drive to the root cause

Find the cause, not the symptom. The symptom is where the bug shows; the root cause is the change or logic that makes it wrong.

- Start from the reproduction and follow the failure back to its origin: read the code on the failing path, inspect the values that are wrong, and narrow down where correct input becomes incorrect output.
- For a manually reproduced bug, the evidence the author gathered is your instrumentation: match log lines, request ids and timestamps to the code path the steps exercise. When that is not enough, add a log line or capture at the point in question and ask the author to run the steps again.
- Name each candidate cause as you form it, and mark it ruled out or confirmed with the evidence that decided it in the running summary. A ruled-out hypothesis is worth keeping visible: it stops the same idea being retried.
- Use `git log` and `git diff` to see whether a recent change introduced the behaviour, when that helps locate the cause.
- Distinguish the root cause from its symptoms and from any contributing factors. A null check that hides a crash is a symptom patch; the reason the value was null is the cause.
- Keep narrowing until you can name the specific code, data, or logic responsible and explain how it produces the observed symptom.

State the root cause to the author in plain terms: what is wrong, where, and why it produces the symptom. Say what the evidence is (the failing path, the values, the introducing commit) and call out anything you are inferring rather than observing.

**Get the author's confirmation of the root cause before changing any code.** If the author corrects the diagnosis, use their account. If the cause cannot be pinned down, say so and do not fix blind; a fix without a known cause is a guess.

## 4. Fix the cause and guard it with a test

Fix the root cause confirmed in step 3, not the symptom.

- Make the smallest change that corrects the cause. Do not refactor unrelated code, add unrequested features, or clean up surrounding code while you are here; note anything worth a follow-up instead.
- Match the project's existing style, patterns, and libraries. Read the surrounding code before writing.

Add a regression test that fails before the fix and passes after, so the bug cannot return unnoticed:

- Find the project's test framework from its config and existing tests. Write the test the way the project writes tests.
- Write the test so it captures the bug: confirm it fails against the unfixed code (or that it would have), then passes with the fix in place. A test that passes without the fix does not guard anything.
- If the project has no test framework, say so, and record a precise manual reproduction-and-check in the ticket or PR instead. Do not add a test framework unless the author asks.

## 5. Verify the fix

Confirm the fix actually resolves the bug and breaks nothing else. A command exiting without error is not enough on its own; check the behaviour.

- Run the reproduction from step 2 and confirm the original symptom is gone and the expected behaviour now holds. For a manual reproduction, ask the author to run the same steps again and report each step's result, and compare them with the failing runs.
- Run the new regression test and confirm it passes. Confirm it fails without the fix if you have not already.
- Run the surrounding test suite, build, or linter the project provides, and confirm the change did not break anything nearby.
- If anything still fails, return to step 3: the root cause may be wrong or incomplete. Do not paper over a remaining failure.

Clean up anything added only for investigation: debug output, temporary scripts, scratch files, and any log lines or stubs added during manual reproduction.

If reproduction was waived in step 2, state clearly which of these checks could not be done and that the fix is unverified against a repro.

## 6. Summarise and hand off to the pr skill

Tell the author, briefly:

- **Root cause**: what was actually wrong, confirmed in step 3.
- **Fix**: what changed and why it corrects the cause, with the files involved.
- **Prevention**: the regression test added, or the recorded manual check if the project has no test framework.
- **Verification**: what was run and the result, including anything that could not be verified.

Then ask the author whether to open the pull request now. On yes, invoke the `pr` skill with the Skill tool (`freethinking:pr`), with the ticket as its argument when there is one: it walks every change with the author, drafts the description to the team standard, and creates the PR only after the author approves the draft. The reproduction and verification runs above are what its Testing section should say. Do not draft or open the PR any other way; a bare `gh pr create` skips the walkthrough.
