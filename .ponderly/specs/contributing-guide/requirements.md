# Requirements Document

## Introduction

The contributing guide is the one document that tells a contributor how to develop, test and submit a change to the plugin, and how the repository uses issues, labels, milestones and discussions to turn requests into work. It comes with the community files an open-source repository is expected to carry, a license, a code of conduct and a security policy, and with a small change to the pr skill so that a pull request names its ticket however the author gives it, and with this repository's own pull request template carrying how an issue is linked, which the skill follows because it uses a repository's own template when there is one. Maintainers get a triage routine they can run in minutes; contributors get the conventions in one place instead of reverse-engineering them from the tree. The documents are written for a public repository.

## Glossary

- **Guide**: `.github/CONTRIBUTING.md`, beside the pull request template GitHub already reads from that folder.
- **Contributor**: Anyone proposing a change to the repository, maintainer or outside developer.
- **Maintainer**: A person with write access who triages issues and reviews pull requests.
- **Issue_Form**: A GitHub issue template under `.github/ISSUE_TEMPLATE/` that renders as a form with named fields.
- **Template_Chooser**: The page GitHub shows when a new issue is opened, listing the Issue_Forms and the links from `.github/ISSUE_TEMPLATE/config.yml`.
- **Issue_Type**: The organization-level type GitHub attaches to an issue, one of `Bug`, `Feature` or `Task`, saying what sort of thing it is.
- **Priority_Label**: One of `priority: high`, `priority: medium` or `priority: low`.
- **Area_Label**: A bare topic label saying which part of the plugin's value an issue serves: `quality` for the behaviour of the skills, agents and rules and for the evals and checks that guard it, and `compatibility` for working across Claude Code, Cursor, Codex and other agent tools. An issue carries the Area_Labels that apply, which may be none.
- **Info_Label**: GitHub's default `question` label, kept with GitHub's own meaning: the issue needs more from its author before it can be classified or worked.
- **Triage_Label**: The `triage` label that marks an issue no Maintainer has classified yet.
- **Milestone**: A GitHub milestone named after a goal, such as "Listing on Claude marketplace".
- **Ticket_Reference**: Any identifier of the work a pull request serves: a GitHub issue number such as `#12`, an issue URL, or a key from another tracker such as `ENG-1234`.
- **PR_Template**: `.github/pull_request_template.md`, this repository's own pull request template, which GitHub shows for a pull request opened by hand and which the pr skill uses in place of its generic one, as it does for any repository that has one.
- **Discussions**: GitHub's forum feature on the repository, used for questions and ideas that are not yet work.
- **Community_Files**: `LICENSE` at the repository root, the only place GitHub detects a license, and `CODE_OF_CONDUCT.md` and `SECURITY.md` under `.github/`, where GitHub reads them as it does from the root.

## Requirements

### Requirement 1: The contributing guide

**User Story:** As a Contributor, I want one document that says how to set up, test and submit a change, so that I do not have to reverse-engineer the repository's conventions.

#### Acceptance Criteria

1. THE Guide SHALL say how to load a working copy for a session (`claude --plugin-dir .`), how to run the free checks (`make validate`: the unit tests under `checks/`, then the validator) and how to run the evals for one component, including that evals are model calls run by hand and that their table goes in the pull request.
2. THE Guide SHALL say that a change to a skill, agent, rule or hook comes with an eval case or a change to one, and that a sizeable change starts with `/ponderly:start-task` and a spec, as the workflow rule says.
3. THE Guide SHALL say how a change is submitted: on a branch named `<issue number>-<short slug>` when an issue exists and a short slug otherwise, never on the default branch, through a pull request opened with `/ponderly:pr`, giving the issue number as the Ticket_Reference, and SHALL point at the PR_Template as the one place that says how the issue is linked, so that the Guide and the template cannot drift.
4. THE Guide SHALL describe the issue workflow of Requirement 2, the labels and Milestones of Requirement 3 and the Discussions of Requirement 5 in a few sentences each, and SHALL link the Community_Files.
5. THE README SHALL keep its "Add or change a skill or rule" heading as a pointer to the Guide of at most three sentences, so that the two documents cannot drift apart.
6. IF a change touches no skill, agent, rule or hook, THEN THE Guide SHALL say that no eval is required and that `make validate` is the whole check.
7. THE Guide SHALL have a compatibility section that says what portability across agent tools (Claude Code, Cursor, Codex and others) means for a skill or rule here, lists the checks known so far, and says the list grows from issues labelled `compatibility`.

### Requirement 2: Issue forms and triage

**User Story:** As a Maintainer, I want every new issue to arrive with the facts I need and a mark saying it is untriaged, so that triage is a short weekly pass rather than a conversation.

#### Acceptance Criteria

1. THE repository SHALL provide three Issue_Forms, each opening with a required preflight checklist, the existing issues searched on every form, plus the latest plugin version in use on the misbehaviour form, Discussions Ideas looked in on the proposal form and `evals/README.md` read on the eval-case form: a misbehaving skill or agent (a dropdown naming the skill, agent, rule or hook, the prompt, what happened, what was expected, the plugin version, and whether it reproduces), a proposal for a new or changed skill, agent or rule (a dropdown for which kind, the proposed behaviour or wording, and the case that motivates it), and a new eval case (the behaviour to guard, the component, how it would be graded).
2. WHEN an Issue_Form is submitted, THE repository SHALL apply the Triage_Label and set the Issue_Type through the form's own settings, `Bug` for a misbehaving skill or agent, `Feature` for a proposal and `Task` for a new eval case, and SHALL apply no Area_Label, since the area is a triage decision.
3. THE Issue_Form SHALL mark every field a Maintainer cannot triage without as required, and SHALL use a dropdown or checkboxes wherever the answer set is known, so that an incomplete or free-form report cannot be submitted.
4. THE Template_Chooser SHALL disable blank issues and SHALL offer three links: questions to Discussions Q&A, ideas to Discussions Ideas, and security reports to the repository's security policy page, which shows `SECURITY.md` with GitHub's Report a vulnerability button, so that a report started in the wrong place still lands in the right one.
5. THE Guide SHALL define triage as: at least weekly, a Maintainer reviews every issue carrying the Triage_Label, confirms or corrects its Issue_Type, sets one Priority_Label and the Area_Labels that apply, none, one or both, applies the Info_Label instead when the issue cannot be classified without more from its author, closes the issue as not planned or keeps it, puts a kept issue into a Milestone only when it serves a goal that already has one and otherwise leaves it in the backlog, and removes the Triage_Label.
6. IF an issue is opened without an Issue_Form, THEN THE Guide SHALL say that a Maintainer applies the Triage_Label by hand at the next triage, so that no issue escapes classification.

### Requirement 3: Labels and milestones

**User Story:** As a Maintainer, I want the organization's issue types for kind, a small fixed label vocabulary for everything else, and milestones that read as a roadmap, so that a filter means the same thing to everyone.

#### Acceptance Criteria

1. THE repository SHALL carry exactly nine labels: the three Priority_Labels, the Area_Labels `quality` and `compatibility`, the Triage_Label, the Info_Label, `good first issue` and `help wanted`; every other label SHALL be removed: GitHub's `bug`, `enhancement` and `documentation` because the Issue_Types carry kind, `duplicate`, `invalid` and `wontfix` because close reasons cover them, and the `effort:` and `area:` labels created earlier, whose values move into this set.
2. THE Guide SHALL say that every issue has one Issue_Type, SHALL define each label group in one sentence, and SHALL say that an issue carries at most one Priority_Label and the Area_Labels that apply, so that an issue with no Area_Label is normal.
3. THE Guide SHALL say that a Milestone names a goal, that the open Milestones are the repository's roadmap, and that Milestones are made in a planning pass separate from triage, pulling issues in from the backlog.
4. IF a label or an Area_Label outside these seems needed, THEN THE Guide SHALL say to propose it in an issue rather than create it, so that the vocabulary stays small.
5. THE Guide SHALL say that `good first issue` is the one label with behaviour on GitHub, feeding the repository's contribute page and GitHub's surfacing of approachable issues, and that `help wanted` marks work a Maintainer would merge but will not write.
6. THE label names SHALL be lowercase throughout, in the repository, the Guide and the Issue_Forms, and the Issue_Types SHALL be written as GitHub names them, `Bug`, `Feature` and `Task`, in the forms' `type` keys and in the Guide.

### Requirement 4: Ticket references and the pull request template

**User Story:** As an author opening a pull request, I want to give the ticket in whatever form I have, so that the pull request names its ticket without my learning a format.

#### Acceptance Criteria

1. WHEN the pr skill asks for a ticket, THE skill SHALL accept a Ticket_Reference of any kind and SHALL say so in its question.
2. WHEN a Ticket_Reference is given, THE skill SHALL carry it in the title in brackets and name it in the Why section, written the way its tracker writes it, `#12` for a GitHub issue and `ENG-1234` for a key, and SHALL leave anything further, such as a check that the ticket exists, to the judgement of the session.
3. WHEN the author says there is no ticket, THE skill SHALL proceed without one, as it does today.
4. THE skill SHALL NOT carry this repository's own conventions, such as branch names, labels or closing keywords, so that it fits any organization's tracker; those conventions live in the Guide and the PR_Template.
5. THE PR_Template SHALL ask, in the Why section's comment, for the issue to be linked and for `Closes #<number>` when merging finishes the issue, and THE pr skill SHALL follow it as this repository's own template, the way it follows any repository's own template, asking the author when the comment wants something their answers did not give, so that the convention is enforced here without living in the skill and nothing enters the description that the author did not say.
6. THE pr skill's generic template SHALL move from `.github/pull_request_template.md` to `skills/pr/pull_request_template.md`, with the skill's path to it updated, so that `.github/pull_request_template.md` is this repository's own PR_Template and the fallback other repositories get carries none of its conventions.

### Requirement 5: Discussions

**User Story:** As a Maintainer, I want questions and ideas to go somewhere other than the tracker, so that issues stay work.

#### Acceptance Criteria

1. THE repository SHALL have Discussions enabled with GitHub's default categories.
2. THE Template_Chooser SHALL link questions to the Q&A category and ideas to the Ideas category.
3. THE Guide SHALL say that a discussion which becomes work is converted to an issue, and that an issue which is really a question is converted to a discussion at triage.

### Requirement 6: Community files

**User Story:** As a future outside Contributor, I want the license, conduct and security expectations stated, so that contributing is safe for both sides.

#### Acceptance Criteria

1. THE repository SHALL carry `LICENSE` at the repository root with the MIT License text and the copyright line `Copyright (c) 2026 Dan Sabin`.
2. THE repository SHALL carry `.github/CODE_OF_CONDUCT.md` with the Contributor Covenant version 2.1, unmodified except for the contact method, which names how a report reaches the Maintainers.
3. THE repository SHALL carry `.github/SECURITY.md` saying that a vulnerability is reported through GitHub's private vulnerability reporting, the Report a vulnerability button on the repository's Security tab, never in a public issue, and that the latest release is the supported version.
4. THE repository SHALL be public with GitHub's private vulnerability reporting enabled, so that the path `SECURITY.md` names exists.

### Requirement 7: Ship

**User Story:** As a Maintainer, I want the new documents and settings to land without breaking the plugin's checks, so that the change is safe to merge on its own.

#### Acceptance Criteria

1. THE free checks SHALL pass after the change: `make validate` with the unit tests and both validators.
2. THE pr skill's eval SHALL still pass after the changes of Requirement 4, at three runs, and the transcript of one of those runs, kept with `--keep-temp`, SHALL show the skill reading `skills/pr/pull_request_template.md`, since the case's graders see only the push, the `gh pr create` call and the URL and cannot tell which template was used.
3. THE plugin version SHALL be bumped, since the pr skill's behaviour changed.
4. WHEN the change is merged to the default branch, the only branch GitHub reads templates from, THE Template_Chooser SHALL show the three Issue_Forms and the three links, and each form SHALL open with its fields rendered; this is checked by hand on GitHub right after the merge.
5. THE label set of Requirement 3, the Discussions setting of Requirement 5 and the visibility and private vulnerability reporting of Requirement 6 SHALL be applied to the repository as part of the work, the four existing issues SHALL be relabelled to the new set and given their Issue_Type, and the Guide SHALL say that labels, Milestones, Discussions and Issue_Types are repository or organization settings rather than files, so that a reader knows they do not travel with the tree.
