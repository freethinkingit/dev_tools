#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on branch calc-mean,
# with calc/ops.py and calc/compare.py from files/ committed in its one commit,
# both split by divider comments, and the bin wrappers the Makefile's
# wave-reviewer target puts on the PATH; then an uncommitted calc/stats.py that
# adds mean with the same divider comments and one real defect, floor division
# where the cited requirement says mean([1, 2]) is 1.5.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
cp -R "$(dirname "$0")/files/." .
bash "$ROOT/evals/fixtures/setup.sh" calc calc-mean wrappers
printf '# ---------------------------------------------------------------------------\n# Averages\n# ---------------------------------------------------------------------------\n\n\ndef mean(values):\n    return sum(values) // len(values)\n' > calc/stats.py
