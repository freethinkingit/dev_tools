#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on branch calc-subtract
# with the two-wave spec from files/.claude/specs/calc-subtract/ committed
# alongside it, and the bin wrappers the Makefile's implement-spec target puts
# on the PATH. The spec is copied in before the setup script runs so that its
# one commit holds it, on main and on the branch.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc calc-subtract wrappers
