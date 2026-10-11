# opens-pr-with-stub-gh

Tests the pr skill's happy path end to end: starting checks, walkthrough, draft,
push, `gh pr create`. Real GitHub cannot be part of an eval, so the case fakes it.

## What the scaffold builds

`scaffold.sh` runs once per eval run, as you, in the empty workspace that becomes
the agent's working directory. It leaves behind:

- a repo on branch `add-greeting`, two commits ahead of `main`;
- `origin.git`, a bare repo on disk that stands in for the GitHub remote, with
  `main` already pushed so `origin/main` exists;
- `bin/gh`, a fake GitHub CLI;
- `bin/git`, a wrapper around the real git.

The Makefile's `eval-skill-pr` target grants Bash, runs the scaffold, and puts
the relative entry `bin` at the front of the agent's `PATH`. A relative entry
resolves against the working directory, so the skill's bare `gh` and `git` calls
hit the files above. Absolute paths would not work: the sandbox lets the agent
execute nothing outside its workspace and the system directories.

## The fake gh

A shell `case` over the first two arguments. It answers exactly the commands the
pr skill runs, the way real gh would:

| Command | Answer |
| --- | --- |
| `gh auth status` | signed in as `example-user` |
| `gh repo view --json defaultBranchRef --jq ...` | `main` |
| `gh pr view ...` | "no pull requests found", exit 1 (gh's real behaviour when the branch has no PR) |
| `gh pr list ...` | nothing, exit 0 |
| `gh pr create ...`, `gh pr edit ...` | `https://github.com/example/demo/pull/1` |
| anything else | error, exit 2, so an unexpected call fails visibly |

## The git wrapper, and why git is real

The skill reads commits and diffs and pushes, so git has to be real; faking it
would mean faking a repository. The wrapper exists only to make real git work
inside the eval sandbox:

- `/usr/bin/git` on macOS is an xcrun shim that writes a cache file to your temp
  directory, which the sandbox forbids, so the wrapper calls the Command Line
  Tools binary directly and points `GIT_EXEC_PATH` at its helper programs. On
  a machine without that path the scaffold uses whatever `git` is on the PATH;
  it has only been run on macOS.
- Git spawns helpers such as `receive-pack` from other directories, where the
  relative `bin` entry no longer resolves and they would fall back to the broken
  shim. The wrapper therefore exports its own directory on `PATH` as an absolute
  path before handing over.
- `GIT_TEMPLATE_DIR=` (empty) stops `git init` copying hook samples from a
  system directory the sandbox cannot read.
- The one answer it fakes: `git remote get-url origin` returns
  `https://github.com/example/demo.git`. The remote's real URL is the local bare
  repo, so fetch and push work offline; the skill's first check only needs the
  URL to look like GitHub.

Everything else passes straight through to real git. Fetch and push go to
`origin.git` on disk, which is why the run needs no network.

## The prompt

The walkthrough asks the author questions, and nothing can answer in a headless
run, so the prompt gives the answers up front (why, ticket, testing, risk, review
focus) and says to treat the draft as approved. The skill then runs to
`gh pr create` on its own.

## Graders

- `pushes-branch`: a Bash call containing `git push`.
- `creates-pr-with-gh`: a Bash call containing `gh pr create` with `--base main`.
- `reports-pr-url`: the final message contains the URL the fake returned.

## Running it

```bash
make eval-skill-pr
```