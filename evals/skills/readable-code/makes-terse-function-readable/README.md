# makes-terse-function-readable

Tests the readable-code pass end to end on one terse function: its one source
file is a group of one, the prompt approves the groups and shared decisions in
advance because the run cannot answer the `Groups` question, the group's
executor makes it read plainly, the behaviour stays the same, and nothing is
committed.

## What the scaffold builds

The `calc` fixture, built by `evals/fixtures/setup.sh` with the `bin`
wrappers, on branch `add-median`, with one commit on the branch that adds this
case's `files/`: `calc/stats.py`, a `median` function with the one-letter
locals `s`, `n` and `m`, a dense one-line ternary and a docstring that walks
through the algorithm in numbered steps, and `tests/test_stats.py`, which
passes. Main holds only the fixture, so the branch's one source file is
`calc/stats.py`. Tests run with `python3 -m unittest`. The Makefile's
readable-code target grants Bash, Write, Edit and Agent and puts `bin` on the
PATH; the case lists Agent and Skill for the executor, reviewer and report
launches.

## Graders

- `names-are-descriptive`: `calc/stats.py` no longer uses `s`, `n` or `m` as a
  name in code.
- `docstring-drops-steps` (llm): the docstring of `median` in `calc/stats.py`
  states only intent, parameters, returns and raises, with no description of
  the algorithm's steps, reworded or not. A regex cannot tell a reworded step
  from a statement of the result, so this one grader is an llm; confirm the
  case at `--runs 3`.
- `tests-still-pass`: the last unittest result in the transcript is `OK`, with
  no `FAILED (` after it.
- `no-test-added`: the Write tool was never called with a `file_path` under
  `tests/`. It sees only the main session's writes: a test file an executor
  sub-agent writes may not appear in the main trace, so it can go unseen.
- `head-unchanged`: `.git/logs/HEAD` holds only the scaffold's three entries,
  so nothing was committed, reset or checked out, by the session or its agents.

## What it cannot check

Whether the new names are good ones; the report shows the file. The
test grader reads the transcript, so a session that never re-runs the suite
after the change passes on the Baseline's run alone.

## Running it

```bash
make eval-skill-readable-code EVAL_ARGS="--runs 1"
```

It spawns two sub-agents, an executor and a reviewer.
