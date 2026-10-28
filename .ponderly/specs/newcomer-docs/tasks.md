# Implementation Plan

## Overview

The first wave lays down what needs nothing else: the capture renderer, the Reference built from today's Listing_Page, the contributor material moved into the contributing guide, and the author's own work, which is the four with-without eval runs and three short sessions that the Guides with no existing transcript need. The second wave turns transcripts into captures and writes the pages that need only the first wave: the Evidence_Page, the Listing_Page, `llms.txt` and the manifests. The third wave writes the five Guides and the Front_Door, which need the captures. The fourth writes the Integrity_Check against the finished pages, and the last tests it and sets the GitHub metadata on the author's yes. Each code task is proved by an ephemeral check plus `make validate`; each page task by `make validate` and the manual check its text names; the renderer and the Integrity_Check have their own test tasks. There is no issue yet; the branch is `newcomer-docs`. Task 10 brings the finished pages up to the plugin as it stands on main at 1.2.0, after #73, #74 and #75 landed while this branch was open; the plugin source under `plugins/ponderly/` is the truth for what each component does.

## Tasks

- [x] 1. Build the capture renderer
  - [x] 1.1 Write `docs/captures/render.py`
    - Standard library only, Python 3.9 syntax, paths resolved from the file's own location. `extract <transcript> --from <uuid> --to <uuid> --name <name>` reads a Claude Code session `.jsonl`, takes the messages from the first id to the last, and writes `docs/captures/<name>.txt` with the header of the design's data model (`title`, `date`, `plugin`, `source`, `alt`, with `date` and `plugin` read from the transcript where it records them and left for the author otherwise), a blank line, and each message's text as recorded with the `> `, `● `, `⏺ ` and `  ` prefixes; an id not in the transcript exits non-zero naming it and writes nothing. `render <name>` writes `docs/images/<name>.svg` from `render_svg(source_text)`, which draws the terminal window the design gives: a 100-column width, wrapped lines, three colours, a title bar, a `<title>` holding `alt`, one `<text>` per line, and a footer with the date and version. Ephemeral check: extract a five-message range of this session's transcript into the scratchpad, render it twice and compare bytes, open the SVG and confirm every body line is present; `make validate` passes
    - _Requirements: 6.4, 6.5, 6.6, 6.8_
  - [x]* 1.2 Write the renderer's property tests in `checks/test_capture_render.py`
    - Render a set of sources twice and compare bytes; confirm every body character survives into the SVG text in order once escaping and wrapping are undone, including lines over 100 columns, `<`, `&` and `"`, and non-ASCII text; confirm `extract` with an unknown id exits non-zero and writes nothing
    - **Property 3: Rendering is deterministic**
    - **Property 4: Rendering keeps the text as recorded**
    - **Validates: Requirements 6.5, 6.6**
  - [x] 1.3 Show subagent hand-backs and question answers in `docs/captures/render.py`
    - `extract` keeps a subagent's hand-back, the `isMeta` user record that opens "Another Claude session sent a message:", as the report it carries: the harness frame and notes around it dropped, its lines de-indented, drawn as `⏺ ` and `  ` lines. It keeps the answer to an AskUserQuestion call, the `tool_result` that opens "Your questions have been answered:", as `  ` lines after the question's tool call. Nothing else in either record changes. Ephemeral check: extract the inline-email stop and the answer after it into the scratchpad and confirm both appear as recorded; `make validate` passes
    - _Requirements: 5.5, 6.5_

- [x] 2. Move the contributor material
  - [x] 2.1 Merge the root README's contributor sections into `.github/CONTRIBUTING.md`
    - Move the repository layout list, "Add or change a skill or rule" and "Testing" with its Validator, Unit tests and Evals parts from `README.md` into the contributing guide's "Make a change" and "Test" sections, dropping only sentences the guide already says, and change nothing in `README.md` yet, which task 7.1 rewrites. Manual check: every paragraph of the old sections is either in the guide or already said there, listed paragraph by paragraph in the Summary; `make validate` passes
    - _Requirements: 1.7_

- [x] 3. Write the Reference
  - [x] 3.1 Write `docs/reference.md`
    - A table of contents, then Skills, Agents, Rules, Hooks, Tune the plugin for a repository, and What the plugin runs and sends, with a `###` heading per component named exactly as its folder or file, from today's `plugins/ponderly/README.md` and each component's frontmatter description. Each skill gives its command and arguments, when it applies, what it asks, what it writes and what it hands off to; each hook script its event and what it loads. Change no file under `plugins/`. Manual check: every skill folder, agent file, rule file and hook script under `plugins/ponderly/` has a heading, and every table-of-contents link resolves to a heading; `make validate` passes
    - _Requirements: 7.1, 7.2, 7.3_

- [x] 4. Gather the Session_Captures
  - [x] 4.1 Run a plan-a-year session (the author, by hand)
    - In a scratch or docs repository, run `/ponderly:strategy`, then `/ponderly:hld` for one candidate, then `/ponderly:lld` for one of its candidates, answering as a real author would, and report the transcript's path and the plugin version. Follow the steps the plan-a-year Guide will give and say where they did not go as written
    - _Requirements: 5.1, 5.3, 6.4_
  - [x] 4.2 Run a contained-change session (the author, by hand)
    - In a repository of the author's choice, ask for one contained change so that `start-task` offers the executor route, accept it, and let `task-executor` make the change; report the transcript's path and the plugin version
    - _Requirements: 5.1, 5.3, 6.4_
  - [x] 4.3 Run a tune-a-template session (the author, by hand)
    - In a repository of the author's choice, replace one template under `.ponderly/` (a report template or a design template), then run the skill that reads it and confirm it used the replacement; report the transcript's path and the plugin version
    - _Requirements: 5.1, 5.3, 6.4_
  - [x] 4.4 Extract and render the captures from existing sessions
    - With `docs/captures/render.py`, extract and render from this repository's design-skills session (`8a0ad5ce-6a20-40f3-9dae-e4e4d8c3519a`) the hero hand-back that lists problems first, then what was done, then the next step, named `hero-handback`; a spec approval summary, an `implement-spec` wave report and the `pr` draft for the feature Guide; and the `bugfix` root-cause confirmation and hand-off for issue #52 for the bug Guide. From the inline-email newcomer-docs session (`4c0c154a-4af6-4bd3-b6c5-b6dbbc7a15b0`), extract the executor's `status: stopped` Summary that begins "The README cannot meet Requirements 1.1 and 1.6" and the author's answer after it. Redact only credentials, tokens, private repository names, email addresses and home-directory paths, and replace the plugin's former names with the current ones, and fill `alt` for each. Manual check: each source's body matches its transcript range apart from the listed redactions, shown as a diff in the Summary; `make validate` passes
    - _Requirements: 5.5, 6.1, 6.4, 6.5, 6.8, 6.9_
  - [x] 4.5 Extract and render the captures from the author's three sessions
    - With `docs/captures/render.py`, extract and render from the transcripts tasks 4.1, 4.2 and 4.3 reported: each skill's question round, summary and approval for plan-a-year; the route question, the executor's Summary and the hand-back for the contained change; the replaced template and the output that used it for tune-a-template. Redact and fill `alt` as in task 4.4. Manual check: as in task 4.4; `make validate` passes
    - _Requirements: 6.4, 6.5, 6.8, 6.9_

- [x] 5. Write the Guides
  - [x] 5.1 Write `docs/guides/build-a-feature.md`
    - The shape the design gives for a Guide, for the job "spec and build a feature with `start-task`, `implement-spec` and `pr`", from the captures of task 4.4: the request, the route statement, the three approvals with their options, the waves, the inline-email stop and what the author did next, and the `pr` draft, with a sequence Diagram of one `implement-spec` wave with its executors and the `wave-reviewer`. "Next" links `fix-a-bug.md` and the Reference sections used. Manual check: every step names the exact command or request, and every image has alt text; `make validate` passes
    - _Requirements: 5.2, 5.3, 5.4, 5.5, 5.6, 5.7, 6.3, 6.8_
  - [x] 5.2 Write `docs/guides/fix-a-bug.md`
    - The Guide shape for the job "fix a bug with `bugfix` and `pr`", from task 4.4's issue #52 captures: the ticket described in words (the captured run began from a description and filed issue #52 after the hand-off), the read-back described in words, the reproduction, the root-cause question with its options, the fix with its regression test, and the hand-off. "Next" links `make-a-small-change.md`. Manual check: as in task 5.1; `make validate` passes
    - _Requirements: 5.2, 5.3, 5.4, 5.6, 5.7, 6.8_
  - [x] 5.3 Write `docs/guides/plan-a-year.md`
    - The Guide shape for the job "plan a year with `strategy`, `hld` and `lld`", from task 4.5's captures and the steps the author reported in task 4.1, with a sequence Diagram of a skill and the `document-reviewer` over its two rounds. "Next" links `build-a-feature.md`. Manual check: as in task 5.1, and every step the author said did not go as written is corrected; `make validate` passes
    - _Requirements: 5.2, 5.3, 5.4, 5.6, 5.7, 6.3, 6.8_
  - [x] 5.4 Write `docs/guides/make-a-small-change.md`
    - The Guide shape for the job "make one contained change through the `task-executor` agent", from task 4.5's captures, with a sequence Diagram of `start-task` launching `task-executor` and handing back. "Next" links `tune-a-template.md`. Manual check: as in task 5.1; `make validate` passes
    - _Requirements: 5.2, 5.3, 5.4, 5.6, 5.7, 6.3, 6.8_
  - [x] 5.5 Write `docs/guides/tune-a-template.md`
    - The Guide shape for the job "tune a template for one repository", from task 4.5's captures: which templates can be replaced and where each goes, the replacement, and the run that used it. "Next" links the Reference. Manual check: as in task 5.1; `make validate` passes
    - _Requirements: 5.2, 5.3, 5.4, 5.6, 5.7, 6.8_

- [x] 6. Show the evidence
  - [x] 6.1 Run the rule targets against the no-plugin baseline (the author, by hand)
    - One at a time: `make eval-rule-workflow EVAL_ARGS="--ablation with-without" EVAL_MAX_COST_USD=10`, then the same for `eval-rule-code-changes`, `eval-rule-collaboration` and `eval-rule-communication`. The workflow run is expected near $7 and the others have no recorded cost. Report each printed table, the date, the plugin version and the exact command
    - _Requirements: 4.2, 4.3_
  - [x] 6.2 Write `docs/evidence.md`
    - The sections the design gives: Why it was built, the Origin_Story quoted exactly from `design.md`; How it is tested, in plain words, with `make validate` and the eval targets; Results against Claude Code without the plugin, each table from task 6.1 copied as printed under a heading with its date, version and command; Not measured, naming every skill and agent eval target and why; A real example, linking `.ponderly/specs/design-skills/`. Manual check: every figure on the page carries a date, a version and a command; `make validate` passes
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [x] 7. Write the front doors
  - [x] 7.1 Rewrite `README.md` as the Front_Door
    - The sections the design gives, in order: the Pitch quoted exactly from `design.md`; the "Docs:" line; the install commands; the `hero-handback` image with its alt text; What it does, with a Mermaid flowchart of how the skills hand off; When to use it, naming Claude Code without the plugin and Kiro, each in one or two sentences sourced from its own documentation or the author's use; How it is tested; What this does not do; Develop the plugin, linking `.github/CONTRIBUTING.md`; License. Ephemeral check: the install commands sit within the first 40 lines; `wc -l README.md`, reported against 220 for the author to set the bound; `make validate` passes
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 3.1, 3.2, 3.3, 6.1, 6.2, 6.8_
  - [x] 7.2 Rewrite `plugins/ponderly/README.md` as the Listing_Page
    - The sections the design gives: the Pitch quoted exactly; Install; Stay up to date, unchanged; one line per skill saying when to use it; one line per agent and per rule; What the plugin runs and sends, unchanged; Learn more, with absolute `https://github.com/sabind/ponderly/blob/main/...` links. Where a section moved to the Reference, leave a one-line pointer to its section. No Mermaid and no relative image. Ephemeral check: `python3 -m unittest discover -s checks -p test_listing.py` passes; every moved section has its pointer; `make validate` passes
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 7.4_
  - [x] 7.3 Write `llms.txt`
    - The llmstxt.org shape the design gives: `# ponderly`, a blockquote of the Pitch's first two sentences, a paragraph with the install commands, what the plugin needs, the license and what it runs and sends, then `## Skills`, `## Agents`, `## Rules` and `## Docs`, each line `- [name](absolute URL): when to use it`. Manual check: every skill folder, agent file and rule file under `plugins/ponderly/` has a line; `make validate` passes
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 8. Align the metadata
  - [x] 8.1 Update the manifests and raise the version
    - Set the `description` of the plugin in `.claude-plugin/marketplace.json` and of `plugins/ponderly/.claude-plugin/plugin.json` to the Pitch's first sentence, at most 350 characters, and `"version": "1.2.0"` in `plugin.json`. Ephemeral check: both files parse as JSON and both descriptions are equal; `make validate` passes, which runs `claude plugin validate`
    - _Requirements: 10.1_
  - [x] 8.2 Set the GitHub description and topics (the author, by hand)
    - Shown the exact values, the description from task 8.1 and the topics `claude-code`, `claude-code-plugin`, `claude-skills`, `ai-coding`, `spec-driven-development` and `developer-tools`, with the homepage left empty, the author approves them and they are set with `gh repo edit sabind/ponderly --description "<description>" --add-topic <topic>` for each topic; report `gh repo view sabind/ponderly --json description,repositoryTopics,homepageUrl`
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [x] 9. Keep the pages true to the code
  - [x] 9.1 Write the Integrity_Check in `checks/test_docs.py`
    - Standard-library `unittest`, Python 3.9 syntax, paths from the file's own location, importing `render_svg` from `docs/captures/render.py` by path. Over `README.md`, `plugins/ponderly/README.md`, `llms.txt` and every `docs/**/*.md`, check what the design's Integrity_Check table lists: relative links and images resolve, with `#anchors` matched to GitHub heading slugs; absolute `github.com/sabind/ponderly/(blob|tree)/main/` links resolve locally; `/ponderly:<skill>` and `ponderly:<agent>` name a skill folder or agent file; `make <target>` names a Makefile rule or an enumerated `eval-skill-`, `eval-rule-` or `eval-agent-` target; backticked paths under `plugins/`, `evals/`, `checks/`, `docs/`, `.github/`, `.claude-plugin/` and `bin/`, and root files, exist, skipping any with `<`, `*` or `{`; every skill folder, agent file and rule file is named in the Listing_Page, has a `###` heading in the Reference and is named in `llms.txt`; every SVG equals its source's re-render, every source has an SVG and every SVG a source; no source holds a credential, token, email address or home-directory path; no image has empty alt text. Every failure message gives the page, the line and the name. Ephemeral check: break one link, one command and one SVG in a scratch copy of the tree and confirm each fails with page and line, and the real tree passes; `make validate` passes
    - _Requirements: 6.6, 6.8, 6.9, 8.5, 9.1, 9.2, 9.3, 9.4, 9.5_
  - [x]* 9.2 Write the Integrity_Check's fixture tests
    - In `checks/test_docs.py`, against fixture trees built in a temporary directory: a broken link, a missing heading, a missing skill in a command, a missing `make` target, a component missing from each of the three pages, a stale SVG, a source with a token and an image with no alt text each fail with page, line and name, and a clean tree passes
    - **Property 1: Every name a page mentions exists**
    - **Property 2: Every component is named where it must be**
    - **Property 5: A failure names its place**
    - **Validates: Requirements 7.1, 8.2, 8.5, 9.2, 9.3, 9.4, 9.5**

- [x] 10. Bring the pages up to the plugin on main
  - [x] 10.1 Update `docs/reference.md`
    - From the current files under `plugins/ponderly/`: add `### readable-code` and `### tighten-tests` under Skills, in the shape of the other skill sections (command and arguments, when it applies, what it asks, what it writes, what it hands off to), and `### tests` under Rules, each with its table-of-contents line; rewrite `### pr` for the explain-and-confirm walkthrough and the ticked-spec short form; rewrite the `workflow`, `code-changes`, `comments`, `collaboration` and `communication` entries to match their rule files; in Agents, name `readable-code` and `tighten-tests` as launching the executor and the wave reviewer, in the intro and in each agent's "Launched by"; make "What the plugin runs and sends" match the Listing_Page's section of the same name; and correct any other skill, agent or hook section the plugin source no longer matches. Change no file under `plugins/`. Manual check: every skill folder, agent file, rule file and hook script has a `###` heading and a working table-of-contents link, each rule entry is compared bullet by bullet with its rule file in the Summary, and the runs-and-sends section is compared with the Listing_Page's; `make validate` passes
    - _Requirements: 7.1, 7.2, 7.3_
  - [x] 10.2 Update `llms.txt`
    - Add `readable-code` and `tighten-tests` under Skills and `tests` under Rules, each line `- [name](absolute URL): when to use it` from the component's own description; bring the summary paragraph's needs and what-it-runs-and-sends in line with the Listing_Page, including `gh` for `tighten-tests` when it files gaps, the project's own tests, synthesis command and coverage tool, and a development dependency only on the author's yes; correct the `pr`, `collaboration` and `communication` lines to the current source. Manual check: every skill folder, agent file and rule file under `plugins/ponderly/` has a line; `make validate` passes
    - _Requirements: 8.1, 8.2, 8.3_
  - [x] 10.3 Update `README.md`
    - Add `readable-code` and `tighten-tests` to the "What it does" flowchart, with the hand-offs their `SKILL.md` files give, and to the prose around it in a sentence; correct "What this does not do" so the sending bullet says those two skills also run the project's own tests and tools and that `tighten-tests` adds a coverage tool only on the author's yes, and the commit bullet holds for them. Ephemeral check: the install commands sit within the first 40 lines; `wc -l README.md` reported against 220; `make validate` passes
    - _Requirements: 1.2, 1.5, 6.2_
  - [x] 10.4 Update the Guides
    - In `docs/guides/build-a-feature.md`, rewrite the `pr` step for a branch built from a ticked spec as the current `pr` skill gives it, in words where the capture predates it, and name `readable-code` and `tighten-tests` as optional steps before it; in `fix-a-bug.md` and `make-a-small-change.md`, correct the `pr` description to the explain-and-confirm walkthrough; correct any other step the current skill source no longer matches. Change no capture. Manual check: each corrected step compared with the skill's `SKILL.md` in the Summary; `make validate` passes
    - _Requirements: 5.3, 5.4, 5.7_
  - [x] 10.5 Update `docs/evidence.md`
    - Say that the four rule runs used version 0.17.0 under the plugin's former name, from this branch's working tree before the rename to `ponderly`, and name the rules changed on main since the run, from `git log` of `plugins/ponderly/rules/`, so the tables read as a snapshot of those rules as they were; leave every table as printed. In Not measured, add the `readable-code` and `tighten-tests` skills and the `tests` rule, which has eval cases with the plugin loaded but no baseline run, and correct the sentence on which components have eval cases. Manual check: every target named has a Makefile target; `make validate` passes
    - _Requirements: 4.3, 4.4_
  - [x] 10.6 Name every launcher and complete what the plugin runs
    - In `plugins/ponderly/agents/task-executor.md` and `wave-reviewer.md`, make the description name every skill that launches the agent: `start-task`, `implement-spec`, `readable-code` and `tighten-tests` for the executor, and `implement-spec`, `readable-code` and `tighten-tests` for the reviewer. In "What the plugin runs and sends" of the Listing_Page and the Reference, and in the summary of `llms.txt` and the sending bullet of `README.md`, add the `git remote get-url origin` that `pr` runs and say that the `task-executor` agent runs the project's own tests. Manual check: the two runs-and-sends sections are identical; `make validate` passes
    - _Requirements: 7.1, 8.3_

## Notes

- Quote the Pitch and the Origin_Story exactly as `design.md` records them; never paraphrase or extend them.
- A Session_Capture's text is the transcript's text; the only edits allowed are the redactions the design lists. Never write a capture by hand, and never show output that no session produced.
- Every Doc_Page except the Listing_Page lives outside `plugins/ponderly/`. No skill, agent, rule or hook changes behaviour in this task.
- Write in the inline-email style: plain short sentences, exact commands, what the Reader sees after each.
- Python follows `checks/`: standard library only, Python 3.9 syntax, paths from the file's own location, no new dependency.
- Eval runs are the author's, by hand, one target at a time.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1", "3.1", "4.1", "4.2", "4.3", "6.1", "10.1", "10.2", "10.3", "10.4", "10.5", "10.6"] },
    { "id": 1, "tasks": ["1.2", "1.3", "4.5", "6.2", "7.2", "7.3", "8.1"] },
    { "id": 2, "tasks": ["4.4"] },
    { "id": 3, "tasks": ["5.1", "5.2", "5.3", "5.4", "5.5", "7.1"] },
    { "id": 4, "tasks": ["9.1"] },
    { "id": 5, "tasks": ["9.2", "8.2"] }
  ]
}
```
