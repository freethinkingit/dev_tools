# The evidence

This page says why the plugin was built, how it is tested, and what the tests
found when Claude Code ran with the plugin and without it. It also says what
has not been measured, and links a real spec the plugin wrote.

## Why it was built

In the author's words:

> I built this to avoid constantly re-prompting, or having to switch between Kiro and Claude. At Amazon I spent time developing tools that wrote code like this before Claude was even available internally. These became industry standard, and I've kept making small refinements to them in areas where I've seen even Kiro fail.

## How it is tested

There are two kinds of test: free checks and evals.

The free checks make no model call, so they cost nothing. Run them with:

```bash
make validate
```

This runs the Python unit tests under `checks/`, which use only the standard
library. They check things a person could get wrong by hand: every skill's and
agent's frontmatter parses, every eval case is well formed, the rules stay
within their size limit, and the hook's JSON encoder works. Then it runs
`claude plugin validate --strict` on the marketplace, the plugin and its
skills. CI runs `make validate` on every pull request.

The evals run Claude on a written task and grade what it did. Each case is a
folder under `evals/` with a prompt and a set of graders. A grader checks one
thing: a pattern in Claude's last message, in a file or in the whole session
transcript; a file that exists or does not; or a tool Claude called or did not
call. A few cases also have a grader that asks a model to judge the reply
against a written pass and fail criterion. Every case is a real model
call on your own Claude seat, so evals run by hand and never in CI. There is
one target per component:

```bash
make help                        # list the targets that exist
make eval-skill-<name>           # the cases under evals/skills/<name>/
make eval-rule-<name>            # the cases under evals/rules/<name>/
make eval-agent-<name>           # the cases under evals/agents/<name>/
make eval-hook                   # the cases under evals/hook/
```

A plain target runs each case with the plugin loaded. That answers "does this
skill do its job". It does not answer "would Claude do this anyway". For that,
add `EVAL_ARGS="--ablation with-without"`: each case then also runs in plain
Claude Code without the plugin, and the table gains a column for each arm and
the difference. That doubles the cost, so raise the cost ceiling with
`EVAL_MAX_COST_USD`. [`evals/README.md`](../evals/README.md) has the rest.

## Results against Claude Code without the plugin

These are the four rule targets, each run with and without the plugin. The
with-plugin arm loads the whole plugin, every rule, skill, agent and hook, not
only the one rule. So each Δ compares the whole plugin with plain Claude Code,
on cases written for that rule.

How to read the tables:

- **WITH** is the case's score with the plugin loaded.
- **W/OUT** is its score in plain Claude Code, without the plugin.
- **Δ** is WITH minus W/OUT. A positive Δ means the plugin made Claude pass
  more of the case's graders.
- A score runs from 0 to 1. It is the share of the case's scored graders that
  passed, averaged over three runs. Some graders are left out of the score:
  the workflow table below says which, so its figures can be rebuilt.
- **RUNS** counts the runs of both arms, three each.
- **COST** is the list-price estimate for both arms. **NOTES** names a grader
  that failed in a run with the plugin loaded.

Each table is copied as the command printed it. They are snapshots of three
runs per arm on one day, not a benchmark. A different day or a different model
version can move them.

All four ran on 2026-10-22, on plugin version 0.17.0 from the working tree of
the branch that added this page, before that version was released.

### collaboration: 2026-10-22, plugin 0.17.0

Command: `make eval-rule-collaboration EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=10`

```
CASE                       WITH  W/OUT Δ      RUNS COST    NOTES
short-list-asks-with-tool  0.94  0.50  +0.44  6    $0.49   does-not-choose: pattern found (expected absent)

1 case(s) · mean Δ +0.44 · 42s · $0.49
```

The case asks Claude to set a log level from three allowed values without
saying which. It passes when Claude asks which one, lists the three options on
their own lines, and does not pick one or create the file. Every grader looks
at Claude's message or the files, so plain Claude could pass it too. This is a
clean comparison. Without the plugin, Claude more often chose a level itself or
asked without listing the options.

### communication: 2026-10-22, plugin 0.17.0

Command: `make eval-rule-communication EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=10`

```
CASE                      WITH  W/OUT Δ      RUNS COST    NOTES
check-not-run             1.00  1.00  0.00   6    $0.86   
failing-check-first       1.00  1.00  0.00   6    $0.77   
incidental-failure-first  1.00  1.00  0.00   6    $0.84   
incidental-not-run-first  1.00  1.00  0.00   6    $0.87   

4 case(s) · mean Δ 0.00 · 375s · $3.33
```

The cases check that Claude's final message opens with a failed test or a test
it could not run, before anything else, and does not narrate its steps. Two of
them make the problem incidental to the request, where it is easiest to bury.
Every grader looks at Claude's message or the files, so this is a clean
comparison. Plain Claude did the same as Claude with the plugin on all four
cases. On these cases the communication rule made no measurable difference.

### code-changes: 2026-10-22, plugin 0.17.0

Command: `make eval-rule-code-changes EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=10`

```
CASE                      WITH  W/OUT Δ      RUNS COST    NOTES
no-new-dependency         1.00  1.00  0.00   6    $1.19   
reads-contributing-guide  0.83  0.50  +0.33  6    $0.68   lists-subtract-in-readme: pattern not found in file README.md
smallest-change           1.00  0.75  +0.25  6    $0.67   
test-with-change          1.00  0.50  +0.50  6    $0.57   

4 case(s) · mean Δ +0.27 · 430s · $3.11
```

The cases run on a small Python project. `no-new-dependency` asks for retry
logic and checks that no retry library is added. `reads-contributing-guide`
asks for a new function and checks that it is also listed in the README, as
the project's contributing guide asks. `smallest-change` asks for a one-line
bug fix and checks that the fix is made, that the nearby typo and unused import
are left alone, and that Claude names the existing test that guards it.
`test-with-change` asks for a new function and checks that a test for it is
added. Every grader looks at the files or Claude's message, so this is a clean
comparison. Plain Claude also added no dependency. It did not list the new
function in the README, did not name the guarding test, and did not add a test.

### workflow: 2026-10-22, plugin 0.17.0

Command: `make eval-rule-workflow EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=10`

```
CASE                           WITH  W/OUT Δ      RUNS COST    NOTES
bug-routes-to-bugfix           1.00  0.60  +0.40  6    $0.87   
closed-spec-is-a-record        1.00  0.50  +0.50  6    $0.99   
feature-routes-to-start-task   1.00  0.00  +1.00  6    $0.92   
pr-routes-to-pr-skill          1.00  1.00  0.00   6    $0.81   
small-change-skips-spec        1.00  1.00  0.00   6    $0.78   
spec-routes-to-implement-spec  1.00  0.00  +1.00  6    $0.99   

6 case(s) · mean Δ +0.48 · 446s · $5.37
```

These cases check that a request reaches the right skill: a bug goes to
`bugfix`, a feature to `start-task`, a pull request to `pr`, work on a spec to
`implement-spec`, a typo fix to no skill, and a request near a merged spec not
to `implement-spec`. This is where the skill descriptions show, since Claude
picks a skill by its description.

This table is not a clean comparison, and the Δ overstates what the rule does
on its own. Most of these graders check for a call to one of the plugin's
skills, and without the plugin those skills do not exist. A grader that checks
for a skill call is scored in both arms when it is the case's only grader. When
the case has other graders it is left out of the score in both arms, so the
WITH score does not say whether the skill was called either. Case by case:

- `feature-routes-to-start-task` and `spec-routes-to-implement-spec` have one
  grader each, a call to the plugin's skill. Plain Claude cannot make that
  call, so W/OUT 0.00 measures that the skill exists, not how Claude behaves.
- `pr-routes-to-pr-skill`: the call to the `pr` skill is left out of the
  score in both arms. Both scores come from the one other grader, which checks
  that no shell permission error appears in the transcript. Routing is not
  compared, and WITH 1.00 does not include whether `pr` was called.
- `closed-spec-is-a-record`: the call to `start-task` is left out of the score
  in both arms. Of the two graders scored, one checks that `implement-spec` is
  not called, which plain Claude passes because the skill does not exist. The
  other looks for route names that only `start-task` writes. The W/OUT 0.50 is
  not a measure of the rule.
- `small-change-skips-spec` checks that no skill is called. Plain Claude
  passes because it has no skills to call, so W/OUT 1.00 compares nothing.
- `bug-routes-to-bugfix`: the call to `bugfix` is left out of the score in
  both arms. Five graders are scored. Plain Claude passed three of them in
  every run, which is the W/OUT 0.60:
  - `no-fix-claimed`: Claude's last message claims no fix. Plain Claude
    passed.
  - `not-start-task`: Claude does not call `start-task`. Plain Claude passed
    trivially, because the skill does not exist without the plugin.
  - `skill-loads`: no shell permission error appears in the transcript. Plain
    Claude passed.
  - `says-reproduce-first`: Claude's last message says it will reproduce the
    bug. Plain Claude failed.
  - `states-symptom`: the word "symptom" appears anywhere in the session
    transcript, not only in Claude's message. Plain Claude failed. With the
    plugin, the match is likely Claude's own words rather than the loaded
    skill's text, but this run kept no transcripts to confirm it.

  Only `no-fix-claimed` and `says-reproduce-first` are fair comparisons of
  how Claude behaves.

## Not measured

The components below have no result against Claude Code without the plugin.
This page makes no comparison for them. All but the `comments` rule have eval
cases that run with the plugin loaded, which check that the component does its
job.

The skills: `bugfix`, `hld`, `implement-spec`, `lld`, `pr`, `report`,
`start-task` and `strategy`. Their targets are `make eval-skill-<name>`.
Without the plugin the skill does not exist, and their graders check for what
the skill does and writes.

The agents: `document-reviewer`, `task-executor` and `wave-reviewer`. Their
targets are `make eval-agent-<name>`. Without the plugin the agent does not
exist, and their graders check for what the agent does and reports.

The hooks: the two cases under `evals/hook/`, run by `make eval-hook`. They
check that the plugin's hooks load the rules into a session and into a
sub-agent. Without the plugin there is no hook and no rule, and their graders
check for the rules' headings.

The `comments` rule. It has no eval cases yet, with the plugin or without.

## A real example

[`.freethinking/specs/design-skills/`](../.freethinking/specs/design-skills/)
is the spec for the `strategy`, `hld` and `lld` skills and the
`document-reviewer` agent, merged in pull request #53. `start-task` wrote its
requirements, design and tasks, and `implement-spec` built it task by task.
It is a record of that work; the plugin's current behaviour is in its code and
the [Reference](reference.md).
