#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on branch calc-subtract,
# with the bin wrappers the Makefile's wave-reviewer target puts on the PATH,
# then an uncommitted calc/ops.py that adds a correct subtract, a - b.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc calc-subtract wrappers
printf 'def add(a, b):\n    return a + b\n\n\ndef subtract(a, b):\n    return a - b\n\n\ndef multiply(a, b):\n    return a * b\n' > calc/ops.py
