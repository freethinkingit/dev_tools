# Martian harness

This folder scores the `review` skill on the offline half of Martian's
[code review benchmark](https://github.com/withmartian/code-review-benchmark):
50 pull requests from five open-source projects, each with golden comments
written by people. It runs the same Docker image as the
[ReviewBench harness](../reviewbench/README.md) on each pull request, converts
the findings into the data file Martian's pipeline reads, runs Martian's own
extraction, deduplication and judge steps on it, and writes a score report with
precision, recall and F1. It is not a leaderboard submission.

## What it costs

Both the run and the judge are real model calls on your own keys, so the
harness runs by hand and never in CI, and `make validate` never calls it.

- Each pull request is one Claude Code session in the image, billed to
  `ANTHROPIC_API_KEY` and capped at `RB_CONFIG_BUDGET_USD`, fifteen dollars by
  default. When the review's findings file needs repair, the adapter runs a
  repair session with its own one-dollar cap, so one pull request can cost the
  cap plus one dollar. A whole run is 50 pull requests, so it can cost up to
  50 times that.
- The judge is a second model cost, billed to `MARTIAN_API_KEY`: Martian's
  extraction, deduplication and judge steps each call the judge model.

Start with `make run ONLY=0`, one pull request, before a whole run.

## What you need

- `docker`, `gh`, `uv`, `jq`, `git` and `python3` on your `PATH`. `make
  check-tools` names the first of `docker`, `gh`, `uv`, `jq` and
  `MARTIAN_API_KEY` that is missing, and each target checks the tools and key
  it needs before it starts.
- `ANTHROPIC_API_KEY` in your environment for the image.
- `MARTIAN_API_KEY` in your environment for the judge: the key of whichever
  endpoint `MARTIAN_BASE_URL` names.
- The image, built by the ReviewBench harness with
  `make -C ../reviewbench image`.

## Run it

Run each target from this folder, or with `make -C benchmarks/martian` from the
repository root, in this order:

```bash
make check-tools          # stop naming the first missing tool or key
make setup                # clone Martian's benchmark at MARTIAN_COMMIT into .martian/ and install it
make prs                  # resolve the golden pull requests into prs.json through gh
make run ONLY=0           # run the image on entry 0 of prs.json
make run                  # run the image on all 50 pull requests into runs/<timestamp>/
make convert              # write <dir>/benchmark_data.json from <dir>/findings/
make judge                # run Martian's steps 2, 2.5 and 3 into <dir>/scoring/evaluations.json
make report               # write and print <dir>/report.md
```

`prs.json` is committed, so `make prs` is needed only to rebuild it from the
golden files. `run` fetches each pull request's base and head from GitHub into
`work/`, logs and skips a pull request it cannot fetch or whose container
fails, and fails only when no pull request produced findings. `convert`,
`judge` and `report` work on `RUN`, which defaults to the newest folder under
`runs/`, so `make run convert judge report` works on the folder the run just
made. Each of them appends its command to the folder's `run.json`.

## Variables

Set any of these on the `make` command line or in your environment.

- `MARTIAN_COMMIT`: the commit of Martian's benchmark `setup` checks out.
- `IMAGE`: the image tag to run, `ponderly-review:dev` by default.
- `ONLY`: an index into `prs.json`, counting from 0, to run one pull request.
- `RUN`: the run folder for `convert`, `judge` and `report`, the newest under
  `runs/` by default.
- `MARTIAN_BASE_URL`: the judge's OpenAI-compatible API base URL,
  `https://api.anthropic.com/v1/` by default, Anthropic's OpenAI-compatible
  endpoint.
- `MARTIAN_MODEL`: the judge model, `claude-sonnet-5` by default. Override
  both for an OpenAI judge.

These three reach the image and are recorded in `run.json`:

- `RB_CONFIG_MODEL`: the Claude model the review runs on, `opus` by default.
- `RB_CONFIG_EFFORT`: its effort level, `high` by default.
- `RB_CONFIG_BUDGET_USD`: the cost cap of one pull request's session in
  dollars, `15` by default.

## The judge endpoint

Whether Anthropic's OpenAI-compatible endpoint satisfies Martian's client is
not yet checked. The first `judge` run with the default `MARTIAN_BASE_URL`
answers it, and the answer goes here.
