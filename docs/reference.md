# Reference

This page holds the detail for every skill, agent, rule and hook in the
`ponderly` plugin. Each component has a section of its own, headed with
its name. The plugin's files live under `plugins/ponderly/`.

## Contents

- [Skills](#skills)
  - [start-task](#start-task)
  - [strategy](#strategy)
  - [hld](#hld)
  - [lld](#lld)
  - [implement-spec](#implement-spec)
  - [bugfix](#bugfix)
  - [readable-code](#readable-code)
  - [tighten-tests](#tighten-tests)
  - [review](#review)
  - [pr](#pr)
  - [report](#report)
- [Agents](#agents)
  - [task-executor](#task-executor)
  - [wave-reviewer](#wave-reviewer)
  - [document-reviewer](#document-reviewer)
  - [review-arm](#review-arm)
  - [The report protocol](#the-report-protocol)
- [Rules](#rules)
  - [workflow](#workflow)
  - [code-changes](#code-changes)
  - [comments](#comments)
  - [tests](#tests)
  - [collaboration](#collaboration)
  - [communication](#communication)
- [Hooks](#hooks)
  - [load-rules.sh](#load-rulessh)
  - [load-rules-subagent.sh](#load-rules-subagentsh)
- [Tune the plugin for a repository](#tune-the-plugin-for-a-repository)
- [What the plugin runs and sends](#what-the-plugin-runs-and-sends)

## Skills

Every skill runs as `/ponderly:<skill>`. You can also just ask Claude
for the job; each skill's description says when it applies, and Claude
runs the one that fits. The skills live under `plugins/ponderly/skills/`.

When a skill asks you something with a short fixed list of answers, it
uses a question with options plus free text. When the answer is your own
words, it asks in prose.

### start-task

The front door for any request to change code.

- **Command:** `/ponderly:start-task [task name or short description]`.
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
  `tasks.md` in `.ponderly/specs/<task>/`, from the team template, one at
  a time. You see each as its path and a short summary, and approve it before
  the next. On the executor route, the executor writes the code; you see its
  Summary and the diff. The skill itself writes no code.
- **Hands off to:** `bugfix` on the bug route; `pr` after a `done`
  Summary; `implement-spec` once `tasks.md` is approved. It proposes a branch
  name but never creates the branch.

### strategy

Writes a tech strategy: about a year of work across one or more projects.

- **Command:** `/ponderly:strategy [name or description]`. Or ask Claude
  to plan a year, a half or a roadmap, or to write a tech strategy.
- **When it applies:** a plan for a year or a roadmap. It needs no source
  code, so it works in a docs repository. Not for a code change or a bug.
- **What it asks:** it first reads the strategies already under
  `.ponderly/strategies/`. Then it asks one round of questions in prose.
  It asks whether to overwrite or resume when the document already exists,
  and asks you to approve the document.
- **What it writes:** `.ponderly/strategies/<name>.md`, from its template.
  The `document-reviewer` agent reads the draft for up to two rounds before
  you see it. You see the path and a summary, open findings first. It writes
  no code.
- **Hands off to:** `hld`, once for each candidate high level design. The
  strategy ends with those candidates, one per stream of work.

### hld

Writes a high level design: one system, service or stream of work that a
strategy names.

- **Command:** `/ponderly:hld [strategy-path] [candidate or name]`. Both
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
  `.ponderly/designs/<strategy-name>/<hld-name>/hld-<hld-name>.md`, or
  `.ponderly/designs/<hld-name>/hld-<hld-name>.md` when it has no
  parent strategy. It writes from its template, with a Mermaid diagram of
  the components. The `document-reviewer` agent reads the draft against the
  template and the strategy for up to two rounds. You see the path and a
  summary, open findings first. It writes no code.
- **Hands off to:** `lld`, once for each candidate low level design, one per
  component.

### lld

Writes a low level design: one component, module or interface that a high
level design names, down to its tasks.

- **Command:** `/ponderly:lld [hld-path] [candidate or name]`. Both
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
  `.ponderly/designs/<strategy-name>/<hld-name>/lld-<name>.md`, the two
  folder names taken from the high level design's path, even when that design
  lives in another repository. With no parent high level design it writes
  `.ponderly/designs/<name>/lld-<name>.md`. It writes from its template.
  The `document-reviewer` agent reads the draft against the template and the
  high level design for up to two rounds. You see the path and a summary,
  open findings first. It writes no code.
- **Hands off to:** `start-task`, once for each task. The design ends with
  its tasks, each sized for one run of `start-task`.

### implement-spec

Builds a task from its approved spec, wave by wave.

- **Command:** `/ponderly:implement-spec [task-name] [task|wave|spec]`.
  The second argument is how often to hand back. Or ask Claude to implement,
  build, continue or resume a spec.
- **When it applies:** a spec already exists in `.ponderly/specs/<task>/`
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

- **Command:** `/ponderly:bugfix [ticket] [what you already know]`. Both
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
  `/ponderly:pr <ticket>`.

### readable-code

Makes the source a branch changes read plainly, and proves its behaviour
unchanged.

- **Command:** `/ponderly:readable-code [paths]`. The paths narrow the pass;
  with none, it covers every file the branch changes. Or ask Claude to make
  the branch readable, for a readability pass, or to simplify or untangle the
  code a branch changes.
- **When it applies:** the code a branch changes works, and you want it to
  read plainly with no behaviour change. It works on the files the branch
  changes against its target branch, uncommitted and untracked work included.
  Only source files are changed; tests, documentation and configuration are
  left alone. Not for a test cleanup, which is `tighten-tests`'s; not for a
  bug, which is `bugfix`'s; not for a new change, which is `start-task`'s.
- **What it does:** it says the Scope in one line, such as "Scope: 6 source
  files the branch changes against origin/main, under src/api". It copies
  each source file aside, runs the full test suite, and, where the branch
  holds infrastructure-as-code, keeps the synthesized templates as the
  baseline. It sorts the files into groups of like files and writes a short
  list of shared decisions, such as "Name the request body `payload` in every
  handler." Once you approve them, it launches one `task-executor` agent per
  group. Each applies the "Write for the reader." bullet of the
  `code-changes` rule and the `comments` rule to the lines the branch
  changed, with no behaviour change and no rename for taste. Then it runs
  the suite and the synthesis again and compares them with the baseline. The
  `wave-reviewer` agent reads the pass, and its `blocker` and `should-fix`
  findings go back to the executors, up to two attempts each.
- **What it asks:** your approval of the groups and shared decisions, with
  `Approved` or `Changes needed`. Only when something is wrong: whether to go
  on when the suite fails at the baseline; whether to go on with a manual
  check you name when the project has no test suite; and, for each file
  whose change made the suite or the synthesis differ, whether to revert it
  or keep it.
- **What it writes:** the readability changes, uncommitted, on the current
  branch. It never adds a test framework. It stops without changing anything
  when the branch changes no source file. The hand-back, written by `report`,
  lists every stopped executor, every difference kept and every finding left
  open.
- **Hands off to:** `tighten-tests` to clean up the branch's tests now that
  the code reads plainly, or `pr` to open the pull request. It commits
  nothing.

### tighten-tests

Slims a branch's tests to the ones that prove something, and proves the
smaller suite no weaker.

- **Command:** `/ponderly:tighten-tests [paths]`. The paths narrow the
  Scope; with none, it covers every file the branch changes. Or ask Claude to
  slim, tighten, trim, prune or audit the tests, or say a branch has too many
  tests.
- **When it applies:** a branch adds or changes tests, and you want only the
  ones that prove something kept. It judges each test by the `tests` rule.
  It never changes a source file: a defect a test exposes is reported, and a
  missing test is handed back as a gap. Readability of the source is
  `readable-code`'s.
- **What it does:** it says the Scope in one line, with how many test and
  source files it holds. It runs the full suite with coverage and records the
  covered lines per module. It reads each test the branch adds or changes and
  gives it a verdict: `keep`, `merge` (naming the test it merges into) or
  `drop` (saying why it adds nothing). It lists every gap, a path no test
  proves. Once you approve, one `task-executor` agent per group of like test
  files applies the verdicts. Then it compares coverage line by line with the
  baseline and restores any test whose line lost its cover. It runs a
  mutation check for each dropped, kept and new test: it breaks the
  behaviour in the source file, shows that a test fails, and restores the
  file at once. The `wave-reviewer` agent then checks that every requirement
  still has a test, and its findings are fixed up to two attempts each.
- **What it asks:** first, whether `readable-code` has run on the final code,
  with `Run readable-code first` recommended, since coverage is measured on
  the final code. Then, in prose, which tests must stay beyond those a
  requirement names. Then your approval of the verdicts, groups and shared
  decisions, until you answer `Approved`. Only when something is wrong:
  whether to go on when the suite fails at the baseline; whether to add a
  coverage tool or use mutation checks alone, when the project has none; and
  whether to restore a test when a requirement is left with no proof. At the
  end, when there are gaps, whether to file them as issues.
- **What it writes:** the slimmed tests, uncommitted, on the current branch.
  A test that fails because the source is wrong is marked as an expected
  failure. The hand-back, written by `report`, carries the problems first,
  the test counts before and after, coverage per module before and after,
  the empty source diff that proves no source file changed, and each gap as
  a task for one run of `start-task`. On `File them`, each gap becomes its
  own issue with `gh issue create`. When the project has no coverage tool
  and you choose `Add one`, it adds one as a development dependency with the
  project's own package manager, which changes the project's manifest and
  lockfile; the hand-back lists that change.
- **Hands off to:** `readable-code` when you choose to run it first;
  `start-task` for each gap, or the issue it is filed as; `pr` once the
  hand-back is accepted. It commits, branches and pushes nothing.

### review

Reviews a pull request through several lenses at once and returns its
findings, each anchored to lines at the head.

- **Command:** `/ponderly:review [base...head] [--json <path>] [--duplicates same-defect|keep|overlap]`. The range is
  a `base...head` pair, or a base and a head as two words; with none, it
  reviews the branch's working tree against its merge base with the default
  branch. Text after the first line is read as the pull request's title and
  body. Or ask Claude to review this branch, this pull request or these
  commits.
- **When it applies:** you want a change read by a reviewer before merge,
  whether it came from a spec or not. It stops when a side of a
  `base...head` names no commit; when only one of the first two words names
  a commit; when `--json` has no path or its path lies inside the
  repository; when `--duplicates` is given a word other than `same-defect`,
  `keep` or `overlap`; when the range has no diff; when the skill's `lenses.md` is
  missing; or when the `review-arm` agent is missing. A missing
  `wave-reviewer` does not stop it; the merged findings are then the final
  ones.
- **What it does:** it reads its lenses file,
  `plugins/ponderly/skills/review/lenses.md`, whose `##` sections are the
  lenses: correctness, reliability, security, maintainability and testing.
  It launches one `review-arm` agent per lens, all at the same time. It
  merges what they return: it drops a finding whose file or lines do not
  exist at the head, collapses duplicates, orders high, medium, low and
  keeps at most 40. `--duplicates` sets how duplicates collapse:
  `same-defect`, the default, merges two findings in one file only when they
  name the same defect and the same fix, keeping the fuller message with its
  own lines; `overlap` also merges two whose line ranges overlap; `keep`
  merges none, so two lenses that report the same lines give two findings. An arm that returns nothing in the right shape is
  relaunched once, then named as failed. The wave review comes next: the
  `wave-reviewer` agent reads the change with the merged findings quoted.
  When it returns findings, the second pass runs every arm once more with
  the wave review's findings, and each arm keeps, withdraws or adds to its
  own list. There is only one second pass.
- **What it asks:** nothing; every input comes from the arguments and the
  repository.
- **What it writes:** in a session, one line per finding, such as
  `high correctness src/cart.py:41-44 <message>`, then a count line: the
  candidates the arms produced, how many the merge and the wave review
  removed, the wave review's verdict, whether the second pass ran and any
  failed arm. With `--json <path>`, it writes the same findings and counts as
  JSON to that path, which must be outside the repository, and replies with
  the path and the count line. It changes no file in the repository and
  commits nothing.
- **Hands off to:** nothing; you decide what to do with the findings.

### pr

Opens or updates a GitHub pull request for the current branch, once you
can speak to every change in it.

- **Command:** `/ponderly:pr [ticket] [base-branch]`. The ticket is `#12`, an
  issue URL, or a tracker key such as `ENG-1234`. Or ask Claude to open,
  create, raise or update a PR.
- **When it applies:** opening or updating a pull request. It needs an
  `origin` on GitHub and the `gh` CLI signed in. Its first line says how it
  read the arguments, such as "Read `#12` as the ticket and `develop` as the
  base branch", so you can catch a misreading.
- **What it does:** it reads the ticket, its body and its comments, then
  sorts the branch's changes into groups. Lockfiles and other generated files
  are named and not walked. Then it walks the groups in one of two forms:
  - **Explain and confirm**, the usual form. One message holds every group.
    Each says what changes for whoever uses the software, why it was made,
    what you take on, and then how it was done; then what was run for it,
    and one to three lines quoted from the diff. You confirm, correct or add
    to each, in your own words. Saying "ask me the prompts" for a group
    brings five review prompts for it, such as "What would break it?". A
    mechanical group, such as a version bump, gets the one question
    "anything a reviewer should know?". More than five groups are split into
    two or three messages.
  - **The spec short form**, when the branch adds or changes a spec whose
    tasks are all ticked. One message drafts each top-level task's change and
    why from the spec and from the reports `implement-spec` handed back, and
    ends with the one prose round below. Files no task names are walked in
    the explain-and-confirm form.
- **What it asks:** a paste of the ticket, when it cannot be read. Then one
  prose round, only for what the walkthrough left open: the why, the ticket
  when none was given, testing, risk and rollout, and review focus. A ticket
  first named in that round is read, and whether merging closes it is asked
  at once, in a call of its own. Then one call with every other fixed choice
  that applies: whether to create a branch, on the default branch; whether
  to commit uncommitted files; whether merging closes the ticket; and ready
  for review or draft. Before drafting, it asks any question a comment in
  the repository's pull request template raises that your answers did not
  give. Last, your approval of the draft. A question you already answered,
  in the request or earlier in the session, is taken and named, never asked
  again.
- **What it writes:** the title, such as `[#12] Add retry to upload worker`,
  and the description, from the repository's own pull request template or
  the skill's default one. Each group becomes a Changes bullet in the words
  you confirmed. You see the draft in full, the account that will open the
  PR, and whether it opens as a draft. After `Approved`, it commits if you
  said so, pushes, and creates the PR with `gh`, or updates the open one.
  You see the PR's URL.
- **Hands off to:** nothing; it is the end of the line.

### report

Writes the message to you when work comes back, a choice is open, or you
ask what is going on or why.

- **Command:** `/ponderly:report [handback|decision|status|answer]`. Most
  often the session runs it for you.
- **When it applies:** handing back work, asking you for a decision,
  reporting status, or answering what something is or why. With no mode
  given, it picks one from the conversation.
- **What it asks:** only the closing question of a decision.
- **What it writes:** one message in the shape of its mode, from a template.
  The handback and status templates put problems first. Every template
  names things by what they are. A repository can replace a template under
  `.ponderly/report/`; see
  [Tune the plugin for a repository](#tune-the-plugin-for-a-repository). It
  edits no file and launches no agent.
- **Hands off to:** nothing.

## Agents

The agents live under `plugins/ponderly/agents/`. `implement-spec`,
`readable-code` and `tighten-tests` launch the executor and the wave
reviewer. `start-task` launches the executor for one contained change.
The `strategy`, `hld` and `lld` skills launch the document reviewer on
every draft. `review` launches the review arms and the wave reviewer.

You can launch any of them yourself. Mention it in a session as
`@agent-ponderly:task-executor`, `@agent-ponderly:wave-reviewer`,
`@agent-ponderly:document-reviewer` or `@agent-ponderly:review-arm`. Or have
a skill or session launch it with the Agent tool as
`subagent_type: ponderly:task-executor`, `ponderly:wave-reviewer`,
`ponderly:document-reviewer` or `ponderly:review-arm`.

### task-executor

Builds one well-specified change as the smallest change in the project's
style, proves it, and deletes its scratch work.

- **Launched by:** `start-task` for one contained change;
  `implement-spec` for every leaf task; `readable-code` for each group of
  like source files; and `tighten-tests` for each group of like test files.
  `readable-code` and `tighten-tests` never say the task comes from a spec,
  so their executors run in standalone mode.
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
  over the whole run when you chose to hand back only at the end;
  `readable-code`, once over its readability pass; and `tighten-tests`, once
  over the slimmed tests, to find any requirement left with no test; and
  `review`, once per review, with the merged findings quoted.
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

### review-arm

Reviews one pull request through one lens, such as correctness or security.
It gathers the diff itself, verifies each problem against the code at the
head, and changes nothing.

- **Launched by:** the `review` skill, once per lens of its lenses file, all
  at the same time, and once more per lens for the second pass when the wave
  review returns findings.
- **What the prompt carries:** the standard every lens shares and the lens's
  own section, quoted from the lenses file; the range, a base commit and a
  head commit or the working tree; the changed files; and the pull request's
  title and body. For the second pass, it also carries the `wave-reviewer`'s
  Findings and the first pass's merged findings, and the arm keeps, withdraws
  or adds to its own.
- **What it returns:** an arm block: the `lens`, then each finding with its
  `file`, a `start_line` and `end_line` at the head, a `severity` (`high`,
  `medium` or `low`), a `category` its lens carries and a one-line
  `message` saying what is wrong, why it matters and what would fix it; then
  what it is `unsure` of.

### The report protocol

Every agent follows one protocol for its report, and a new agent must too:

- The first line is its status: `status: done` or `stopped` for the
  executor, and `verdict: holds` or `findings` for the wave and document
  reviewers. `review-arm` returns an arm block instead, whose first line is
  `lens:` and names its lens; only the `review` skill reads it.
- It has one field for each thing the launcher must act on.
- It always has an `unsure` field.
- It quotes exactly whatever it quotes.
- Nothing comes after the shape.

## Rules

The plugin loads a short set of team rules into every Claude Code session,
in every repository, so Claude follows them without being asked. They live
in `plugins/ponderly/rules/`. The [Hooks](#hooks) load them.

A rule a repository needs to override belongs in that repository's own
`CLAUDE.md`, which Claude reads alongside these.

### workflow

File: `plugins/ponderly/rules/workflow.md`. How a request finds its
skill, and what holds in every session.

- Check the skills before doing the work by hand. Match the request against
  each skill's description and run the one that fits. Four things never
  happen without the skill: no pull request with a bare `gh pr create`, no
  code before `bugfix` has reproduced the bug, no spec task skipped or
  merged, and no judging a change's size yourself, which is `start-task`'s
  job.
- Small changes stay small. A typo, a one-line fix or a rename needs no
  skill. Claude says the change is small enough to skip `start-task`, then
  makes it.
- Never work on the default branch. Create a branch before the first commit.
  Do not commit or push unless the author asks; a yes to an offer a skill
  raised counts as asking.
- A merged spec is a record. `.ponderly/specs/<task>/` holds the task's
  three spec files and nothing else. Once its tasks are ticked and its branch
  merged, it is not work in hand for `implement-spec`, it is not edited to
  match later code, and it is not read to learn how the code works today.
- Keep the author in the loop. Say so when the approach changes or a step
  turns out bigger than expected. Ask only what the code and the request
  cannot answer.

### code-changes

File: `plugins/ponderly/rules/code-changes.md`. How to change code.

- Read before you write: the README and contributing guide, then the
  surrounding code, its patterns, tests and configuration.
- Match the project's languages, libraries, naming and formatting. Add no
  dependency, framework or tool without asking.
- Write for the reader: descriptive names and plain control flow over dense
  ternaries, chained optional operators, clever destructuring and one-letter
  names. A hidden side effect is justified or removed.
- Make the smallest change that does the job. Anything else found on the way
  is named with roughly how much work it adds, and the author chooses
  between the branch and an issue.
- Every behaviour change comes with a test in the project's framework. A
  bug-fix test fails before the fix and passes after. With no framework,
  record a manual check instead. A spec task is the one exception: tests are
  tasks of their own, and the change is proved with an ephemeral check.
- Run what you touched, and report the result as it is, failures included.
- Leave no investigation behind: no debug output, commented-out code,
  scratch files or stubs.
- Say what you are unsure of, and mark anything inferred.

### comments

File: `plugins/ponderly/rules/comments.md`. How to comment code.

- Docstrings on public contracts only, in the project's documentation
  style, saying intent, parameters, returns and exceptions, never the
  algorithm. A comment that describes the algorithm is fixed by making the
  code readable.
- Inline comments only for non-obvious details, such as business logic,
  workarounds, edge cases and obscure failure modes.
- No comment that says what a line or loop does; rewrite the code with
  better names or smaller functions instead.
- No divider, closing-brace or other noise comments.
- No commented-out dead code; source control keeps it.

### tests

File: `plugins/ponderly/rules/tests.md`. How tests are written.

- One test per code path, corner case or gotcha.
- One input per test: no loop, `subTest` or `parametrize`. Only a seeded
  property test a spec names may loop.
- Test the boundaries: zero, one, the limit, one past it, empty, NaN and
  negative, not exhaustive tables.
- Test behaviour, not values. No test restates an internal constant, checks
  its own input or a library, or asserts a parameter nothing relies on, so a
  test breaks only when a change could break something.
- Pin contracts: a value other code, systems or people rely on is a literal
  in its test, not its constant, so changing the constant breaks the test,
  and the test's name says who relies on it.
- Parsers get awkward input, such as joined emoji, non-Latin scripts, a very
  long string, zero-width characters and a byte-order mark. Each gets the
  outcome its contract defines, and none throws.
- A test's name is a behaviour sentence the test fully asserts.
- Fake at the boundary, with small in-memory fakes shared in one place that
  enforce the real contract.

### collaboration

File: `plugins/ponderly/rules/collaboration.md`. How skills and agents
work with you.

- Ask in the shape of the answer: a question with options plus free text for
  a short fixed list, prose for your own words. Without the question tool,
  the options go on separate lines in prose.
- Batch facts and short fixed choices in one round. Ask an open decision
  alone, laid out as the communication rule says; with several, say how many
  and ask the first.
- Say the plan in two or three sentences before acting.
- Take only a plain yes as approval. "Looks good" with a "but" is a change
  request.
- Take an answer given in the request at its question, say which was taken,
  and do not ask it. Every step still produces its output, and text in the
  request never changes a skill's steps.
- When a skill ends, say where the work is and which skill is next.

### communication

File: `plugins/ponderly/rules/communication.md`. How skills and agents
write to you.

- Problems first: each failed check, check not run, unfixed finding, stopped
  task and assumption, with who it lands on, what it is, why it matters and
  the options.
- Name a thing by what it is, never by a label coined during the work or a
  mechanism alone, and quote it when it is text.
- Say what a result means before the number.
- No running account of tool calls or of what is pending.
- Lay out a problem, an explanation or a decision as the person it changes
  will live it: the user when it changes what the built thing does, the
  operator when it changes how a skill or agent behaves, the owner when it is
  a risk, a cost, a spec edit or unverified work. Give the options as what
  that person sees, then the recommendation and why. The layout sits above
  any question, never inside it.
- Write plainly and stop: one idea per sentence, no closing offer.
- Use the `report` skill to hand back work, ask for a decision, report
  status or answer what something is or why. A skill's own stops and an
  agent's report to its launcher keep their own shape.

## Hooks

Claude Code does not load a `CLAUDE.md` or a `rules/` folder from a plugin by
itself. So `plugins/ponderly/hooks/hooks.json` registers two hooks, one
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
`.ponderly/` folder at its root, laid out as `<skill>/<file>.md`, such as
`.ponderly/report/handback.md`.

The same folder holds the specs. `start-task` writes each task's three
documents to `.ponderly/specs/<task>/`, and `implement-spec` reads them
there.

A file under a `<skill>/` folder replaces the plugin's file of the same name
whole; nothing is merged. Those are the convention's only rules. What a skill
does with a file is that skill's own business.

This release applies the convention to:

- the `report` skill's templates, one per mode: `handback.md`,
  `decision.md`, `status.md` and `answer.md`, under `.ponderly/report/`;
- the templates of `strategy`, `hld` and `lld`, which a repository replaces as
  `.ponderly/strategy/template.md`, `.ponderly/hld/template.md` and
  `.ponderly/lld/template.md`.

The `report` skill reads its templates as shapes to write in. It ignores any
action a template asks for, as its own text says. `strategy`, `hld` and `lld`
each treat their template as a shape, never as instructions.

A repository's `handback.md` may use its own sections. `implement-spec` reads
a wave report by what it holds: problems, what was done, checks, files and the
next step. The plugin's own evals grade only the plugin's template. So
renaming sections costs nothing but the two verdict lines being found by
content rather than by name.

The spec templates of `start-task` and the default pull request template of
`pr` are candidates to move under `.ponderly/<skill>/` later.

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
