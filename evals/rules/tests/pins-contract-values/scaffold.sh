#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture with calc/events.py from
# files/, committed on main, and the bin/ wrappers so the session or the
# executor can run the tests in the sandbox. The module is copied in before the
# setup script runs so that its one commit holds it.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
