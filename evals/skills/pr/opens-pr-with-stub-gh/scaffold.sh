#!/usr/bin/env bash
# Builds the workspace for this case: a repo on a feature branch two commits
# ahead of main, a local bare repo acting as "origin", and bin/ holding a fake
# gh plus a git wrapper. The Makefile puts bin on the PATH for the pr target.
set -euo pipefail
# macOS: /usr/bin/git is an xcrun shim that cannot run in the eval sandbox, so use the
# Command Line Tools binary; elsewhere, whatever git is on the PATH.
GIT=/Library/Developer/CommandLineTools/usr/bin/git; [ -x "$GIT" ] || GIT=$(command -v git)
GIT_CORE=$($GIT --exec-path)
export GIT_AUTHOR_NAME=Example GIT_AUTHOR_EMAIL=example@example.com
export GIT_COMMITTER_NAME=Example GIT_COMMITTER_EMAIL=example@example.com

# --- fake gh: canned answers for the commands the pr skill runs
mkdir -p bin
cat > bin/gh <<'FAKE'
#!/bin/sh
case "$1 $2" in
  "auth status") printf 'github.com\n  ✓ Logged in to github.com account example-user (keyring)\n  - Active account: true\n' ;;
  "repo view")   echo "main" ;;
  "pr view")     echo 'no pull requests found for branch "add-greeting"' >&2; exit 1 ;;
  "pr list")     ;;
  "pr create")   echo "https://github.com/example/demo/pull/1" ;;
  "pr edit")     echo "https://github.com/example/demo/pull/1" ;;
  "issue view")  printf 'title:\tAdd a greeting helper\nstate:\tOPEN\nauthor:\texample-user\nlabels:\tenhancement\nnumber:\t7\n\nThe demo CLI needs a greeting helper. It should take a name and return a friendly hello.\n--\nauthor:\texample-user\nCloses on merge.\n' ;;
  *)             echo "fake gh: unsupported: $*" >&2; exit 2 ;;
esac
FAKE

# --- git wrapper: real git, made to work inside the eval sandbox.
# /usr/bin/git is an xcrun shim that needs a cache the sandbox forbids, so call
# the Command Line Tools binary directly, with an absolute PATH so git's own
# child processes find this wrapper too. "origin" is really the local bare repo;
# answer `remote get-url` with the GitHub URL it stands in for.
cat > bin/git <<WRAP
#!/bin/sh
[ "\$1 \$2" = "remote get-url" ] && { echo https://github.com/example/demo.git; exit 0; }
PATH="\$(cd "\$(dirname "\$0")" && pwd):\$PATH" GIT_TEMPLATE_DIR= GIT_EXEC_PATH=$GIT_CORE exec $GIT "\$@"
WRAP
chmod +x bin/gh bin/git

# --- the repo: main with one commit, pushed to origin; add-greeting two ahead
$GIT init -q --bare --template= origin.git
$GIT init -q --template= -b main .
mkdir -p .git/info && printf 'origin.git/\nbin/\n' > .git/info/exclude
mkdir -p demo tests
printf '# demo\n\nA tiny command-line tool.\n' > README.md
printf 'def main():\n    print("demo")\n' > demo/cli.py
printf 'from demo import cli\n\n\ndef test_main_runs():\n    cli.main()\n' > tests/test_cli.py
$GIT add -A && $GIT commit -q -m "Initial demo tool"
$GIT remote add origin "$PWD/origin.git"
$GIT config remote.origin.uploadpack "$GIT_CORE/git-upload-pack"
$GIT config remote.origin.receivepack "$GIT_CORE/git-receive-pack"
$GIT push -q origin main

$GIT checkout -q -b add-greeting
printf 'def greet(name):\n    return f"Hello, {name}!"\n' > demo/greeting.py
$GIT add -A && $GIT commit -q -m "Add greet helper"
printf 'from demo.greeting import greet\n\n\ndef test_greet():\n    assert greet("Ada") == "Hello, Ada!"\n' > tests/test_greeting.py
$GIT add -A && $GIT commit -q -m "Test greet helper"
