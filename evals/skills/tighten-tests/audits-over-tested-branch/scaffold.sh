#!/usr/bin/env bash
# Builds the workspace for this case: the clamp fixture with main holding the
# module and one test, from files/tests/test_clamp.py copied in before the
# setup script's one commit, and branch clamp-tests holding the fixture's
# over-tested tests/test_clamp.py, committed, so the branch adds fourteen tests
# and the workspace is clean. Adds the bin wrappers the Makefile's tighten-tests
# target puts on the PATH.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" clamp clamp-tests wrappers
cp "$ROOT/evals/fixtures/clamp/tests/test_clamp.py" tests/test_clamp.py
git -c user.name=fixture -c user.email=fixture@example.com commit -q -am "Test clamp"
