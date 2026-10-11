#!/usr/bin/env bash
# Builds the workspace for this case: the calc-smells fixture, committed on main.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc-smells main
