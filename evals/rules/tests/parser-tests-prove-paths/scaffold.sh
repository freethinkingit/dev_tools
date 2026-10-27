#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture, committed on main, with
# the bin/ wrappers so the session or the executor can run the tests in the sandbox.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
