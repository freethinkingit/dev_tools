#!/usr/bin/env bash
# Builds the workspace for this case: the links-2027 strategy, the shortener
# service HLD under it and the visit counter LLD under that, from files/, with a
# copy of the plugin's LLD template at templates/lld-template.md, since the
# eval's plugin copy sits at a temporary path the prompt cannot name. The files
# are copied in before the setup script runs so that its one commit holds them.
# No wrappers: the agent has no Bash.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main
