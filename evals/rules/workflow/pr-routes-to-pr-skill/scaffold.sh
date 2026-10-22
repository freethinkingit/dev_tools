#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main, with the bin
# wrappers the Makefile's workflow target puts on the PATH. The target grants
# Bash so the commands the skill the request routes to runs while it loads are
# allowed, git through the wrapper; gh is absent in the sandbox, and its failure
# is absorbed by the skill's `|| true`.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
