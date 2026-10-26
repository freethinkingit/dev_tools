# Reference

This page holds the detail for every skill, agent, rule and hook in the
`freethinking` plugin. Each component has a section of its own, headed with
its name. The plugin's files live under `plugins/freethinking/`.

## Contents

- [Skills](#skills)
  - [start-task](#start-task)
  - [strategy](#strategy)
  - [hld](#hld)
  - [lld](#lld)
  - [implement-spec](#implement-spec)
  - [bugfix](#bugfix)
  - [pr](#pr)
  - [report](#report)
- [Agents](#agents)
  - [task-executor](#task-executor)
  - [wave-reviewer](#wave-reviewer)
  - [document-reviewer](#document-reviewer)
  - [The report protocol](#the-report-protocol)
- [Rules](#rules)
  - [workflow](#workflow)
  - [code-changes](#code-changes)
  - [comments](#comments)
  - [collaboration](#collaboration)
  - [communication](#communication)
- [Hooks](#hooks)
  - [load-rules.sh](#load-rulessh)
  - [load-rules-subagent.sh](#load-rules-subagentsh)
- [Tune the plugin for a repository](#tune-the-plugin-for-a-repository)
- [What the plugin runs and sends](#what-the-plugin-runs-and-sends)

## Skills

Every skill runs as `/freethinking:<skill>`. You can also just ask Claude
for the job; each skill's description says when it applies, and Claude
runs the one that fits. The skills live under `plugins/freethinking/skills/`.

When a skill asks you something with a short fixed list of answers, it
uses a question with options plus free text. When the answer is your own
words, it asks in prose.

### start-task

The front door for any request to change code.

- **Command:** `/freethinking:start-task [task name or short description]`.
  Or ask Claude to change something, or to start, plan, spec, scope or
  design a task.
- **When it applies:** any request to change code that no other skill takes.
  A bug you name goes to `bugfix`. An existing spec goes to `implement-spec`.
  A pull request goes to `pr`. A strategy or a design goes to `strategy`,
  `hld` or `lld`. A typo-sized change needs no skill.
- **What it does:** reads the code the request touches, then picks one of
  three routes. One contained change goes to the `task-executor` agent. A
  defect goes to `bugfix`. Everything else becomes a spec.
- **What it asks:** which route, when it picks the executor or `bugfix`; the
  fit, when the request extends nothing in the codebase; the spec questions,
  in prose, before the requirements; your approval of each spec document;
  and whether to relaunch, after the executor stops.
- **What it writes:** on the spec route, `requirements.md`, `design.md` and
  `tasks.md` in `.freethinking/specs/<task>/`, from the team template, one at
  a time. You see each as its path and a short summary, and approve it before
  the next. On the executor route, the executor writes the code; you see its
  Summary and the diff. The skill itself writes no code.
- **Hands off to:** `bugfix` on the bug route; `pr` after a `done`
  Summary; `implement-spec` once `tasks.md` is approved. It proposes a branch
  name but never creates the branch.

### strategy

Writes a tech strategy: about a year of work across one or more projects.

- **Command:** `/freethinking:strategy [name or description]`. Or ask Claude
  to plan a year, a half or a roadmap, or to write a tech strategy.
- **When it applies:** a plan for a year or a roadmap. It needs no source
  code, so it works in a docs repository. Not for a code change or a bug.
- **What it asks:** it first reads the strategies already under
  `.freethinking/strategies/`. Then it asks one round of questions in prose.
  It asks whether to overwrite or resume when the document already exists,
  and asks you to approve the document.
- **What it writes:** `.freethinking/strategies/<name>.md`, from its template.
  The `document-reviewer` agent reads the draft for up to two rounds before
  you see it. You see the path and a summary, open findings first. It writes
  no code.
- **Hands off to:** `hld`, once for each candidate high level design. The
  strategy ends with those candidates, one per stream of work.

### hld

Writes a high level design: one system, service or stream of work that a
strategy names.

- **Command:** `/freethinking:hld [strategy-path] [candidate or name]`. Both
  arguments are optional. With a strategy, the second names one of its
  candidates; with no strategy, it is the design's name. Or ask Claude to
  design a system or a service, or to write a high level design.
- **When it applies:** taking a candidate from a strategy. Not for a code
  change or a bug.
- **What it asks:** it reads the strategy in full first. It asks you to paste
  the strategy when its path cannot be read, whether to go on with no parent
  when no path was given, and which candidate when your words name none of
  the strategy's. Then one round of questions in prose; overwrite or resume
  when the document exists; and your approval.
- **What it writes:**
  `.freethinking/designs/<strategy-name>/<hld-name>/hld-<hld-name>.md`, or
  `.freethinking/designs/<hld-name>/hld-<hld-name>.md` when it has no
  parent strategy. It writes from its template, with a Mermaid diagram of
  the components. The `document-reviewer` agent reads the draft against the
  template and the strategy for up to two rounds. You see the path and a
  summary, open findings first. It writes no code.
- **Hands off to:** `lld`, once for each candidate low level design, one per
  component.

### lld

Writes a low level design: one component, module or interface that a high
level design names, down to its tasks.

- **Command:** `/freethinking:lld [hld-path] [candidate or name]`. Both
  arguments are optional. With a high level design, the second names one of
  its candidates; with no design, it is the document's name. Or ask Claude to
  design a component or a module, or to write a low level design.
- **When it applies:** taking a candidate from a high level design. Not for
  a code change or a bug.
- **What it asks:** it reads the high level design and the code the
  component touches first. It asks you to paste the design when its path
  cannot be read, whether to go on with no parent when no path was given,
  and which candidate when your words name none. Then one round of questions
  in prose; overwrite or resume when the document exists; and your approval.
- **What it writes:** `lld-<name>.md` in the high level design's folder, in
  this repository:
  `.freethinking/designs/<strategy-name>/<hld-name>/lld-<name>.md`, the two
  folder names taken from the high level design's path, even when that design
  lives in another repository. With no parent high level design it writes
  `.freethinking/designs/<name>/lld-<name>.md`. It writes from its template.
  The `document-reviewer` agent reads the draft against the template and the
  high level design for up to two rounds. You see the path and a summary,
  open findings first. It writes no code.
- **Hands off to:** `start-task`, once for each task. The design ends with
  its tasks, each sized for one run of `start-task`.

### implement-spec

Builds a task from its approved spec, wave by wave.

- **Command:** `/freethinking:implement-spec [task-name] [task|wave|spec]`.
  The second argument is how often to hand back. Or ask Claude to implement,
  build, continue or resume a spec.
- **When it applies:** a spec already exists in `.freethinking/specs/<task>/`
  with a `tasks.md`.
- **What it asks:** once, at set-up: how often to hand back (after each task,
  after each wave, or only once every wave is done), how to treat optional
  tests (ask, always, never), and, when you are on the default branch,
  whether to create a branch under the task's name. Only when
  needed: which spec, when several exist and you named none; approval of a
  fix to the task graph; how to go on after a failing suite or an unfixed
  finding; and a proposal when the design cannot be followed.
- **What it writes:** the code, through one `task-executor` agent per leaf
  task. It ticks a task in `tasks.md` only once its tests pass or its manual
  check is done. It runs the full suite at the end of every wave, and the
  `wave-reviewer` agent reads each wave. You get a short report after each
  wave and a final review of the whole run. Each discovery outside the task
  in hand is listed with its size and the choice between a task and an issue.
  It never edits the spec beyond its checkboxes without your approval.
- **Hands off to:** `pr` when every non-optional task is ticked;
  `start-task` when there is no spec or no `tasks.md`.

### bugfix

Fixes a bug the disciplined way, starting from a ticket.

- **Command:** `/freethinking:bugfix [ticket] [what you already know]`. Both
  arguments are optional; with no ticket, it asks for the symptom and the
  expected behaviour. Or ask Claude to fix, debug or investigate a bug.
- **When it applies:** a bug, issue or defect.
- **What it asks:** what you already know, when you gave only the ticket; a
  paste of the ticket, when it cannot be read; the approach, when nothing
  points to a lead; manual reproduction steps, in prose, when no test or
  script can reproduce the bug; your confirmation of the root cause before
  any code changes; a manual re-run after a manual reproduction; and how to
  hand off at the end.
- **What it writes:** it reproduces the bug before touching code, keeps the
  steps, evidence and hypotheses in the conversation, then fixes the cause
  with a regression test and checks nothing else broke. On request, it
  comments its findings on the ticket. It does not branch, commit or push.
- **Hands off to:** `pr` on `Open it now`, with the ticket as its argument.
  Or it stops, with or without a comment on the ticket, and tells you
  `/freethinking:pr <ticket>`.

### pr

Opens or updates a GitHub pull request for the current branch.

- **Command:** `/freethinking:pr [ticket] [base-branch]`. Or ask Claude to
  open a PR.
- **When it applies:** opening, creating, raising or updating a pull request.
  It needs the `gh` CLI signed in.
- **What it asks:** whether to create a branch, on the default branch;
  whether to commit uncommitted work; a paste of the ticket, when it cannot
  be read. Then it walks the branch's changes with you one at a time, in
  prose, with a short set of review prompts. Your own words become the
  description's Changes bullets. It asks once for what the diff cannot
  answer, whether the PR closes the ticket, and for your approval of the
  draft.
- **What it writes:** the title and description, from the repository's own
  pull request template or the skill's default one. After you approve, it
  commits if you said so, pushes, and opens the PR with `gh`. You see the
  draft in full, then the PR's URL.
- **Hands off to:** nothing; it is the end of the line.

### report

Writes the message to you when work comes back, a choice is open, or you
ask what is going on or why.

- **Command:** `/freethinking:report [handback|decision|status|answer]`. Most
  often the session runs it for you.
- **When it applies:** handing back work, asking you for a decision,
  reporting status, or answering what something is or why. With no mode
  given, it picks one from the conversation.
- **What it asks:** only the closing question of a decision.
- **What it writes:** one message in the shape of its mode, from a template.
  The handback and status templates put problems first. Every template
  names things by what they are. A repository can replace a template under
  `.freethinking/report/`; see
  [Tune the plugin for a repository](#tune-the-plugin-for-a-repository). It
  edits no file and launches no agent.
- **Hands off to:** nothing.

## Agents

The agents live under `plugins/freethinking/agents/`. `implement-spec`
launches the executor and the wave reviewer. `start-task` launches the
executor for one contained change. The `strategy`, `hld` and `lld` skills
launch the document reviewer on every draft.

You can launch any of them yourself. Mention it in a session as
`@agent-freethinking:task-executor`, `@agent-freethinking:wave-reviewer` or
`@agent-freethinking:document-reviewer`. Or have a skill or session launch it
with the Agent tool as `subagent_type: freethinking:task-executor`,
`freethinking:wave-reviewer` or `freethinking:document-reviewer`.

### task-executor

Builds one well-specified change as the smallest change in the project's
style, proves it, and deletes its scratch work.

- **Launched by:** `start-task` for one contained change, and
  `implement-spec` for every leaf task.
- **What the prompt carries:** the change, in your own words. When the task
  comes from a spec, say so; that sentence switches it to spec mode.
- **Modes:** the launch prompt alone sets the mode.
  - **Spec mode**, when the prompt says the task comes from a spec, in any
    words. `implement-spec` says "This task is a leaf task from a spec; tests
    are tasks of their own." There it writes a test only when the task asks
    for one. It proves a code task with an ephemeral check, deletes it, and
    reports it in its Summary.
  - **Standalone mode**, otherwise. The change comes with its test, written
    the way the project writes tests.
- **When it stops:** it stops and asks instead of guessing when the task is
  unclear, the design does not fit the code, or the task would need a new
  dependency, framework or tool.
- **What it returns:** a Summary: `status` (`done` or `stopped`), `files
  changed`, `checks run` with their results, the ephemeral check it ran or
  why none applied, what it is `unsure` of, and, when stopped, the question
  or evidence under `stopped because`.

### wave-reviewer

Reviews one set of changes against the requirements and design they
implement and the files that cite them. It gathers the diff itself and
changes nothing.

- **Launched by:** `implement-spec`, at the end of every wave, and once more
  over the whole run when you chose to hand back only at the end.
- **What the prompt carries:** the files that changed, or a git range; the
  requirement or design text they implement, if any; the files that cite
  them; and, when they come from a spec, the sentence "These changes come
  from a spec wave". Only that sentence waives a missing test; otherwise a
  missing test is a finding.
- **What it returns:** Findings: a `verdict` (`holds` or `findings`), the
  `base` commit the diffs were measured against, then each problem with its
  `file`, an exact `quote`, the `problem` and a `severity` (`blocker`,
  `should-fix` or `nit`), and what it is `unsure` of.

### document-reviewer

Reviews one strategy, high level design or low level design against its
template and its parent, section by section. It reads the three itself and
changes nothing.

- **Launched by:** the `strategy`, `hld` and `lld` skills, on every draft
  before you see it, for up to two rounds.
- **What the prompt carries:** `Document:` the path of the document;
  `Template:` the path of the template it was written from; and `Parent:` the
  parent's path, `none`, or the parent's text pasted below the line.
- **What it returns:** Findings: a `verdict` (`holds` or `findings`), then
  each problem with its `section`, an exact `quote`, the `problem` and a
  `severity` (`blocker`, `should-fix` or `nit`), and what it is `unsure` of.

### The report protocol

Every agent follows one protocol for its report, and a new agent must too:

- The first line is its status: `status: done` or `stopped` for the
  executor, `verdict: holds` or `findings` for the reviewers.
- It has one field for each thing the launcher must act on.
- It always has an `unsure` field.
- It quotes exactly whatever it quotes.
- Nothing comes after the shape.

## Rules

The plugin loads a short set of team rules into every Claude Code session,
in every repository, so Claude follows them without being asked. They live
in `plugins/freethinking/rules/`. The [Hooks](#hooks) load them.

A rule a repository needs to override belongs in that repository's own
`CLAUDE.md`, which Claude reads alongside these.

### workflow

File: `plugins/freethinking/rules/workflow.md`. How a request finds its
skill.

- Check the skills' own descriptions first, and run the one that fits rather
  than doing its work by hand.
- Four things never happen without the skill: no bare `gh pr create`, no
  code before `bugfix` has reproduced the bug, no spec task skipped or
  merged, and no sizing a change yourself.
- Only a typo-sized change needs no skill.
- Never work on the default branch. A yes to a skill's offer counts as
  asking to commit or push.
- A merged spec is a record, not work in hand.
- Say so when the approach changes.

### code-changes

File: `plugins/freethinking/rules/code-changes.md`. How to change code.

- Read the repository's README and contributing guide, then the surrounding
  code.
- Match the project's style and libraries.
- Make the smallest change that does the job. Let the author choose whether
  anything else you found goes in the branch or in an issue.
- Add a test with every behaviour change.
- Run what you touched.
- Leave no debug residue behind.

### comments

File: `plugins/freethinking/rules/comments.md`. How to comment code.

- Docstrings on public contracts only, saying intent, parameters, returns
  and exceptions.
- Inline comments only for non-obvious details, such as workarounds and edge
  cases; never for what a line does.
- No divider or closing-brace comments.
- No commented-out dead code.

### collaboration

File: `plugins/freethinking/rules/collaboration.md`. How skills and agents
work with you.

- Ask in the shape of the answer: fixed options, or prose.
- Batch the questions.
- Say the plan before acting.
- Take only a plain yes as approval.
- Take an answer given in the request at its question without asking; every
  step still produces its output.
- When a skill ends, say where the work is and which skill is next.

### communication

File: `plugins/freethinking/rules/communication.md`. How skills and agents
write to you.

- Problems first, each with why it matters and the options.
- Name a thing by what it is, never by a label coined during the work, and
  quote it when it is text.
- Say what a result means before the number.
- No running account of the work.
- Lay out a decision, its options and a recommendation before asking it.
- Write plainly and stop.
- Use the `report` skill to hand back work, ask for a decision, report
  status or answer a question.

## Hooks

Claude Code does not load a `CLAUDE.md` or a `rules/` folder from a plugin by
itself. So `plugins/freethinking/hooks/hooks.json` registers two hooks, one
per script below.

Keep the combined rules under 10,000 characters; past that, Claude Code
replaces a hook's output with a file path and a 2,000-character preview, so
the rules after it would not be seen. `make validate` fails when they go over,
or when a rule goes over its own limit: 1,600 characters for `collaboration`,
1,900 for `communication`, 1,000 for `tests`, 2,450 for `code-changes` and
1,450 for `comments`.

### load-rules.sh

- **Event:** `SessionStart`, on every session start, whatever started it: a
  new session, a resume, a clear, a compact or a fork.
- **What it loads:** every `.md` file under the plugin's `rules/` folder,
  under a short "Handbook rules" header, printed into the session context.
  With no rule files it prints only the header.

### load-rules-subagent.sh

- **Event:** `SubagentStart`, every time a sub-agent starts.
- **What it loads:** the same header and rules as `load-rules.sh`, wrapped in
  the JSON that this event needs. This is how the agents get the rules. It
  exits with an error, naming the problem, when the plugin has no rule files.

## Tune the plugin for a repository

A repository can keep its own versions of the plugin's template files in a
`.freethinking/` folder at its root, laid out as `<skill>/<file>.md`, such as
`.freethinking/report/handback.md`.

The same folder holds the specs. `start-task` writes each task's three
documents to `.freethinking/specs/<task>/`, and `implement-spec` reads them
there.

A file under a `<skill>/` folder replaces the plugin's file of the same name
whole; nothing is merged. Those are the convention's only rules. What a skill
does with a file is that skill's own business.

This release applies the convention to:

- the `report` skill's templates, one per mode: `handback.md`,
  `decision.md`, `status.md` and `answer.md`, under `.freethinking/report/`;
- the templates of `strategy`, `hld` and `lld`, which a repository replaces as
  `.freethinking/strategy/template.md`, `.freethinking/hld/template.md` and
  `.freethinking/lld/template.md`.

The `report` skill reads its templates as shapes to write in. It ignores any
action a template asks for, as its own text says. `strategy`, `hld` and `lld`
each treat their template as a shape, never as instructions.

A repository's `handback.md` may use its own sections. `implement-spec` reads
a wave report by what it holds: problems, what was done, checks, files and the
next step. The plugin's own evals grade only the plugin's template. So
renaming sections costs nothing but the two verdict lines being found by
content rather than by name.

The spec templates of `start-task` and the default pull request template of
`pr` are candidates to move under `.freethinking/<skill>/` later.

## What the plugin runs and sends

The `pr` and `bugfix` skills read issues through the `gh` command already
signed in on your machine. `bugfix` also comments on issues and hands off to
`pr`, which opens the pull request. Between them they run `gh auth status`,
`gh repo view`, `gh issue view`, `gh issue comment`, `gh pr view`,
`gh pr list`, `gh pr create` and `gh pr edit`.

The `start-task`, `implement-spec`, `bugfix` and `pr` skills and the
`wave-reviewer` agent run `git` on the current repository: status, diff, log,
branch, rev-parse, merge-base, `checkout -b`, and in `pr` add and commit.
Only `pr` reaches the remote, with `git fetch` and `git push` to the
repository's own `origin` and the `gh` commands above.

The `strategy`, `hld` and `lld` skills and the `document-reviewer` agent run
no `git` and no `gh`. They read the repository's `.freethinking/` folders,
whatever parent path you give them and, for `lld`, the code the component
touches. The skills write only the document under `.freethinking/`, and the
agent writes nothing.

The `SessionStart` and `SubagentStart` hooks read only the files under the
plugin's `rules/` folder.

No skill, agent or hook reads a credential, runs a package launcher or sends
anything anywhere else.

The source repository's `evals/` and `.freethinking/specs/` folders are its
test suite and its design records. They sit outside the plugin, and an
installed plugin never runs them.
