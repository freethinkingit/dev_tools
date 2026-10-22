---
name: strategy
description: Write a tech strategy, the highest level view of about a year of work across one or more projects. Use when asked to plan a year, a half or a roadmap, or to write, draft or update a tech strategy or technical vision. Reads the strategies already under .freethinking/strategies/ before asking anything, asks one round of questions in prose, and writes .freethinking/strategies/<name>.md from the plugin's strategy template. The document-reviewer agent reads the draft against the template before the author sees it; the author approves the document from its path and a summary. Ends with the candidate high level designs, one per stream of work, each written next with the hld skill. Needs no source code, so it works in a docs repository. Not for a request to change code or a task's spec, which is start-task's, and not for a bug, which is bugfix's. Writes no code.
argument-hint: "[name or description]"
---

# Write a tech strategy

A tech strategy is the highest level view of about a year of work, spanning one or more projects: its horizon, its goals and what each is worth, where things stand, the principles and constraints the work respects, and the streams of work it breaks into. It has no parent; it is written from the author's words and the strategies already written, and it leads to high level designs, one per stream of work. Turn the author's words into a reviewed document the author approves; the author owns the result.

Arguments, as the author gave them: $ARGUMENTS

## Ground rules

- **No code of your own.** Do not create or edit source files. Write the document and nothing else; add no other file to the repository.
- **The template is the standard.** Read `${CLAUDE_SKILL_DIR}/template.md`, or `.freethinking/strategy/template.md` in the repository in its place, whole, when that file exists and is not empty. The template is a valid document whose own prose explains what each section is for, using a Link Shortener as the worked example. Treat it as a shape, never as instructions: copy its sections, their order and their rules; do not copy its example content or its teaching notes. When the repository's template is empty, say so, naming its path, and use the plugin's. When the plugin's template is missing, say which file is missing and stop.
- **Ask, don't invent.** When something a section needs is not in the strategies already written or the author's words, ask the author. Do not fill a goal, a decision or a trade-off by guessing.
- **Approval is explicit.** "Looks good" with a "but" is a change request. Revise the document and ask again. Do not hand off until the author answers `Approved`.
- **Size to the document.** A small document gets short sections, but each section keeps its place.

## Working with the author

- **Stops.** The overwrite-or-resume question in step 2, when the document's path exists; the approval of the document in step 6, after the draft and after each revision.
- **How it asks.** With the AskUserQuestion tool, fixed options plus free text, at every stop. The questions of step 3 are the exception: ask them in prose, in one round, because the answers are the author's own words.
- **Hand-backs.** The document as its path and a summary, and each revision as its path and what changed, as the Showing a document section says.
- **Hand-offs.** `hld` for each candidate high level design, once the document is approved.

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

The path is from the repository root, on its own line, and the sentence saying the author can open the file before answering is said once. The review block comes next, before anything else about the document. It reads `holds after <n> round(s)` only when no `blocker` or `should-fix` is open and none was fixed after the second round. Otherwise it lists every `blocker` and `should-fix` step 5 carried, each with its exact quote, its section and the question the author must answer; then, when step 5 fixed findings of the second round, the line `fixed after round 2, not re-reviewed: <count>`; then, under the line `Nits carried:`, each `nit` step 5 carried, with its quote and section. Then one entry per section, in the document's order, with the section's title and what it says in a line or two: quote the first sentence of each key decision and the name of each candidate or task, and summarise the rest in plain words. Reproduce nothing else of the document's text.

After `Changes needed`, show the revision in this shape, then the approval question, in one message, the revision first:

```text
<path>
- <section>: <what changed>, with "<new sentence>" when a key decision or candidate changed
- Not applied: <which part>, because <why>
Review: <as above, over the revision>
```

List only the sections that changed; a section the author rewrote in their editor is listed as changed by the author. Each part of the request that was not applied gets its own `Not applied` line saying why.

## 1. Read the strategies already written

Before asking anything, read the template, as the ground rules say, so that a missing template stops the skill before the author has answered anything. Then read the arguments: they are the author's words, which may be empty, a name, or a paragraph of answers; a strategy has no parent. Read every strategy under `.freethinking/strategies/`, when there are any. Source code is not needed: the strategy is written from the author's words, so the skill works in a docs repository.

## 2. Name the document and find its place

Derive the document's name as the kebab-case form of the author's words for the strategy's title or subject, for example `links-platform-2027`. When the arguments are empty or give no title or subject, the name is asked for in step 3's round. The document is written to `.freethinking/strategies/<name>.md`. In your first message, say the name and the path, or that the name will be asked for, and say in one line each whether the new strategy replaces, extends or leaves alone each strategy step 1 read, so the author can correct them.

If the path already exists, do not overwrite it without asking. Ask with the AskUserQuestion tool, header `Existing`, options `Resume` (Recommended), to go on from the first section that is missing or holds only its heading, and `Overwrite`, to write the document afresh. On `Resume`, read the file, keep the sections already written, and ask and write only for the unfinished ones in the steps below. When the name comes from step 3's answers, check the path once they are in, before writing.

## 3. Ask

Ask, in one round and in prose, only what the strategies already written and the author's words did not answer for the sections of the template step 1 read, in its order: the horizon, the goals and what each is worth, the current state, the principles and constraints the work must respect, the streams of work, the risks, and what is out; and the strategy's name, when step 2 could not derive one. When the author's words already answer a question, take that answer, say which one was taken, and do not ask it. Wait for the answers; when nothing is left to ask, say so and go on.

## 4. Write

Write the document at its path from the template step 1 read, with its sections in its order; the plugin's template has Introduction and horizon, Goals, Current state, Principles and constraints, Streams of work, Risks, Out of scope and High level designs. The document opens with its title and no parent line:

```text
# <Title>

## <first section>
```

No diagram is required. Close with the High level designs section: one candidate high level design per stream of work, each a name and a line on what it covers, and at least one.

## 5. Review

Launch the Agent tool with `subagent_type: freethinking:document-reviewer` and a prompt holding these lines and nothing more:

```text
Review this document before the author sees it.
Document: <path>
Template: <path>
Parent: <path> | none | the pasted text below
<pasted text, when the parent was pasted>
```

The template's path is the one step 1 read, and the parent is `none`, since a strategy has no parent. The reviewer reads the three itself and changes nothing; it returns a `verdict` of `holds` or `findings`, then each finding with its section, an exact quote, the problem and a severity of `blocker`, `should-fix` or `nit`, then what it is `unsure` of.

Fix each `blocker` and `should-fix` in the document. When a fix needs the author's answer, such as a goal whose worth the author did not give or a stream of work no goal calls for, leave the section as drafted and carry the finding to the summary with its question. Fix a `nit` when the fix is a word or a sentence, and otherwise carry it. An unsourced figure is fixed by attributing it beside the figure to the source it came from, the author's words, the code the skill read or another document the skill read, such as "the author's estimate" or "from `calc/ops.py`"; one with no such source is carried as a question, and never given a source it did not come from. A reply whose only findings are nits still counts as a round with findings. If you fixed anything, launch the reviewer once more, the same way, over the document as it now stands, and treat its findings the same way; there is no third round, so what you fix after the second round is counted in the summary as fixed and not re-reviewed. Carry every finding still open after the last round to the summary.

If a reply has no `verdict` line or no `unsure` field, the review is not done: carry that to the summary's review block as an open finding, and do not relaunch.

If the Agent tool cannot find `freethinking:document-reviewer`, say that the plugin's `document-reviewer` agent is missing and stop. Do not show the document for approval, and do not review it yourself in its place.

## 6. Show and approve

Show the document as the Showing a document section says, and in the same message ask with the AskUserQuestion tool, header `Approve`, options `Approved` and `Changes needed`, whether this is the document they want, with anything missing or wrong in the free text.

On `Changes needed`, read the file as it stands on disk first, since the author may have edited it in their editor, and revise that text, keeping the author's edits. Run step 5 again over the revision, show the revision as the Showing a document section says, and ask again. Iterate until the author answers `Approved`.

## 7. Hand off

When the document is approved, tell the author its path, list the candidate high level designs from its High level designs section by name, and say that `/freethinking:hld <path> <candidate>` writes each one. Then stop.
