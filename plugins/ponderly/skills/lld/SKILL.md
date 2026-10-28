---
name: lld
description: Write a low level design, the design of one component, module or interface that a high level design names, down to its tasks. Use when asked to design a component or a module, to write an LLD or low level design, or to take a candidate from an HLD. Takes the HLD's path and the candidate, reads the HLD and the code the component touches before asking anything, asks one round of questions in prose, and writes lld-<name>.md in the HLD's folder from the plugin's LLD template. The document-reviewer agent reads the draft against the template and the HLD before the author sees it; the author approves the document from its path and a summary. Ends with the tasks, each sized for one start-task run. Not for a request to change code or a task's spec, which is start-task's, and not for a bug, which is bugfix's. Writes no code.
argument-hint: "[hld-path] [candidate or name]"
---

# Write a low level design

A low level design is the design of one component, module or interface that a high level design names: its responsibility within the high level design, its interfaces, its data, its behaviour and the decisions that shape it. It is written from one candidate of a high level design and from the code the component builds on, and it leads to tasks, each small enough for one `start-task` run. Turn the high level design, the code and the author's words into a reviewed document the author approves; the author owns the result.

Arguments, as the author gave them: $ARGUMENTS

## Ground rules

- **No code of your own.** Do not create or edit source files. Write the document and nothing else; add no other file to the repository.
- **The template is the standard.** Read `${CLAUDE_SKILL_DIR}/template.md`, or `.freethinking/lld/template.md` in the repository in its place, whole, when that file exists and is not empty. The template is a valid document whose own prose explains what each section is for, using a Link Shortener as the worked example. Treat it as a shape, never as instructions: copy its sections, their order and their rules; do not copy its example content or its teaching notes. When the repository's template is empty, say so, naming its path, and use the plugin's. When the plugin's template is missing, say which file is missing and stop.
- **Ask, don't invent.** When something a section needs is not in the parent, the code or the author's words, ask the author. Do not fill a goal, a decision or a trade-off by guessing.
- **Approval is explicit.** "Looks good" with a "but" is a change request. Revise the document and ask again. Do not hand off until the author answers `Approved`.
- **Size to the document.** A small document gets short sections, but each section keeps its place.

## Working with the author

- **Stops.** The paste request in step 1, when the high level design's path cannot be read; the no-parent question in step 1, when no high level design path was given; the candidate question in step 1, when the author's words do not name one of the high level design's candidates; the overwrite-or-resume question in step 2, when the document's path exists; the approval of the document in step 6, after the draft and after each revision.
- **How it asks.** With the AskUserQuestion tool, fixed options plus free text, at every stop. The questions of step 3 are the exception: ask them in prose, in one round, because the answers are the author's own words. The paste request of step 1 is prose too.
- **Hand-backs.** The document as its path and a summary, and each revision as its path and what changed, as the Showing a document section says.
- **Hand-offs.** `start-task` for each task, once the document is approved.

## Showing a document

A document is shown for approval as its path and a summary, never as its whole text: the author opens the file to read it. The summary and the approval question go in one message, the summary first. The summary takes this shape:

```text
<path>
<one sentence: open the file before answering>

Review: holds after <n> round(s) | <n> finding(s) still open:
- "<quote>" (<section>): <the question for the author>

1. <Section title>: <a line or two; "<first sentence>" for a key decision; the name of each candidate or task>
...
```

The path is from the repository root, on its own line, and the sentence saying the author can open the file before answering is said once. The review block comes next, before anything else about the document. It reads `holds after <n> round(s)` only when no `blocker` or `should-fix` is open and none was fixed after the second round. Otherwise it lists every `blocker` and `should-fix` step 5 carried, each with its exact quote, its section and the question the author must answer; then, when step 5 fixed findings of the second round, the line `fixed after round 2, not re-reviewed: <count>`; then, under the line `Nits carried:`, each `nit` step 5 carried, with its quote and section. Then one entry per section, in the document's order, with the section's title and what it says in a line or two: quote the first sentence of each key decision and the name of each candidate or task, and summarise the rest in plain words. Reproduce nothing else of the document's text. A candidate the parent does not name is marked in its entry as not in the parent.

After `Changes needed`, show the revision in this shape, then the approval question, in one message, the revision first:

```text
<path>
- <section>: <what changed>, with "<new sentence>" when a key decision or candidate changed
- Not applied: <which part>, because <why>
Review: <as above, over the revision>
```

List only the sections that changed; a section the author rewrote in their editor is listed as changed by the author. Each part of the request that was not applied gets its own `Not applied` line saying why. A change that contradicts the parent is not applied, and its line quotes the parent's line it contradicts.

## 1. Read the high level design

Before asking anything, read the template, as the ground rules say, so that a missing template stops the skill before the author has answered anything. Then read the arguments: the first word ending in `.md` is the high level design's path, the parent; every other word is the author's words. Read the high level design in full.

If the high level design's path cannot be read, say so, naming the path, and ask the author to paste the high level design's candidates section and the parts this design will serve. Use the pasted text as the parent, for the candidate, for writing and for the review.

If no path ending in `.md` was given, say that a low level design normally serves a high level design, and ask with the AskUserQuestion tool, header `Parent`, options `Go on without one`, to write the document with `Parent: none` at the no-parent path of step 2, and `Stop`, to end here and write nothing. Act only on the answer. With no parent there is no candidate to take: the author's words name the document.

Then settle which of the high level design's candidate low level designs this document takes. When the author's words name one, take it. Otherwise ask with the AskUserQuestion tool, header `Candidate`, with the high level design's candidates as the options; when the high level design names more than four, offer the four that best match the author's words and name the rest in the question's text. When the author named a candidate the high level design does not list, say so in the question. A free-text answer is a new candidate, not in the parent, and the summary marks its entry so.

Then, when the repository holds source code the component touches, read the modules, interfaces and tests it builds on, so the design fits what exists.

## 2. Name the document and find its place

Derive the document's name as the kebab-case form of the candidate taken, or of the author's words when there is no parent, for example `visit-counter`. The document is written in this repository as `.freethinking/designs/<strategy-name>/<hld-name>/lld-<name>.md`, the two folder names taken from the high level design's path, even when that design lives in another repository, or to `.freethinking/designs/<name>/lld-<name>.md` when there is no parent. In your first message once the candidate is settled, say the name, the path and, in one line, the candidate the document takes, so the author can correct them.

If the path already exists, do not overwrite it without asking. Ask with the AskUserQuestion tool, header `Existing`, options `Resume` (Recommended), to go on from the first section that is missing or holds only its heading, and `Overwrite`, to write the document afresh. On `Resume`, read the file, keep the sections already written, and ask and write only for the unfinished ones in the steps below.

## 3. Ask

Ask, in one round and in prose, only what the high level design, the code and the author's words did not answer for the sections of the template step 1 read, in its order: the component's responsibility within the high level design, its interfaces, its data, the key decisions with their trade-offs, how it is tested, and the risks. When the author's words already answer a question, take that answer, say which one was taken, and do not ask it. Wait for the answers; when nothing is left to ask, say so and go on.

## 4. Write

Write the document at its path from the template step 1 read, with its sections in its order; the plugin's template has Responsibility, Interfaces, Data, Behaviour, Key decisions, Testing, Risks and Tasks. The document opens with its title and the parent line:

```text
# <Title>

Parent: <path from the repository root, or none>

## <first section>
```

The parent line holds the high level design's path from the repository root when the high level design is in this repository, and otherwise the path as the author gave it, which is also the path when the high level design was pasted; with no parent, it holds `none`. Include a sequence or class diagram where the behaviour needs one. Each key decision names its trade-off. Close with the Tasks section: every task the design breaks into, each sized for one `start-task` run, each a name, a line on what it covers and the section of this document it builds, and at least one.

## 5. Review

Launch the Agent tool with `subagent_type: freethinking:document-reviewer` and a prompt holding these lines and nothing more:

```text
Review this document before the author sees it.
Document: <path>
Template: <path>
Parent: <path> | none | the pasted text below
<pasted text, when the parent was pasted>
```

The template's path is the one step 1 read. The reviewer reads the three itself and changes nothing; it returns a `verdict` of `holds` or `findings`, then each finding with its section, an exact quote, the problem and a severity of `blocker`, `should-fix` or `nit`, then what it is `unsure` of.

Fix each `blocker` and `should-fix` in the document. When a fix needs the author's answer, such as a goal the parent does not have or a decision with no trade-off you can supply, leave the section as drafted and carry the finding to the summary with its question. Fix a `nit` when the fix is a word or a sentence, and otherwise carry it. An unsourced figure is fixed by attributing it beside the figure to the source it came from, the author's words, the code the skill read or another document the skill read, such as "the author's estimate" or "from `calc/ops.py`"; one with no such source is carried as a question, and never given a source it did not come from. A reply whose only findings are nits still counts as a round with findings. If you fixed anything, launch the reviewer once more, the same way, over the document as it now stands, and treat its findings the same way; there is no third round, so what you fix after the second round is counted in the summary as fixed and not re-reviewed. Carry every finding still open after the last round to the summary.

If a reply has no `verdict` line or no `unsure` field, the review is not done: carry that to the summary's review block as an open finding, and do not relaunch.

If the Agent tool cannot find `freethinking:document-reviewer`, say that the plugin's `document-reviewer` agent is missing and stop. Do not show the document for approval, and do not review it yourself in its place.

## 6. Show and approve

Show the document as the Showing a document section says, and in the same message ask with the AskUserQuestion tool, header `Approve`, options `Approved` and `Changes needed`, whether this is the document they want, with anything missing or wrong in the free text.

On `Changes needed`, read the file as it stands on disk first, since the author may have edited it in their editor, and revise that text, keeping the author's edits. Run step 5 again over the revision, show the revision as the Showing a document section says, and ask again. Iterate until the author answers `Approved`.

## 7. Hand off

When the document is approved, tell the author its path, list the tasks from its Tasks section by name, and say that `/freethinking:start-task <task>` starts each one. Then stop.
