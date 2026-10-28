# Requirements Document

## Introduction

On its spec route, the start-task skill writes `requirements.md`, `design.md` and `tasks.md` in turn and asks the author to approve each one. Today it prints each document in full into the conversation before the approval question, and prints it again after every change-request round, so a three-document spec with one revision each puts six full documents in front of the author, who reads the file in an editor anyway. This change makes the skill show the document's path and a short summary instead: enough for the author to know what they are approving at a high level and to trust it, without flooding the conversation. The author opens the file before approving; the approval question itself does not change. Only start-task changes. GitHub issue #47 is the ticket.

## Glossary

- **Skill**: The start-task skill at `plugins/ponderly/skills/start-task/SKILL.md`.
- **Author**: The person running the Skill, who approves each document.
- **Spec_Folder**: `.ponderly/specs/<task-name>/`, where the three Spec_Documents of a task live.
- **Spec_Document**: One of `requirements.md`, `design.md` and `tasks.md` in the Spec_Folder.
- **Approval_Question**: The question the Skill puts with the AskUserQuestion tool after each Spec_Document, header `Approve`, options `Approved` and `Changes needed`.
- **Document_Summary**: The text the Skill shows in place of a Spec_Document's body: the document's path, its Highlights, and a short account of the rest at the depth the requirements below set for that document.
- **Highlight**: A passage of a Spec_Document that its Document_Summary quotes verbatim because the document's shape names it: the user story of each requirement in `requirements.md`, and the paragraph of each Key_Decision in `design.md`.
- **Leaf_Task**: A checkbox task in `tasks.md` with no sub-tasks, the unit the Task Dependency Graph lists.
- **Revision_Summary**: The text the Skill shows after revising a Spec_Document on a change request: the document's path and what changed, section by section.
- **Key_Decision**: A design decision that chose between alternatives with a real trade-off, so the Author may disagree with it.
- **Wave**: One entry of the `waves` block in a `tasks.md` Task Dependency Graph.
- **Hand_Backs_Bullet**: The bullet in the Skill's "Working with the author" section that says what the Skill hands back on each route.
- **README**: The plugin README at `plugins/ponderly/README.md`, whose Skills table describes the Skill.
- **Eval_Case**: A folder under `evals/` with a `prompt.md` and graders, run by its component's make target; Requirement 7's case is under `evals/skills/start-task/`, run with `make eval-skill-start-task`.
- **System**: The handbook plugin: the Skill, the README and the Eval_Cases.

## Requirements

### Requirement 1: The path and a summary replace the full text

**User Story:** As an Author approving a Spec_Document, I want the Skill to tell me where the file is and what it says at a high level, so that I can open the file and approve it without the whole document being printed into the conversation.

#### Acceptance Criteria

1. WHEN the Skill has written a Spec_Document, THE Skill SHALL show a Document_Summary and put the Approval_Question, in that order and in the same message, and SHALL not reproduce the Spec_Document's body in the conversation.
2. THE Document_Summary SHALL open with the Spec_Document's path, relative to the repository root, on its own line.
3. THE Document_Summary SHALL say, once, that the Author can open the file before answering.
4. THE Document_Summary SHALL quote from the Spec_Document only the Highlights Requirements 2 and 3 name for that document, and SHALL summarise the rest, so the Document_Summary stays far shorter than the file.
5. THE Approval_Question SHALL keep its header, its options and its wording as they are today.
6. WHEN the Skill resumes at an existing Spec_Document that the Author says is not approved, THE Skill SHALL show it the same way, as a Document_Summary followed by the Approval_Question.

### Requirement 2: The requirements summary

**User Story:** As an Author, I want the requirements summarised as each requirement's user story, so that I know at a high level what is being built and for whom before I read the criteria in the file.

#### Acceptance Criteria

1. THE Document_Summary for `requirements.md` SHALL list every requirement, in order, as one entry giving its number and title, then its user story, the first sentence of the requirement, quoted verbatim as its Highlight.
2. THE Document_Summary for `requirements.md` SHALL quote no acceptance criterion and SHALL not list the glossary.
3. IF the requirements leave a question open that the Author did not answer, THEN THE Document_Summary SHALL name it after the requirement entries.

### Requirement 3: The design summary

**User Story:** As an Author, I want the design's key decisions quoted for review and the rest summarised for discussion, so that I can push back on a decision and talk through the shape of the solution without reading the lower-level detail in the conversation.

#### Acceptance Criteria

1. THE Document_Summary for `design.md` SHALL open with each Key_Decision as a Highlight, its decision paragraph quoted verbatim, in the document's order, as the things for the Author to review.
2. THE Document_Summary for `design.md` SHALL then summarise the rest for discussion: the main flows and design concepts, the components or parts, what each is for, and how a request or piece of work moves through them, in a few lines.
3. THE Document_Summary for `design.md` SHALL leave out the lower-level content: data fields and types, the operations table, the correctness properties, the error-handling rows and the testing strategy.
4. WHEN the Skill's traceability check finds a requirement the design does not satisfy or a decision that traces to no requirement, THE Document_Summary SHALL name it, as the Skill already requires.

### Requirement 4: The tasks summary

**User Story:** As an Author, I want the task list shown as a table of its leaf tasks by wave, so that I can accept the order of the work at a glance, in the shape implement-spec later shows me at its graph check.

#### Acceptance Criteria

1. THE Document_Summary for `tasks.md` SHALL be a table with one row per Leaf_Task in Wave order, with columns for the Wave, the task's number, what it builds in one line, whether it is an optional test, the requirements it cites and the design property it names if any.
2. THE Document_Summary for `tasks.md` SHALL carry none of a task's detail bullets and SHALL quote nothing else from the document.

### Requirement 5: A revision shows what changed

**User Story:** As an Author who asked for changes, I want to see plainly what changed in the document, so that I can check my request was understood without rereading the whole file.

#### Acceptance Criteria

1. WHEN the Author answers `Changes needed` and the Skill has revised the Spec_Document, THE Skill SHALL show a Revision_Summary and put the Approval_Question again, in that order and in the same message.
2. THE Revision_Summary SHALL open with the Spec_Document's path and SHALL list one line per section that changed, saying what changed in it; a section that did not change SHALL not be listed.
3. IF part of the Author's change request was not applied, THEN THE Revision_Summary SHALL say which part and why, before the Approval_Question.
4. THE Revision_Summary SHALL quote a Highlight that changed, a user story or a Key_Decision, and SHALL otherwise say what changed without reproducing the Spec_Document's body.

### Requirement 6: The skill text and the README agree

**User Story:** As a reader of the Skill or the README, I want them to describe the hand-back as it now works, so that neither promises a full print the Skill no longer makes.

#### Acceptance Criteria

1. THE Hand_Backs_Bullet SHALL say that on Spec_Route the Skill hands back each Spec_Document as its path and a Document_Summary, and a revision as a Revision_Summary.
2. THE Skill's steps that write the three Spec_Documents SHALL each say to show the Document_Summary at the depth Requirements 2, 3 and 4 set for that document, and the Skill SHALL hold the shape of the Revision_Summary once, where the three steps can refer to it.
3. THE README's row for the Skill SHALL say that the Author sees each document's path and a summary and approves each before the next.
4. THE System SHALL change no skill, agent or rule beyond what Requirements 1 to 7 and 8.1 name.

### Requirement 7: An eval proves the shape

**User Story:** As a maintainer, I want an Eval_Case that reaches a written Spec_Document and grades its hand-back, so that the change is proven by behaviour rather than by reading the skill text.

#### Acceptance Criteria

1. THE System SHALL add one Eval_Case that gives the Skill a request on the calc fixture with the spec questions answered in the request, so that the run writes `requirements.md` and ends at its Approval_Question.
2. THE Eval_Case SHALL grade that `requirements.md` was written in the Spec_Folder, at `.ponderly/specs/*/requirements.md`, that the final message names its path, that it does not reproduce the document's sections, that it quotes a user story, that no criterion is reproduced, and that every entry quotes its user story; whether there is one entry per requirement is read by the wave reviewer and by the first real spec written with the Skill, since a grader that sees only the reply cannot count the document's requirements.
3. THE Eval_Case SHALL pass `make validate` and carry the `start-task` tag so `make eval-skill-start-task` selects it.
4. THE System SHALL run `make eval-skill-start-task` after the change, and SHALL record the result table in the pull request's Testing section, with every existing case still passing.

### Requirement 8: Specs live under `.ponderly/specs/`

**User Story:** As a maintainer of the plugin and its forks, I want every spec to live in the Spec_Folder, `.ponderly/specs/<task-name>/`, instead of `.claude/specs/<task-name>/`, so that the folder names the plugin rather than one tool, a fork for another tool keeps the same path, and the eval sandbox, which refuses every write under `.claude/`, can grade a spec being written. GitHub issue #48 is the ticket.

#### Acceptance Criteria

1. THE start-task Skill, THE implement-spec Skill, THE task-executor agent, THE workflow Rule and THE README SHALL name the Spec_Folder wherever they name `.claude/specs/<task-name>/` today, and THE README's "Tune the plugin for a repository" section SHALL say that `.ponderly/specs/` holds specs beside the `<skill>/<file>.md` overrides.
2. THE root README SHALL name the Spec_Folder where it names the old folder.
3. THE Eval_Cases SHALL plant, name and grade the Spec_Folder wherever they plant, name or grade `.claude/specs/` today, their fixture folders moved with `git mv`, and `evals/README.md` SHALL replace its note that edits under `.claude/` cannot be graded with one saying the Spec_Folder is writable in the sandbox while `.claude/` is not.
4. THE System SHALL move this repository's spec records from `.claude/specs/` to `.ponderly/specs/` with `git mv`, content untouched, this spec included.
5. IF the sandbox refuses a write under `.ponderly/` too, THEN THE System SHALL stop and report it, since the folder would then need another name.
