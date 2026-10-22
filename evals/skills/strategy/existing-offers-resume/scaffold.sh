#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main and, from
# files/.freethinking/strategies/, a links-2027 strategy with its title and
# first two sections written and the rest absent, so the path the prompt's name
# derives to already exists. The files are copied in before the setup script
# runs so that its one commit holds them.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main
