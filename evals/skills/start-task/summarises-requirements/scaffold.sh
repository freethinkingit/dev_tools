#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main, with no spec
# files, so start-task has code to read and a spec folder to write.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main
