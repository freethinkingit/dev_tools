#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main with the
# links-2027 strategy from files/.ponderly/strategies/, three candidate
# high level designs in its last section, so hld has a parent to read. The file
# is copied in before the setup script runs so that its one commit holds it.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main
