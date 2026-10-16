#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main with the bin
# wrappers the Makefile's bugfix target puts on the PATH, then plants the
# defect, add returning a - b, so test_add fails. The defect is committed, so the
# workspace is clean and the defect reads as existing code, not a pending edit.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
sed 's/return a + b/return a - b/' calc/ops.py > calc/ops.py.tmp && mv calc/ops.py.tmp calc/ops.py
grep -q 'return a - b' calc/ops.py
git -c user.name=fixture -c user.email=fixture@example.com commit -q -am "Plant the defect: add returns a - b"
