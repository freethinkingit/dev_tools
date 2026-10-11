#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on branch calc-subtract,
# with the bin wrappers the Makefile's task-executor target puts on the PATH.
# There are no spec files: the agent takes its mode from the launch prompt alone.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc calc-subtract wrappers
