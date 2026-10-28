# Requirements Document

## Introduction

The workflow rule is read into every Claude Code session by the handbook's SessionStart hook, skill or no skill. Today its route bullets also describe what each skill does once it is running, and those descriptions go stale when a skill changes: the pull request bullet still says the pr skill drafts "to the team template" after the skill learned to prefer the repository's own. This change makes the rules routing plus what no skill can cover, and nothing else: one route bullet says that the skills exist, that each skill's own description says when it applies, and that a session checks them before doing the work itself, keeping the guards a session needs when tempted to skip a skill; the triggers and behaviour the route bullets used to restate are owned by the skills' descriptions and text and proven by their evals; and two standing rules the skills cannot hold, that a merged spec is a closed record and that a discovery outside the work is the author's call, are added where they belong. It serves everyone the handbook applies to, by making the rules short enough to stay true and the skills the single place a behaviour is written. GitHub issues #6, #7 and #15 are the tickets.

## Glossary

- **Rule**: One file under `rules/`, printed into every session by the SessionStart hook.
- **Workflow_Rule**: The Rule at `rules/workflow.md`, which says which skill to reach for and when.
- **Code_Changes_Rule**: The Rule at `rules/code-changes.md`, which says how code is changed in any repository.
- **Route_Bullet**: A bullet of the Workflow_Rule that sends a request to a Skill: today the five bullets after "The first bullet that matches the request is the route."
- **Trigger**: The condition in a Route_Bullet that makes it match a request, such as the author calling the request a bug.
- **Skill_Description**: The `description` in a Skill's frontmatter, which Claude Code loads into every session and which says when the Skill applies.
- **Guard**: A sentence in a Route_Bullet that stops a session from doing the Skill's work without the Skill, such as "Do not open a PR with a bare `gh pr create`."
- **Skill_Narration**: A sentence in a Route_Bullet that says what a Skill does once it is running, such as "It walks the changes with the author."
- **Standing_Rule**: A bullet of the Workflow_Rule that is not a Route_Bullet and applies in every session, such as "Never work on the default branch."
- **Skill**: A skill under `skills/` or an agent under `agents/` of the handbook plugin.
- **Offer**: A question a Skill puts to the author proposing an action the Skill will take on a yes, such as the pr skill's branch and commit offers.
- **Spec_Folder**: The directory `.claude/specs/<task>/` holding a task's `requirements.md`, `design.md` and `tasks.md`.
- **Closed_Spec**: A Spec_Folder whose non-optional tasks are all ticked and whose branch has merged.
- **Discovery**: A problem or improvement found while working that is outside the work in hand: outside the spec's requirements, design and tasks, or outside the change asked for.
- **Hand_Back**: The report the implement-spec Skill writes when it returns control to the author at the end of a task or a wave.
- **Hook_Limit**: The 10,000-character ceiling on the SessionStart hook's output, enforced by `checks/test_rules_size.py`.
- **Eval_Case**: A folder under `evals/` with a `prompt.md` and graders, run by hand with `make eval-…`.
- **Target_Evals**: The Eval_Cases of one component, selected by its `make eval-skill-<name>` or `make eval-rule-<name>` target.
- **System**: The handbook plugin: its Rules, Skills, README and Eval_Cases.

## Requirements

### Requirement 1: One route bullet, pointing at the skills

**User Story:** As an author whose sessions load the Workflow_Rule, I want the rule to say that the Skills exist and that their Skill_Descriptions say when each applies, instead of restating those descriptions bullet by bullet, so that the rule cannot go stale when a Skill changes and does not duplicate what every session already has loaded.

#### Acceptance Criteria

1. THE Workflow_Rule SHALL route with one Route_Bullet, which says that the handbook ships a Skill for each common kind of work, that each Skill_Description says when its Skill applies, and that a session matches the request against the Skill_Descriptions and runs the Skill that fits before doing the work itself.
2. THE Route_Bullet SHALL carry the Guards of today's five bullets: no pull request with a bare `gh pr create`, no code before the bugfix Skill has reproduced the bug, no spec task skipped or merged, and no judging a change's size yourself.
3. THE System SHALL remove from the Workflow_Rule every Skill_Narration and every Trigger that restates a Skill_Description.
4. IF a sentence being removed has no counterpart in its Skill's text or Skill_Description, THEN THE System SHALL add that sentence to the Skill, so no behaviour is lost by the trim.
5. THE Workflow_Rule SHALL keep the small-change bullet, that a typo, a one-line fix or a rename needs no Skill, and one sentence after the Route_Bullet introducing the Standing_Rules.
6. WHEN the start-task Skill_Description refers to the Workflow_Rule for the requests it does not take, THE System SHALL make that Skill_Description name them itself: a named bug, an existing spec, a pull request and a typo-sized change.
7. IF the Target_Evals of the workflow rule score lower on the case that routes a feature to start-task after the change than at their baseline, THEN THE System SHALL restore one explicit bullet routing any other code change to start-task, and SHALL restore nothing else.

### Requirement 2: The pull request bullet and the author's yes

**User Story:** As a reader of the Workflow_Rule alone, I want the pull request bullet and the default-branch rule to agree with the pr skill, so that the rule neither claims which template wins nor reads as forbidding the commit the skill makes on my yes. This is GitHub issue #7.

#### Acceptance Criteria

1. THE Workflow_Rule SHALL keep the Guard against a bare `gh pr create` and SHALL say nothing about which template the pull request description follows.
2. THE Standing_Rule "Never work on the default branch" SHALL say that a yes to an Offer a Skill raised counts as the author asking, in one sentence, so that "Do not commit or push unless the author asks" and the pr skill's commit Offer do not contradict.
3. THE pr Skill SHALL still state its own template precedence: the repository's `.github/pull_request_template.md` first, its sections and comments taking precedence, and the skill's default template otherwise.

### Requirement 3: A merged spec is a record

**User Story:** As an author, I want the Workflow_Rule to say that a Spec_Folder holds specs only and that a Closed_Spec is a record, so that no session reads a Closed_Spec to learn how the code works today, drops scratch files into a Spec_Folder, or routes new work on the same area to implement-spec because an old spec exists. This is the first addition of GitHub issue #6.

#### Acceptance Criteria

1. THE Workflow_Rule SHALL carry one Standing_Rule saying that a Spec_Folder holds the three spec files and nothing else, that a Closed_Spec is not edited to match later code and not read for current behaviour, and that current behaviour lives in the code and the repository's own documentation.
2. THE Standing_Rule in criterion 1 SHALL name no file particular to the handbook repository, since the Rule applies in every repository.
3. WHEN a request concerns an area whose only Spec_Folder is a Closed_Spec, THE Workflow_Rule SHALL not send the request to implement-spec, and the request SHALL take the route the Skill_Descriptions give it.
4. IF a session is asked how code works today and a Closed_Spec for it exists, THEN THE session SHALL answer from the code and the repository's documentation, not from the Closed_Spec.

### Requirement 4: A discovery is the author's call

**User Story:** As an author, I want a Discovery stated with its likely size so that I choose between keeping it in the branch and filing an issue, rather than every Discovery being silently fixed, silently dropped, or carried from report to report. This is the third addition of GitHub issue #6 as revised by its triage comment; the second addition, choices going back into the spec, is already owned by implement-spec's proposal step and is not repeated in a Rule.

#### Acceptance Criteria

1. THE Code_Changes_Rule SHALL extend its "Make the smallest change that does the job" bullet so that a Discovery is stated with roughly how much work it would add to the branch, and the author chooses between keeping it in the branch and filing an issue.
2. THE Code_Changes_Rule SHALL keep that bullet's existing instruction not to make the Discovery's change unasked.
3. WHEN implement-spec writes a Hand_Back that lists a Discovery under follow-ups, THE implement-spec Skill SHALL give each Discovery its likely size and ask the author to choose, for each, between a proposed task in `tasks.md` and an issue.
4. WHEN the author chooses the branch for a Discovery, THE implement-spec Skill SHALL treat it as a spec edit proposal, applied to `tasks.md` only on the author's approval, as its existing proposal step already does.
5. WHEN the author chooses an issue for a Discovery, THE implement-spec Skill SHALL draft the issue's title and body once the author has chosen and leave filing it to the author, and SHALL not list that Discovery again in later Hand_Backs.
6. THE Workflow_Rule SHALL not repeat the Discovery rule, since the Code_Changes_Rule holds it.

### Requirement 5: The skills prove they hold the behaviour

**User Story:** As a maintainer removing Skill_Narrations and restated Triggers from the Rule, I want the evals to show that each Skill carries the behaviour on its own, so that the trim is measured, not assumed, and any gap is patched in the Skill. This is the eval run and skill patching the author asked for.

#### Acceptance Criteria

1. THE System SHALL run the Target_Evals of bugfix, implement-spec, pr and start-task before the trim, as the baseline, and after the trim and any Skill patch, and record both result tables in the pull request's Testing section.
2. IF a Target_Eval case fails at the baseline or after the trim for a behaviour the Rule used to describe, THEN THE System SHALL patch the Skill until the case passes, and SHALL not restore the sentence to the Rule.
3. THE System SHALL add one Eval_Case under `evals/rules/workflow/` for Requirement 3 criterion 3: a workspace with a Closed_Spec and a request on the same area, graded on not invoking implement-spec.
4. THE System SHALL add one Eval_Case under `evals/skills/pr/` for Requirement 2 criterion 3: a workspace with its own `.github/pull_request_template.md`, graded on the PR body following that template's sections.
5. THE System SHALL add one Eval_Case under `evals/skills/pr/` for Requirement 2 criterion 2: a workspace with uncommitted changes, graded on the commit Offer being made and nothing committed before the author's yes.
6. THE System SHALL add one Eval_Case under `evals/skills/implement-spec/` for Requirement 4 criterion 3: a fixture where the wave's work exposes a Discovery, graded on the Hand_Back stating its size and offering the choice.
7. WHEN an Eval_Case is added, THE Eval_Case SHALL pass `make validate`, carry its component's tag, and give the case a grader on the result as `evals/README.md` asks.
8. THE System SHALL run the Target_Evals of the workflow rule and the code-changes rule with `--ablation with-without` before the Rule edits, as the baseline, and after them, so that the routing table in the pull request shows the plugin still changes behaviour and Requirement 1 criterion 7 can be judged.

### Requirement 6: The rest of the repository agrees

**User Story:** As a reader of the README, I want its one-line summary of the Workflow_Rule to match the trimmed rule, so that the documentation does not describe sentences the rule no longer has.

#### Acceptance Criteria

1. THE README's `rules/workflow.md` row SHALL describe the rule as it reads after this change: check the Skill_Descriptions first and run the Skill that fits, the Guards, the small-change exception, the default-branch rule with the author's yes, and the record rule for merged specs.
2. THE README's `rules/code-changes.md` row, if it names the follow-up behaviour, SHALL match the extended bullet.
3. THE hook output SHALL stay under the Hook_Limit after every Rule edit, as `make check` proves.
4. IF the combined Rule edits would cross the Hook_Limit, THEN THE System SHALL shorten the Rules further rather than raise the limit.

### Requirement 7: Read the repository's own guide first

**User Story:** As a maintainer of a repository with a contributing guide, I want every session to read the repository's README and contributing guide before changing code, so that conventions the code alone does not show are followed without a skill of their own. This is GitHub issue #15 as triaged: one sentence in a Rule, not a new skill.

#### Acceptance Criteria

1. THE Code_Changes_Rule SHALL say, in its "Read before you write" bullet, that the repository's README and contributing guide are read before the surrounding code.
2. THE Code_Changes_Rule SHALL name no file particular to the handbook repository, since the Rule applies in every repository.
3. THE System SHALL add one Eval_Case under `evals/rules/code-changes/` for criterion 1: a workspace whose contributing guide states a convention the code does not show, graded on a change that follows it, and run with the no-plugin baseline.
4. THE hook output SHALL stay under the Hook_Limit after the edit, as `make check` proves.

### Requirement 8: The author sees the task name before the fit question

**User Story:** As an author starting a task in a repository that has nothing the request extends, I want start-task to state the route, the task name and the branch name before it asks whether this is the right repository, so that I can correct the name in the same breath, as the skill already promises. Found by the names-task-and-asks eval case missing one run in three on phrasing.

#### Acceptance Criteria

1. WHEN step 2 of start-task finds nothing the request would extend, THE start-task Skill SHALL write the route statement, with the task name and branch name, first in the same message as the Fit question.
2. THE Eval_Case `evals/skills/start-task/names-task-and-asks/` SHALL run on a fixture the request extends, so that it exercises the spec route it describes, with the task name proposed, the route stated and the spec questions asked in the final message.
3. THE System SHALL run the start-task Target_Evals after the edit and record the table in the pull request's Testing section.
