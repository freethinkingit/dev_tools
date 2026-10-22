#!/usr/bin/env bash
# Builds the workspace for this case: a docs repository on main whose one
# commit holds only a README, with no source code and no strategies under
# .freethinking/strategies/, so the strategy skill has nothing to read before
# asking and proves it needs no code. The git binary and author match
# evals/fixtures/setup.sh.
set -euo pipefail
GIT=/Library/Developer/CommandLineTools/usr/bin/git; [ -x "$GIT" ] || GIT=$(command -v git)
export GIT_AUTHOR_NAME=Example GIT_AUTHOR_EMAIL=example@example.com
export GIT_COMMITTER_NAME=Example GIT_COMMITTER_EMAIL=example@example.com
cat > README.md <<'README'
# Docs

Planning documents for the company's product documentation.
README
$GIT init -q --template= -b main .
$GIT add -A && $GIT commit -q -m "Initial commit"
