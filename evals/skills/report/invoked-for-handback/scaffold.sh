#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture, committed on main, with
# the bin wrappers the Makefile's eval-skill-report target puts on the PATH.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
