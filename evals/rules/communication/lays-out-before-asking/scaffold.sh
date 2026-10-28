#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main, with the bin
# wrappers the Makefile's rule-communication target puts on the PATH, and the
# README from files/. It describes an upload worker whose retry ceiling is not
# chosen yet, offers 3, 5 or 10, and gives the observed facts and what the
# uploader waits through under each. The file is copied in before the setup
# script runs so that its one commit holds it, and it replaces the fixture's
# README.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
