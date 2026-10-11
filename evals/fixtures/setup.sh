#!/usr/bin/env bash
# Builds a case's workspace in the current directory from a fixture tree:
#
#   setup.sh <tree> <branch> [wrappers]
#
# Copies evals/fixtures/<tree>/ in, commits it on main as Example in one
# commit, and checks out <branch> (main stays checked out when <branch> is
# main). With `wrappers`, also writes bin/git and bin/python3, excluded from
# git, for cases that grant Bash and put bin on the PATH: the /usr/bin shims on
# macOS need an xcrun cache the eval sandbox forbids. The wrappers bake in this
# host's git and python3 paths, so they are generated here, not stored.
set -euo pipefail
FIXTURES=$(cd "$(dirname "$0")" && pwd)
usage() { echo "usage: setup.sh <tree> <branch> [wrappers]" >&2; exit 1; }
[ $# -ge 2 ] && [ $# -le 3 ] || usage
TREE=$1 BRANCH=$2 WRAPPERS=${3:-}
if [ -z "$TREE" ] || [ ! -d "$FIXTURES/$TREE" ]; then
  echo "setup.sh: no fixture tree '$TREE' under $FIXTURES; trees:" >&2
  for d in "$FIXTURES"/*/; do echo "  $(basename "$d")" >&2; done
  exit 1
fi
[ -n "$BRANCH" ] || usage
[ $# -lt 3 ] || [ "$WRAPPERS" = wrappers ] || usage
if [ -e .git ]; then
  echo "setup.sh: builds in the current directory, which must be a fresh workspace, and $(pwd) already has .git" >&2
  exit 1
fi
GIT=/Library/Developer/CommandLineTools/usr/bin/git; [ -x "$GIT" ] || GIT=$(command -v git)
export GIT_AUTHOR_NAME=Example GIT_AUTHOR_EMAIL=example@example.com
export GIT_COMMITTER_NAME=Example GIT_COMMITTER_EMAIL=example@example.com

cp -R "$FIXTURES/$TREE/." .

if [ "$WRAPPERS" = wrappers ]; then
  GIT_CORE=$($GIT --exec-path)
  PY=/opt/homebrew/bin/python3; [ -x "$PY" ] || PY=/Library/Developer/CommandLineTools/usr/bin/python3; [ -x "$PY" ] || PY=$(command -v python3)
  mkdir -p bin
  cat > bin/git <<WRAP
#!/bin/sh
PATH="\$(cd "\$(dirname "\$0")" && pwd):\$PATH" GIT_TEMPLATE_DIR= GIT_EXEC_PATH=$GIT_CORE exec $GIT "\$@"
WRAP
  cat > bin/python3 <<WRAP
#!/bin/sh
exec $PY "\$@"
WRAP
  chmod +x bin/git bin/python3
fi

$GIT init -q --template= -b main .
if [ "$WRAPPERS" = wrappers ]; then
  mkdir -p .git/info && printf 'bin/\n' > .git/info/exclude
fi
$GIT add -A && $GIT commit -q -m "Initial commit"
[ "$BRANCH" = main ] || $GIT checkout -q -b "$BRANCH"
