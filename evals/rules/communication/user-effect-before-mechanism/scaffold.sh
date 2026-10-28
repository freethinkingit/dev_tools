#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on main, with the bin
# wrappers the Makefile's rule-communication target puts on the PATH, and the
# digest package from files/. Its README says the package builds the weekly
# email subscribers see in their inbox; render_subject slices the subject at 60
# characters mid-word, so test_render_subject_width fails. The files are copied
# in before the setup script runs so that its one commit holds them, and
# files/README.md replaces the fixture's copy.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc main wrappers
