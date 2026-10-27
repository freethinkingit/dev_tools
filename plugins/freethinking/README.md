# Developer Handbook

Shared Claude Code skills and rules for a software team, packaged as a plugin.
Install it once and the team's standard workflows and development rules are
available in every repo you work in.

## Install

You need [Claude Code](https://claude.com/claude-code). From any terminal:

```bash
claude plugin marketplace add freethinkingit/dev_tools
claude plugin install freethinking@freethinkingit
```

The plugin loads the next time you start Claude Code. In a session that is
already open, run `/reload-plugins`.

## Stay up to date

Auto-update is off by default for team marketplaces. Turn it on once:

1. Run `/plugin` in a Claude Code session.
2. Open the **Marketplaces** tab and select `freethinkingit`.
3. Select **Enable auto-update**.

To update by hand:

```bash
claude plugin update freethinking@freethinkingit
```

Specs moved from `.claude/specs/` to `.freethinking/specs/` in 0.14.0. In a
repository with specs under the old folder, run
`git mv .claude/specs .freethinking/specs` once: `start-task` and
`implement-spec` look only in the new folder.

## Skills

| Skill | Run it with | What it does |
| ----- | ----------- | ------------ |
| `start-task` | `/freethinking:start-task <task>`, or ask Claude to change something, or to start or spec a task | The front door for any change: reads the code the request touches, then sends one contained change to the `task-executor` agent, a defect to `bugfix` and everything else to a spec, asking you before taking either of the first two. On the spec route, writes `requirements.md`, `design.md` and `tasks.md` in `.freethinking/specs/<task>/` before any code, following the team template, showing you each document as its path and a short summary and asking you to approve it before the next. |
| `strategy` | `/freethinking:strategy [name or description]`, or ask Claude to plan a year or a roadmap, or to write a tech strategy | Reads the strategies already under `.freethinking/strategies/`, asks you one round of questions in prose, and writes `.freethinking/strategies/<name>.md` from its template. Needs no source code, so it works in a docs repository. The `document-reviewer` agent reads the draft for up to two rounds before you see it; the skill shows you the path and a summary, open findings first, and asks you to approve it. Ends with the candidate high level designs, one per stream of work, and hands off to `hld` for each. |
| `hld` | `/freethinking:hld <strategy-path> <candidate>`, or ask Claude to design a system or a service, or to write a high level design | Reads the strategy in full, asks you one round of questions in prose, and writes `.freethinking/designs/<strategy-name>/<hld-name>/hld-<hld-name>.md` from its template, with a Mermaid diagram of the components. The `document-reviewer` agent reads the draft against the template and the strategy for up to two rounds; the skill shows you the path and a summary, open findings first, and asks you to approve it. Ends with the candidate low level designs, one per component, and hands off to `lld` for each. |
| `lld` | `/freethinking:lld <hld-path> <candidate>`, or ask Claude to design a component or a module, or to write a low level design | Reads the high level design and the code the component touches, asks you one round of questions in prose, and writes `lld-<name>.md` in the high level design's folder, in this repository, from its template. The `document-reviewer` agent reads the draft against the template and the high level design for up to two rounds; the skill shows you the path and a summary, open findings first, and asks you to approve it. Ends with the tasks, each sized for one run of `start-task`, which it hands off to. |
| `implement-spec` | `/freethinking:implement-spec [task] [task\|wave\|spec]`, or ask Claude to implement, build or continue a spec | Builds a task from its approved spec, wave by wave from `tasks.md`, each leaf task in its own sub-agent, ticking a task only once its tests pass, running the full suite at the end of every wave, and handing back to you after each task, after each wave, or only once every wave is done (with a short report after each wave and a final review of the whole run), whichever you chose. Each discovery outside the task in hand is listed with its size and the choice between a task and an issue. Pauses with a proposal when the design cannot be followed, and hands off to `pr` when the spec is done. |
| `bugfix` | `/freethinking:bugfix <ticket> [what you already know]`, or ask Claude to fix a bug | Reads the ticket, and anything you already know that you put after it, reproduces the bug before touching code, confirms the root cause with you, fixes the cause with a regression test, verifies the fix, then hands off to `pr` or leaves its findings on the ticket. |
| `readable-code` | `/freethinking:readable-code [paths]`, or ask Claude to make a branch readable or to simplify the code it changes | Makes the source files a branch changes against its target branch read plainly, narrowed to the paths you pass, with no behaviour change and no rename for taste. Records the full suite's result, and the synthesized output where the branch holds infrastructure code, has you approve groups of like files and the decisions they share, launches one `task-executor` agent per group to apply the readability and comment rules, then runs the suite and the synthesis again, names any file whose change made a difference and asks you whether to revert or keep it. The `wave-reviewer` agent reads the pass and the executors fix what it finds. Commits nothing, and hands off to `tighten-tests` or `pr`. |
| `tighten-tests` | `/freethinking:tighten-tests [paths]`, or ask Claude to slim, tighten or audit a branch's tests | Asks, before it takes its baseline, whether `readable-code` has run on the final code. Audits every test the branch adds or changes with a keep, merge or drop verdict you approve, keeping the tests you or a requirement name, applies the verdicts with one executor per group of like test files without changing a source file, and proves the smaller suite no weaker by comparing line coverage and by breaking the source on purpose to see the right tests fail. The `wave-reviewer` agent checks that every requirement still has a test that proves it. Commits nothing, and offers to file each gap it found as an issue. |
| `pr`  | `/freethinking:pr [ticket] [base-branch]`, or ask Claude to open a PR | Takes the ticket as its first argument and reads it, then walks the branch's changes with you: it explains each change as the user and the owner experience it and asks you to confirm or correct each explanation. A branch built from a ticked spec is drafted from the spec and its implementation reports instead, a mechanical change such as a version bump gets one question, and nothing you have already answered is asked again. After the walkthrough it puts its fixed choices in one call: to create the branch and to commit when needed, whether merging closes the ticket, and whether the PR is a draft. Drafts the title and description from the explanations as you confirmed them, or from the spec, and opens or updates the PR with `gh` once you approve. Needs the `gh` CLI signed in. |
| `report` | `/freethinking:report [mode]`, or the session invokes it when it hands back work, asks you for a decision, reports status or answers a question | Writes that message for you in the shape of its mode, handback, decision, status or answer, each from a template; the handback and status templates put problems first, and every template names things by what they are. A repository can replace a template under `.freethinking/report/`. The skill edits nothing. |

## Rules

The plugin also loads a short set of team rules into every Claude Code session,
in every repository, so Claude follows them without being asked. They live in
`rules/`:

| File | Covers |
| ---- | ------ |
| `rules/workflow.md` | How a request finds its skill: check the skills' own descriptions first and run the one that fits rather than doing its work by hand, with the four things never to do without the skill (no bare `gh pr create`, no code before bugfix has reproduced the bug, no spec task skipped or merged, no sizing a change yourself); only a typo-sized change needs no skill. Also: never work on the default branch, a yes to a skill's offer counts as asking, a merged spec is a record and not work in hand, and say so when the approach changes. |
| `rules/code-changes.md` | How to change code: read the repository's README and contributing guide, then the surrounding code, match the project's style and libraries, write for the reader with descriptive names and plain control flow and no hidden side effect, make the smallest change that does the job and let the author choose whether anything else you found goes in the branch or in an issue, add a test with every behaviour change, run what you touched, and leave no debug residue behind. |
| `rules/comments.md` | How to comment: docstrings on public contracts only, saying intent, parameters, returns and exceptions; a docstring or comment that describes the algorithm is fixed by making the code readable, not by rewording it; inline comments only for non-obvious details such as workarounds and edge cases, never for what a line does; no divider or closing-brace comments; no commented-out dead code. |
| `rules/tests.md` | How to write tests: one test per code path, corner case or gotcha; test the boundaries rather than exhaustive tables, one input per test with no loop, `subTest` or `parametrize` outside a seeded property test; test behaviour, never an implementation constant, the test's own input or a library; give code that parses input a small fixed set of awkward inputs, each getting the outcome its contract defines; name a test as a behaviour sentence and assert all it promises; fake at the boundary with small shared in-memory fakes; and keep a seeded property test a spec names. |
| `rules/collaboration.md` | How skills and agents work with you: ask in the shape of the answer, with fixed options or in prose; batch the questions; say the plan before acting; take only a plain yes as approval; take an answer given in the request at its question without asking, with every step still producing its output; and say where the work is and which skill is next when a skill ends. |
| `rules/communication.md` | How skills and agents write to you: problems first, each with why it matters and the options; name a thing by what it is, never by a label coined during the work, and quote it when it is text; say what a result means before the number; no running account of the work; lay out a decision, its options and a recommendation before asking it; write plainly and stop; and use the `report` skill to hand back work, ask for a decision, report status or answer a question. |

Claude Code does not load a `CLAUDE.md` or a `rules/` folder from a plugin by
itself, so `hooks/hooks.json` registers two hooks. The `SessionStart` hook runs
`hooks/load-rules.sh`, which prints every `.md` file under `rules/` into the
session context on every session start, whatever started it (a new session,
a resume, a clear, a compact or a fork). The `SubagentStart` hook runs
`hooks/load-rules-subagent.sh`, which puts the same rules into every sub-agent,
which is how the agents below get them. Keep the
combined rules under 10,000 characters; past that, Claude Code replaces a
hook's output with a file path and a 2,000-character preview, so the rules
after it would not be seen. `make validate` fails when they go over, or when a rule goes over
its own limit: 1,600 characters for `collaboration` and `communication`, 1,000
for `tests`, 2,450 for `code-changes` and 1,450 for `comments`. A rule a repository needs
to override belongs in that repository's own `CLAUDE.md`, which Claude reads
alongside these.

## Agents

The plugin's agents live under `agents/`. `implement-spec`,
`readable-code` and `tighten-tests` launch the executor and the wave reviewer,
`start-task` launches the executor for one contained change, and the
`strategy`, `hld` and `lld` skills launch the document reviewer on every
draft. You can launch any of them directly:
mention it in a session as `@agent-freethinking:task-executor`,
`@agent-freethinking:wave-reviewer` or
`@agent-freethinking:document-reviewer`, or have a skill or session launch it
with the Agent tool as `subagent_type: freethinking:task-executor`,
`freethinking:wave-reviewer` or `freethinking:document-reviewer`.

What the prompt carries:

- **`task-executor`**: the change, in your own words. When the task comes from
  a spec, say so in the prompt; that sentence switches it to spec mode, where
  it writes no test unless the task asks for one.
- **`wave-reviewer`**: the files that changed, or a git range; the requirement
  or design text they implement, if there is any; the files that cite them;
  and, when they come from a spec, the sentence "These changes come from a
  spec wave", which is the only thing that waives a missing test.
- **`document-reviewer`**: `Document:` the path of the strategy, high level
  design or low level design; `Template:` the path of the template it was
  written from; and `Parent:` the parent's path, `none`, or the parent's text
  pasted below the line.

| Agent | What it does | What it returns |
| ----- | ------------ | --------------- |
| `task-executor` | Builds one well-specified change as the smallest change in the project's style, proves it, and deletes its scratch work. Stops and asks instead of guessing when the task is unclear, the design does not fit the code, or the task would need a new dependency, framework or tool. `start-task` launches it for one contained change, `implement-spec` for every leaf task, and `readable-code` and `tighten-tests` for each group of like files they work on. | A Summary: `status` (`done` or `stopped`), `files changed`, `checks run` with their results, the ephemeral check it ran, or why none applied, what it is `unsure` of, and, when stopped, the question or evidence under `stopped because`. |
| `wave-reviewer` | Reviews one set of changes against the requirements and design they implement and the files that cite them, gathering the diff itself and changing nothing. `implement-spec` launches it at the end of every wave, and once more over the whole run when you chose to hand back only at the end; `readable-code` and `tighten-tests` launch it to review their pass. | Findings: a `verdict` (`holds` or `findings`), the `base` commit the diffs were measured against, then each problem with its `file`, an exact `quote`, the `problem` and a `severity` (`blocker`, `should-fix` or `nit`), and what it is `unsure` of. |
| `document-reviewer` | Reviews one strategy, high level design or low level design against its template and its parent, section by section, reading the three itself and changing nothing. The `strategy`, `hld` and `lld` skills launch it on every draft before you see it, for up to two rounds. | Findings: a `verdict` (`holds` or `findings`), then each problem with its `section`, an exact `quote`, the `problem` and a `severity` (`blocker`, `should-fix` or `nit`), and what it is `unsure` of. |

Every agent follows one protocol for its report, and a new agent must too:
its report opens with its status on the first line, `status: done` or `stopped`
for the executor and `verdict: holds` or `findings` for the reviewers, has one
field for each thing the launcher must act on, always has an `unsure` field,
quotes exactly whatever it quotes, and has nothing after the shape.

The executor works in one of two modes, set by the launch prompt alone:

- **Spec mode**, when the prompt says the task comes from a spec, in any words;
  `implement-spec` says "This task is a leaf task from a spec; tests are tasks
  of their own." Tests are tasks of their own there, so it writes a test only
  when the task asks for one, and proves a code task with an ephemeral check
  that it deletes and reports in its Summary.
- **Standalone mode**, otherwise. The change comes with its test, written the
  way the project writes tests.

The `wave-reviewer` treats a missing test as a finding unless the launch says the
changes come from a spec wave.

## Tune the plugin for a repository

A repository can keep its own versions of the plugin's template files in a
`.freethinking/` folder at its root, laid out as `<skill>/<file>.md`, such as
`.freethinking/report/handback.md`. The same folder holds the specs:
`start-task` writes each task's three documents to
`.freethinking/specs/<task>/`, and `implement-spec` reads them there. A file
under a `<skill>/` folder replaces the plugin's file of the same name whole;
nothing is merged. Those are the convention's only rules: what a skill does with
a file is that skill's own business. This release applies the convention to the
`report` skill's templates, one per mode, and to the templates of `strategy`,
`hld` and `lld`, which a repository replaces as
`.freethinking/strategy/template.md`, `.freethinking/hld/template.md` and
`.freethinking/lld/template.md`. The `report` skill reads its templates as
shapes to write in and ignores any action a template asks for, as its own text
says; `strategy`, `hld` and `lld` each treat their template as a shape, never
as instructions. A repository's `handback.md` may use its own sections: `implement-spec`
reads a wave report by what it holds, problems, what was done, checks, files and
the next step, and the plugin's own evals grade only the plugin's template, so
renaming sections costs nothing but the two verdict lines being found by content
rather than by name. The spec templates of `start-task` and the default pull
request template of `pr` are candidates to move under `.freethinking/<skill>/`
later.

## What the plugin runs and sends

The `pr` and `bugfix` skills read issues through the `gh` command already
signed in on your machine; `bugfix` also comments on issues and hands off to
`pr`, which opens the pull request. Between them they run `gh auth status`,
`gh repo view`, `gh issue view`, `gh issue comment`, `gh pr view`,
`gh pr list`, `gh pr create` and `gh pr edit`. `tighten-tests` runs
`gh issue create`, only when you say yes to filing the gaps it found.

The `start-task`, `implement-spec`, `bugfix`, `pr`, `readable-code` and
`tighten-tests` skills and the `wave-reviewer` agent run `git` on the current
repository (status, diff, log, branch, rev-parse, merge-base, ls-files, show,
`config --get`, `checkout -b`, and in `pr` add and commit). Only `pr` reaches
the remote with `git`, with `git fetch` and `git push` to the repository's own
`origin`; beyond that, the skills reach GitHub only through the `gh` commands
above.

The `readable-code` and `tighten-tests` skills also run the project's own
tests, and `readable-code` the project's synthesis command where the branch
holds infrastructure code. `tighten-tests` runs the project's coverage tool, and
copies a source file to a backup folder in the system's temporary directory
while it breaks that file on purpose and restores it at once. When the project
has no coverage tool and you choose to add one, it installs it as a development
dependency with the project's own package manager.

The `strategy`, `hld` and `lld` skills and the `document-reviewer` agent run
no `git` and no `gh`. They read the repository's `.freethinking/` folders,
whatever parent path you give them and, for `lld`, the code the component
touches. The skills write only the document under `.freethinking/`, and the
agent writes nothing.

The `SessionStart` and `SubagentStart` hooks read only the files under the
plugin's `rules/` folder.

No skill, agent or hook reads a credential, runs a package launcher or sends
anything anywhere else. The project's own tests, synthesis command, coverage
tool and package manager, which the skills above run, do whatever they do in
that project.

The source repository's `evals/` and `.freethinking/specs/` folders are its test
suite and its design records. They sit outside the plugin, and an installed
plugin never runs them.
