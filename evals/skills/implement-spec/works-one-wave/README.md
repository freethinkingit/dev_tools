# works-one-wave

Tests the implement-spec work loop end to end: validate the graph, launch the
executor agent for the wave's task, verify its work by running the checks
yourself, have the reviewer agent read the wave, run the suite, hand back
without starting the next wave. The hand-back is written by the `report`
skill in its handback shape: Problems first, or `No problems.`, then Done.

## What the scaffold builds

A small Python package on branch `calc-subtract` with a committed spec under
`.freethinking/specs/calc-subtract/`: two tasks in two waves (add `subtract`, then
test it). The package is `evals/fixtures/calc/`, built by
`evals/fixtures/setup.sh`; the spec is this case's `files/` folder, copied in
before that script's one commit. Tests run with `python3 -m unittest`. `bin/`
holds wrappers for `git` and `python3`, because the `/usr/bin` shims on macOS
need an xcrun cache the sandbox forbids; the Makefile's implement-spec target
puts `bin` on the PATH and grants Bash, Write and Edit.

The prompt gives the start answers up front (wave cadence, no optional tests,
already on a branch), since nothing can answer mid-run. implement-spec's step 6
writes the hand-back by invoking the Skill tool with `freethinking:report` and
`handback` in the session itself, which is what the `invokes-report` and
`problems-first` graders read.

## Graders

- `launches-sub-agent`: the Agent tool was called.
- `runs-tests-itself`: the orchestrator ran `unittest` through Bash, not just
  the sub-agent.
- `adds-subtract`: `calc/ops.py` contains the function task 1 describes.
- `leaves-wave-1`: `tests/test_ops.py` gained no `test_subtract`, so wave 1 was
  not started.
- `reviews-the-wave`: the report carries the wave review's verdict, so the
  reviewer agent was launched.
- `invokes-report`: the Skill tool was called with the `report` skill, so the
  hand-back came from it.
- `problems-first`: the output has `## Problems` or `No problems.` before
  `## Done`, the handback shape's opening.

## What it cannot check

The tick. Its tick of task 1 lands in
`.freethinking/specs/calc-subtract/tasks.md`, since the eval sandbox allows
writes under `.freethinking/`: in a run on 2026-10-19 the sandbox's `tasks.md`
was modified with `[x] 1.` and `[ ] 2.`. No grader reads that file yet, so the
tick is seen but not scored. The follow-up is a grader on that file for
`[x] 1.`.

## Running it

```bash
make eval-skill-implement-spec EVAL_ARGS="--case works-one-wave"
```

About $0.45 a run at list price; it spawns two sub-agents, an executor and a
reviewer, both on Opus.
