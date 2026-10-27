#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on branch add-median
# with the bin wrappers the Makefile's readable-code target puts on the PATH,
# then commits this case's files/ on the branch: a terse median function in
# calc/stats.py and its passing test. Main holds only the fixture, so the
# branch's change against main is those two files.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc add-median wrappers
cp -R "$(dirname "$0")/files/." .
git add calc/stats.py tests/test_stats.py
git -c user.name=fixture -c user.email=fixture@example.com commit -q -m "Add median to calc.stats"
