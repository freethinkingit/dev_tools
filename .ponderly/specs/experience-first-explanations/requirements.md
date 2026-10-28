# Requirements Document

## Introduction

When a skill or agent explains a problem or puts a choice to the author, it speaks in the vocabulary of the work: requirement numbers, grader names, file paths, a verdict word. The author then has to ask what it means for the person it lands on before they can decide. Between 2026-10-09 and 2026-10-22 the author asked for that view eight times across two repositories, and every reply written after the request was accepted first time. In the same period one question in three asked with the AskUserQuestion tool arrived with nothing laid out before it, and open design decisions arrived five or six to a message. This task changes the two rules that govern how the plugin talks to the author, `communication` and `collaboration`, and the `report` skill's templates, so that an explanation or a choice is stated as the experience of the person it changes, in one shape, laid out above the question, and so that open decisions are asked one at a time. Authors of any repository the plugin applies to can decide from the message in front of them; owners approve consequences they can see. Issues #56 and #57.

## Glossary

- **Rule**: The communication rule, `rules/communication.md`, which the plugin's two hooks put into every session and every sub-agent.
- **Collaboration_Rule**: The collaboration rule, `rules/collaboration.md`, loaded the same way, which says how questions are asked.
- **Skill**: The report skill, `skills/report/SKILL.md`, and its four Templates.
- **Template**: A Markdown file under `skills/report/templates/<mode>.md` holding one mode's shape and its Worked_Example.
- **Worked_Example**: The Before and After texts in a Template, a real message and the same message in the mode's shape.
- **Author**: The person the session is working with, who sees only the messages written to them.
- **Operator**: The person running the skill or agent in the session; what they see on screen and have to do next.
- **User**: The person who uses what is being built, such as a template author, a reader of the docs or a customer of the product.
- **Owner**: The person accountable for the code and the repository, who takes on a risk, a cost, a spec edit or unverified work.
- **Role**: One of Operator, User or Owner.
- **Leading_Role**: The Role whose experience a Choice or Problem changes, named first in the Message.
- **Choice**: Anything the Author is asked to decide, whether put in prose or with the Question_Tool.
- **Open_Decision**: A Choice whose answer needs the Author's judgement and the context behind it, such as a design option, a spec edit or what to do about a finding.
- **Fixed_Choice**: A Choice whose answer is a fact or a short fixed list that needs no context to pick, such as a branch name, a version, who runs a command, or a plain yes.
- **Problem**: A failed check, a check not run, a finding not fixed, a task that stopped, or an assumption made on the Author's behalf.
- **Mechanism**: How a thing works or what in the code, spec or eval it touches: requirement numbers, grader names, file paths, verdicts and the like.
- **Layout**: The text that lays out a Choice before its question: what is being decided, what each option means for the Leading_Role, the recommendation and its reason.
- **Question_Tool**: The AskUserQuestion tool, which puts a question with fixed options plus free text.
- **Message**: Any text the session writes to the Author, in a skill or outside one.
- **Rule_Limit**: The 1,600 characters `checks/test_rules_size.py` allows each of the Rule and the Collaboration_Rule.
- **Case**: One eval case under `evals/rules/<rule>/<case>/`, run by `make eval-rule-<rule>`.
- **Baseline**: The no-plugin arm of an eval run with `--ablation with-without`.

## Requirements

### Requirement 1: Lead with the Role the choice changes

**User Story:** As an Author, I want a Problem or a Choice stated as what the person it lands on experiences, so that I can decide without first asking what it means for them.

#### Acceptance Criteria

1. WHEN a Message states a Problem or lays out a Choice, THE Rule SHALL require it to name the Leading_Role's experience before any Mechanism: who is affected, what they see or have to do, and what changes for them under each option.
2. THE Rule SHALL say how the Leading_Role is picked: the User when the Choice changes what the built thing does; the Operator when it changes how a skill or agent behaves in the session; the Owner when it is whether to accept a risk, a cost, a spec edit or unverified work.
3. THE Rule SHALL require one Leading_Role per Problem or Choice, with a second Role named only where its experience differs from the first.
4. WHERE a Choice changes nothing any Role experiences, such as a name or a version, THE Rule SHALL require no Role to be named.
5. IF a Message names a Problem or an option by a Mechanism alone, THEN THE Rule SHALL count that as a thing not named by what it is.

### Requirement 2: One shape for an explanation or a decision

**User Story:** As an Author, I want every explanation and every decision to come in the same order, so that I know where the answer to "what happens to me" is before I read it.

#### Acceptance Criteria

1. THE Rule SHALL name the shape of an explanation or a Choice in this order: what the thing is and what happens when it is used, then what each option means for the Leading_Role in practice, then the recommendation and its reason, then what is needed from the Author.
2. THE Skill's decision Template SHALL put the Leading_Role's experience into its "What is being decided" and "Options" sections, each option saying what the Leading_Role sees or takes on under it before what it costs.
3. THE Skill's answer Template SHALL put the Leading_Role's experience into its "What it is" section, before "Why or how".
4. THE Skill's handback Template SHALL require each Problem bullet to open with who it lands on and how, before the Mechanism and the options.
5. WHEN a Template changes, THE Skill SHALL keep a Worked_Example in it whose After text shows the Leading_Role named first and the Mechanism after.
6. THE Skill SHALL keep `SKILL.md` under 4,000 characters and each Template under 3,000, as `checks/test_report_skill.py` requires.

### Requirement 3: The Layout comes above the question

**User Story:** As an Author, I want a question asked with the Question_Tool to arrive with its Layout above it in the same Message, so that I never see a list of options for a problem that was not laid out.

#### Acceptance Criteria

1. WHEN a Choice is asked with the Question_Tool, THE Rule SHALL require the Message that carries the call to hold the Layout above it, and the tool's options to hold only the choices.
2. IF a Question_Tool call would be the whole Message, THEN THE Rule SHALL count that as a decision asked before it was laid out.
3. THE Rule SHALL leave a skill's own fixed stops as they are where the Layout already precedes them, such as an approval asked after a document's summary.

### Requirement 4: The rules stay within their limits

**User Story:** As a maintainer, I want the two rules to carry this without growing past the hook's limits, so that every session still loads every rule whole.

#### Acceptance Criteria

1. THE Rule SHALL carry Requirements 1 to 3 by rewriting its existing "Lay out a decision before asking it" bullet, and SHALL stay at or under the Rule_Limit.
2. THE Collaboration_Rule SHALL carry Requirement 5 and SHALL stay at or under the Rule_Limit.
3. THE System SHALL keep the output of `hooks/load-rules.sh` under 10,000 characters, as `checks/test_rules_size.py` requires.
4. IF the rewritten Rule cannot hold the meaning of Requirements 1 to 3 within the Rule_Limit, THEN THE System SHALL raise the communication limit in `checks/test_rules_size.py` and the README by the smallest amount that fits, and say so in the pull request.

### Requirement 5: Open decisions one at a time

**User Story:** As an Author, I want an Open_Decision asked on its own with its context, and Fixed_Choices still batched, so that I answer each decision having read what it rests on.

#### Acceptance Criteria

1. THE Collaboration_Rule SHALL split its "Batch the questions" bullet by kind of question: Fixed_Choices asked together in one round; an Open_Decision asked one at a time.
2. WHEN an Open_Decision is asked, THE Collaboration_Rule SHALL require its context first, what the ticket, code or report says, then the Layout, then the question, and the next Open_Decision only after the answer.
3. WHEN a Message would carry more than one Open_Decision, THE Collaboration_Rule SHALL require it to name how many there are and ask the first.
4. THE System SHALL leave `start-task`, `implement-spec` and the Skill to follow the Collaboration_Rule without restating it, changing a skill's text only where it contradicts the rule.

### Requirement 6: Evals prove the behaviour

**User Story:** As a maintainer, I want eval cases that show the rules change what Claude writes, so that a wording change is measured and not assumed.

#### Acceptance Criteria

1. THE System SHALL add a communication Case that hands Claude a failing check whose effect on a User is not obvious from its name, with graders that pass only when the Message states the User's experience before the Mechanism.
2. THE System SHALL add a communication Case that puts a Choice with a short fixed list of answers, with graders that pass only when the Message carries a Layout with a recommendation and the options follow it as lines in prose, the form the collaboration rule gives where the Question_Tool is absent, as it is in the eval sandbox, and the record of how the tool would have been called, rather than standing alone.
3. THE System SHALL add a collaboration Case that gives a request holding three Open_Decisions, with graders that pass only when the first reply asks exactly one of them, with its options.
4. THE System SHALL keep every existing communication and collaboration Case passing, including `short-list-asks-with-tool`.
5. WHEN the three new Cases are run for the pull request, THE System SHALL run them with `--ablation with-without` and report the table as it comes out, with the Baseline score beside the plugin score.
6. IF a new Case scores the same in both arms, THEN THE System SHALL read the Baseline's transcript and say whether its graders passed on the behaviour or passed for another reason, and SHALL not count the equal score as a failure of this task.
7. THE System SHALL give each Case a prompt whose description says what it proves and which requirement it serves, and SHALL keep `checks/test_eval_cases.py` passing.

### Requirement 8: Every message template follows the rule

**User Story:** As an Author, I want every template the report skill ships to ask for who a problem lands on, so that no mode hands me the old shape.

#### Acceptance Criteria

1. THE Skill's status Template SHALL require each Problem bullet to open with who it lands on and how, before the Mechanism and the options, as the handback Template does.
2. THE System SHALL check every template under `plugins/ponderly/skills/*/` and every skill's text for the old Problems shape, "what it is, why it matters, the options" without who it lands on, and SHALL report any found.

### Requirement 7: The plugin's own documents follow

**User Story:** As a maintainer, I want the README and the version to match the rules, so that a reader installing the plugin reads what it now does.

#### Acceptance Criteria

1. THE System SHALL update the README rows for `rules/communication.md`, `rules/collaboration.md` and the `report` skill to say what each now requires, in the rows' existing shape.
2. THE System SHALL bump the plugin version in `plugins/ponderly/.claude-plugin/plugin.json` to the next minor version.
3. THE System SHALL keep `make validate` passing.
4. THE System SHALL leave the `pr` skill's walkthrough as it is; its change is #69.
