# Implementation Plan

## Overview

The labels and the two pull request templates come first, because the issues, the forms, the Guide and the skill all refer to them; then the documents, the forms and the skill change; then the README pointer and the version; then the runs and the author's own actions. The repository has no code, so proof is `make validate` after every change, an ephemeral check that reads each file back against the design, one eval run with a kept transcript, and manual checks the author performs, two of them after the merge because GitHub reads templates and community files from the default branch only.

## Tasks

- [x] 1. Repository settings
  - [x] 1.1 Create the three new labels
    - `gh label create quality --color 5319e7 --description "The behaviour of the skills, agents and rules, and the evals and checks that guard it"`, `gh label create compatibility --color 1d76db --description "Working across Claude Code, Cursor, Codex and other agent tools"`, `gh label create triage --color e4e669 --description "Not yet classified by a maintainer"`. Prove it with `gh label list --json name,color,description`: the three present with those colours and descriptions
    - _Requirements: 3.1, 7.5_
  - [x] 1.2 Relabel and type issues #1 to #4
    - For each: `gh issue edit <n> --add-label quality --remove-label "effort: <its value>" --remove-label "area: quality"`, keeping its priority label, then `gh issue edit <n> --type <Type>` with #1 Feature and #2, #3 and #4 Task, confirmed by the author. Prove it with `gh issue list --state all --json number,labels,issueType`: each issue carries one `priority:` label and `quality`, no `effort:` or `area:` label, and its type
    - _Requirements: 7.5_
  - [x] 1.3 Delete the ten labels that are no longer in the set
    - `gh label delete <name> --yes` for `bug`, `enhancement`, `documentation`, `duplicate`, `invalid`, `wontfix`, `effort: high`, `effort: medium`, `effort: low` and `area: quality`; after 1.2, so that the issues already carry `quality`. Prove it with `gh label list`: exactly the nine of the design's Labels table, each once, nothing else
    - **Property 1: Label closure**
    - **Validates: Requirements 3.1, 7.5**
  - [x] 1.4 The author makes the repository public and enables private vulnerability reporting
    - An action for the author, by hand: `gh repo edit sabind/ponderly --visibility public --accept-visibility-change-consequences`, then `gh api -X PUT repos/sabind/ponderly/private-vulnerability-reporting`. Ticked on their report, checked with `gh repo view --json visibility` showing `PUBLIC` and `gh api repos/sabind/ponderly/private-vulnerability-reporting` showing `"enabled": true`
    - _Requirements: 6.4, 7.5_

- [ ] 2. The pr skill and its two templates
  - [x] 2.1 Two templates, one role each
    - `git mv .github/pull_request_template.md skills/pr/pull_request_template.md`, content unchanged. Then write a new `.github/pull_request_template.md` with the same six sections and comments, the Why comment now reading "The problem or goal behind the change. Link the issue, and write `Closes #<number>` when merging finishes it." Nothing else differs. Prove it: `diff <(git show HEAD:.github/pull_request_template.md) skills/pr/pull_request_template.md` is empty; the two files' `## ` headings are identical; `grep -c "Closes #"` is 1 in the `.github/` file and 0 in the `skills/pr/` file
    - _Requirements: 4.5, 4.6_
  - [x] 2.2 Three places in `skills/pr/SKILL.md`
    - Step 5, the Ticket bullet: ask for the ticket in whatever form the author has it, an issue number such as `#12`, an issue URL, or a key from another tracker such as `ENG-1234`, and say any form works. Step 6, Title: the GitHub example `[#12] Add retry to upload worker` beside the key example; the Why bullet: name the ticket as its tracker writes it, link it when the author gave a URL, and add nothing the author's answers or the repository's own template did not call for. Step 6, Description: the sentence as the design's pr skill table quotes it, preferring the repository's own template, whose sections and comments say what that repository wants and take precedence over the bullets below, asking when a comment wants something the author's answers did not give, and falling back to `${CLAUDE_PLUGIN_ROOT}/skills/pr/pull_request_template.md`. Step numbers, `allowed-tools` and every other step stay as they are. Prove it: `grep -rn 'CLAUDE_PLUGIN_ROOT}/.github' .` finds nothing, `grep -c 'pull_request_template.md' skills/pr/SKILL.md` is 2, and `make validate`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  - [x] 2.3 Run the pr eval and keep one transcript
    - `make eval-skill-pr`, both cases at three runs, then `make eval-skill-pr EVAL_ARGS="--keep-temp --runs 1 --case opens-pr-with-stub-gh"`. Read the kept run's `out/trace.jsonl` by its full path from outside the directory, as `evals/README.md` says, and confirm a Read of a path ending `skills/pr/pull_request_template.md` and a `gh pr create` body carrying the template's six headings; the graders cannot see either. Record the eval table and the two facts for the PR's Testing section, then `rm -rf` the kept directory. This run is the no-ticket half of Property 4, the case's "No ticket" answer being unchanged
    - _Requirements: 7.2_
  - [x] 2.4 Manual check: the pr skill with an issue number as the ticket
    - An action for the author: in a session started with `claude --plugin-dir .` on this branch, run `/ponderly:pr`, answer the ticket question with `#<n>` for an open issue of this repository, and stop at the draft without approving it. Confirm that the question says any form works, that the title begins `[#n]`, that the skill asked whether merging finishes the issue unless the answer came with the ticket, that Why names `#n` and ends with `Closes #n` when it does, and that the description carries this repository's six headings. Record it for the PR; the real pull request is opened afterwards with the skill as usual
    - **Property 4: The ticket passes through untouched**
    - **Validates: Requirements 4.1, 4.2, 4.5**

- [x] 3. The Guide and the README
  - [x] 3.1 Write `.github/CONTRIBUTING.md`
    - The eight sections of the design's Guide table, in its order, each saying what its row says and no more. Opening: what the plugin is, links to `LICENSE`, `CODE_OF_CONDUCT.md` and `SECURITY.md`. Set up: clone, `claude --plugin-dir .` for one session, `make validate`, taking over the README's command block. Test: `make validate` is the unit tests under `checks/` then the two validators; evals run by component with `make eval-<kind>-<name>`, are model calls run by hand, and their table goes in the PR's Testing section; a change to a skill, agent, rule or hook comes with an eval case or a change to one, a new skill with at least one case under `evals/skills/<name>/`; a change touching none of them needs no eval and `make validate` is the whole check; the README's Testing section and `evals/README.md` are linked for the how, not restated. Make a change: small, make it; sizeable, `/ponderly:start-task` then `/ponderly:implement-spec`; bug, `/ponderly:bugfix`; branch `<issue number>-<short slug>` when an issue exists and a short slug otherwise, never the default branch, the shape GitHub's Create a branch link gives, and the issue number in front when implement-spec proposes the task name; `/ponderly:pr` with the issue number as the ticket, and the pull request template, linked, as the one place that says how the issue is linked and when to write `Closes #<number>`; a new skill, agent, rule or hook is added to the `component` dropdown of all three forms. Issues: the three forms by name and what submitting one does, the chooser's three links, triage at least weekly in the six steps of Requirement 2.5, an issue opened without a form gets `triage` by hand, a discussion that becomes work is converted to an issue and an issue that is a question to a discussion. Labels and milestones: one Issue_Type per issue; each label group in one sentence; labels lowercase, Issue_Types as GitHub names them; at most one priority and the areas that apply, none being normal; a new label is proposed in an issue; `good first issue` feeds the contribute page and GitHub's surfacing, `help wanted` is work a Maintainer would merge but will not write; a Milestone names a goal, the open ones are the roadmap. Compatibility: what portability across Claude Code, Cursor, Codex and other agent tools means for a skill or rule here, the three seed checks of the design's Data Models, and that the list grows from issues labelled `compatibility`. Settings, not files: one paragraph. Plain Markdown, no company name. Prove it: the eight headings present in order; every relative link resolves to a path in the tree; the README's Testing section is linked, not copied
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.6, 1.7, 2.5, 2.6, 3.2, 3.3, 3.4, 3.5, 3.6, 5.3, 7.5_
  - [x] 3.2 The README pointer
    - Shrink "Add or change a skill or rule" in `README.md` to at most three sentences, one of them linking `.github/CONTRIBUTING.md`, and drop its command block, now in the Guide's Set up. In the Evals subsection remove the sentence "A new skill needs at least one case under `evals/skills/<name>/`.", now in the Guide's Test section; everything else in Testing stays, it is the how. Prove it: count the section's sentences; `grep -rn "at least one case" README.md .github/CONTRIBUTING.md` shows the rule once, in the Guide; `make validate`
    - **Property 5: One source for the contributing conventions**
    - **Validates: Requirements 1.5**

- [x] 4. Issue forms and the chooser
  - [x] 4.1 `.github/ISSUE_TEMPLATE/misbehaving-skill-or-agent.yml`
    - `name: Report a misbehaving skill or agent`, a one-line `description`, `labels: ["triage"]`, `type: Bug`, and a `body` in the order of the design's table: a `markdown` pointer to the Guide's Issues section; `preflight` checkboxes, searched the existing issues and on the latest plugin version, each required; `component` dropdown with the twelve options the design lists; `version` input, the version as `claude plugin list` shows it; `prompt`, `happened` and `expected` textareas; `reproduces` dropdown. Every field required. Prove it by parsing with `ruby -ryaml -e 'p YAML.load_file(ARGV[0])'` (the machine has no PyYAML; ruby is used for the check only, nothing is added to the repository): the top-level keys, unique ids, `required: true` on every field, the dropdown options as listed; then `make validate`
    - _Requirements: 2.1, 2.2, 2.3, 3.6_
  - [x] 4.2 `.github/ISSUE_TEMPLATE/proposal.yml`
    - `name: Propose a new or changed skill, agent or rule`, `labels: ["triage"]`, `type: Feature`; body: the Guide pointer; `preflight` checkboxes, searched the existing issues and looked in Discussions under Ideas, each required; `kind` dropdown with the six options; `component` dropdown with the same list as 4.1, not required, for a change; `behaviour` and `case` textareas, required. Same proof as 4.1
    - _Requirements: 2.1, 2.2, 2.3, 3.6_
  - [x] 4.3 `.github/ISSUE_TEMPLATE/eval-case.yml`
    - `name: Propose an eval case`, `labels: ["triage"]`, `type: Task`; body: the Guide pointer; `preflight` checkboxes, searched the existing issues and read `evals/README.md`, each required; `component` dropdown as in 4.1, required; `behaviour` and `grading` textareas, required; `prompt` textarea, optional. Same proof as 4.1
    - _Requirements: 2.1, 2.2, 2.3, 3.6_
  - [x] 4.4 `.github/ISSUE_TEMPLATE/config.yml`
    - `blank_issues_enabled: false` and three `contact_links`, each with `name`, `url` and `about`: a question to `https://github.com/sabind/ponderly/discussions/categories/q-a`, an idea to `https://github.com/sabind/ponderly/discussions/categories/ideas`, a vulnerability to `https://github.com/sabind/ponderly/security/policy`. Prove it: the ruby parse as in 4.1, and `gh api graphql -f query='{ repository(owner:"sabind", name:"ponderly") { discussionCategories(first:20) { nodes { slug } } } }'` listing `q-a` and `ideas`, the categories Discussions already has
    - _Requirements: 2.4, 5.1, 5.2_

- [x] 5. Community files
  - [x] 5.1 `LICENSE` and the manifest's license field
    - `LICENSE` at the repository root: the text of `gh api licenses/mit --jq .body` with `[year]` replaced by `2026` and `[fullname]` by `Dan Sabin`. `.claude-plugin/plugin.json` gains `"license": "MIT"`. Prove it: `diff` the file against the API text with the two replacements made, and `make validate`; if `claude plugin validate --strict` rejects the field, drop it, keep `LICENSE`, and say so in the summary
    - _Requirements: 6.1, 7.1_
  - [x] 5.2 `.github/CODE_OF_CONDUCT.md`
    - The Contributor Covenant 2.1 Markdown from `https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md`, unchanged except `[INSERT CONTACT METHOD]`, replaced by the address the organization's profile already lists. Prove it: `diff` against the downloaded source shows that one line and nothing else
    - _Requirements: 6.2_
  - [x] 5.3 `.github/SECURITY.md`
    - A short policy: a vulnerability is reported through GitHub's private vulnerability reporting, the Report a vulnerability button on the repository's Security tab, never in a public issue or discussion; the latest release is the supported version. Nothing the requirement does not say. Manual check: read it against Requirement 6.3
    - _Requirements: 6.3_

- [ ] 6. Ship
  - [x] 6.1 Bump the plugin version
    - `.claude-plugin/plugin.json` from `0.5.0` to `0.5.1`; `make validate`
    - _Requirements: 7.1, 7.3_
  - [ ]* 6.2 After the merge: the forms on GitHub
    - An action for the author, once the branch is on `main`: open each of the three forms from the Template_Chooser and confirm its fields, dropdown options and required marks render, that the title shows the form's `name`, and that submitting with a required field empty is refused; do not submit. Record the result in a follow-up or the merged PR's conversation
    - **Property 2: Every form arrives marked**
    - **Validates: Requirements 2.1, 2.2, 2.3, 7.4**
  - [ ]* 6.3 After the merge: the chooser and the community profile
    - An action for the author, once the branch is on `main`: the Template_Chooser lists the three forms and the three links with no blank issue offered, each link resolves, and the repository's community profile page lists the license, the code of conduct, the contributing guide and the security policy; `gh repo view --json licenseInfo` shows MIT. Record the result as in 6.2
    - **Property 3: No unrouted entry**
    - **Validates: Requirements 2.4, 5.2, 6.1, 7.4**

## Notes

- Sub-tasks marked `*` are optional; implementation sub-tasks are never optional. 6.2 and 6.3 can only run after the merge, so a run of this plan skips them and the author does them from the merged branch.
- `make validate` is the unit test and the full suite for this repository. Run it after every change under `skills/`, `.claude-plugin/`, `checks/` or `README.md`, and at the end of every wave. Nothing in this plan adds a check, a script, a grader or a skill sentence about this repository's labels, branches or `Closes` lines: the plugin stays tracker-agnostic and the checks maintain the plugin, not this repository's project management.
- Evals cost real model calls. Run them only at task 2.3.
- The author settled the two inputs on 2026-10-12: the code of conduct contact is the organization's contact address (5.2), and the Issue_Types are #1 Feature and #2 to #4 Task, as the design proposes (1.2).
- Tasks 1.4, 2.4, 6.2 and 6.3 are the author's own actions; the executor asks for them and ticks them on the author's report.
- Ephemeral checks of the YAML forms use `ruby -ryaml`, which macOS ships; the machine has no PyYAML, and no parser is added to the repository.
- Task numbers identify tasks; the graph below decides the order. Review happens at the end of each task or each wave, by the author's cadence.
- Work on the `contributing-guide` branch, never on main.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1", "5.1", "5.2", "5.3"] },
    { "id": 1, "tasks": ["1.2", "2.2", "3.1", "4.1", "4.2", "4.3", "4.4"] },
    { "id": 2, "tasks": ["1.3", "3.2", "6.1"] },
    { "id": 3, "tasks": ["1.4", "2.3", "2.4", "6.2", "6.3"] }
  ]
}
```
