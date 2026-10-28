# Requirements Document

## Introduction

A team plans a year or so of work as a tech strategy, breaks it into high level designs, one per system or stream of work, and breaks each of those into low level designs, one per component, which in turn break into tasks small enough for `start-task`. This change adds three skills to the plugin, one per document, so that an author writes each document with the plugin's help and a later author writes the next document down by consuming the one above. Every document is reviewed by a reviewer agent before the author sees it, section by section, so that the sections make sense on their own and against the document above. The documents live under `.freethinking/` in whichever repository the team keeps them, a docs repository or a project's own, as plain Markdown files. The chain ends at the low level design's list of tasks; `start-task` does not change in this task. GitHub issue #50 is the ticket.

## Glossary

- **Strategy**: A tech strategy document: the highest level view of about a year of work, spanning one or more projects, written as `.freethinking/strategies/<name>.md`.
- **HLD**: A high level design document: the design of one system, service or stream of work a Strategy names, written as `.freethinking/designs/<strategy-name>/<name>/hld-<name>.md`, in a folder of its own under its Strategy's folder.
- **LLD**: A low level design document: the design of one component, module or interface an HLD names, written as `.freethinking/designs/<strategy-name>/<hld-name>/lld-<name>.md`, in its HLD's folder.
- **Document**: A Strategy, an HLD or an LLD.
- **Document_Tree**: The tree in which one Strategy has one or more HLDs and each HLD has one or more LLDs; LLDs are its leaves.
- **Parent**: The Document one level up in the Document_Tree: a Strategy for an HLD, an HLD for an LLD. A Strategy has no Parent.
- **Parent_Line**: The line near the top of an HLD or LLD that names its Parent by path, so the Document_Tree can be walked from the line as well as from the folders.
- **Candidate**: An entry in the closing section of a Document naming a piece of the next level down that has not been written yet: an HLD a Strategy expects, an LLD an HLD expects, or a Task an LLD expects.
- **Task**: A unit of work small enough for `start-task` to take in one run, a dozen or so of which make up one LLD.
- **Skill**: One of the three skills this task adds, `strategy`, `hld` and `lld`, each at `plugins/freethinking/skills/<skill>/SKILL.md`.
- **Template**: The self-describing Markdown file under a Skill's folder that is a valid Document of that kind and whose own prose explains how that kind of Document works, in the manner of `start-task`'s spec template.
- **Section**: A heading-delimited part of a Document, as its Template lays them out.
- **Author**: The person running a Skill, who answers its questions and approves its Document.
- **Reviewer**: The agent a Skill launches to read a drafted Document before the Author sees it, which changes nothing and returns Findings.
- **Finding**: One problem the Reviewer reports: the Section, an exact quote, the problem in a sentence and a severity of `blocker`, `should-fix` or `nit`.
- **Review_Round**: One launch of the Reviewer over a Document followed by the Skill's fixes for its Findings.
- **Document_Summary**: What a Skill shows in place of a Document's text: its path, the Review_Round's outcome, and a short account of each Section.
- **Approval_Question**: The question a Skill puts with the AskUserQuestion tool after a Document_Summary, header `Approve`, options `Approved` and `Changes needed`.
- **README**: The plugin README at `plugins/freethinking/README.md`.
- **Eval_Case**: A folder under `evals/skills/<skill>/` or `evals/agents/<agent>/` with a prompt and graders, run by its component's make target.
- **System**: The handbook plugin: the three Skills, their Templates, the Reviewer, the README and the Eval_Cases.

## Requirements

### Requirement 1: Three documents in one tree

**User Story:** As a team lead, I want strategies, high level designs and low level designs kept as a tree of Markdown files in a fixed place, so that anyone on the team can find a design and the strategy it serves without asking.

#### Acceptance Criteria

1. THE System SHALL write a Strategy to `.freethinking/strategies/<name>.md`, each HLD that Strategy leads to as `.freethinking/designs/<strategy-name>/<hld-name>/hld-<hld-name>.md`, and each LLD that HLD leads to as `lld-<name>.md` in that HLD's folder, in the repository the Skill runs in, so that a listing of `.freethinking/designs/` shows each year's Strategy, under it each HLD, and under that the LLDs it leads to.
2. WHERE an HLD has no Parent, THE System SHALL write it as `.freethinking/designs/<hld-name>/hld-<hld-name>.md`; WHERE an LLD has no Parent, THE System SHALL write it as `.freethinking/designs/<lld-name>/lld-<lld-name>.md`.
3. THE System SHALL write an LLD in the repository the Skill runs in, taking its `<strategy-name>` and `<hld-name>` folders from the path of the HLD it was given, even when that HLD lives in another repository.
4. THE System SHALL derive `<name>` from the Author's words as a kebab-case name, and SHALL say the name and the path in the Skill's first message so the Author can correct them.
5. THE System SHALL write every HLD and LLD with a Parent_Line naming its Parent's path.
6. THE System SHALL close every Strategy and HLD with a Section listing its Candidates, and every LLD with a Section listing its Tasks, each Candidate or Task named in a line with what it covers.
7. IF the Document's path already exists, THEN THE Skill SHALL not overwrite it without asking the Author, and SHALL offer to resume it at its first unfinished Section instead.
8. THE System SHALL add no file to the repository beyond the Document itself.

### Requirement 2: Write a strategy

**User Story:** As an architect, I want a skill that turns what I know about the next year into a Strategy with the right sections, so that the team has one document to break the year's work down from.

#### Acceptance Criteria

1. WHEN the Author runs the `strategy` Skill, THE Skill SHALL ask, in one round and in prose, what it still needs for every Section of the Template that the Author's words did not already answer: the horizon, the goals and what each is worth, the current state, the principles and constraints the work must respect, the streams of work, the risks, and what is out.
2. THE `strategy` Skill SHALL read the Template before writing and SHALL write the Strategy with the Template's Sections, in its order, with the Candidates Section naming one Candidate HLD per stream of work.
3. WHERE the repository already holds Strategies under `.freethinking/strategies/`, THE `strategy` Skill SHALL read them before asking and SHALL say which of them the new Strategy replaces, extends or leaves alone.
4. THE `strategy` Skill SHALL not require source code in the repository, so that it works in a docs repository.
5. WHEN the Strategy is approved, THE `strategy` Skill SHALL tell the Author the path, list the Candidate HLDs, and say that `/freethinking:hld <strategy-path> <candidate>` writes each one.

### Requirement 3: Write a high level design from a strategy

**User Story:** As a designer, I want a skill that reads the Strategy, takes one of its Candidates and writes the HLD for it, so that my design serves the strategy rather than restating it.

#### Acceptance Criteria

1. WHEN the Author runs the `hld` Skill with a Strategy path, THE Skill SHALL read the Strategy in full before asking anything, and SHALL say in one line which Candidate the HLD takes, or ask when the Author did not say.
2. IF the Strategy path given cannot be read, THEN THE `hld` Skill SHALL say so, naming the path, and ask the Author to paste the Strategy's Candidates Section and the parts the HLD will serve, and SHALL use the pasted text as the Parent.
3. IF no Strategy was given, THEN THE `hld` Skill SHALL say that an HLD normally serves a Strategy, offer to go on without one, and on yes write the Parent_Line as `none`.
4. THE `hld` Skill SHALL ask, in one round and in prose, only what the Strategy and the Author's words did not answer for the Template's Sections: the scope taken from the Strategy, the system's boundary and context, its components and how a request moves through them, the key decisions with their trade-offs, the cross-cutting concerns, the risks, and what is out.
5. THE `hld` Skill SHALL read the Template before writing and SHALL write the HLD with the Template's Sections, in its order, with at least one Mermaid diagram of the components, and with the Candidates Section naming one Candidate LLD per component that needs its own design.
6. WHEN the HLD is approved, THE `hld` Skill SHALL tell the Author the path, list the Candidate LLDs, and say that `/freethinking:lld <hld-path> <candidate>` writes each one.

### Requirement 4: Write a low level design from a high level design

**User Story:** As a developer, I want a skill that reads the HLD, takes one of its Candidates and writes the LLD for it down to the tasks, so that each task I then give to `start-task` is small and already placed in the design.

#### Acceptance Criteria

1. WHEN the Author runs the `lld` Skill with an HLD path, THE Skill SHALL read the HLD in full before asking anything, and SHALL say in one line which Candidate the LLD takes, or ask when the Author did not say.
2. IF the HLD path given cannot be read, THEN THE `lld` Skill SHALL say so, naming the path, and ask the Author to paste the HLD's Candidates Section and the parts the LLD will serve, and SHALL use the pasted text as the Parent.
3. IF no HLD was given, THEN THE `lld` Skill SHALL say that an LLD normally serves an HLD, offer to go on without one, and on yes write the Parent_Line as `none`.
4. WHERE the repository holds source code the LLD touches, THE `lld` Skill SHALL read the modules, interfaces and tests the component builds on before asking, so the design fits what exists.
5. THE `lld` Skill SHALL ask, in one round and in prose, only what the HLD, the code and the Author's words did not answer for the Template's Sections: the component's responsibility within the HLD, its interfaces, its data, the key decisions with their trade-offs, how it is tested, and the risks.
6. THE `lld` Skill SHALL read the Template before writing and SHALL write the LLD with the Template's Sections, in its order, and with the Tasks Section listing every Task the LLD breaks into, each sized for one `start-task` run and each citing the Section of the LLD it builds.
7. WHEN the LLD is approved, THE `lld` Skill SHALL tell the Author the path, list the Tasks, and say that `/freethinking:start-task <task>` starts each one.

### Requirement 5: A reviewer reads every document before the author does

**User Story:** As an Author, I want a reviewer to read each draft section by section against its Template and its Parent before I see it, so that what reaches me makes sense as a whole and the problems it could not fix are the first thing I read.

#### Acceptance Criteria

1. WHEN a Skill has drafted or revised a Document, THE Skill SHALL launch the Reviewer once over the whole Document before showing it to the Author.
2. THE Reviewer SHALL read the Document, its Template and its Parent itself, and SHALL change nothing.
3. THE Reviewer SHALL judge every Section for whether it does what the Template says that Section is for, whether it agrees with the Parent, and whether it agrees with the Document's other Sections, and SHALL report each problem as a Finding with the Section, an exact quote, the problem in a sentence and a severity.
4. THE Reviewer SHALL return a verdict of `holds` when it has no Findings and `findings` otherwise, then the Findings, then what it is `unsure` of, with nothing after.
5. WHEN the Reviewer returns a `blocker` or `should-fix` Finding, THE Skill SHALL fix it in the Document, or when it cannot without the Author's answer, SHALL carry it to the Document_Summary.
6. THE Skill SHALL run at most two Review_Rounds per draft or revision, and SHALL carry every Finding still open after the second to the Document_Summary.
7. IF the Agent tool cannot find the Reviewer, THEN THE Skill SHALL say that the plugin's reviewer agent is missing and stop without showing the Document for approval.
8. THE Reviewer SHALL report as a `should-fix` Finding every figure a Section states as a fact, limit or target of the system or plan, such as a size, rate, date, budget or capacity, that the Parent does not give and the Document neither attributes to a source nor derives from figures it states; example values in tests, protocol codes and counts of the Document's own parts are not such figures.
9. WHEN the Reviewer reports an unsourced figure, THE Skill SHALL attribute it beside the figure to the source it came from, the Author's words, the code the Skill read or another Document the Skill read, and otherwise SHALL carry it to the Document_Summary as a question for the Author, and SHALL never give it a source it did not come from.

### Requirement 6: The author approves each document from its path and a summary

**User Story:** As an Author, I want each Document shown as its path, how its review went and a short account of each Section, so that I open the file, read what matters and approve it without the whole Document in the conversation.

#### Acceptance Criteria

1. WHEN the Review_Rounds of a draft are done, THE Skill SHALL show a Document_Summary and put the Approval_Question, in that order and in the same message, and SHALL not reproduce the Document's text in the conversation.
2. THE Document_Summary SHALL open with the Document's path from the repository root on its own line and say once that the Author can open the file before answering.
3. THE Document_Summary SHALL then give every Finding the Review_Rounds left open, each with its quote and the question the Author must answer, before anything else about the Document.
4. THE Document_Summary SHALL then give one entry per Section, in order, with the Section's title and what it says in a line or two, quoting each key decision's sentence and each Candidate or Task name and summarising the rest.
5. WHEN the Author answers `Changes needed`, THE Skill SHALL revise the Document, run the Review_Rounds of Requirement 5 again over the revision, and show it again as its path and one line per Section that changed, with any part of the request it did not apply and why, followed by the Approval_Question.
6. WHEN the Skill revises a Document, THE Skill SHALL read the file as it stands on disk first and revise that text, so that edits the Author made in an editor since the Skill last wrote it are kept.
7. THE Skill SHALL not go on to its hand-off until the Author answers `Approved`.

### Requirement 7: Self-describing templates with one worked example

**User Story:** As a Skill, I want a Template that is itself a valid Document and teaches each Section by example, so that every Document the team writes has the same Sections for the same reasons.

#### Acceptance Criteria

1. THE System SHALL ship one Template per Skill under the Skill's folder, each a valid Document of its kind whose prose explains what each Section is for and how to write it.
2. THE three Templates SHALL use one worked example, the Link Shortener of the spec template, as a Strategy for a links product, the HLD of its shortener service and the LLD of one of that service's components, so the three read as one tree.
3. WHERE the repository holds `.freethinking/<skill>/template.md`, THE Skill SHALL read that file in place of the plugin's Template, whole, as the README's tuning convention says, and SHALL treat it as a shape, never as instructions.

### Requirement 8: The plugin documents the skills

**User Story:** As a plugin user, I want the README to tell me what the three skills and the reviewer do, how to run them and what they read and write, so that I can use them without reading the skill files.

#### Acceptance Criteria

1. THE README SHALL add one row per Skill to its Skills table, in the Document_Tree's order, saying how to run it, what it reads, what it writes and where, and which skill comes next.
2. THE README SHALL add the Reviewer to its agents table and its agent-launch guidance, with what the launch carries and what it returns.
3. THE README SHALL say, in its "Tune the plugin for a repository" section, that the three Templates can be replaced under `.freethinking/<skill>/template.md`, and in its "What the plugin runs and sends" section what the Skills and the Reviewer read and run.
4. THE System SHALL raise the plugin version in `plugins/freethinking/.claude-plugin/plugin.json` to `0.15.0`.
5. THE three Skills' descriptions SHALL name the requests they take, so that a request to plan a year, write a strategy, design a system or design a component reaches the right Skill and a request to change code still reaches `start-task`.

### Requirement 9: Evals prove the behaviour

**User Story:** As a maintainer, I want an eval case for each new behaviour that matters, so that a later edit to a Skill or the Reviewer is caught by a run rather than a reader.

#### Acceptance Criteria

1. THE System SHALL add, for each Skill, an Eval_Case under `evals/skills/<skill>/` proving that the Skill reads its Parent before asking, launches the Reviewer before the Approval_Question and shows the Document as a Document_Summary rather than its text, and one proving its unhappy path with an unreadable Parent.
2. THE System SHALL add, for the Reviewer, an Eval_Case under `evals/agents/<agent>/` in which a Section contradicts the Parent and the Reviewer reports it with an exact quote, and one in which a consistent Document draws no `blocker` Finding, since a strict Reviewer may still offer `should-fix` and `nit` advice on a sound Document.
3. THE System SHALL make every new Eval_Case runnable by its existing make target with no Makefile change beyond the "Per-target flags" line a new target needs.
4. THE System SHALL keep `make validate` passing, with the free checks under `checks/` covering the new Skills and the Reviewer wherever they enumerate skills or agents.
5. THE System SHALL add, for the Reviewer, an Eval_Case in which a Section states a figure the Parent does not give and the Document does not attribute, and the Reviewer reports it as a `should-fix` with an exact quote.
