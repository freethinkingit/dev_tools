#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main with no
# .freethinking/strategies/ folder, so the strategy path the prompt names
# cannot be read.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main
