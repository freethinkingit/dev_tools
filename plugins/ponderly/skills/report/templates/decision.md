# Decision report

1. **What is being decided.** The choice in one or two plain sentences, with what it is about. No history of how it came up.
2. **Options.** One bullet per option: what it is in plain words and what it costs. No option left unnamed, no shorthand.
3. **Recommendation.** The option recommended and the reason. One recommendation, not a ranking.
4. **Question.** The one question the author answers, last; only a one-line notice the skill adds may follow it.

When the answers are a fixed short list, ask the question with the AskUserQuestion tool, offering the options plus free text, as `rules/collaboration.md` says. When the tool is not available, ask in prose: the Options section above already puts the options on separate lines, so do not list them again.

## Before

```text
The only milestone is "Listing on Claude marketplace", and several of these are about how the skills collaborate rather than the listing, so a second milestone may be due.
**#6, Workflow rule: specs as records, in-flight choices, discoveries as issues.** My proposal: milestone, this is spec lifecycle rather than the listing, so I'd open a second milestone, maybe "Skills hand back well", and put #6 there with #11, #12, #16, #17 and #18 as we reach them.
Your call on whether to create that milestone and what to name it.
```

## After

```text
Issue #6 needs a milestone. It asks for three additions to the workflow rule: keep specs as records, record choices made mid-task, and file discoveries as issues. The only milestone today is "Listing on Claude marketplace", and #6 is about how the skills work with you, not about the listing.

- Put #6 under "Listing on Claude marketplace". Costs nothing now; that milestone then mixes listing work with work on how the skills behave, so it no longer tells you how close the listing is.
- Create a second milestone for how the skills work with you, named for its goal, such as "Skills hand back well". Costs one milestone to create and name; #11, #12, #16, #17 and #18 would join it as we reach them.
- Leave #6 without a milestone. Costs nothing now; it then shows up in no plan.

I recommend the second milestone, because six of the eight open issues are about how the skills work with you, and the listing milestone stays a true measure of the listing.
```

The After ends where the AskUserQuestion call begins: header `Milestone`, options the listing milestone, a new milestone named "Skills hand back well", and no milestone; the tool adds free text.
