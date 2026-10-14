# Evals

Cases for `claude plugin eval`, one folder per component of the plugin, so you
can run only the ones for what you changed. Every case is a real model call on
your own Claude seat, so evals run by hand, never in CI. Costs printed are
list-price estimates, usually ten to thirty cents a case.

```text
evals/
  hook/<case>/                  # the SessionStart and SubagentStart hooks that load the rules
  rules/<rule>/<case>/          # one folder per rules/<rule>.md
  skills/<skill>/<case>/        # one folder per skills/<skill>/
  agents/<agent>/<case>/        # one folder per agents/<agent>.md
  fixtures/<tree>/              # a project the scaffolds build, copied in by fixtures/setup.sh
  results/                      # one folder per run, gitignored
```

## Running

```bash
make help                        # the targets that exist, enumerated from the folders above
make eval-skill-pr               # the cases tagged pr
make eval-rule-code-changes      # the cases tagged code-changes
make eval-hook
make eval                        # the whole suite
```

Every case carries its component's name as a tag, and each target is
`claude plugin eval . --tag <name>` plus the flags its cases need, which live
in the Makefile's "Per-target flags" block. Anything extra goes through
`EVAL_ARGS`, and the per-invocation cost ceiling through `EVAL_MAX_COST_USD`
(default $2, which the full suite needs raised):

```bash
make eval-skill-pr EVAL_ARGS="--runs 1"                          # one run per case while iterating
make eval-rule-code-changes EVAL_ARGS="--case smallest-change"   # one case
make eval EVAL_MAX_COST_USD=5
```

Run only the target of the component your change touched, never the whole
suite, unless the change is to `hooks/` or the Makefile. A single run is noisy,
so iterate with `EVAL_ARGS="--runs 1"`, then confirm before trusting a change:
pass `--runs 2` when every grader of the case is `regex`, `tool_used` or
`file_exists`, and `--runs 3` when any grader is `llm`. A target whose cases
mix the two confirms at 3, or run it at 2 and then each `llm` case at 3 with
one `--case` each. Without `--runs`, a plain `make eval-…` still runs each case
three times and the table shows the mean.

`--case` takes one glob, and when you pass it more than once the last flag
wins, so run several named cases with one invocation each.

Every target runs one arm, the plugin loaded, which answers "does the skill
work". For a change to a rule or to a skill's `description`, the question is
whether the plugin changed Claude's behaviour at all, and that needs the
no-plugin baseline: run the table you paste into the PR with
`EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=5`. It doubles that run's
cost, so raise the ceiling or the table comes back partial, and adds the `W/OUT`
and `Δ` columns; a case that scores the same in both arms proves nothing about
the plugin. A case whose only positive grader is a Skill check reads Δ 0.00 in
that table, because Skill graders are not scored without the plugin; give such
a case a grader on the result too.

## Reading results

Every run writes `evals/results/<timestamp>/` with `aggregate-result.json`
and `report.html`. The report shows each grader's
verdict with the text it matched or failed to match. The JSON has the same
plus, per run, `tracePath`: the transcript of what Claude did.

## Debugging a failing case

A case usually fails for one of three reasons: the grader is wrong, the case
gives Claude too few turns, or the plugin really misbehaved. The transcript
tells you which. Keep it with `--keep-temp`, which the docs provide for exactly
this:

```bash
make eval-skill-pr EVAL_ARGS="--keep-temp --case opens-pr-with-stub-gh"
```

The run prints `kept temp: /private/tmp/e-XXXXXX` for each run (failed runs
are kept even without the flag). Inside it, `out/trace.jsonl` is the session
as JSON, one message per line: Claude's text, every tool call with its input,
and every tool result. `home/cwd/` is the workspace after the run.

Treat a kept directory as the output of an untrusted session: read its files,
do not run things inside it. The agent wrote the workspace, home and tmp in
there, and the tool seals the home and tmp parts (mode 000) for that reason,
printing a `chmod` to open them when you need to. Many tools load configuration
from the directory they run in: git reads `.git/config` and hooks from the repo
you stand in, Claude Code reads `.claude/` and `CLAUDE.md`, Python imports from
the current directory. Running one of them from inside a kept workspace would
execute whatever the agent left there, as you, outside the sandbox. With our own
fixtures that is harmless, but the habit should not depend on it. Open
`trace.jsonl` by its full path from outside, and `rm -rf` the directory when
you are done: macOS clears `/private/tmp` of files untouched for three days and
on reboot, but the sealed parts can make the periodic clean skip a directory.

`report.html` in the results folder shows each grader's verdict with the text
it matched or failed to match, which is usually enough to tell a wrong grader
from wrong behaviour without opening the trace. `--verbose` additionally logs
per-message trace events to Claude Code's debug log under `~/.claude/debug/`.

What to look for:

- **Hit the turn limit** (`Reached maximum number of turns` in NOTES): see what
  the turns went on. Often Claude is searching for something the sandbox does
  not have, which is a skill or fixture problem; otherwise the cap is too
  tight. Set `max_turns` generously and let `EVAL_MAX_COST_USD` bound the cost,
  rather than using small caps as a cost control.
- **Pattern not found in last_message**: a `regex` grader reads only Claude's
  final reply unless you give it a `target`. If the behaviour happened earlier
  (a tool call, a file written), grade that instead: `tool_used` with an
  `input_match`, or a `target: { source: file, path: ... }`.
- **Bash called 0x**: either the case's target does not grant Bash, or Claude
  chose not to use it. The run's progress output lists tools it asked for and
  was refused as `not granted`.
- **scaffold failed**: run the scaffold by hand in an empty directory with the
  environment the eval gives it, and read the error:

  ```bash
  mkdir /tmp/w && cd /tmp/w && env -i PATH="$PATH" HOME=$PWD TMPDIR=$PWD TERM=dumb bash /path/to/scaffold.sh
  ```

## What the sandbox allows

Learned by probing; see `skills/pr/opens-pr-with-stub-gh/README.md` for the
worked example.

- Only the read-only tools a case lists in `allowed_tools` are available.
  `Bash`, `Write`, `Edit` and the web tools need `--allow-tools`, which a
  per-target Makefile line provides. There is no user to approve anything
  mid-run, so an ungranted tool is simply absent.
- A granted Bash runs under the OS sandbox: writes only inside the workspace,
  your home and Claude Code config unreadable, no network, and nothing
  executable outside the workspace and the system paths. A stub binary must
  therefore come from the scaffold and be reached through a relative `PATH`
  entry such as `bin`.
- The stock `/usr/bin/git` and `/usr/bin/python3` on macOS are xcrun shims that
  need a cache the sandbox forbids, so they fail. The Command Line Tools git
  works when called directly; the pr fixture's wrapper shows how, and the
  scaffolds fall back to whatever `git` is on the PATH elsewhere. The fixtures
  have only been run on macOS.
- The scaffold runs as you, outside the sandbox, with a minimal environment
  (`PATH`, `HOME`, `TMPDIR`, `TERM`) and a 120-second limit. It can create
  files and git state only; nothing it writes is loaded as configuration.
- The harness puts the workspace's git status into the session context at
  start, so a skill can know the branch and dirty state without running git.
- Edits to files under `.claude/` in the workspace are refused even when Edit
  is granted, and so is a shell fallback. A skill that writes there (ticking a
  spec's task list) cannot be graded on that write; grade the rest and expect
  the skill to report the refusal.
- A prompt that starts with `/freethinking:<skill>` is expanded before the model
  runs, so a `tool_used` grader on `Skill` never fires for it; grade the
  behaviour instead. A prompt that merely describes the work does trigger the
  Skill tool, which is what the workflow-rule cases grade.

## Writing a case

A folder with `prompt.md` (frontmatter plus the prompt) and at least one grader
under `graders/`; `claude plugin eval init --bare <name>` writes the template.
Tag it with its component's name so the `make` target finds it. Add `case.yaml`
only for a `context.scaffold_script`. A project a case builds lives once as
real files under `evals/fixtures/<tree>/`, and one script,
`evals/fixtures/setup.sh <tree> <branch> [wrappers]`, copies it into the
workspace, commits it and checks out the branch; `wrappers` adds the `bin/`
wrappers for cases that grant Bash and put `bin` on the PATH. Each case's
`scaffold.sh` is its own regular file, never a symlink: it finds the setup
script from the repository root, `git -C "$(dirname "$0")" rev-parse
--show-toplevel`, calls it and adds only what the case needs. The pr cases
are the exception to the fixture rule: each carries a full copy of the fake
`gh` and the git wrapper in its own scaffold, because the fake must be
reachable through a relative `bin` entry built in the workspace, so a change
to the fake is made in every pr scaffold. Extra files a case needs live in its own `files/` folder; the harness copies nothing from
it, the case's scaffold does. Copied before `setup.sh` runs, they land in its
one commit, on main and on the branch, as works-one-wave does; copied after,
they are left uncommitted. Give a case one grader on the result and one on the
steps where both make sense. Prefer graders that read the transcript or a file
(`regex`, `tool_used`, `file_exists`, `target: { source: file }`); an `llm`
grader adds three judge calls per run. `file_exists` counts only files created
during the run, so a scaffold-created or edited file is invisible to it. A
"must not invoke" grader (`tool_used` with `min: 0`, `max: 0`) needs `arm: both`
so it is scored the same with and without the plugin. A case that needs flags
gets one line in the Makefile; a new skill or rule folder gets its `make`
target with no Makefile change.

`checks/test_eval_cases.py`, run by `make validate`, keeps every case's tag,
graders and scaffold valid.

Reference: https://code.claude.com/docs/en/plugin-evals
