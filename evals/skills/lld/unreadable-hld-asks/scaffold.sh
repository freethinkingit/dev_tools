#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main and no design
# files, so the HLD path the prompt gives cannot be read.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main
