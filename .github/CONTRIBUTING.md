# Contributing

This repository is a Claude Code plugin: shared skills, agents and rules for a
software team; its hooks put the rules in every session's context. This guide
says how to set up, test and submit a change, and how the repository uses
issues, labels, milestones and discussions.

The plugin is under the [MIT License](../LICENSE). Taking part means following
the [Code of Conduct](CODE_OF_CONDUCT.md). Report a vulnerability as the
[security policy](SECURITY.md) says, never in a public issue.

## Set up

Clone the repository and work from its root:

```bash
claude --plugin-dir .      # load your working copy for one session
make validate              # the unit tests and the validators; CI runs this on every PR
```

## Test

The free checks are `make validate`: the unit tests under `checks/`, then the
two validators. They make no model call.

Evals run by component with `make eval-<kind>-<name>`, such as
`make eval-skill-pr`, and `make eval-hook` for the hooks. Every case is a model
call on your own Claude seat, so evals run by hand, never in CI. Paste the
table the command prints into the Testing section of your pull request.

A change to a skill, agent, rule or hook comes with an eval case or a change to
one. A new skill comes with at least one case under `evals/skills/<name>/`. A
change that touches no skill, agent, rule or hook needs no eval, and
`make validate` is the whole check.

For how the checks and evals work, see the README's
[Testing](../README.md#testing) section and
[`evals/README.md`](../evals/README.md).

## Make a change

A small change, such as a typo, a one-line fix or a rename: make it. A bug:
run `/freethinking:bugfix`. Anything else: run `/freethinking:start-task`. It
reads the code and decides between the `task-executor` agent for one contained
change, `bugfix` for a defect, and a spec for the rest, and asks before taking
the first two. When it writes a spec, `/freethinking:implement-spec` builds it.
On every route, `start-task` proposes the branch name, and you or
`implement-spec` create it.

Work on a branch named `<issue number>-<short slug>` when an issue exists, such
as `12-ticket-reference`, and on a short slug otherwise. Never work on the
default branch. The Create a branch link under Development on an issue page
gives that shape. When `/freethinking:implement-spec` proposes the task name as
the branch, answer with the issue number in front.

Open the pull request with `/freethinking:pr` and give the issue number as the
ticket. The [pull request template](pull_request_template.md) is the one place
that says how the issue is linked and when to write `Closes #<number>`.

A new skill, agent, rule or hook is also added to the `component` dropdown of
the "Report a misbehaving skill or agent", "Propose a new or changed skill,
agent or rule" and "Propose an eval case" forms.

## Issues

New issues start from one of three forms:

- **Report a misbehaving skill or agent**, for something the plugin did wrong.
- **Propose a new or changed skill, agent or rule**, for something it should
  do.
- **Propose an eval case**, for a behaviour an eval should guard.

Submitting a form labels the issue `triage` and sets its Issue_Type: `Bug`,
`Feature` and `Task` respectively. Blank issues are off. The new-issue page
also links questions to Discussions Q&A, ideas to Discussions Ideas, and
vulnerabilities to the security policy page.

At least weekly, a maintainer triages:

1. Reviews every issue labelled `triage`.
2. Confirms or corrects its Issue_Type.
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

Every issue has one Issue_Type, `Bug`, `Feature` or `Task`, which says what
sort of thing it is. Labels are lowercase, and there are nine:

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
   the list: `$ARGUMENTS` and `${CLAUDE_PLUGIN_ROOT}` in skills, the hooks that
   load the rules, and the agents' frontmatter.

The list grows from issues labelled `compatibility`.

## Settings, not files

Labels, milestones, Discussions and Issue_Types are repository or organization
settings, not files, so they do not travel with the tree. A fork or a copy of
this repository does not carry them.
