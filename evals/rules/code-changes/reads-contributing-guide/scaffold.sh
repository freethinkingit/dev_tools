#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main with
# files/CONTRIBUTING.md, which states a convention the code does not show, and
# files/README.md, which replaces the fixture's copy with the Operations table
# that convention names. The files are copied in before the setup script runs
# so that its one commit holds them.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main
