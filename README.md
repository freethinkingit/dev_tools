# Developer Handbook

This repository holds the `freethinking` Claude Code plugin, its eval suite,
its free checks and its spec records. To install and use the plugin, read
[the plugin README](plugins/freethinking/README.md). To change it, read
[the contributing guide](.github/CONTRIBUTING.md).

- `plugins/freethinking/`: the plugin itself, with its manifest, skills,
  agents, rules, hooks and its README.
- `evals/`: the eval cases, kept outside the plugin folder because Anthropic's
  plugin directory scans every file in that folder when the plugin is
  submitted.
- `checks/`: the free unit tests.
- `.claude/specs/`: the design records of past tasks.
- `.claude-plugin/marketplace.json`: the marketplace entry that points at the
  plugin folder.

## Add or change a skill or rule

Each skill is a folder under `plugins/freethinking/skills/` with a `SKILL.md`;
each rule is a Markdown file under `plugins/freethinking/rules/`. The
[contributing guide](.github/CONTRIBUTING.md) says how to set up, test and
submit a change. To try a change in one session, load the plugin from your
clone with `claude --plugin-dir ./plugins/freethinking`.

## Testing

Using the plugin needs only Claude Code, except the `pr` and `bugfix` skills,
which need the `gh` CLI signed in. Developing it needs make, python3 and Claude
Code, and CI adds Node only to install Claude Code.

`make validate` runs the unit tests and then the validators, with no model
call, and CI runs `make validate` on every PR. Run it after every change to a
skill, rule, agent, the hooks, the manifest or `checks/`. It needs make,
python3 and Claude Code; make and python3 ship with git in the macOS Command
Line Tools, and there is no venv, pip or requirements file.

### Validator

`claude plugin validate . --strict` checks the marketplace at the repository
root, `claude plugin validate ./plugins/freethinking --strict` checks the
plugin, and `claude plugin validate ./plugins/freethinking/skills --strict`
checks the skills. They are built into Claude Code and make no model call. They
check the manifests and skill frontmatter; for an agent file they check only
that a frontmatter block with a description exists.

### Unit tests

`checks/` holds standard-library `unittest` files, written for the tooling the
plugin's development and evals depend on. `make check` discovers every one of
them, and each file covers one concern, named by its module docstring.

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
  rules/<rule>/<case>/      # one folder per plugins/freethinking/rules/<rule>.md
  skills/<skill>/<case>/    # one folder per plugins/freethinking/skills/<skill>/
  agents/<agent>/<case>/    # one folder per plugins/freethinking/agents/<agent>.md
```

`evals/` sits outside the plugin, but `claude plugin eval` reads cases only
from inside the plugin root. So every eval target builds a temporary tree: a
copy of `plugins/freethinking/` with a copy of `evals/`, minus its results,
inside it, and `git init` at its top. It runs `claude plugin eval` against that
tree, writes the results to `evals/results/<timestamp>/` at the repository
root, and deletes the tree afterwards whether the run passed or failed.

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
change; `make help` shows them. A target whose cases need more than the
read-only tools gets one line in the Makefile's "Per-target flags" block, which
is the one place to read for what each target grants: `--scaffold` to run the
cases' scaffold scripts, whose project trees live under `evals/fixtures/`;
`--allow-tools` for the tools the skill or agent under test needs, such as
Bash, Write and Edit; and `bin` first on the PATH for the wrappers the scaffolds
write, wherever Bash is granted. `eval` carries the union so the whole suite
runs. Each invocation runs under a list-price ceiling, `EVAL_MAX_COST_USD`,
default $2.

Each case runs three times by default; iterate with `EVAL_ARGS="--runs 1"`,
confirm as [`evals/README.md`](evals/README.md) says (2 runs for deterministic
graders, 3 when any is llm), and run the table you paste for a rule or
skill-description change with `EVAL_ARGS="--ablation with-without"` so the Δ
column shows what the plugin added. Results land in
`evals/results/<timestamp>/` (gitignored).

[`evals/README.md`](evals/README.md) covers writing a case, reading results,
keeping a run's transcript to debug a failure, and what the eval sandbox
allows.
