# Developer Handbook

Shared Claude Code skills and rules for a software team, packaged as a plugin.
Install it once and the team's standard workflows and development rules are
available in every repo you work in.

## Install

You need [Claude Code](https://claude.com/claude-code) and read access to this
repo. From any terminal:

```bash
claude plugin marketplace add freethinkingit/dev_tools
claude plugin install freethinking@freethinkingit
```

The plugin loads the next time you start Claude Code. In a session that is
already open, run `/reload-plugins`.

The clone uses the git credentials already on your machine and never prompts.
If the first command fails on access, sign in with `gh auth login`, run
`gh auth setup-git`, and try again.

## Stay up to date

Auto-update is off by default for team marketplaces. Turn it on once:

1. Run `/plugin` in a Claude Code session.
2. Open the **Marketplaces** tab and select `freethinkingit`.
3. Select **Enable auto-update**.

To update by hand:

```bash
claude plugin update freethinking@freethinkingit
```

## Skills

| Skill | Run it with | What it does |
| ----- | ----------- | ------------ |
| `start-task` | `/freethinking:start-task <task>`, or ask Claude to start or spec a task | Writes the spec before any code: `requirements.md`, `design.md` and `tasks.md` in `.claude/specs/<task>/`, following the team template, with you approving each document before the next. |
| `implement-spec` | `/freethinking:implement-spec [task] [task\|wave]`, or ask Claude to implement, build or continue a spec | Builds a task from its approved spec, wave by wave from `tasks.md`, each leaf task in its own sub-agent, ticking a task only once its tests pass, running the full suite at the end of every wave, and handing back to you after each task or each wave, whichever you chose. Pauses with a proposal when the design cannot be followed, and hands off to `pr` when the spec is done. |
| `bugfix` | `/freethinking:bugfix <ticket>`, or ask Claude to fix a bug | Reads the ticket, reproduces the bug before touching code, confirms the root cause with you, fixes the cause with a regression test, verifies the fix, then hands off to `pr`. |
| `pr`  | `/freethinking:pr`, or ask Claude to open a PR | Walks the branch's changes with you, asks what the code can't answer, drafts the title and description to the team standard, and opens the PR with `gh` once you approve. Needs the `gh` CLI signed in. |

## Rules

The plugin also loads a short set of team rules into every Claude Code session,
in every repository, so Claude follows them without being asked. They live in
`rules/`:

| File | Covers |
| ---- | ------ |
| `rules/workflow.md` | Which skill to use when: spec new work with `start-task`, build an existing spec with `implement-spec`, fix bugs with `bugfix`, open PRs with `pr`, never work on the default branch, and when a change is small enough to skip all of that. |
| `rules/code-changes.md` | How to change code: read the surrounding code first, match the project's style and libraries, make the smallest change that does the job, add a test with every behaviour change, run what you touched, and leave no debug residue behind. |
| `rules/comments.md` | How to comment: docstrings on public contracts only, saying intent, parameters, returns and exceptions; inline comments only for non-obvious details such as workarounds and edge cases, never for what a line does; no divider or closing-brace comments; no commented-out dead code. |

Claude Code does not load a `CLAUDE.md` or a `rules/` folder from a plugin by
itself, so `hooks/hooks.json` registers two hooks. The `SessionStart` hook runs
`hooks/load-rules.sh`, which prints every `.md` file under `rules/` into the
session context on every session start, whatever started it (a new session,
a resume, a clear, a compact or a fork). The `SubagentStart` hook runs
`hooks/load-rules-subagent.sh`, which puts the same rules into every sub-agent,
which is how both agents below get them. Keep the
combined rules under 10,000 characters; Claude Code truncates hook output past
that. A rule a repository needs to override belongs in that repository's own
`CLAUDE.md`, which Claude reads alongside these.

## Agents

The plugin ships two agents under `agents/`. `implement-spec` launches both,
and you can launch either directly: mention it in a session as
`@agent-freethinking:task-executor` or `@agent-freethinking:wave-reviewer`, or have a
skill or session launch it with the Agent tool as
`subagent_type: freethinking:task-executor` or `freethinking:wave-reviewer`.

What the prompt carries:

- **`task-executor`**: the change, in your own words. When the task comes from
  a spec, say so in the prompt; that sentence switches it to spec mode, where
  it writes no test unless the task asks for one.
- **`wave-reviewer`**: the files that changed, or a git range; the requirement
  or design text they implement, if there is any; the files that cite them;
  and, when they come from a spec, the sentence "These changes come from a
  spec wave", which is the only thing that waives a missing test.

| Agent | What it does | What it returns |
| ----- | ------------ | --------------- |
| `task-executor` | Builds one well-specified change as the smallest change in the project's style, proves it, and deletes its scratch work. Stops and asks instead of guessing when the task is unclear, the design does not fit the code, or the task would need a new dependency, framework or tool. `implement-spec` launches it for every leaf task. | A Summary: `status` (`done` or `stopped`), `files changed`, `checks run` with their results, the ephemeral check it ran, or why none applied, what it is `unsure` of, and, when stopped, the question or evidence under `stopped because`. |
| `wave-reviewer` | Reviews one set of changes against the requirements and design they implement and the files that cite them, gathering the diff itself and changing nothing. `implement-spec` launches it at the end of every wave. | Findings: a `verdict` (`holds` or `findings`), then each problem with its `file`, an exact `quote`, the `problem` and a `severity` (`blocker`, `should-fix` or `nit`), and what it is `unsure` of. |

The executor works in one of two modes, set by the launch prompt alone:

- **Spec mode**, when the prompt says the task comes from a spec, in any words;
  `implement-spec` says "This task is a leaf task from a spec; tests are tasks
  of their own." Tests are tasks of their own there, so it writes a test only
  when the task asks for one, and proves a code task with an ephemeral check
  that it deletes and reports in its Summary.
- **Standalone mode**, otherwise. The change comes with its test, written the
  way the project writes tests.

The reviewer treats a missing test as a finding unless the launch says the
changes come from a spec wave.

## Add or change a skill or rule

Each skill is a folder under `skills/` with a `SKILL.md`; each rule is a Markdown
file under `rules/`. To work on one:

```bash
claude --plugin-dir .      # load your working copy for one session
make validate              # the unit tests and the validator under Testing; CI runs this on every PR
```

Then open a PR. `/freethinking:pr` works on this repo too. Evals are tests like the
rest, so the table for any skill, rule, agent or hook you changed goes in the
PR's Testing section with everything else you ran.

## Testing

Using the plugin needs only Claude Code, except the `pr` skill, which needs
the `gh` CLI signed in. Developing it needs make, python3 and Claude Code, and
CI adds Node only to install Claude Code.

`make validate` runs the unit tests and then the validator, with no model call,
and CI runs `make validate` on every PR. Run it after every change to a skill,
rule, agent, the hook, the manifest or `checks/`. It needs make, python3 and
Claude Code; make and python3 ship with git in the macOS Command Line Tools,
and there is no venv, pip or requirements file.

### Validator

`claude plugin validate . --strict` and `claude plugin validate ./skills --strict`
are built into Claude Code and make no model call. They check the manifests and
skill frontmatter; for an agent file they check only that a frontmatter block
with a description exists.

### Unit tests

`checks/` holds standard-library `unittest` files, written for the tooling the
plugin's development and evals depend on:

- `test_hook_encoder.py`: the sub-agent hook's JSON encoder, with a fixed
  table, a seeded fuzz and a real run of the hook.
- `test_agents.py`: every agent's frontmatter, and every `freethinking:<name>` a
  skill references names an existing agent or skill.

```bash
make check                                                 # all of them
python3 -m unittest discover -s checks                     # the same, without make
python3 -m unittest discover -s checks -v                  # list each test
python3 -m unittest discover -s checks -p test_agents.py   # one file
python3 -m unittest discover -s checks -k test_real_run    # one test, by name
```

To add one, write a `test_*.py` under `checks/` in plain `unittest`: standard
library only, Python 3.9 syntax, no model call, and paths resolved from the
file's own location so it passes from any directory. Discovery picks it up with
no Makefile change, and CI runs it through `make validate`.

### Evals

`evals/` holds cases for `claude plugin eval`, organised by the component they
test, so you can run only the ones for what you changed:

```text
evals/
  hook/<case>/              # the SessionStart and SubagentStart hooks that load the rules
  rules/<rule>/<case>/      # one folder per rules/<rule>.md
  skills/<skill>/<case>/    # one folder per skills/<skill>/
  agents/<agent>/<case>/    # one folder per agents/<agent>.md
```

Each case runs Claude in a sandbox with only this plugin loaded. Every case is
a real model call on your own Claude seat, so evals run by hand, not in CI. The
dollar figures printed are list-price estimates, not charges.

```bash
make help                       # list the eval targets that exist
make eval-skill-bugfix          # one skill
make eval-rule-workflow         # one rule
make eval-hook                  # the hook
make eval-agent-task-executor   # the task-executor agent
make eval-agent-wave-reviewer   # the wave-reviewer agent
make eval                       # everything
make eval-skill-pr EVAL_ARGS="--runs 2 --ablation with-without"   # pass extra flags through
make eval EVAL_MAX_COST_USD=5                                     # raise the per-invocation cost ceiling
```

The `eval-skill-<name>`, `eval-rule-<name>` and `eval-agent-<name>` targets are
enumerated from the folders under `evals/` and select cases by the tag that
names the component, so a new case folder gets its target with no Makefile
change; `make help` shows them. A case that needs its own flags gets one line
in the Makefile's "Per-target flags" block: the implement-spec, pr,
code-changes, task-executor and wave-reviewer targets run their cases' scaffold
scripts with `--scaffold`, and the project trees those scaffolds copy live
under `evals/fixtures/`. implement-spec and task-executor grant Bash, Write and
Edit, pr and wave-reviewer grant Bash, and code-changes grants Write and Edit;
the four that grant Bash put `bin` first on the PATH for the wrappers the
scaffolds write. `eval` carries the union so the whole suite runs. Each
invocation runs under a list-price ceiling, `EVAL_MAX_COST_USD`, default $2.

Each case runs three times by default; iterate with `EVAL_ARGS="--runs 1"`, and
run the table you paste for a rule or skill-description change with
`EVAL_ARGS="--ablation with-without"` so the Δ column shows what the plugin
added. Results land in `evals/results/<timestamp>/` (gitignored). Paste the
table the command prints into the PR's Testing section. A new skill needs at
least one case under `evals/skills/<name>/`.

`evals/README.md` covers writing a case, reading results, keeping a run's
transcript to debug a failure, and what the eval sandbox allows.
