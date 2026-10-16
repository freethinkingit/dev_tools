#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main with the bin/
# wrappers. The prompt asks for pytest -q, which the sandbox does not have, so
# the check cannot run. No Makefile: /usr/bin/make is the same xcrun shim as
# git and python3, so make test would fail on xcrun before pytest is reached.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
