#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main with subtract
# already in calc/ops.py and tested, and the calc-subtract spec from
# files/.claude/specs/ with every task ticked, so the spec reads as merged
# work. The files are copied in before the setup script runs so that its one
# commit holds them, and a file at a fixture path, calc/ops.py and
# tests/test_ops.py here, replaces the fixture's copy. No wrappers: the case
# grants no Bash.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main
