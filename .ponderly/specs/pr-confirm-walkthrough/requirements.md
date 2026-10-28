# Requirements Document

## Introduction

The pr skill walks every group of changes with five review prompts and forbids itself from drafting any answer, so the author writes the why, the gaps, the risk, the testing and the review focus for each group, even on a branch built from a spec they already approved. Across 2026-10-08 to 2026-10-26 the author stopped the walkthrough on a seven-group branch, answered "trivial, no other questions" on a four-file rename, called a version bump "not a big PR thing", and had three pull requests opened by a short form that exists only in the session's memory. This task turns the walkthrough around: the skill explains each change as the person it changes experiences it and asks the author to confirm or correct, a branch built from a ticked spec is drafted from the spec and its reports, a mechanical change gets one question, nothing already answered is asked again, and the fixed choices go in one call. The author remains accountable for every change by reading and confirming each explanation and approving the whole draft. Issues #69, #45 and #55.

## Glossary

- **Skill**: The pr skill, `skills/pr/SKILL.md`, invoked as `/ponderly:pr [ticket] [base]`.
- **Author**: The person running the Skill, accountable for every change in the Branch.
- **Branch**: The current git branch, compared against its base to give the changes.
- **Group**: A set of source changes made together for one purpose, as the Skill's step 5 groups them today.
- **Spec**: The three files under `.ponderly/specs/<task>/`: `requirements.md`, `design.md` and `tasks.md`.
- **Ticked_Spec**: A Spec whose `tasks.md` has every non-optional leaf task ticked and whose task names cover the Branch's source changes.
- **Reports**: The wave and final hand-back messages written by `implement-spec` for a Ticked_Spec, present in the conversation, each with Problems, Done, Checks, Files and Next.
- **Spec_Form**: The walkthrough the Skill takes on a Branch with a Ticked_Spec: Groups by spec task, drafted from the Spec and the Reports, one prose round, the Fixed_Choices, the draft.
- **Confirm_Form**: The walkthrough the Skill takes on every other Branch: every Group's Explanation in one message, or in two or three messages on a large Branch, each followed by the Author's Confirmations.
- **Explanation**: The Skill's own account of one Group: what changed; what it means for whoever uses the software (the user) and what the Author takes on (the owner): what it does not cover, what would break it, any rollout care; and what was run with its result, drawn from the diff, the commits, the ticket, and the Spec and Reports where they exist.
- **Confirmation**: The Author's answer to an Explanation: confirm, correct or add, in prose.
- **Correction**: The Author's own words replacing part or all of an Explanation, which then stand in the description.
- **Review_Prompts**: The five numbered prompts of the Skill today (why; what it does not cover; what would break it; what was run; what a reviewer should question), available on request.
- **Mechanical_Group**: A Group whose diff is a version bump, a rename, generated output or a one-line configuration change, with no logic.
- **Marker**: The text "Reason not provided by the author", which the Skill puts in place of a why the Author declined to give.
- **Fixed_Choice**: A question with a short fixed list of answers the Author can pick without context: the branch offer, the commit offer, the Closes question and the draft question.
- **Ticket_Context**: The ticket's title, body and comments as the Skill's step 3 reads them today.
- **Case**: One eval case under `evals/skills/pr/<case>/`, run by `make eval-skill-pr`.
- **Baseline**: The no-plugin arm of an eval run with `--ablation with-without`.

## Requirements

### Requirement 1: Two forms, chosen by the branch

**User Story:** As an Author, I want the walkthrough to fit the branch, so that a branch I already accounted for in a spec is not walked as if it were new.

#### Acceptance Criteria

1. WHEN the Branch has a Ticked_Spec, THE Skill SHALL take the Spec_Form.
2. WHEN the Branch has no Ticked_Spec, THE Skill SHALL take the Confirm_Form.
3. THE Skill SHALL say in one line which form it takes and why, naming the Spec when there is one, before the first Group.
4. IF a Spec exists whose `tasks.md` has an unticked non-optional leaf task, THEN THE Skill SHALL take the Confirm_Form and say which task is unticked.
5. IF the Branch's source changes include files no task of the Ticked_Spec names, THEN THE Skill SHALL walk those files as Groups in the Confirm_Form after the spec Groups, and say so.

### Requirement 2: The skill explains, the author confirms

**User Story:** As an Author, I want each change explained to me as the person it changes experiences it, so that I confirm what I read instead of writing five answers.

#### Acceptance Criteria

1. WHEN the Confirm_Form walks a Group, THE Skill SHALL write its Explanation, the user's and the owner's experience before the mechanism, then ask one question in prose: confirm, correct or add.
2. THE Skill SHALL put every Group's Explanation in one message and take the Confirmations in one reply; WHEN the Branch has more than five Groups, THE Skill SHALL split them into two or three messages of roughly equal size, in branch-story order, each with its own Confirmation reply, and SHALL say how many messages there are in the first.
3. WHEN the Author gives a Correction, THE Skill SHALL replace the Explanation's words with the Author's for that Group.
4. WHEN the Author asks for the Review_Prompts for a Group, THE Skill SHALL put the five prompts for that Group as it does today.
5. IF the Skill cannot infer a Group's why from the diff, the commits or the Ticket_Context, THEN THE Skill SHALL say so and ask only the why for that Group.
6. IF the Author declines to give a why the Skill could not infer, THEN THE Skill SHALL keep the Group's bullet with the Marker and list it under Notes for reviewers, as today.
7. THE Skill SHALL quote one to three lines of the diff or the commits as evidence with each Explanation, as today.

### Requirement 3: A ticked spec drafts the walkthrough

**User Story:** As an Author, I want a branch built from a spec I approved to be drafted from that spec and its reports, so that I am not asked again what I already decided.

#### Acceptance Criteria

1. WHEN the Skill takes the Spec_Form, THE Skill SHALL group the source changes by the Spec's top-level tasks and name each Group by its task.
2. THE Skill SHALL draft each Group's why from the requirements its tasks cite and from the Spec's introduction, its testing from the Reports' Checks and the tasks' ephemeral checks, and its notes from the Reports' Problems.
3. THE Skill SHALL show the Groups in one message, each with what changed and its drafted why in one or two lines, and then ask one round in prose for what the Spec and the Reports do not answer: risk and rollout, review focus, and any reason that changed during the run.
4. WHERE the Reports are not in the conversation, THE Skill SHALL draft from the Spec alone and say that the testing comes from the tasks' checks as written, not from a run it saw.
5. THE Skill SHALL carry the Reports' eval tables into the Testing section when a Report holds one.

### Requirement 4: Nothing is asked twice, and a mechanical change gets one question

**User Story:** As an Author, I want a version bump or a rename to take one question and an answer I already gave to stand, so that the walkthrough is sized to the change.

#### Acceptance Criteria

1. WHEN a Group is a Mechanical_Group, THE Skill SHALL show what changed and ask one question, "anything a reviewer should know?", in place of the Explanation and the Confirmation.
2. WHEN the Author answered a Group's question, or a Review_Prompt, earlier in the session or in the request, THE Skill SHALL take that answer, say which was taken, and not ask it again.
3. IF the Skill would list a prompt or a question as open that the Author has answered, THEN THE Skill SHALL count that as a defect of the walkthrough.
4. WHEN the Author says a Group is self-explanatory, THE Skill SHALL record a bullet that says what changed and nothing more, as today.

### Requirement 5: The fixed choices go in one call

**User Story:** As an Author, I want the branch, commit, Closes and draft questions put to me together, so that I answer them once.

#### Acceptance Criteria

1. THE Skill SHALL put every Fixed_Choice that applies in one AskUserQuestion call after the walkthrough and before the draft: the branch offer when the Branch is the default branch, the commit offer when there are uncommitted changes, the Closes question when the ticket is a GitHub issue and the template has the Closes convention, and the draft question.
2. WHERE no ticket was given and the Author names one in the prose round, THE Skill SHALL ask the Closes question in a call of its own after reading the ticket, since it depends on that answer.
3. THE Skill SHALL still stop at the starting checks it stops at today: no origin, no signed-in `gh`, and an unreadable ticket.
4. THE Skill SHALL keep the approval of the draft as its own call, with the draft shown in full before it.

### Requirement 6: The description carries the confirmed words

**User Story:** As an Author, I want the description to hold what I confirmed, so that my approval of the draft is the record of my accountability.

#### Acceptance Criteria

1. THE Skill SHALL write each Changes bullet from the Group's Explanation as confirmed, or from the Author's Correction where one was given.
2. THE Skill SHALL add no marker or line saying which words the Skill drafted and which the Author wrote; the Author's approval of the draft is the record.
3. THE Skill SHALL carry each Explanation's gaps, risks and review points into Testing, Risk and rollout or Notes for reviewers, as the answers to prompts 2 to 5 are carried today.
4. THE Skill SHALL keep the title rule, the repository template rule, the name-the-ticket-once rule and the `gh` steps as they are today.

### Requirement 7: Evals prove both forms

**User Story:** As a maintainer, I want cases that show each form does what it says, so that the change is measured.

#### Acceptance Criteria

1. THE System SHALL rewrite the `opens-pr-with-ticket` Case so its prompt gives a Confirmation in advance instead of five answers, with graders that pass only when the Changes bullet carries the Skill's explanation as confirmed, or the Author's Correction, and the Closes line and title as today.
2. THE System SHALL add a Case on a branch with no spec whose graders pass only when the first walkthrough message explains the first Group by its effect on the user and the owner, asks one confirm-or-correct question, and lists no five prompts.
3. THE System SHALL add a Case on a branch with a Ticked_Spec whose graders pass only when the Skill names the Spec_Form, groups by the Spec's tasks, and asks one prose round without the five prompts.
4. THE System SHALL add a Case with a version-bump Group and a pre-answered Confirmation whose graders pass only when that Group gets one question and no answered question is asked again.
5. THE System SHALL keep every existing pr Case passing.
6. WHEN the Cases are run for the pull request, THE System SHALL run them with `--ablation with-without` and report the table as it comes out; an equal score in both arms is not a failure, and the Baseline transcript is read to say whether the graders passed on the behaviour or for another reason.
7. THE System SHALL give each Case a prompt whose description says what it proves and which requirement it serves, and SHALL keep `checks/test_eval_cases.py` passing.

### Requirement 8: The plugin's own documents follow

**User Story:** As a maintainer, I want the skill's description, the README and the version to match, so that a reader installing the plugin reads what it now does.

#### Acceptance Criteria

1. THE Skill's description SHALL say that it explains each change and asks the Author to confirm, that a ticked spec is drafted from the spec and its reports, and SHALL stay under 1,024 characters.
2. THE System SHALL update the README row for `pr` to say what it now does, in the row's existing shape.
3. THE System SHALL bump the plugin version in `plugins/ponderly/.claude-plugin/plugin.json` to the next minor version above the one on `main` when the branch is merged.
4. THE System SHALL keep `make validate` passing.
