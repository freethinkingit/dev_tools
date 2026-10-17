# offers-choice-on-discovery

Tests how implement-spec hands back a discovery: something the wave's work
turned up that no task covers. The hand-back lists it under Problems with
where it is, roughly how much work it would add to the branch, and its two
options, a proposed task in `tasks.md` or an issue, and leaves the author to
choose. The executor reports it under `unsure` and does not fix it unasked.

## What the scaffold builds

The works-one-wave workspace: the calc package from `evals/fixtures/calc/` on
branch `calc-subtract`, with the two-wave spec under
`.claude/specs/calc-subtract/` committed, and the `bin/` wrappers the
Makefile's implement-spec target puts on the PATH. The one difference is
`files/tests/test_ops.py`. A file at a fixture path replaces the fixture's
copy, because `evals/fixtures/setup.sh` copies a fixture file only where the
workspace has none, so the committed `tests/test_ops.py` starts with
`import os  # left over`, then a blank line, then the fixture's file
unchanged. No task of the first wave changes that file, so the import is never
a wave finding for implement-spec to fix; the executor meets it while reading
the tests it runs.

The prompt is works-one-wave's, verbatim: wave cadence, no optional tests,
already on a branch, and no fork for the Agent tool, so the hand-back is
written inline by the `report` skill, whose Problems section comes first.

## Graders

All six are `regex`. The four on the final message start with
`## Problems((?!\n## )[\s\S])*`, which matches only up to the next `## `
heading, so each match has to fall inside the Problems section, and they carry
the `i` flag so "Import os" or "Issue" at a sentence start still match.

- `adds-subtract`: `calc/ops.py` contains the function task 1 describes.
- `leaves-import`: `import os` is still in `tests/test_ops.py`, so it was not
  fixed unasked.
- `names-discovery`: Problems names the discovery, `import os`,
  `unused import` or `leftover import`.
- `states-size`: Problems states a size, such as a line, minutes, small,
  trivial or a one-liner.
- `offers-task`: Problems offers the task option, `a task` or `tasks.md`.
- `offers-issue`: Problems offers the issue option, the word `issue`.

## What it cannot check

That the executor noticed the import on its own rather than the hand-back
finding it some other way, and whether the size and the options belong to the
discovery: each grader reads only that its words appear somewhere in Problems,
so another problem in the same section could supply them. `states-size` is
loose, since `line` also matches "line 1" in the location. The plant may also
go unnoticed: the executor reports the import only if it notices it while
reading the tests it runs, and the report skill then has to carry it under
Problems. If runs miss it, iterate the plant.

## Running it

```bash
make eval-skill-implement-spec EVAL_ARGS="--case offers-choice-on-discovery"
```
