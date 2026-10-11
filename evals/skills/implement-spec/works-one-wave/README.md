# works-one-wave

Tests the implement-spec work loop end to end: validate the graph, launch the
executor agent for the wave's task, verify its work by running the checks
yourself, have the reviewer agent read the wave, run the suite, hand back
without starting the next wave.

## What the scaffold builds

A small Python package on branch `calc-subtract` with a committed spec under
`.claude/specs/calc-subtract/`: two tasks in two waves (add `subtract`, then
test it). The package is `evals/fixtures/calc/`, built by
`evals/fixtures/setup.sh`; the spec is this case's `files/` folder, copied in
before that script's one commit. Tests run with `python3 -m unittest`. `bin/`
holds wrappers for `git` and `python3`, because the `/usr/bin` shims on macOS
need an xcrun cache the sandbox forbids; the Makefile's implement-spec target
puts `bin` on the PATH and grants Bash, Write and Edit.

The prompt gives the start answers up front (wave cadence, no optional tests,
already on a branch), since nothing can answer mid-run.

## Graders

- `launches-sub-agent`: the Agent tool was called.
- `runs-tests-itself`: the orchestrator ran `unittest` through Bash, not just
  the sub-agent.
- `adds-subtract`: `calc/ops.py` contains the function task 1 describes.
- `leaves-wave-1`: `tests/test_ops.py` gained no `test_subtract`, so wave 1 was
  not started.
- `reviews-the-wave`: the report carries the wave review's verdict, so the
  reviewer agent was launched.

## What it cannot check

The tick. Inside an eval run, Claude Code refuses edits to files under
`.claude/` even when Edit is granted, so the skill's attempt to tick task 1 is
denied, as is a shell fallback. The skill is expected to report that and stop,
which it does; a grader on the tick would only ever test the sandbox. Observed
on Claude Code 2.1.x; if that changes, add a grader on
`.claude/specs/calc-subtract/tasks.md` for `[x] 1.`.

## Running it

```bash
make eval-skill-implement-spec EVAL_ARGS="--case works-one-wave"
```

About $0.45 a run at list price; it spawns two sub-agents, an executor and a
reviewer, both on Opus.
