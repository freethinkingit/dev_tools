# Requirements Document

## Introduction

`start-task` is the handbook's front door for a piece of work, but today it has one exit: three approved spec documents. The only other route is the workflow rule's bullet that lets a typo, a one-line fix or a rename skip the skill, and that decision is made outside the skill, by whoever reads the rule. Work in the middle, one contained change that is too big to just type but too small to design, gets a full spec it does not need, while the `task-executor` agent, which was built for exactly that size of work, is reachable only from `implement-spec`. This change makes `start-task` triage the request after it has read the codebase: a bug goes to `bugfix`, a single contained change goes to `task-executor`, and only work that needs design goes on to the spec. The engineer starts every piece of work the same way and is asked, not told, when the skill reaches a sizing call. The workflow rule changes to match, and the plugin version moves to 0.6.0.

## Glossary

- **Skill**: The `start-task` skill described by this document, run as `/freethinking:start-task`.
- **Author**: The engineer whose session runs the Skill and who is accountable for the resulting code.
- **Request**: The work as the Author gave it: the Skill's argument and the Author's surrounding message.
- **Triage**: The Skill's judgement, made after reading the codebase and before writing any document, of which Route the Request takes.
- **Route**: One of the three outcomes of Triage: Bug_Route, Executor_Route or Spec_Route.
- **Bug_Route**: The Route for a Request that describes a defect: observed behaviour that differs from intended behaviour in code that already exists.
- **Executor_Route**: The Route for a Contained_Change: the Skill launches the Executor in Standalone_Mode with the Request and reports its Summary.
- **Spec_Route**: The Route for every other Request: the Skill writes the three spec documents as it does today.
- **Contained_Change**: A Request that is one change, describable in a sentence or two, touching a place in the code the Skill can name after reading the codebase, needing no design decision and no new dependency, framework or tool.
- **Executor**: The `task-executor` plugin agent, addressed as `freethinking:task-executor`.
- **Standalone_Mode**: The Executor's behaviour when its launch prompt does not say the task comes from a spec: the change comes with its test.
- **Summary**: The fixed-shape report the Executor returns: status, files changed, checks run, ephemeral check, things unsure of, and a reason when stopped.
- **Question**: A question the Skill puts to the Author with the AskUserQuestion tool, offering a fixed set of answers plus the Author's own text.
- **Rule**: The handbook workflow rule in `rules/workflow.md`, printed into every session by the plugin's hooks.
- **Collaboration_Rule**: A new handbook rule in `rules/collaboration.md` that sets the defaults for how any skill or agent works with the Author: how it asks, when it batches, when it says its plan, what approval means, how it reports and how it hands off.
- **CX_Block**: A short section near the top of a skill that lists the skill's stops for the Author and states where it departs from the Collaboration_Rule.
- **Eval_Case**: A case under `evals/` that runs the plugin against a prompt and grades the transcript, run by hand with `make eval-*`.

## Requirements

### Requirement 1: Triage every Request

**User Story:** As an Author, I want to start every piece of work with the same skill and have it decide how big the work is, so that I do not sort work myself and small work does not get a spec it does not need.

#### Acceptance Criteria

1. WHEN the Skill has read the parts of the codebase the Request touches, THE Skill SHALL perform Triage before asking the Author any of the spec questions and before writing any document.
2. THE Skill SHALL choose Bug_Route WHEN the Request describes a defect, Executor_Route WHEN the Request is a Contained_Change, and Spec_Route otherwise.
3. THE Skill SHALL state its chosen Route and the reason for it, in two or three sentences that name the code it read, before acting on it.
4. WHEN the Route is Bug_Route or Executor_Route, THE Skill SHALL put a Question to the Author offering that Route, Spec_Route and a free-text answer, and SHALL act only on the Author's answer.
5. WHEN the Route is Spec_Route, THE Skill SHALL say so in one sentence and continue to the spec questions without a Question, since that is today's behaviour.
6. IF the Author's answer to the Question changes the Route, THEN THE Skill SHALL take the Route the Author chose without arguing for its own.
7. WHEN a spec for the Request already exists in `.claude/specs/<task-name>/`, THE Skill SHALL take Spec_Route and resume at the first unapproved document, without Triage, since the sizing decision was already made.
8. THE Skill SHALL open with a CX_Block, placed after its ground rules, that lists every point at which it stops for the Author (the Question at Triage, then approval of each document), says that each stop asks with the AskUserQuestion tool except where the answer is the Author's own words, says what each hand-back contains, and names the skills it hands off to.
9. THE CX_Block SHALL state only what is specific to the Skill or departs from the Collaboration_Rule, and SHALL NOT restate the Collaboration_Rule.
10. WHEN the Skill derives the task name, THE Skill SHALL propose a branch name in the contributing guide's shape, the issue number and the task name when the Request names or links an issue and the task name alone otherwise, and SHALL NOT create the branch.

### Requirement 2: Bug_Route

**User Story:** As an Author, I want a bug I bring to `start-task` to be handled the bug way, so that it gets reproduced before it is fixed rather than specified.

#### Acceptance Criteria

1. WHEN the Author accepts Bug_Route, THE Skill SHALL invoke the `bugfix` skill with the Request as its argument and SHALL do nothing else.
2. THE Skill SHALL NOT reproduce, diagnose or fix the defect itself.

### Requirement 3: Executor_Route

**User Story:** As an Author, I want a contained change built by the executor straight away, so that the handbook's disciplined executor does the work without a spec in between.

#### Acceptance Criteria

1. WHEN the Author accepts Executor_Route, THE Skill SHALL launch the Executor once with the Agent tool as `subagent_type: freethinking:task-executor`.
2. THE launch prompt SHALL hold the Request in the Author's words, the files and code the Skill found that the change touches, and anything the Author added in the Question's free text, and SHALL NOT say the task comes from a spec, so that the Executor is in Standalone_Mode.
3. THE Skill SHALL NOT edit, create or delete any source file itself on Executor_Route.
4. WHEN the Executor returns a Summary with status `done`, THE Skill SHALL show the Author the Summary and the diff of the files it names, and SHALL recommend opening a pull request with the `pr` skill.
5. WHEN the Executor returns a Summary with status `stopped`, THE Skill SHALL show the Author the Summary and put a Question offering to answer the Executor's question and relaunch, or to take Spec_Route, and SHALL NOT relaunch unprompted.
6. IF the Executor's Summary reports a check that failed, THEN THE Skill SHALL say so plainly before recommending anything.
7. THE Skill SHALL NOT commit, push or create a branch on Executor_Route.

### Requirement 4: The Rule sends all work through the Skill

**User Story:** As an Author, I want the workflow rule to agree with the skill, so that Claude reaches for `start-task` first and does not sort work by size on its own.

#### Acceptance Criteria

1. THE Rule SHALL direct Claude to run `/freethinking:start-task` for any request to change code that no other bullet of the Rule names, and SHALL say that the skill reads the code and decides between the executor, `bugfix` and a spec.
5. THE Rule SHALL NOT ask Claude to judge the size of a request beyond the trivial cases of criterion 3; every other bullet SHALL route on what the Author said or on a file that exists.
6. THE Rule SHALL say that the first bullet that matches the request is the route, so that a request matching two bullets has one answer.
2. THE Rule SHALL keep direct routes to `/freethinking:bugfix` for a request the Author names as a bug, to `/freethinking:implement-spec` when a `tasks.md` exists, and to `/freethinking:pr` for a pull request.
3. THE Rule SHALL keep the "small changes stay small" bullet for a typo, a one-line fix or a rename, so that trivial work still needs no skill.
4. THE combined text of `rules/*.md` SHALL stay under 10,000 characters, since Claude Code truncates hook output past that.

### Requirement 5: Documentation, version and evals

**User Story:** As a contributor, I want the README, the version and the evals to describe the skill that now ships, so that the plugin stays honest about what it does.

#### Acceptance Criteria

1. THE README's row for `start-task` and its row for `rules/workflow.md` SHALL describe Triage and its three Routes in the voice of the other rows.
2. THE plugin version in `.claude-plugin/plugin.json` SHALL be `0.6.0`.
3. THE plugin SHALL include an Eval_Case under `evals/skills/start-task/` whose prompt is a Contained_Change against a fixture, and which passes when the transcript shows the Skill stating Executor_Route, asking the Question, and writing no spec document before the answer.
4. THE plugin SHALL include an Eval_Case under `evals/skills/start-task/` whose prompt is a defect, and which passes when the transcript shows the Skill stating Bug_Route and asking the Question without reproducing or fixing anything.
5. THE existing Eval_Case `evals/skills/start-task/names-task-and-asks` SHALL still pass, with its prompt sized so that Triage chooses Spec_Route.
6. THE existing Eval_Cases under `evals/rules/workflow/` SHALL still pass after the Rule changes, with their prompts or graders adjusted only where the Rule's new wording requires it.
7. THE `make validate` target SHALL pass.

### Requirement 6: The Collaboration_Rule

**User Story:** As an Author, I want every skill and agent to work with me the same way by default, so that I know how I will be asked, when I will be stopped and what I will be shown, whichever skill is running.

#### Acceptance Criteria

1. THE plugin SHALL ship `rules/collaboration.md`, loaded by the same hooks as the other rules, so that it reaches every session and every sub-agent.
2. THE Collaboration_Rule SHALL say to ask with the AskUserQuestion tool when the answers are a short fixed list, offering the options plus free text, and to ask in prose when the answer is the Author's own words.
3. THE Collaboration_Rule SHALL say to batch questions into one round unless an answer decides the next question, in which case to ask one at a time.
4. THE Collaboration_Rule SHALL say to state the plan in two or three sentences before acting on it.
5. THE Collaboration_Rule SHALL say that approval is explicit and that "looks good" with a "but" is a change request.
6. THE Collaboration_Rule SHALL say to report failures and anything not run before any recommendation.
7. THE Collaboration_Rule SHALL say that a skill which ends hands off by naming where the work is and which skill is next.
8. THE Collaboration_Rule SHALL be under 1,600 characters, and the combined text of `rules/*.md` SHALL stay under 10,000 characters.
9. THE README's rules table SHALL gain a row for `rules/collaboration.md` in the voice of the other rows.
10. THE plugin SHALL include an Eval_Case under `evals/rules/collaboration/` whose prompt leads to a short-list question, and which passes when the transcript shows the question asked with the AskUserQuestion tool or, where the eval runs without that tool, in prose that offers the same fixed options.
11. THE `implement-spec`, `bugfix` and `pr` skills SHALL NOT change in this task; their CX_Blocks are issues #16, #17 and #18.
