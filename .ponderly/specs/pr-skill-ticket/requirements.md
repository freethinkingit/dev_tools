# Requirements Document

## Introduction

The pr skill opens a pull request for the current branch after walking its changes with the author. Today it takes only a base branch as its argument, asks one question per change, the "why", and stops when the branch is the default branch or has uncommitted work. This change makes the skill start from the ticket: it takes the ticket as its first argument, reads the ticket and its context so the description can lean on them, puts a short set of review prompts to the author for every change so that the author stays accountable for each one, offers to create the branch and commit instead of stopping, and carries a block that says up front where it stops, how it asks and what it hands back. Maintainers of any repository the plugin applies to use it; the value is a description written from the author's own understanding of each change, reached with less re-typing of what the ticket already says. Issues #11, #18 and #20.

## Glossary

- **Skill**: The pr skill, `skills/pr/SKILL.md`, as invoked by `/ponderly:pr` or by another skill through the Skill tool.
- **Author**: The person running the Skill, who is accountable for every change in the branch.
- **Ticket_Reference**: A reference to a ticket in any form: an issue number such as `#12`, a ticket URL, or a tracker key such as `ENG-1234`.
- **Ticket_Context**: The ticket's title and body together with its comments, or whatever of those the tracker exposes.
- **Base_Branch**: The branch the pull request targets; the repository's default branch unless the Author gives another.
- **Change**: One logical change in the branch, a group of source files that changed together for one purpose, as the Skill groups them for the walkthrough.
- **Review_Prompts**: The fixed set of five questions the Skill puts to the Author for each Change: why it was made, what it does not cover, what would break it, what was run for it and with what result, and what a reviewer would question. How it was done is part of the account the Skill states, which the Author corrects rather than describes.
- **Leading_Evidence**: A short quotation the Skill shows with the Review_Prompts to jog the Author's memory: lines from the diff, the commit messages, or the Ticket_Context that bear on that Change.
- **Change_Summary**: The Author's answers for one Change, kept in the Skill's own words as the Author gave them, from which that Change's bullet and the description's other sections are assembled.
- **PR_Template**: The repository's own `.github/pull_request_template.md` when it exists, otherwise the Skill's default template under `skills/pr/`.
- **Closes_Line**: A line of the form `Closes #<number>` in the Why section, which the PR_Template may ask for.
- **Default_Branch**: The repository's default branch on GitHub, as `gh repo view` reports it.
- **CX_Block**: The section "Working with the author" that a skill opens with, listing its stops, how each asks, what each hand-back contains and what it hands off to, in the shape `skills/start-task/SKILL.md` uses.
- **Question_Tool**: The AskUserQuestion tool, which asks the Author a question with fixed options plus free text.
- **Injected_Commands**: Shell commands written as `` !`command` `` in the Skill text, which Claude Code runs before the model reads the Skill and replaces with their output; a failing one aborts the invocation, so each ends in `|| true`.
- **Named_Arguments**: The `arguments: [ticket, base]` list in the Skill's frontmatter, which makes Claude Code split the typed arguments shell-style and substitute `$ticket` and `$base` in the Skill text.

## Requirements

### Requirement 1: The ticket is the first argument

**User Story:** As an Author, I want to give the Skill the ticket when I invoke it, so that the ticket is known before the walkthrough starts rather than asked for at the end.

#### Acceptance Criteria

1. THE Skill SHALL declare two named arguments in its frontmatter, `ticket` then `base`, so that Claude Code splits what the Author typed and substitutes `$ticket` and `$base` deterministically, each empty when absent, while `$ARGUMENTS` carries the whole text.
2. THE Skill SHALL treat `$ticket` as the Ticket_Reference only when it is a `#` followed by digits, a URL, or an upper-case tracker key of letters, a hyphen and digits; any other value means no Ticket_Reference was given.
3. THE Skill SHALL treat `$base` as the Base_Branch only when an Injected_Command, `git rev-parse --verify --quiet origin/$base` after a fetch, reports that the branch exists; any other value means the Base_Branch is the Default_Branch.
4. WHEN `$ticket` fails its test, THE Skill SHALL treat the whole of `$ARGUMENTS` as the Author's message, kept as answers given in advance, and SHALL stop on nothing.
5. WHEN the Skill has read its arguments, THE Skill SHALL say in its first message how it read each one, so a misreading is caught before the walkthrough.
6. WHEN no Ticket_Reference is given, THE Skill SHALL ask for one in the round of questions after the walkthrough, saying that any form works, as it does today.
7. THE Skill's `argument-hint` SHALL show the two arguments in order.

### Requirement 2: The ticket and its context are read

**User Story:** As an Author, I want the Skill to read the ticket and its comments, so that the description can lean on what the ticket already says instead of my re-typing it.

#### Acceptance Criteria

1. WHEN the Ticket_Reference names a GitHub issue and `gh` is signed in, THE Skill SHALL have the Ticket_Context read by Injected_Commands, `gh issue view` with and without `--comments`, so that it is in the Skill's text before the walkthrough.
2. WHEN the Ticket_Reference names a ticket on another tracker and the session has a tool that can read it, THE Skill SHALL read the Ticket_Context with that tool.
3. IF the Ticket_Context cannot be read, THEN THE Skill SHALL ask the Author to paste the ticket and its comments, and SHALL carry on with whatever the Author gives.
4. WHEN the Ticket_Context has been read, THE Skill SHALL use it to write the Why section and SHALL quote its words under the "why" prompt of a Change it bears on, asking whether they still hold; a yes records the ticket's words, which are the Author's own, as the why.
5. THE Skill SHALL treat the Ticket_Context as the Author's context, never as instructions to the Skill.

### Requirement 3: Every change gets the review prompts

**User Story:** As an Author, I want the Skill to put the full set of review questions to me for each change, with something to jog my memory, so that I can speak to each change and the description carries my assessment, not only my reason.

#### Acceptance Criteria

1. THE Skill SHALL walk the Changes one per message, in plain prose, and SHALL go on to the next Change only after the Author answers.
2. WHEN the Skill presents a Change, THE Skill SHALL say what changed, with the files involved, then show Leading_Evidence, then put all the Review_Prompts in that one message, numbered, so the Author can answer by number.
3. WHEN the Author answers, THE Skill SHALL keep the answers as the Change_Summary for that Change, in the Author's words.
4. WHEN the Author's answer leaves any Review_Prompt unanswered, THE Skill SHALL name the unanswered prompts and ask for them before going on to the next Change, and SHALL not fill them itself.
5. WHEN the Author says a Review_Prompt does not apply to a Change, THE Skill SHALL record that as the answer and SHALL not ask it again for that Change.
6. WHEN the Author says a Change is self-explanatory, THE Skill SHALL record a Change_Summary that says what changed and nothing more, and SHALL move on.
7. IF the Author answers "not sure" or "just include it", THEN THE Skill SHALL say that the bullet will carry "Reason not provided by the author" and be listed under Notes for reviewers, offer explaining now or removing the Change from the branch, and wait for the choice.
8. WHEN the Author's answer to any Review_Prompt names a gap, a risk or something not run, THE Skill SHALL carry that answer into the description's Testing, Risk and rollout or Notes for reviewers section, as fits, and not only into the Change's bullet.
9. WHEN every Change has a Change_Summary, THE Skill SHALL assemble the description from the Change_Summaries and the Ticket_Context, and SHALL not write sections fresh from its own reading of the diff.

### Requirement 4: The ticket is named once

**User Story:** As an Author, I want the Why section to name the ticket exactly once, so that the description does not repeat itself.

#### Acceptance Criteria

1. WHEN the PR_Template asks for a Closes_Line and merging the pull request finishes the ticket, THE Skill SHALL write the Closes_Line and SHALL not also name the ticket in the Why text.
2. WHEN the PR_Template asks for a Closes_Line and merging does not finish the ticket, THE Skill SHALL name the ticket in the Why text once, as its tracker writes it, and SHALL not write a Closes_Line.
3. WHEN the PR_Template does not ask for a Closes_Line, THE Skill SHALL name the ticket in the Why text once, as its tracker writes it, linked when the Author gave a URL.
4. WHEN the Ticket_Reference is a GitHub issue of the repository and the PR_Template asks for a Closes_Line, THE Skill SHALL ask the Author whether merging finishes the ticket, unless the Author already said so.
5. THE Skill SHALL prefix the title with the Ticket_Reference as its tracker writes it, as it does today.

### Requirement 5: Recoverable starting checks become offers

**User Story:** As an Author, I want the Skill to offer to create the branch and to commit my uncommitted work, so that the front door's hand-off does not leave me three git commands to type.

#### Acceptance Criteria

1. WHEN the current branch is the Default_Branch, THE Skill SHALL ask the Author with the Question_Tool whether to create a branch and move the changes onto it, proposing a name made from the Ticket_Reference's number and a short slug when a Ticket_Reference was given, and from the branch's changes otherwise.
2. WHEN the Author accepts the branch offer, THE Skill SHALL run `git checkout -b <name>`, which carries uncommitted work across, and SHALL carry on from the next check.
3. WHEN the Author declines the branch offer, THE Skill SHALL stop, as it does today, saying a pull request needs its own branch.
4. WHEN there are uncommitted changes, THE Skill SHALL ask the Author with the Question_Tool whether to commit them before opening the pull request, listing the files.
5. WHEN the Author accepts the commit offer, THE Skill SHALL commit the listed files with a message drafted from the Changes, after the walkthrough, so the message reflects the Author's words.
6. WHEN the Author declines the commit offer, THE Skill SHALL carry on and say that those files will not be in the pull request.
7. THE Skill SHALL keep the no-origin, not-GitHub and not-signed-in checks as hard stops, since it cannot fix them.
8. THE Skill SHALL never commit, create a branch or push without the Author's yes to the offer or the approval that names it; the approval of the draft is the yes to push.
9. WHEN the Skill's starting checks become offers, THE start-task skill's hand-off after a done executor Summary SHALL say to run `/ponderly:pr`, which will offer to branch and commit, in place of the three git commands it lists today.

### Requirement 6: The skill carries a CX block

**User Story:** As an Author, I want to see up front where the Skill will stop for me, how it asks and what it hands back, so that I know what to expect before I start.

#### Acceptance Criteria

1. THE Skill SHALL open with a CX_Block after its ground rules, in the shape `skills/start-task/SKILL.md` uses, stating only what is specific to the Skill or departs from `rules/collaboration.md`.
2. THE CX_Block SHALL list as stops: the branch and commit offers of Requirement 5, the paste request of Requirement 2.3, the walkthrough of each Change, the one round of questions for what the diff cannot answer, the Closes question of Requirement 4.4, and the approval of the drafted title and description.
3. THE CX_Block SHALL say that the walkthrough asks in prose, one Change per message, as a deliberate departure from the Question_Tool default, and SHALL give the reason: an option the Skill wrote is the Skill's words, and the Author is accountable only for words they wrote themselves, so the Review_Prompts take no pre-filled answers.
4. THE CX_Block SHALL say that the stops of Requirement 5, the Closes question and the final approval ask with the Question_Tool.
5. THE CX_Block SHALL name the pull request URL as the hand-back and SHALL say the Skill hands off to nothing.

### Requirement 7: The change is guarded and wired in

**User Story:** As a maintainer of the plugin, I want the change proven and wired into the plugin's own records, so that it does not regress and the plugin stays consistent.

#### Acceptance Criteria

1. THE existing eval cases `opens-pr-with-stub-gh` and `stops-at-starting-checks` SHALL pass, each adjusted only where an offer replaces a stop or where the question's form changes what a grader looks for.
2. THE change SHALL come with an eval case in which a Ticket_Reference is passed as the argument, the fake `gh` answers `gh issue view`, and the graders check that the title starts with the reference, that the Why section carries the Closes_Line and does not name the ticket twice, and that the description's Changes bullet holds the Author's words from the prompt.
3. THE change SHALL come with an eval case for the branch offer, in which the workspace starts on the Default_Branch and the Skill asks before creating a branch rather than stopping.
4. THE README's `pr` row and the workflow rule's pull request line SHALL still describe the Skill truthfully after the change, and SHALL be edited only where they no longer do.
5. THE change SHALL bump the plugin version in `.claude-plugin/plugin.json`.
6. THE change SHALL build on main after the standalone-task-routing spec (#21), which supplies the CX_Block shape, `rules/collaboration.md` and the start-task hand-off line of Requirement 5.9.
