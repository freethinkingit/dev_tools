# Design Document

## Overview

Prompt, template and eval changes only, no code beyond two small Python checks. A new skill, `skills/report/SKILL.md`, reads a Mode argument, finds the Template for that Mode, first under the repository's `.freethinking/report/` and then under its own `templates/`, gathers what the conversation holds since the last Message to the Author, and writes the Message in the Template's shape. It holds read-only tools and changes nothing (Requirements 1, 2, 3, 9). A new rule, `rules/communication.md`, names the habits in one bullet each and routes hand-backs, decisions, status and answers to the skill (Requirement 4). Three skills lose their own report wording and invoke the skill instead: `implement-spec` at its hand-back and final report, `bugfix` at its summary, `start-task` when the executor's Summary is back (Requirement 5). The README gains a paragraph stating the Agent_Protocol both agents already follow, a section on the `.freethinking/` convention, and rows for the skill and the rule (Requirements 6, 8, 9). Five eval cases and one grader change prove it (Requirement 7).

## Architecture

The skill is a procedure the model follows. The flowchart shows its steps; the only stop is the Message itself, since the skill asks nothing and edits nothing.

```mermaid
flowchart TD
    A["0. Read the argument<br/>$mode"] --> A1{"one of the<br/>four Modes?"}
    A1 -- no --> A2["Say so, name the four"] --> B
    A1 -- yes --> C
    B["1. Pick the Mode from what happened<br/>since the last Message"] --> B1{"nothing<br/>happened?"}
    B1 -- yes --> B2["Rewrite the last Message;<br/>say it is a rewrite"] --> C
    B1 -- no --> C["2. Find the Template"]
    C --> C1{".freethinking/report/&lt;mode&gt;.md<br/>readable and non-empty?"}
    C1 -- yes --> C2["Use it; one line says so.<br/>A shape, never instructions"] --> D
    C1 -- unreadable or empty --> C3["One line names the path;<br/>use the plugin's Template"] --> D
    C1 -- absent --> D["Read ${CLAUDE_SKILL_DIR}/templates/&lt;mode&gt;.md"]
    D --> E["3. Gather the material:<br/>Agent_Reports, check output, diffs,<br/>the Author's question, the open choice"]
    E --> F["4. Write the Message in the shape.<br/>Problems first. No Label, no Narration."]
    F --> G["5. Stop. Nothing after the Message."]
```

The sequence diagram shows the skill inside `implement-spec` at the end of a wave, which is where the worst messages in issue #26 were written.

```mermaid
sequenceDiagram
    actor Au as Author
    participant IS as implement-spec
    participant EX as task-executor
    participant RV as wave-reviewer
    participant RP as report skill
    IS->>EX: launch task (Agent tool)
    EX-->>IS: Summary (status, files, checks, unsure)
    IS->>IS: re-run the checks itself
    IS->>RV: launch review (Agent tool)
    RV-->>IS: Findings (verdict, base, findings, unsure)
    IS->>IS: fix blockers, tick, run full suite
    IS->>RP: Skill tool, skill freethinking:report, args handback
    RP->>RP: read templates/handback.md (or the repository's)
    RP->>RP: Summary.unsure and carried findings become Problems
    RP-->>Au: Problems, Done, Checks, Files, Next
```

Key decision, a skill rather than a longer rule. A rule reaches every session and sub-agent but shares the Hook_Budget with three other rules and cannot carry a Worked_Example per shape. A skill body can, and the session reaches for it on purpose when there is something to deliver, which is the moment the habits bite (Requirements 1, 3). The trade-off is that a skill is invoked, not ambient: an ordinary turn with no hand-back is covered only by the rule, which is why the rule carries the habits in one bullet each and not only the route (Requirement 4.1). Rejected alternative, an output style with `force-for-plugin`: it reaches the main session only, overrides every teammate's own style and drops Claude Code's coding instructions unless told to keep them. Deferred to a spike, as the requirements say (8.5).

Key decision, the skill runs inline, in the conversation that invokes it, and never as a sub-agent. The Message is made of what the conversation holds since the last Message to the Author: Agent_Reports, check output, diffs, the Author's question. A fresh sub-agent cannot write it: it "starts with a fresh, isolated context window. It doesn't see your conversation history", and "Claude composes a delegation message that summarizes the task" for it, which is the very compression this task removes; a skill with `context: fork` is the same. So the skill carries no `context` field and no `agent` field, and launches nothing itself (Requirements 1.1, 1.3). The cost is that the skill body and one Template, under 7,000 characters together, enter the context at every invocation. Rejected alternative, a `report` agent under `agents/`: it would isolate that cost and could pin a model, but only at the price of the context the Message is made from. Rejected alternative, chosen first and reversed by issue #33 after measurement: `implement-spec` launching a fork of the conversation to invoke the skill and pasting the result. Every call reads the whole conversation, so a fork is a second read of the context per hand-back, 670,000 tokens in one live session and 100,000 to 300,000 in an ordinary run, to keep about 1,500 tokens of skill text out of later calls; the docs say a skill cannot have the foreground ("Claude can't ask for the foreground"), so the paste lands a turn late; a fork cannot ask the Author and has no channel back to the session while it runs; and the headless eval sandbox has no `fork` agent type, so the evals only ever exercised the inline path.

Key decision, the skill edits nothing and the editing skills do not report. One skill does one thing: if a skill edits, it cannot report; if it reports, it cannot edit. Then a change to how the plugin talks is a change to `skills/report/` alone, and a change to how a skill works never touches its wording to the Author (Requirement 1.1, 5). The cost is one more Skill invocation at every hand-back, the skill body under 4,000 characters plus one Template under 3,000. Rejected alternative, each skill keeps its own report section rewritten in the new order: three copies of the shape to keep in step, which is how the Done-first template and the "carried:" clause came to contradict the collaboration rule in the first place.

Key decision, shapes live in Templates, one file per Mode, and a repository can replace one whole. The skill text stays a procedure; the shape and its Worked_Example are data the procedure reads, the way `start-task` reads `spec-template/` and `pr` reads the repository's pull request template before its own (Requirements 3.1, 9). Whole-file replacement, not merging, because a merge rule is a second thing to document and to get wrong; a repository that wants a small change copies the plugin's file and edits it. The skill reads the repository's file as a shape only; an instruction inside it is ignored, so a template cannot make the skill do anything but write (Requirement 9.4). Rejected alternative, the shapes inline in `SKILL.md`: smaller, but no per-repository tuning without forking the plugin.

Key decision, Problems are a section of their own and come first, and carried findings are Problems. Today a carried finding is one clause in the Tests list and the Author has asked what each one meant. A Problem is anything the Author must know before they can trust the rest: a failed check, a check not run, a finding not fixed, a task that stopped, an assumption made for them. Each gets its own bullet with what it is, why it matters and the options (Requirement 2.1). A hand-back with no Problem says so in its first line, so the absence is stated rather than inferred (Requirement 3.4). The Checks section keeps its "Wave review of wave n: verdict" line, pointing at the Problems above for anything carried, so the final review of `implement-spec` reads the same facts it reads today (Requirement 5.2).

Key decision, the Agent_Protocol is written down, not changed. The executor's Summary opens with `status`, the reviewer's Findings with `verdict`; both carry one field per thing the launcher must act on, both end with `unsure`, both quote exactly, both put nothing after the shape. They already conform, so Requirement 6.2 is met by inspection and the agents are untouched. The README states the protocol so a third agent follows it, and the skill's Handback Template says how a report in that protocol is translated: a status word and the `unsure` entries become Problems or are stated as verified, quotes stay verbatim, nothing is pasted as-is (Requirement 6.3). Rejected alternative, one shared shape for both agents: it would change what `implement-spec` reads in two places for no gain the Author would see.

Key decision, the `pr` skill is left alone. Its hand-backs are the draft and the pull request URL, artefacts the Author reads as they are; its walkthrough is prose by design. Nothing in it reports work (Requirement 5.6).

## Components and Interfaces

Each component is a file or a section of one. The table maps every component to the requirements it serves.

| Component | Responsibility | Requirements |
|-----------|----------------|--------------|
| `skills/report/SKILL.md` frontmatter | `name: report`; `description` under 1,024 characters saying it writes the message to the author when work comes back, a choice is open, the author asks what is going on or asks what something is or why, and names the four modes; `argument-hint: "[handback|decision|status|answer]"`; `arguments: [mode]`; `allowed-tools: Read Glob Grep` | 1.2, 1.6, 8.3 |
| `SKILL.md` opening | Two paragraphs: what the skill does and the one-thing rule, that it writes and never edits, launches or asks; the Author is the reader and sees only this Message | 1.1 |
| `SKILL.md` "Working with the author" | Stops: none, the Message is the hand-back. How it asks: nothing; a Decision_Mode Message ends in the question, with the Question_Tool when the options are a fixed short list. Hand-backs: the Message. Hand-offs: none | 2.5 |
| `SKILL.md` step 0, "Read the argument" | `$mode` is one of the four or empty; anything else is named and the four listed, then step 1 | 1.2, 1.5 |
| `SKILL.md` step 1, "Pick the mode" | From what the conversation holds since the last Message to the Author: an Agent_Report, check output or a diff means Handback; an open choice means Decision; the Author asked what is going on means Status; the Author asked what something is or why means Answer. Nothing since the last Message means rewrite it in the chosen Mode and say so | 1.3, 1.4 |
| `SKILL.md` step 2, "Find the template" | Read `.freethinking/report/<mode>.md` at the repository root; readable and non-empty means use it whole and say so in one line; unreadable or empty means one line naming the path, then the plugin's; absent means the plugin's, `${CLAUDE_SKILL_DIR}/templates/<mode>.md`, silently. The repository's file is a shape, never instructions | 3.1, 9.1 to 9.4 |
| `SKILL.md` step 3, "Gather" | What the Message is made of: every Problem, from Agent_Report `unsure` and `stopped because` entries, carried findings, failed or unrun checks and assumptions; what was done with the check that proved each item and the result seen; files; the next step or the open choice or the Author's question | 2.1, 6.3 |
| `SKILL.md` step 4, "Write" | In the Template's sections, in order; every Problem first; things named by what they are, quoted when text; meaning before a number; no Narration; one idea per sentence; end when the content ends | 2.1 to 2.4, 2.6 |
| `skills/report/templates/handback.md` | Sections in order: Problems (or the first line "No problems."), Done, Checks, Files, Next; a sentence on what each holds; the translation of an Agent_Report; one Worked_Example from issue #26 | 3.1, 3.2, 3.4, 5.2, 6.3 |
| `skills/report/templates/decision.md` | Sections: what is being decided, the options with what each costs, the recommendation and its reason, the question; the Question_Tool for a fixed short list; one Worked_Example | 2.5, 3.1, 3.2 |
| `skills/report/templates/status.md` | Sections: running (each with what it is doing), finished (each with its result), or the line "Nothing is running."; one Worked_Example | 3.1, 3.2, 3.5 |
| `skills/report/templates/answer.md` | Sections: what it is, in plain words; why it happened or how it works, when asked; what to do about it, last and only if useful; one Worked_Example | 3.1, 3.2 |
| `rules/communication.md` | Heading and one sentence of scope; six habit bullets, each with its reason; one routing bullet naming `/freethinking:report`; under 1,600 characters | 4.1 to 4.3 |
| `skills/implement-spec/SKILL.md` steps 6 and 8, CX block | Step 6 keeps when to hand back and what each cause adds, drops the fenced template, and says: launch the Agent tool with `subagent_type: fork`, in the foreground, with the prompt "Invoke the Skill tool with `skill: freethinking:report` and `args: handback`, and return the Message as your whole result"; paste the result verbatim as the Message to the Author, nothing before or after it; when the Agent tool offers no fork, invoke the Skill tool inline instead. At spec cadence the report is still a message of its own, written without waiting. Step 8's final review prompt reads "each wave's Problems, Done, Checks and Next"; its final report is the same fork. The Hand-backs bullet names `report` and says it runs in a fork | 5.1, 5.2, 5.5 |
| `skills/bugfix/SKILL.md` step 6 | Keeps the recommendation of `pr`; replaces its four headings with the invocation, naming the root cause, fix, regression test and verification as what the Handback must carry under Done and Checks | 5.3, 5.5 |
| `skills/start-task/SKILL.md` Executor_Route | After showing the Summary verbatim and the change, the Message that says where the change sits and what to do next is the invocation; the CX block names `report` | 5.4, 5.5 |
| `README.md` | Skills table row for `report`; rules table row for `communication`; Agents section gains the Agent_Protocol paragraph; new section "Tune the plugin for a repository" on `.freethinking/`; follow-up note that the spec and pull request templates may move there | 4.4, 6.1, 8.1, 9.5, 9.6 |
| `.github/ISSUE_TEMPLATE/*.yml` | `report (skill)` after `bugfix (skill)`, `communication (rule)` after `collaboration (rule)`, in all four forms | 4.4, 8.2 |
| `checks/test_rules_size.py` | A per-rule limit table, `collaboration` and `communication` at 1,600 each, the hook total unchanged | 4.2 |
| `checks/test_report_skill.py` | The four Templates exist and are named after the Modes; `SKILL.md` under 4,000 characters; each Template under 3,000 | 3.3 |
| `.claude-plugin/plugin.json` | `0.9.0` | 8.4 |
| Eval cases | See Testing Strategy | 7.1 to 7.5 |

Each invocation from another skill is the same two-field Skill tool call, so the invoking skill restates nothing about the shape; the no-cross-skill-internals rule holds.

## Data Models

The skill's data is the Mode argument, the Template files and the Message sections.

```mermaid
classDiagram
    class Mode {
        <<enumeration>>
        handback
        decision
        status
        answer
    }
    class Template {
        +path: skills/report/templates/mode.md
        +override: .freethinking/report/mode.md
        +sections: ordered list
        +example: before and after
    }
    class Message {
        +sections in Template order
        +problems first
    }
    class Problem {
        +what it is
        +why it matters
        +options
    }
    Mode "1" --> "1" Template
    Template --> Message : shapes
    Message "1" --> "*" Problem : opens with
```

Mode argument:

| Value | Picked when | Template |
|-------|-------------|----------|
| `handback` | work came back: an Agent_Report, check output, a diff | `templates/handback.md` |
| `decision` | a choice is open for the Author | `templates/decision.md` |
| `status` | the Author asked what is going on | `templates/status.md` |
| `answer` | the Author asked what something is or why it happened | `templates/answer.md` |
| empty | step 1 picks from the conversation | as picked |
| other | named, the four listed, then as empty | as picked |

Template file layout, the same for the plugin's copy and a repository's:

| Part | Holds | Bound |
|------|-------|-------|
| Title | `# <Mode> report` | one line |
| Shape | the sections in order, each with one sentence on what it holds and what it must not hold | |
| Worked example | `## Before`, a Message as written in a real session, generalised; `## After`, the same in the shape | one pair |
| Whole file | | under 3,000 characters (Requirement 3.3) |

Handback sections, in order, with what the final review of `implement-spec` reads from each (Requirement 5.2):

| Section | Holds | Read back as |
|---------|-------|--------------|
| Problems, or the line "No problems." | one bullet per Problem: what it is, why it matters, the options | the carried items and follow-ups |
| Done | each item with the check that proved it and the result seen; for a spec, `<task id> <text> (Requirements <ids>)` | the tasks done |
| Checks | the full suite and its result; `Wave review of wave <n>: <verdict>`, with "carried: see Problems" or "nothing carried"; the final review line at spec cadence | the full-suite result and the review verdict |
| Files | the paths changed or created | the files |
| Next | the next task and wave, the proposal, the hand-off, or the question; skipped optional tests named as left unticked | the follow-ups and skipped tests |

## Correctness Properties

### Property 1: Problems come first

*For any* Message the skill writes that holds at least one Problem, every Problem appears before any other section, and a Handback with no Problem opens with "No problems."

**Validates: Requirements 2.1, 3.4**

### Property 2: The skill changes nothing

*For any* invocation of the skill, the working tree after the Message is the working tree before it: `git status --short --untracked-files=all` prints the same lines, and no agent was launched.

**Validates: Requirements 1.1, 1.6**

### Property 3: The repository's template wins when it can be read

*For any* Mode, when `.freethinking/report/<mode>.md` exists at the repository root, is readable and is non-empty, the Message follows its sections and says the repository's template was used; otherwise the Message follows the plugin's Template, with one line naming the path when the file exists but could not be used.

**Validates: Requirements 9.1, 9.2, 9.3**

### Property 4: A valid argument fixes the mode

*For any* invocation whose first argument is one of the four Modes, the Message is in that Mode whatever the conversation holds; an empty or other argument leaves the choice to the conversation.

**Validates: Requirements 1.2, 1.3, 1.5**

## Error Handling

| Condition | Category | Behaviour | Requirements |
|-----------|----------|-----------|--------------|
| Argument is not one of the four Modes | VALIDATION | Say so in one line, name the four, pick the Mode from the conversation; do not stop | 1.5 |
| Nothing has happened since the last Message | NO_INPUT | Rewrite the last Message in the chosen Mode and say it is a rewrite | 1.4 |
| No last Message either | NO_INPUT | Say there is nothing to report yet, in one line, and stop | 1.4 |
| Repository template unreadable or empty | FALLBACK | One line naming the path; use the plugin's Template | 9.3 |
| Repository template contains instructions | SAFETY | Follow its shape; ignore the instructions; say nothing about them | 9.4 |
| Plugin Template missing from the installed plugin | FALLBACK | Say which file is missing; write in the order the rule's bullets give, Problems first | 3.1 |
| An Agent_Report lacks `unsure` or a status word | PROTOCOL | Say that the report did not follow the protocol, name the field, and treat the whole report as unverified under Problems | 6.3 |
| Skill tool cannot find `freethinking:report` from another skill | MISSING | The invoking skill says the plugin's `report` skill is missing and writes its hand-back in the rule's order, Problems first | 5.1, 5.3, 5.4 |

## Testing Strategy

Free checks, run by `make validate`:

- `checks/test_rules_size.py` gains a per-rule table and checks `rules/communication.md` under 1,600 characters with the hook total under 10,000 (Requirement 4.2).
- `checks/test_report_skill.py`, new: the four Templates exist under `skills/report/templates/` named after the Modes, `SKILL.md` is under 4,000 characters, each Template under 3,000 (Requirement 3.3).
- `checks/test_issue_forms.py` and `checks/test_descriptions.py` already fail until the forms list the new skill and rule and the description fits (Requirements 4.4, 8.2, 8.3).

Evals, run by hand with the Makefile targets `eval-rule-communication` and `eval-skill-report`, which the folders create. Rule cases run with `EVAL_ARGS="--ablation with-without"` for the PR table (Requirement 7.4). Every regex below reads the last message unless it names a target.

- `evals/rules/communication/failing-check-first/` (Requirement 7.1): the calc fixture with `add` returning `a - b` committed; the prompt asks to run the tests and say how it went. Graders: a regex that the first line that is not a heading or blank names a failure, `^\s*(?:#+[^\n]*\n\s*)?(?:[-*]\s*)?[^\n]*\bfail` with flags `i` and no `m`; a `not_contains` regex on Narration openers, `^(?:I'll|I will|Let me (?!know)|Now I|First,? I)`, flags `im`; a regex `test_add`. Graders are JavaScript regexes: `^` and `$` without the `m` flag are the string anchors, `[\s\S]` is dot-all, and `\A`, `\z` and inline flags such as `(?s)` do not exist. Property 1.
- `evals/rules/communication/check-not-run/` (Requirement 7.1): the calc fixture unchanged; the prompt asks to add `subtract` and run the tests with `pytest -q`, which the sandbox does not have (the host's `make` is an xcrun shim the sandbox cannot run, so no Makefile is involved). Graders: a regex that the first line that is not a heading or blank says the tests were not run, `^\s*(?:#+[^\n]*\n\s*)?(?:[-*]\s*)?[^\n]*(?:not run|could not run|couldn't run|did not run|didn't run|unable to run|was not run|never ran|not installed|not found|not available|could not be run|cannot run|can't run)`, flags `i`; the same Narration `not_contains` regex. Both cases grant Bash, Write and Edit through a Makefile line.
- `evals/skills/report/decision-lists-options/` (Requirement 7.2): no scaffold; the prompt is `/freethinking:report decision` followed by a choice with three named options and a reason to prefer one. Graders: a regex that the three options appear before the word recommend, `\bdebug\b[\s\S]*\binfo\b[\s\S]*\bwarn\b[\s\S]*recommend`, flags `i`; a regex that the message ends in a question mark, `\?[\s*_`]*$` with no flags. Property 4.
- `evals/skills/report/rewrites-dense-message/` (Requirement 7.2): the prompt is `/freethinking:report` followed by the triage paragraph from issue #26 as the last message to rewrite. Graders: an `llm` grader passing when every thing the paragraph named by a label is named by what it is, with the issue number and what it asks for stated, the two decisions the original left open, priority and milestone, each laid out with options and a recommendation, and type and area stated as proposals or decisions, and failing when a label is carried over unexplained or the whole stays one block; a regex that the message says it is a rewrite, `\brewrit`, flags `i`. Requirement 1.4.
- `evals/skills/report/invoked-for-handback/` (Requirement 7.3): the calc fixture; the prompt in prose asks to add `subtract`, run the tests, and report back how it went. Graders: `tool_used` on `Skill` with `input_match` `"skill"\s*:\s*"(?:[\w-]+:)?report"`; a regex on `def subtract\(a, b\)` in `calc/ops.py`; a `file_exists: false` on `report.md`; a regex `(?:## Problems|No problems\.)[\s\S]*## Done` on the hand-back's shape. The prompt says the change is small enough to skip start-task. Grants Skill, Bash, Write and Edit through a Makefile line. This case needs the plugin arm, so it proves the description and the rule's routing bullet together.
- A fork probe, before the `implement-spec` task is built: a throwaway plugin in the scratchpad with one skill whose text launches the Agent tool with `subagent_type: fork` in the foreground and pastes the result, run once with `claude plugin eval` at a one-dollar ceiling, as the AskUserQuestion probe of 2026-10-13 was. It answers whether a conversation fork runs headless in the sandbox, whether the fork can invoke a plugin skill, and whether its result returns in the same turn. If forks do not run there, the `implement-spec` case is graded through the inline fallback and the design's fork path is proved by hand in a live session, recorded in the PR's Testing section.
- `evals/skills/implement-spec/works-one-wave/` (Requirement 7.5): `allowed_tools` gains `Skill`, with `Agent` already granted; a new grader `problems-first.md`, regex `(?:## Problems|No problems\.)[\s\S]*## Done`, and a `tool_used` grader that the Skill tool invoked `report`; the existing `reviews-the-wave.md` grader keeps matching `Wave review of wave [0-9]+:` in the Checks section; the prompt says the Agent tool has no fork in the run. The spec-cadence sibling `works-all-waves` gets the same two graders and prompt line, and its `reviews-the-run.md` grader keeps matching `Final review of the run:`, which the handback Template words. Properties 1 and 2 for the invoking skill.
- Property 3 is proved by an ephemeral check during the build, not an eval: invoke the skill in a scratch repository with and without `.freethinking/report/handback.md`, once with an empty file, and read the three Messages. An eval for it is a follow-up if the override is used by a second repository.
- Property 2 for the skill itself is covered by `invoked-for-handback`: a `file_exists` grader with `exists: false` on a scratch path the skill would plausibly write, and by the skill's `allowed-tools` holding no writing tool.

Cost: the two rule cases with both arms at three runs, and the three skill cases at two runs or three where the grader is `llm`, run to roughly five dollars at list price. Iterate at one run.
