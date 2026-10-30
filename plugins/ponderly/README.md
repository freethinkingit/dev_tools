# ponderly

This plugin helps you write code like a seasoned engineer, even if you don't know all the best practices. It leans on our own thinking for reasoning, since even the best AIs cannot reason: they predict the next token in a sequence, and we have to decide which direction to point them in. It aims to slow the AI down when the scope is unclear and let it run fast when it knows what to do. At the same time, it catches the AI before it lets itself make mistakes or assumptions, so the pace always fits the level of understanding.

## Install

You need [Claude Code](https://claude.com/claude-code). From any terminal:

```bash
claude plugin marketplace add sabind/ponderly
claude plugin install ponderly@sabind
```

The plugin loads the next time you start Claude Code. In a session that is
already open, run `/reload-plugins`.

## Stay up to date

Auto-update is off by default for team marketplaces. Turn it on once:

1. Run `/plugin` in a Claude Code session.
2. Open the **Marketplaces** tab and select `sabind`.
3. Select **Enable auto-update**.

To update by hand:

```bash
claude plugin update ponderly@sabind
```

## Skills

Run a skill as `/ponderly:<skill>`, or just ask Claude for the job and it
runs the one that fits.

- `start-task`: when you want to change code and no other skill fits; it sends one contained change to the `task-executor` agent, a defect to `bugfix` and anything bigger to a spec.
- `strategy`: when you plan a year, a half or a roadmap, or write a tech strategy.
- `hld`: when you design a system or a service that a strategy names.
- `lld`: when you design a component or a module that a high level design names, down to its tasks.
- `implement-spec`: when a spec is approved and you want it built, wave by wave.
- `bugfix`: when you have a bug to fix, starting from its ticket.
- `readable-code`: when you want the code a branch changes to read plainly, with no behaviour change.
- `tighten-tests`: when you want a branch's tests slimmed to the ones that prove something, with the suite proved no weaker.
- `review`: when you want a pull request, a branch or a range of commits reviewed; it reads the change through each lens at once and returns findings anchored to lines.
- `pr`: when you want to open or update a pull request for the current branch.
- `report`: when work comes back, a decision is open, or you ask for status or why something happened; the session usually runs it for you.

Each skill's arguments, questions and outputs are in the Reference's [Skills](https://github.com/sabind/ponderly/blob/main/docs/reference.md#skills) section.

## Agents

- `task-executor`: builds one well-specified change, from a spec task or a change you describe, and proves it.
- `wave-reviewer`: reviews one set of changes against the requirements and design they implement.
- `document-reviewer`: reviews one strategy, high level design or low level design against its template and its parent.
- `review-arm`: reviews one pull request through one lens, such as correctness or security, and returns the problems it verified, each anchored to its lines.

How to launch each agent, what its prompt carries and what it returns are in the Reference's [Agents](https://github.com/sabind/ponderly/blob/main/docs/reference.md#agents) section.

## Rules

The plugin loads these team rules into every Claude Code session and sub-agent:

- `workflow`: how a request finds its skill, and never working on the default branch.
- `code-changes`: how to change code: read first, match the project, make the smallest change, test it.
- `comments`: docstrings on public contracts only, and inline comments only for what is not obvious.
- `tests`: one test per path and per input, at the boundaries, testing behaviour rather than values.
- `collaboration`: how skills and agents ask you questions, state their plan and wait for a plain yes.
- `communication`: how skills and agents write to you: problems first, plain words, then stop.

What each rule says is in the Reference's [Rules](https://github.com/sabind/ponderly/blob/main/docs/reference.md#rules) section, and how the hooks load them is in its [Hooks](https://github.com/sabind/ponderly/blob/main/docs/reference.md#hooks) section.

## Tune the plugin for a repository

How a repository replaces the plugin's templates is in the Reference's [Tune the plugin for a repository](https://github.com/sabind/ponderly/blob/main/docs/reference.md#tune-the-plugin-for-a-repository) section.

## What the plugin runs and sends

The `pr` and `bugfix` skills read issues through the `gh` command already
signed in on your machine; `bugfix` also comments on issues and hands off to
`pr`, which opens the pull request. Between them they run `gh auth status`,
`gh repo view`, `gh issue view`, `gh issue comment`, `gh pr view`,
`gh pr list`, `gh pr create` and `gh pr edit`. `tighten-tests` runs
`gh issue create`, only when you say yes to filing the gaps it found.

The `start-task`, `implement-spec`, `bugfix`, `pr`, `readable-code`,
`tighten-tests` and `review` skills and the `wave-reviewer` and `review-arm`
agents run `git` on the current repository (status, diff, log, branch,
rev-parse, merge-base, ls-files, show, `config --get`, `checkout -b`, in `pr`
`remote get-url origin`, add and commit, and in `review` `cat-file`).
`review` also runs `awk` to count a file's lines, and writes one file, outside
the repository, only when you give it `--json <path>`. Only `pr` reaches the remote with `git`, with `git fetch` and
`git push` to the repository's own `origin`; beyond that, the skills reach
GitHub only through the `gh` commands above.

The `task-executor` agent runs the project's own tests for the code it
changes. The `readable-code` and `tighten-tests` skills also run the project's
own tests, and `readable-code` the project's synthesis command where the branch
holds infrastructure code. `tighten-tests` runs the project's coverage tool, and
copies a source file to a backup folder in the system's temporary directory
while it breaks that file on purpose and restores it at once. When the project
has no coverage tool and you choose to add one, it installs it as a development
dependency with the project's own package manager.

The `strategy`, `hld` and `lld` skills and the `document-reviewer` agent run
no `git` and no `gh`. They read the repository's `.ponderly/` folders,
whatever parent path you give them and, for `lld`, the code the component
touches. The skills write only the document under `.ponderly/`, and the
agent writes nothing.

The `SessionStart` and `SubagentStart` hooks read only the files under the
plugin's `rules/` folder.

No skill, agent or hook reads a credential, runs a package launcher or sends
anything anywhere else. The project's own tests, synthesis command, coverage
tool and package manager, which the skills and agent above run, do whatever they do in
that project.

The source repository's `evals/` and `.ponderly/specs/` folders are its test
suite and its design records. They sit outside the plugin, and an installed
plugin never runs them.

## Learn more

- [The project's front page](https://github.com/sabind/ponderly/blob/main/README.md)
- Guides: [plan a year](https://github.com/sabind/ponderly/blob/main/docs/guides/plan-a-year.md), [build a feature](https://github.com/sabind/ponderly/blob/main/docs/guides/build-a-feature.md), [fix a bug](https://github.com/sabind/ponderly/blob/main/docs/guides/fix-a-bug.md), [make a small change](https://github.com/sabind/ponderly/blob/main/docs/guides/make-a-small-change.md) and [tune a template](https://github.com/sabind/ponderly/blob/main/docs/guides/tune-a-template.md)
- [The Reference](https://github.com/sabind/ponderly/blob/main/docs/reference.md), with every skill, agent, rule and hook in detail
- [The evidence](https://github.com/sabind/ponderly/blob/main/docs/evidence.md), on how the plugin is tested and what it measured against Claude Code without it
