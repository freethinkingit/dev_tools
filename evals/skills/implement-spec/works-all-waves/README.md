# works-all-waves

Tests the implement-spec work loop at spec cadence: work every wave without
waiting, each with its executor, its own test run, its wave review and its
full suite, write a short report after each wave, have the reviewer agent read
the whole run once more in a final review, and hand back once at the end. Each
wave report and the final report are written by the `report` skill in its
handback shape: Problems first, or `No problems.`, then Done; the final report
also carries the `Final review of the run:` line.

## What the scaffold builds

The same workspace as works-one-wave: a small Python package on branch
`calc-subtract` with a committed spec under `.freethinking/specs/calc-subtract/`,
two tasks in two waves (add `subtract`, then test it). The package is
`evals/fixtures/calc/`, built by `evals/fixtures/setup.sh`; the spec is this
case's `files/` folder, a copy of works-one-wave's, copied in before that
script's one commit. Tests run with `python3 -m unittest`. `bin/` holds
wrappers for `git` and `python3`, because the `/usr/bin` shims on macOS need an
xcrun cache the sandbox forbids; the Makefile's implement-spec target puts
`bin` on the PATH and grants Bash, Write and Edit.

The prompt gives the start answers up front (spec cadence, no optional tests,
already on a branch), since nothing can answer mid-run. implement-spec writes
each wave report and the final report by invoking the Skill tool with
`freethinking:report` and `handback` in the session itself, which is what the
`invokes-report` and `problems-first` graders read.

## Graders

- `launches-sub-agents`: the Agent tool was called at least three times. A
  full run makes five calls (two executors, two wave reviewers, one final
  reviewer); three proves the loop went past the first wave.
- `runs-tests-itself`: the orchestrator ran `unittest` through Bash, not just
  the sub-agents.
- `adds-subtract`: `calc/ops.py` contains the function task 1 describes.
- `works-wave-1`: `tests/test_ops.py` gained `test_subtract`, so wave 1 ran
  without a hand-back after wave 0. works-one-wave grades the opposite.
- `ticks-both-tasks`: `.freethinking/specs/calc-subtract/tasks.md` has
  `- [x] 1.` and then `- [x] 2.`, so both waves were ticked.
- `reports-every-wave`: the final report carries the wave review line of
  wave 1, so the report covers each wave and not only the first.
- `reviews-the-run`: the final report carries the final review's verdict, so
  the reviewer was launched once more over the whole run.
- `invokes-report`: the Skill tool was called with the `report` skill, so the
  reports came from it.
- `problems-first`: the output has `## Problems` or `No problems.` before
  `## Done`, the handback shape's opening.
- `reports-wave-0-inline`: reads the whole trace in order and needs the wave 0
  review line to be followed, later in the session, by an executor launch.
  That only happens when the wave 0 report was written before wave 1 began,
  so it grades the inline report; a run that writes the review lines only in
  the final report has no launch after them and fails. One run on 2026-10-14
  did exactly that, with four short progress lines and then the final report.

## What it cannot check

Whether each tick came after its wave review: the graders read the file at
the end of the run, not when it changed. At spec cadence a tick must not end
the run early; if it does, `works-wave-1` and `reviews-the-run` fail, and the
transcript shows the hand-back after wave 0.

## Running it

```bash
make eval-skill-implement-spec EVAL_ARGS="--case works-all-waves"
```

About $0.90 a run at list price, roughly double works-one-wave; it spawns five
sub-agents, two executors and three reviewers, all on Opus. With this case the
`make eval-skill-implement-spec` target runs past the default $2
`EVAL_MAX_COST_USD` ceiling at three runs a case, so raise it, for example
`EVAL_MAX_COST_USD=6`, or run one case at a time with `--case`.
