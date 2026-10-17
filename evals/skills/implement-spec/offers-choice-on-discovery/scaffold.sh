#!/usr/bin/env bash
# Builds the workspace for this case: the works-one-wave workspace, the calc
# fixture on branch calc-subtract with the two-wave spec committed, except that
# files/tests/test_ops.py replaces the fixture's copy, because setup.sh copies
# a fixture file only where the workspace has none, so the commit carries a
# leftover `import os` in a file no task of the first wave changes: the
# discovery the hand-back is graded on. The spec and the overlay are copied in
# before the setup script runs so that its one commit holds them, on main and
# on the branch.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc calc-subtract wrappers
