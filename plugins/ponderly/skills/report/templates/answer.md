# Answer report

1. **What it is.** The thing asked about as the leading role meets it, in plain words, named by what it is and quoted when it is text. No name coined during the work.
2. **Why or how.** Why it happened or how it works, only when the author asked. No history the answer does not need.
3. **What to do.** What the author can do about it, last and only if useful. No offer and no restatement.

Answer only what was asked; leave out status of other work.

## Before

After the Message below, the author asked: "use more words and explain the 2.1 issue as if I'm an exec and you need me to make a decision".

```text
Tasks 1.2 and 2.1 are back; the hook script, task 1.1, is still running. One thing from 2.1's report to settle at verification: it read Requirement 2.4 through the design's flowchart, so a standalone change is proved by the test it wrote plus existing tests, with the ephemeral check reserved for spec-mode code tasks. That is the design's reading too, so I'll accept it unless you say otherwise. Waiting on 1.1.
```

## After

```text
Whoever runs the executor on a standalone change, that is, a change made outside a spec, gets a real test added to the project's suite, with no scratch check run on top of it; the literal reading would give them both. That is how task 2.1 read its instructions.

The instruction behind it is Requirement 2.4: a change is proved by its tests and an ephemeral check, a scratch script that exercises the new code and is deleted afterwards. It does not say whether a standalone change needs both. The executor followed the design's flowchart, which keeps the ephemeral check for code tasks from a spec, because those tasks write no test of their own; their tests are separate tasks.

The design reads Requirement 2.4 the same way, so I will go with that reading unless you say otherwise. If you want an ephemeral check on standalone changes too, say so: Requirement 2.4 and the executor's text then change to require it, and every standalone change carries a scratch check as well as its test.
```
