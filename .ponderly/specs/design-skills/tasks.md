# Implementation Plan

## Overview

The first wave lays down everything the plugin ships and the checks enumerate: the three templates, the reviewer agent, the three skills written as one task from one skeleton, and the issue-form dropdowns that `checks/test_issue_forms.py` holds to the components on disk, so `make validate` passes at the end of the wave. The second wave describes and proves them: the `start-task` clause, the README and version, the ten eval cases and the Makefile lines, all on disjoint files. The last wave is the author's: the eval runs that cost tokens, with the tables for the pull request. Each task is proved by `make validate` plus the ephemeral check its text names; the eval runs are the integration proof. GitHub issue #50 is the ticket; the branch is `50-design-skills`.

## Tasks

- [x] 1. Write the three templates
  - [x] 1.1 Write `plugins/ponderly/skills/strategy/template.md`
    - A valid Strategy for `links-platform-2027` as the design's templates section lays it out, with teaching prose beside each section in the manner of `start-task/spec-template/requirements.md`, the sections the design's skill table gives for `strategy` in that order, no `Parent` line, and a closing High level designs section with one Candidate per stream, each a name and what it covers. Ephemeral check: every section heading of the table is present once, in order, by `grep -n '^## '`; `make validate` passes
    - _Requirements: 1.6, 2.2, 7.1, 7.2_
  - [x] 1.2 Write `plugins/ponderly/skills/hld/template.md`
    - A valid HLD `hld-shortener-service.md` with `Parent: .ponderly/strategies/links-platform-2027.md` under the title, the sections of the design's table for `hld`, at least one Mermaid flowchart of the components, each key decision with its trade-off and a rejected alternative, and a closing Low level designs section naming `visit-counter` among its Candidates. Ephemeral check: the `Parent:` line is the third line of the file; the headings are present once, in order; a ```` ```mermaid ```` fence exists; `make validate` passes
    - _Requirements: 1.5, 1.6, 3.5, 7.1, 7.2_
  - [x] 1.3 Write `plugins/ponderly/skills/lld/template.md`
    - A valid LLD `lld-visit-counter.md` with `Parent: .ponderly/designs/links-platform-2027/shortener-service/hld-shortener-service.md`, the sections of the design's table for `lld`, a sequence diagram of the counting path, and a closing Tasks section whose entries are each one `start-task` run and cite the section they build. Ephemeral check: the `Parent:` line is the third line; the headings are present once, in order; every Tasks entry names a section of the file; `make validate` passes
    - _Requirements: 1.5, 1.6, 4.6, 7.1, 7.2_

- [x] 2. Write the document-reviewer agent
  - Create `plugins/ponderly/agents/document-reviewer.md` as the design's agent section gives it: frontmatter with name, a description under 1,024 characters, `tools: Read, Glob, Grep`, `model: opus`, `effort: high`; the procedure (read the three inputs, a blocker per missing one, judge every section against the template's purpose, the parent and the other sections, check the parent line and the closing section); the severities; and the Findings shape quoted in the design with `section`, `quote`, `problem`, `severity` and `unsure`. Ephemeral check: `checks/test_agents.py` and `checks/test_descriptions.py` pass under `make validate`
  - _Requirements: 5.2, 5.3, 5.4_

- [x] 3. Write the three skills from one skeleton
  - Create `plugins/ponderly/skills/strategy/SKILL.md`, `plugins/ponderly/skills/hld/SKILL.md` and `plugins/ponderly/skills/lld/SKILL.md` in one sitting, each with the eleven sections the design's skills section lists, in that order, identical where the skeleton is shared and differing only where the design's per-skill table sets the arguments, the parent, the path written, what else is read, the sections, the diagram, the closing section and the hand-off. Each description, under 1,024 characters, names the requests it takes and says a task's spec is `start-task`'s and a bug is `bugfix`'s. Each "Showing a document" section carries the Document_Summary and revision shapes of the design's data models. Each step 6 reads the file from disk before revising, so the author's own edits are kept. Each step 5 launches `ponderly:document-reviewer` with the three-line prompt of the data models and nothing more, fixes `blocker` and `should-fix`, relaunches once if anything was fixed, and stops with the missing-agent sentence when the Agent tool cannot find it. Ephemeral check: `diff` of the three files shows differences only inside the lines the per-skill table governs; each file names `${CLAUDE_SKILL_DIR}/template.md` and `.ponderly/<skill>/template.md`; `make validate` passes, which runs the skills validator on the frontmatter and `checks/test_descriptions.py`
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.5, 5.6, 5.7, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 7.3, 8.5_

- [x] 4. Add the components to the issue forms
  - In the four forms under `.github/ISSUE_TEMPLATE/` that have a `component` dropdown, add `strategy (skill)`, `hld (skill)` and `lld (skill)` and `document-reviewer (agent)` at the positions `checks/test_issue_forms.py` requires, skills then agents in disk order. Ephemeral check: `python3 -m unittest discover -s checks -p test_issue_forms.py` passes once tasks 2 and 3 are on disk; `make validate` passes
  - _Requirements: 9.4_

- [x] 5. Add the exclusion clause to start-task's description
  - In the `description` of `plugins/ponderly/skills/start-task/SKILL.md`, after the pull-request exclusion, add "not a tech strategy, a system's high level design or a component's low level design, which are `strategy`, `hld` and `lld`'s", and change nothing else in the file. Ephemeral check: `git diff --stat` shows one file and one line; the description stays under 1,024 characters by `checks/test_descriptions.py`; `make validate` passes
  - _Requirements: 8.5_

- [x] 6. Document the skills and raise the version
  - In `plugins/ponderly/README.md`: three Skills rows after `start-task` in tree order, each with the command, what it reads, what it writes and where, the review, and the next skill; the `document-reviewer` launch bullet and table row in the Agents section; the templates named under "Tune the plugin for a repository"; the three skills and the reviewer under "What the plugin runs and sends". In `plugins/ponderly/.claude-plugin/plugin.json`, `"version": "0.15.0"`. Ephemeral check: `grep -c 'document-reviewer' README.md` is at least 3; `make validate` passes, which runs `checks/test_listing.py` on the README
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [x] 7. Add the eval cases
  - [x] 7.1 Add the two `strategy` cases
    - `evals/skills/strategy/writes-strategy/` and `evals/skills/strategy/existing-offers-resume/` as the design's eval table lays them out: `case.yaml` naming `scaffold.sh`, an executable `scaffold.sh` that copies `files/` in, `prompt.md` with description, `tags: [skill, strategy]`, `max_turns`, `allowed_tools` including Write, Edit, Agent and Skill, and `expected_outcome`, and the graders of the table. Ephemeral check: each scaffold run by hand in an empty directory plants the files its case needs; `checks/test_eval_cases.py` passes under `make validate`
    - _Requirements: 1.7, 9.1, 9.3_
  - [x] 7.2 Add the two `hld` cases
    - `evals/skills/hld/writes-from-strategy/` and `evals/skills/hld/unreadable-strategy-asks/` as the design's eval table lays them out, the first with `files/.ponderly/strategies/links-2027.md` holding three Candidates and graders on the written file's `Parent:` line, its Low level designs heading and its mermaid fence. Ephemeral check: as 7.1
    - _Requirements: 3.2, 9.1, 9.3_
  - [x] 7.3 Add the two `lld` cases
    - `evals/skills/lld/writes-from-hld/` and `evals/skills/lld/unreadable-hld-asks/` as the design's eval table lays them out, both scaffolds running `evals/fixtures/setup.sh calc main` and the first copying the HLD under `files/.ponderly/designs/links-2027/shortener-service/`. Ephemeral check: as 7.1, with `calc/ops.py` present after the scaffold
    - _Requirements: 4.2, 4.4, 9.1, 9.3_
  - [x] 7.4 Add the two `document-reviewer` cases
    - `evals/agents/document-reviewer/finds-the-contradiction/` and `evals/agents/document-reviewer/passes-a-clean-document/` as the design's eval table lays them out: `files/` holding a strategy, an HLD, an LLD and copies of the three templates, the LLD of the first contradicting the HLD's asynchronous-counting decision in its Data section; a prompt that launches the agent with the three paths and replies with its Findings verbatim, in the shape of `evals/agents/wave-reviewer/finds-the-contradiction/prompt.md`; `tags: [agent, document-reviewer]`; the graders of the table. Ephemeral check: as 7.1
    - _Requirements: 5.3, 5.4, 9.2, 9.3_
  - [x] 7.5 Add the four Makefile lines
    - In the "Per-target flags" block of the `Makefile`: `eval-skill-strategy`, `eval-skill-hld` and `eval-skill-lld` with `CASE_ARGS += --allow-tools Write Edit --scaffold`, and `eval-agent-document-reviewer` with `CASE_ARGS += --scaffold`. Ephemeral check: `make help` lists the four targets once the case folders exist; `make -n eval-skill-hld` shows the flags
    - _Requirements: 9.3_

- [x] 9. Check that each skill's name matches its folder
  - Add a free check under `checks/` that, for every `plugins/ponderly/skills/*/SKILL.md`, the frontmatter `name` equals the folder's name, in plain `unittest`, standard library only, Python 3.9 syntax, paths resolved from the file's own location, in its own file whose module docstring names the concern, as the root README's Testing section says. Found in wave 1: `strategy/SKILL.md` and `lld/SKILL.md` were written with `name: hld`, and nothing caught it. Ephemeral check: set one skill's `name` wrong in a scratch copy of the tree and see the check fail, then pass on the real tree; `make validate` passes
  - _Requirements: 9.4_

- [x] 10. Realign the root README's make block
  - In the root `README.md` Evals section, the comments of the `make ...  # ...` lines start at column 33 except the new `make eval-agent-document-reviewer` line, whose comment starts at column 37. Pad the eight short lines, `make help` through `make eval`, so their comments start in one column, the one the longest of them needs; the two lines that pass flags keep their own column; change nothing else. Ephemeral check: `git diff -- README.md` shows whitespace changes inside that block only; `make validate` passes
  - _Requirements: 9.3_

- [x] 8. Run the evals
  - The author runs `make eval-skill-strategy`, `make eval-skill-hld`, `make eval-skill-lld` and `make eval-agent-document-reviewer`, one at a time, iterating with `EVAL_ARGS="--runs 1 --case <name>"` and confirming at the default three runs, fixing a grader or the skill text as the design's error-handling rows say; then `make eval-rule-workflow` once as the regression check for task 5; and pastes the tables into the pull request's Testing section
  - **Property 2: No draft reaches the author unreviewed**
  - **Validates: Requirements 9.1, 9.2, 5.1, 6.1, 1.5**

- [x] 11. Check that every frontmatter block parses as YAML
  - Add a free check under `checks/`, in its own file whose module docstring names the concern, in plain `unittest`, standard library only, Python 3.9 syntax, paths resolved from the file's own location, that reads the frontmatter of every `evals/**/prompt.md`, every `evals/**/graders/*.md`, every `plugins/ponderly/skills/*/SKILL.md` and every `plugins/ponderly/agents/*.md`, and fails on anything a YAML parser would reject in the shapes those files use: a plain (unquoted) scalar holding `: ` or ` #`, an unbalanced quote, a single-quoted value with an unescaped `'`, a flow list `[...]` that does not close, or a line that is neither `key: value`, a continuation of a block scalar, nor a list item. Found during task 8: two `prompt.md` files held `"Parent: ..."` unquoted, `make validate` passed, and the harness skipped both cases with "invalid YAML frontmatter". Ephemeral check: plant each of those faults in a scratch copy and see the check fail on each, then pass on the real tree; `make validate` passes
  - _Requirements: 9.3, 9.4_

- [x] 12. Flag figures with no source
  - [x] 12.1 Have the reviewer report unsourced figures
    - In `plugins/ponderly/agents/document-reviewer.md`, add to the procedure the sentence the design's agent section gives: every figure, a number, size, rate, date or target, that the parent does not give and the document neither attributes to the author nor derives from figures it states, is reported as a `should-fix`. Change nothing else. Ephemeral check: `checks/test_agents.py` and `checks/test_descriptions.py` pass; `make validate` passes
    - _Requirements: 5.8_
  - [x] 12.2 Have the three skills attribute or carry an unsourced figure
    - In step 5 of `plugins/ponderly/skills/strategy/SKILL.md`, `plugins/ponderly/skills/hld/SKILL.md` and `plugins/ponderly/skills/lld/SKILL.md`, add one identical sentence after the nit rule: an unsourced figure the author gave is fixed by attributing it beside the figure, such as "the author's estimate"; one the author did not give is carried as a question, and never given a source the author did not give. Change nothing else. Ephemeral check: the sentence appears once in each file and `diff` of the three files shows no new difference; `make validate` passes
    - _Requirements: 5.9_

- [x] 13. Add the unsourced-figure reviewer case
  - Create `evals/agents/document-reviewer/flags-an-unsourced-figure/` in the shape of `passes-a-clean-document`: a scaffold that copies `files/` in and runs `evals/fixtures/setup.sh calc main`; `files/` with the strategy, the HLD and an LLD consistent with the HLD whose Risks section states one plain figure the HLD does not give and the LLD does not attribute (for example "the store holds at most 50 GB"), and a copy of the LLD template; a prompt that launches the agent with the three paths and replies with its Findings verbatim; graders `tool_used` Agent, a regex quoting the figure, and a regex `severity:\s*should-fix`. In `passes-a-clean-document`, attribute its "20,000 owner reads a day" figure to the author, so the clean case is not asked where it comes from. Ephemeral check: the scaffold run by hand plants the files; `make validate` passes, which runs the YAML frontmatter check
  - _Requirements: 9.5_


## Notes

- Every task runs `make validate` before it is done; an ephemeral check is created in a scratch location and deleted afterwards.
- Tasks 1.1, 1.2, 1.3, 2, 3 and 4 run together: they touch disjoint files, and `make validate` passes only once all six are on disk, because `checks/test_issue_forms.py` compares the forms with the skills and agents present.
- Task 3 writes three files in one sitting on purpose: the design's first key decision wants the skeleton identical across the three skills, and three executors writing in parallel would drift.
- The executor quotes the design's text where the design quotes it, the Findings shape, the launch prompt, the Document_Summary, and the exclusion clause, and invents nothing the design does not say; a gap in the design is reported as drift, not filled.
- Task 8 is the author's, since the eval runs cost tokens; it gets no sub-agent. Expect a dollar or two per happy-path run, since each launches a real reviewer.
- `start-task`, `implement-spec`, `bugfix`, `pr`, `report`, `wave-reviewer`, `task-executor` and the rules are not touched beyond task 5.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "1.3", "2", "3", "4"] },
    { "id": 1, "tasks": ["5", "6", "7.1", "7.2", "7.3", "7.4", "7.5", "9", "10"] },
    { "id": 2, "tasks": ["8"] },
    { "id": 3, "tasks": ["11", "12.1", "12.2", "13"] }
  ]
}
```
