#!/usr/bin/env bash
# Builds the workspace for this case: a repo on a feature branch three commits
# ahead of main, the third committing the add-greeting spec with both of its
# tasks ticked, this repository's pull request template committed on main, a
# local bare repo acting as "origin", and bin/ holding a fake gh plus a git
# wrapper. The Makefile puts bin on the PATH for the pr target.
set -euo pipefail
# macOS: /usr/bin/git is an xcrun shim that cannot run in the eval sandbox, so use the
# Command Line Tools binary; elsewhere, whatever git is on the PATH.
GIT=/Library/Developer/CommandLineTools/usr/bin/git; [ -x "$GIT" ] || GIT=$(command -v git)
GIT_CORE=$($GIT --exec-path)
ROOT=$($GIT -C "$(dirname "$0")" rev-parse --show-toplevel)
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

# --- the repo: main with one commit, pushed to origin; add-greeting three ahead
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

# The template carries the Closes #<number> convention; committing it on main
# keeps it out of the branch's changes.
mkdir -p .github && cp "$ROOT/.github/pull_request_template.md" .github/
$GIT add -A && $GIT commit -q -m "Add pull request template"
$GIT push -q origin main

$GIT checkout -q -b add-greeting
printf 'def greet(name):\n    return f"Hello, {name}!"\n' > demo/greeting.py
$GIT add -A && $GIT commit -q -m "Add greet helper"
printf 'from demo.greeting import greet\n\n\ndef test_greet():\n    assert greet("Ada") == "Hello, Ada!"\n' > tests/test_greeting.py
$GIT add -A && $GIT commit -q -m "Test greet helper"

# The spec is committed on the branch, not on main, so it is in the branch's
# diff: the pr skill counts only a spec the diff adds or changes. No
# implement-spec reports exist in this sandbox.
mkdir -p .freethinking/specs/add-greeting
cat > .freethinking/specs/add-greeting/requirements.md <<'SPEC'
# Requirements Document

## Introduction

The demo CLI has no way to greet its user. This feature adds a greeting helper that takes a name and returns a friendly hello, so the CLI can greet people by name. Issue #7.

## Glossary

- **System**: The demo package.
- **Greeting**: The string `Hello, <name>!` for a given name.

## Requirements

### Requirement 1: Greet by name

**User Story:** As a user of the demo CLI, I want to be greeted by name, so that the tool feels friendly.

#### Acceptance Criteria

1. WHEN the greeting helper is called with a name, THE System SHALL return the Greeting for that name.

### Requirement 2: Prove the greeting

**User Story:** As the maintainer of the demo package, I want the greeting covered by a test, so that a change to its wording is caught.

#### Acceptance Criteria

1. THE System SHALL have a test that checks the Greeting returned for a sample name.
SPEC
cat > .freethinking/specs/add-greeting/design.md <<'SPEC'
# Design Document

## Overview

One new module, `demo/greeting.py`, holds a `greet(name)` function that returns `f"Hello, {name}!"`, and one new test file, `tests/test_greeting.py`, checks it. Nothing else in the package changes. Issue #7.

## Components and Interfaces

| Component | Responsibility | Interface | Requirements |
| --- | --- | --- | --- |
| `demo/greeting.py` | Build the Greeting | `greet(name: str) -> str` | 1.1 |
| `tests/test_greeting.py` | Prove the Greeting | `test_greet()` | 2.1 |

## Testing Strategy

`pytest tests/test_greeting.py` runs the one test.
SPEC
cat > .freethinking/specs/add-greeting/tasks.md <<'SPEC'
# Implementation Plan

## Overview

Two tasks: the helper first, then its test, which reads the finished helper.

## Tasks

- [x] 1. Add the greet helper to the demo package
  - Add `demo/greeting.py` with `greet(name)` returning `f"Hello, {name}!"`. Ephemeral check: `python -c 'from demo.greeting import greet; print(greet("Ada"))'` prints `Hello, Ada!`
  - _Requirements: 1.1_

- [x] 2. Test the greet helper
  - Add `tests/test_greeting.py` with a test that `greet("Ada")` returns `Hello, Ada!`. Check: `pytest tests/test_greeting.py` passes
  - _Requirements: 2.1_

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2"] }
  ]
}
```
SPEC
$GIT add -A && $GIT commit -q -m "Add the add-greeting spec"
