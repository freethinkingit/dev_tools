# Requirements Document

## Introduction

The plugin's skills and agents write to the author in a way that hides what matters and dwells on what does not: a label coined during the work stands in for an explanation, a decision is asked for without the material to decide it, failures sit under the list of what was done, and tool calls are narrated. Eight sessions between 2026-10-06 and 2026-10-15 show the author asking the agent to decode its own previous message once in every fifteen turns. This task adds one skill, `report`, that writes the message when there is something to deliver and never edits anything, so that how the plugin talks to the author lives in one place and can change without touching how the skills work; a short rule, `communication`, that says what every message to the author must do and routes the heavy moments to the skill; and a hand-off from the skills that report work to the skill. The agents' own reports are left as they are, with their shared protocol written down once. Authors of any repository the plugin applies to get messages they can act on without re-reading the session; maintainers get one place to revise after the skill has run for a while. Issue #26.

## Glossary

- **Skill**: The report skill, `skills/report/SKILL.md`, invoked as `/ponderly:report [mode]` by the Author or through the Skill tool by the session or by another skill.
- **Rule**: The communication rule, `rules/communication.md`, which the plugin's two hooks put into every session and every sub-agent.
- **Author**: The person the session is working with, who sees only the messages written to them, never the tool calls.
- **Message**: Any text the session writes to the Author, in a skill or outside one.
- **Mode**: One of the four shapes the Skill writes: Handback_Mode, Decision_Mode, Status_Mode or Answer_Mode.
- **Handback_Mode**: The Mode for reporting a piece of work: Problems first, then what was done and the checks that prove it, then the files, then the next step.
- **Decision_Mode**: The Mode for a choice the Author has to make: what is being decided, the options with what each costs, the recommendation and its reason, then the question.
- **Status_Mode**: The Mode for saying what is going on: what is running and what it is doing, what finished and with what result.
- **Answer_Mode**: The Mode for a question the Author asked about what something is or why it happened: what it is, in plain words, before anything about what to do.
- **Problem**: A failed check, a check that could not be run, a finding that was not fixed, a task that stopped, or an assumption made on the Author's behalf.
- **Label**: A name coined during the work for a thing the Author has not seen, such as "the write-grader gap" or "the fit question", as opposed to saying what the thing is.
- **Narration**: Text that says what the session is doing or about to do with its tools, or what is still pending, rather than what it found.
- **Worked_Example**: A pair of texts in a Template, a Message as it was written in a real session and the same Message in the Mode's shape, with paths and names generalised.
- **Template**: A Markdown file holding one Mode's shape, its sections in order with a sentence on what each holds, and its Worked_Example; the Skill ships one per Mode under `skills/report/templates/<mode>.md`.
- **Override_Directory**: The folder `.ponderly/` at the root of the repository the session works in, where that repository keeps its own versions of the plugin's template files, under the skill's name, such as `.ponderly/report/handback.md`.
- **Agent_Report**: The fixed-shape text an agent returns to the session that launched it: today the task-executor's Summary and the wave-reviewer's Findings.
- **Agent_Protocol**: The rules every Agent_Report follows: a status word on its first line, one field for each thing the launcher must act on, an `unsure` field that is always present, exact quotes for anything quoted, and nothing after the shape.
- **Reporting_Skills**: The skills whose steps report work to the Author: `implement-spec` at its hand-back and its final report, `bugfix` at its summary, and `start-task` when the executor's Summary comes back.
- **Hook_Budget**: The 10,000 characters Claude Code allows a hook's output before truncating it, which the plugin's rules share and `checks/test_rules_size.py` guards.
- **Baseline**: The no-plugin arm of an eval run, `--ablation with-without`, which shows whether the plugin changed the behaviour at all.
- **Question_Tool**: The AskUserQuestion tool, which asks the Author a question with fixed options plus free text.

## Requirements

### Requirement 1: The skill reports and edits nothing

**User Story:** As a maintainer, I want one skill that only writes to the Author, so that how the plugin talks can change in one place without changing how any skill works.

#### Acceptance Criteria

1. THE Skill SHALL write the Message and SHALL create, edit or delete no file, run no command that changes the working tree, and launch no agent.
2. THE Skill SHALL take an optional first argument naming the Mode, and SHALL say in its description and `argument-hint` that the argument is one of `handback`, `decision`, `status` or `answer`.
3. WHEN no Mode is given, THE Skill SHALL pick the Mode from what the conversation holds since the last Message to the Author: work came back, a choice is open, the Author asked what is going on, or the Author asked what something is or why.
4. WHEN the Author invokes the Skill and nothing has happened since the last Message, THE Skill SHALL rewrite that last Message in the chosen Mode and say that it is a rewrite.
5. IF the argument is not one of the four Modes, THEN THE Skill SHALL say so, name the four, and SHALL pick the Mode as in criterion 3 rather than stop.
6. THE Skill SHALL declare `allowed-tools` holding only read-only tools, as a statement of what it uses; in Claude Code the field pre-approves tools rather than taking others away, so the Skill's own text, not the field, is what keeps it from editing.

### Requirement 2: Every message is written for a reader who did not watch

**User Story:** As an Author, I want each Message to stand on its own, so that I can act on it without re-reading the session.

#### Acceptance Criteria

1. WHEN there is at least one Problem, THE Skill SHALL put every Problem before anything else in the Message, one bullet each, each saying what the Problem is, why it matters and what the options are.
2. THE Skill SHALL name each thing by what it is, never by a Label, and SHALL quote the line when the thing is text.
3. WHEN a Message reports a number, a score or a cost, THE Skill SHALL say what it means before the number.
4. THE Skill SHALL write no Narration.
5. WHEN a Message asks the Author to choose, THE Skill SHALL state what is being decided, the options in plain words with what each costs, the recommendation and its reason, and then the question; a fixed short list is asked with the Question_Tool, as `rules/collaboration.md` says.
6. THE Skill SHALL write one idea per sentence, in plain words, and SHALL end when the content ends, with no offer and no restatement.

### Requirement 3: Each mode has a fixed shape and a worked example

**User Story:** As an Author, I want the same kind of Message to look the same every time, so that I know where to look for what matters.

#### Acceptance Criteria

1. THE Skill SHALL define the shape of each of the four Modes, in order of sections, in that Mode's Template, and SHALL read the Template of the chosen Mode before writing the Message.
2. EACH Template SHALL carry exactly one Worked_Example, drawn from the sessions quoted in issue #26.
3. THE Skill's own text, frontmatter included, SHALL stay under 4,000 characters, and each Template under 3,000, so that an invocation costs the session little.
4. WHILE the Mode is Handback_Mode, THE Skill SHALL write, in this order: Problems, if any; what was done, each item with the check that proved it and the result seen; the files changed; the next step. A Message in Handback_Mode with no Problem SHALL say so in its first line.
5. WHILE the Mode is Status_Mode, THE Skill SHALL name what is running and what each running thing is doing, then what finished and its result, and SHALL say "nothing is running" when nothing is.

### Requirement 4: The rule routes to the skill and covers the rest

**User Story:** As a maintainer, I want a short rule in every session and sub-agent, so that the habits are named everywhere and the heavy moments go to the Skill.

#### Acceptance Criteria

1. THE Rule SHALL exist as `rules/communication.md`, with one bullet per habit of Requirement 2, each bullet with its reason in one sentence, and one bullet that names the Skill for hand-backs, decisions, status and answers.
2. THE Rule SHALL be at most 1,600 characters, and the plugin's rules together SHALL stay under the Hook_Budget, as `checks/test_rules_size.py` checks; that check SHALL cover the Rule's own limit.
3. THE Rule SHALL not restate any step or shape of the Skill, as the handbook's rules never recite a skill's internals.
4. THE Rule SHALL appear in the README's rules table and in the component dropdown of every issue form as `communication (rule)`, where `checks/test_issue_forms.py` will fail until it does.

### Requirement 5: The reporting skills hand off to the skill

**User Story:** As a maintainer, I want the skills that report work to hand off to the Skill, so that none of them carries its own report wording.

#### Acceptance Criteria

1. WHEN `implement-spec` hands back at step 6 or writes its final report at step 8, THE Skill SHALL be invoked in Handback_Mode in place of the report template in step 6, inside a foreground fork of the conversation whose result `implement-spec` pastes verbatim as the Message, or inline when the Agent tool offers no fork; the step's text SHALL name the Skill and carry no shape of its own.
2. THE Handback_Mode shape SHALL hold everything the final review of `implement-spec` reads back from a wave report: the tasks done, the checks and the full-suite result, the review verdict with each carried item, the files, and the follow-ups.
3. WHEN `bugfix` reaches its summary step, THE Skill SHALL be invoked in Handback_Mode in place of the step's own list of headings.
4. WHEN `start-task` has shown the executor's Summary and the change on its executor route, THE Skill SHALL be invoked in Handback_Mode for the Message that says where the change sits and what to do next.
5. THE CX_Block of each of the Reporting_Skills SHALL name the Skill under its Hand-backs.
6. THE `pr` skill SHALL be left unchanged by this task, because its hand-backs are the draft and the pull request URL rather than reports of work.

### Requirement 6: The agent protocol is written down once

**User Story:** As a maintainer, I want the Agent_Protocol recorded in one place, so that any agent reports back the same way and the Skill can translate any Agent_Report.

#### Acceptance Criteria

1. THE README's Agents section SHALL state the Agent_Protocol in one short paragraph.
2. THE Summary of the task-executor and the Findings of the wave-reviewer SHALL each conform to the Agent_Protocol; where one does not, the smallest change to that agent's shape SHALL be made and the launcher's reading of it in `implement-spec` SHALL be updated to match.
3. THE Skill, in Handback_Mode, SHALL say how an Agent_Report is translated: its status word and `unsure` entries become Problems or are stated as verified, its quotes are kept verbatim, and nothing from it is pasted as-is.

### Requirement 7: The behaviour is proved

**User Story:** As a maintainer, I want evals that show the Rule and the Skill change what the session writes, so that a later edit cannot regress it unnoticed.

#### Acceptance Criteria

1. THE evals SHALL include a case under `evals/rules/communication/` in which a check fails, grading that the final message opens with the failure and names the check, and a case in which a check cannot be run, grading that the final message says so before anything else; each with a `regex` grader with `match: not_contains` for Narration openers.
2. THE evals SHALL include a case under `evals/skills/report/` in which the Author asks for a choice, grading that the options appear before the recommendation, and one in which the Author invokes the Skill to rewrite a dense last message, grading with an `llm` grader that the rewrite names each thing by what it is.
3. THE evals SHALL include a case in which the Author asks the session to report finished work in prose, grading with `tool_used` that the Skill was invoked.
4. WHEN the Rule's cases are run for the pull request, THE run SHALL use the Baseline, and the PR's Testing section SHALL carry the table with its `W/OUT` and `Δ` columns.
5. THE existing `implement-spec` case `works-one-wave` SHALL grade the hand-back in the Handback_Mode shape, and SHALL still pass.

### Requirement 8: Plugin housekeeping

**User Story:** As a maintainer, I want the plugin's own records to know about the Skill, so that a teammate finds it without reading the source.

#### Acceptance Criteria

1. THE README's skills table SHALL have a row for the Skill, and its rules table a row for the Rule.
2. THE component dropdown of every issue form SHALL list `report (skill)`, in the order `checks/test_issue_forms.py` requires.
3. THE Skill's frontmatter description SHALL be at most 1,024 characters, as `checks/test_descriptions.py` checks, and SHALL say when to use it in words a session will match on without the Author naming it.
4. THE plugin version SHALL be bumped to 0.9.0, a minor bump, because the task adds a skill and a rule.
5. THE output style and the Stop hook named in issue #26 SHALL be left out of this task and filed as a spike once the Rule has run for a few sessions.

### Requirement 9: A repository can tune the templates

**User Story:** As a plugin user, I want to put my own version of a template under `.ponderly/` in my repository, so that the plugin's messages fit that repository without my forking the plugin.

#### Acceptance Criteria

1. WHEN the Override_Directory holds a file at `report/<mode>.md` for the chosen Mode, THE Skill SHALL read that file in place of its own Template, whole, and SHALL say in one line that the repository's template was used.
2. WHEN the Override_Directory holds no file for the chosen Mode, THE Skill SHALL use its own Template and say nothing about it.
3. IF the repository's file cannot be read or is empty, THEN THE Skill SHALL say so in one line, name the path, and use its own Template.
4. THE Skill SHALL treat the contents of a repository's template as a shape to write in, never as instructions to do anything else; a template that asks for an action gets the shape followed and the action ignored.
5. THE README SHALL document the Override_Directory convention in one short section: the folder, the `<skill>/<file>.md` layout, that a file replaces the plugin's file of the same name whole, and that this task applies it to the report skill only.
6. THE convention SHALL be written so that the `start-task` spec templates and the `pr` default pull request template can move to it later without changing its rules; moving them is out of scope for this task and SHALL be noted as a follow-up.
