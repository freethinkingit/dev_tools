# Contributing

This repository holds a Claude Code plugin, in `plugins/ponderly/`: shared
skills, agents and rules for a software team, whose hooks put the rules in every
session's context. This guide
says how to set up, test and submit a change, and how the repository uses
issues, labels, milestones and discussions.

The plugin is under the [MIT License](../LICENSE). Taking part means following
the [Code of Conduct](CODE_OF_CONDUCT.md). Report a vulnerability as the
[security policy](SECURITY.md) says, never in a public issue.

## Set up

Clone the repository and work from its root:

```bash
claude --plugin-dir ./plugins/ponderly   # load your working copy for one session
make validate                                # the unit tests and the validators; CI runs this on every PR
```

## Test

Using the plugin needs only Claude Code, except the `pr` and `bugfix` skills,
which need the `gh` CLI signed in, and `tighten-tests`, which needs it only to
file the gaps it found as issues. Developing it needs make, python3 and Claude
Code, and CI adds Node only to install Claude Code.

The free checks are `make validate`: the unit tests under `checks/`, then
three `claude plugin validate` runs, on `.`, `./plugins/ponderly` and
`./plugins/ponderly/skills`. They make no model call. Run `make validate`
after every change to a skill, rule, agent, the hooks, the manifest or
`checks/`. The make and python3 it needs ship with git in the macOS Command
Line Tools, and there is no venv, pip or requirements file.

A change to a skill, agent, rule or hook comes with an eval case or a change to
one. A new skill comes with at least one case under `evals/skills/<name>/`. A
change that touches no skill, agent, rule or hook needs no eval, and
`make validate` is the whole check.

### Validator

`claude plugin validate . --strict` checks the marketplace at the repository
root, `claude plugin validate ./plugins/ponderly --strict` checks the
plugin, and `claude plugin validate ./plugins/ponderly/skills --strict`
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

Evals run by component with `make eval-<kind>-<name>`, such as
`make eval-skill-pr`, and `make eval-hook` for the hooks. Every case is a model
call on your own Claude seat, so evals run by hand, never in CI. Paste the
table the command prints into the Testing section of your pull request.

`evals/` holds cases for `claude plugin eval`, organised by the component they
test, so you can run only the ones for what you changed:

```text
evals/
  hook/<case>/              # the SessionStart and SubagentStart hooks that load the rules
  rules/<rule>/<case>/      # one folder per plugins/ponderly/rules/<rule>.md
  skills/<skill>/<case>/    # one folder per plugins/ponderly/skills/<skill>/
  agents/<agent>/<case>/    # one folder per plugins/ponderly/agents/<agent>.md
```

`evals/` sits outside the plugin folder, so Anthropic's plugin directory, which
scans every file in the plugin folder when the plugin is submitted, sees only
the plugin. But `claude plugin eval` reads cases only from inside the plugin
root, so every eval target builds a temporary tree: a copy of
`plugins/ponderly/` with a copy of `evals/`, minus its results, inside it,
and `git init` at its top. It runs `claude plugin eval` against that tree,
writes the results to `evals/results/<timestamp>/` at the repository root, and
deletes the tree afterwards whether the run passed or failed.

Each case runs Claude in a sandbox with only this plugin loaded. The dollar
figures printed are list-price estimates, not charges.

```bash
make help                           # list the eval targets that exist
make eval-skill-bugfix              # one skill
make eval-rule-workflow             # one rule
make eval-hook                      # the hook
make eval-agent-task-executor       # the task-executor agent
make eval-agent-wave-reviewer       # the wave-reviewer agent
make eval-agent-document-reviewer   # the document-reviewer agent
make eval-agent-review-arm          # the review-arm agent
make eval                           # everything
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
default $2. `make eval-skill-review` defaults to $10, because one review
launches six to eleven agents; a value on the command line still wins.

Each case runs three times by default; iterate with `EVAL_ARGS="--runs 1"`,
confirm as [`evals/README.md`](../evals/README.md) says (2 runs for
deterministic graders, 3 when any is llm), and run the table you paste for a
rule or skill-description change with `EVAL_ARGS="--ablation with-without"` so
the Δ column shows what the plugin added. Results land in
`evals/results/<timestamp>/` (gitignored).

[`evals/README.md`](../evals/README.md) covers writing a case, reading results,
keeping a run's transcript to debug a failure, and what the eval sandbox
allows.

## Make a change

The repository is laid out as:

- `plugins/ponderly/`: the plugin itself, with its manifest, skills,
  agents, rules, hooks and its README.
- `evals/`: the eval cases, kept outside the plugin folder for the reason
  [Evals](#evals) gives.
- `checks/`: the free unit tests.
- `benchmarks/`: the ReviewBench and Martian harnesses that score the `review`
  skill, kept outside the plugin folder and never shipped with it.
- `.ponderly/specs/`: the design records of past tasks.
- `.claude-plugin/marketplace.json`: the marketplace entry that points at the
  plugin folder.

Each skill is a folder under `plugins/ponderly/skills/` with a `SKILL.md`;
each rule is a Markdown file under `plugins/ponderly/rules/`.

A small change, such as a typo, a one-line fix or a rename: make it. A bug:
run `/ponderly:bugfix`. Anything else: run `/ponderly:start-task`. It
reads the code and decides between the `task-executor` agent for one contained
change, `bugfix` for a defect, and a spec for the rest, and asks before taking
the first two. When it writes a spec, `/ponderly:implement-spec` builds it.
On every route, `start-task` proposes the branch name, and you or
`implement-spec` create it; `pr` can also create it at its branch offer,
naming it from the issue you pass it.

Work on a branch named `<issue number>-<short slug>` when an issue exists, such
as `12-ticket-reference`, and on a short slug otherwise. Never work on the
default branch. The Create a branch link under Development on an issue page
gives that shape. When `/ponderly:implement-spec` proposes the task name as
the branch, answer with the issue number in front.

Open the pull request with `/ponderly:pr` and give the issue number as the
ticket. The [pull request template](pull_request_template.md) is the one place
that says how the issue is linked and when to write `Closes #<number>`.

A new skill, agent, rule or hook is also added to the `component` dropdown of
every issue form.

## Issues

New issues start from one of the issue forms:

- **Report a misbehaving skill or agent**, for something the plugin did wrong.
- **Propose a new or changed skill, agent or rule**, for something it should
  do.
- **Propose an eval case**, for a behaviour an eval should guard.
- **Propose a spike**, for a question that has to be answered before work can
  be designed.

Submitting a form labels the issue `triage` and applies its type label:
`type: bug`, `type: feature`, `type: task` and `type: spike` respectively.
Blank issues are off. The new-issue page also links questions to Discussions
Q&A, ideas to Discussions Ideas, and vulnerabilities to the security policy
page.

At least weekly, a maintainer triages:

1. Reviews every issue labelled `triage`.
2. Sets, confirms or corrects its type label.
3. Sets one priority label and the area labels that apply, none, one or both.
4. Applies `question` instead when the issue cannot be classified without more
   from its author.
5. Closes the issue as not planned, or keeps it. A kept issue goes into a
   milestone only when it serves a goal that already has one; otherwise it
   waits in the backlog, the open issues with no milestone.
6. Removes `triage`.

An issue opened without a form gets `triage` by hand at the next triage. A
discussion that becomes work is converted to an issue, and an issue that is
really a question is converted to a discussion at triage.

## Labels and milestones

Every issue has one type label. Labels are lowercase:

- `type: bug`, `type: feature`, `type: task` and `type: spike` say what sort of
  thing the issue is.
- `priority: high`, `priority: medium` and `priority: low` say how soon the
  issue should be done.
- `quality` and `compatibility` are areas: the behaviour of the skills, agents
  and rules with the evals and checks that guard it, and working across agent
  tools.
- `triage` marks an issue no maintainer has classified yet.
- `question` marks an issue that needs more from its author.
- `good first issue` and `help wanted` invite contributors.

An issue carries at most one priority label and the area labels that apply; an
issue with no area label is normal. If another label seems needed, propose it
in an issue rather than create it.

`good first issue` is the one label with behaviour on GitHub: it feeds the
repository's contribute page and GitHub's surfacing of approachable issues.
`help wanted` marks work a maintainer would merge but will not write.

A milestone names a goal. The open milestones are the roadmap. Milestones
are made in a planning pass, separate from triage: when a goal is chosen, it
gets a milestone and the issues that serve it are pulled in from the backlog.

## Compatibility

Portability means a skill or rule here does its job when another agent tool,
such as Cursor or Codex, loads it, not only Claude Code. The checks known so
far:

1. A rule is plain Markdown with no tool-specific syntax, so another tool can
   load it as instructions as it is.
2. A skill's steps run on commands anyone has, `git`, `gh`, `make`, and name a
   Claude-only tool only where no command does the job.
3. The Claude-only pieces are listed so a `compatibility` issue can start from
   the list: `$ARGUMENTS`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_SKILL_DIR}` and
   the `arguments:` frontmatter list in skills, the hooks that load the rules,
   and the agents' frontmatter.

The list grows from issues labelled `compatibility`.

## Settings, not files

Labels, milestones and Discussions are repository settings, not files, so they
do not travel with the tree. A fork or a copy of this repository does not carry
them.
