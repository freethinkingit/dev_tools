#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main, with the
# shortener-service HLD from files/.freethinking/designs/ copied in first so
# the setup script's one commit holds it, and calc/ code for the LLD to read.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main
