# Status report

Each section is a `## <Name>` heading, in this order.

1. **Problems.** Only when there is at least one Problem: a failed or stalled run, a check not run, a finding not fixed, a task that stopped, an assumption made for the author. One bullet each: what it is, why it matters, the options.
2. **Running.** Each thing still running, and what it is doing now. Never what the session will do after it ends.
3. **Finished.** Each thing that finished since the last Message, with its result. No result that was not seen.

When nothing is running, the first line after any Problems is "Nothing is running." and Finished follows. Say what a number means before the number.

## Before

```text
Two `--case` flags ran only the last one, so that rerun covered `stops-at-starting-checks` alone, and it hit a second timeout: one run stopped after 300 seconds at a cost of one cent, which means the sandbox hung before the model did anything, not that the skill misbehaved. The other two runs passed at 1.00. `opens-pr-with-ticket` is now running on its own; the draft follows with all tables when it finishes.
```

## After

```text
## Problems
- In the rerun of `stops-at-starting-checks`, the API stalled before the model did anything: one run hit the 300-second limit having spent one cent. It says nothing about the skill. Options: rerun that case alone, or accept the two runs that finished.
- The rerun covered only `stops-at-starting-checks`, so the other case named has no rerun result. Two cases were named with `--case`, and when `--case` is given twice only the last one runs. Options: rerun the other case on its own, or leave it at its first result.

## Running
- The eval case `opens-pr-with-ticket`, on its own under `make eval-pr`. It is running the pr skill against a sample ticket and grading the result.

## Finished
- The rerun of `stops-at-starting-checks`, three runs: one stalled, see Problems; every grader passed on the other two runs, a score of 1.00, the top score.
```
