# Requirements Document

## Introduction

The `ponderly` plugin and the `ponderly` repository that holds it are documented today for the people who build them: the root README describes the repository's layout and its tests, and the plugin README is a table of every skill and rule. Someone who arrives without knowing the plugin cannot tell in a minute what it does, why it exists or whether it works. This task gives both front doors the documentation `inline-email` has: a page that opens with the author's own pitch and an install, task-shaped guides for the real jobs, a reference that holds the detail, evidence measured against Claude Code without the plugin, and an `llms.txt` for AI assistants, with checks that keep every page true to what is on disk. Three readers use it: a Teammate who already trusts the recommendation and only needs to install, an Evaluator who needs convincing before installing, and an AI_Assistant reading on someone's behalf. A changelog is out of scope for this task.

## Glossary

- **Teammate**: A reader who already trusts the recommendation to use the plugin and needs only to install it and start.
- **Evaluator**: A reader who arrives from GitHub or the plugin listing without knowing the plugin and needs to learn what it does, and to see evidence, before installing it.
- **AI_Assistant**: A language model reading the documentation on a person's behalf, to describe, recommend or install the plugin.
- **Reader**: Any of a Teammate, an Evaluator or an AI_Assistant.
- **Front_Door**: The root `README.md` of the repository, which GitHub shows on the repository's page.
- **Listing_Page**: `plugins/ponderly/README.md`, which the plugin listing shows and which ships to every user with the plugin.
- **Pitch**: The author's own statement of what the plugin is and who it is for, as given while this spec was written.
- **Origin_Story**: The author's own statement of why the plugin was built and the experience behind it, as given while this spec was written.
- **Guide**: A page under `docs/guides/` that walks one real job from start to finish with the plugin.
- **Reference**: `docs/reference.md`, which holds the per-skill, per-agent, per-rule and per-hook detail.
- **Evidence_Page**: A page that says how the plugin is tested and shows Eval_Results.
- **Eval_Result**: A score from a `claude plugin eval` run, reported with the run's date, the plugin version, the command that produced it and, where the run measured it, the no-plugin baseline.
- **Session_Capture**: An image of a real Claude Code session with the plugin loaded, either a screenshot or an emulated terminal rendered from the session's saved transcript, labelled with the session's date and the plugin version.
- **Diagram**: A Mermaid flowchart or sequence diagram in a Doc_Page.
- **Neighbour**: A tool a Reader might use instead of the plugin, named in the Front_Door's "when to use it" list.
- **Doc_Page**: Any of the Front_Door, the Listing_Page, a Guide, the Reference, an Evidence_Page or `llms.txt`.
- **Integrity_Check**: A standard-library `unittest` file under `checks/`, run by `make validate`, that compares what the Doc_Pages name with what is on disk.
- **Repo_Metadata**: The GitHub repository's description, topics and homepage, and the `description` fields of `.claude-plugin/marketplace.json` and `plugins/ponderly/.claude-plugin/plugin.json`.
- **System**: The documentation set described by this document, together with its Integrity_Check.

## Requirements

### Requirement 1: Open the Front_Door for a newcomer

**User Story:** As an Evaluator, I want the repository's GitHub page to tell me in the first screen what the plugin does and how to install it, so that I can decide in a minute whether to read further.

#### Acceptance Criteria

1. THE Front_Door SHALL open with the Pitch, in the author's words with spelling and grammar corrected and no claim added.
2. THE Front_Door SHALL state, within its first 40 lines, what the plugin does at a high level and the two commands that install it.
3. THE Front_Door SHALL say that the `sabind` marketplace holds one plugin, `ponderly`, so a Reader knows the repository and the plugin are the same product.
4. THE Front_Door SHALL link each Guide, the Reference, the Evidence_Page and the contributing guide in one line near its top.
5. THE Front_Door SHALL hold a "what this does not do" section that names what the plugin leaves to the author.
6. WHEN the first draft of the Front_Door is shown to the author, THE System SHALL report its line count against a starting bound of 220 lines, the bound `inline-email`'s own newcomer-docs spec set for its README, and the author sets the final bound.
7. IF a section of the current root README is about developing the plugin rather than using it, THEN THE System SHALL move it to `.github/CONTRIBUTING.md` or `evals/README.md`, so that no content is lost and the Front_Door links where it went.

### Requirement 2: Keep the Listing_Page self-contained

**User Story:** As an Evaluator who found the plugin in the plugin listing, I want its page to stand on its own, so that I can understand and install it without visiting GitHub.

#### Acceptance Criteria

1. THE Listing_Page SHALL open with the Pitch, the install commands and one line per skill saying when to use it.
2. THE Listing_Page SHALL keep its "What the plugin runs and sends" section.
3. THE Listing_Page SHALL link the Guides, the Reference and the Evidence_Page with absolute `https://github.com/sabind/ponderly/...` URLs, because it is read outside the repository.
4. THE System SHALL keep every Doc_Page other than the Listing_Page outside `plugins/ponderly/`, so that the plugin ships no page its users did not need.
5. IF the Listing_Page holds fewer than 40 words outside code blocks, THEN THE System SHALL fail `make validate`, as `checks/test_listing.py` does today.

### Requirement 3: Say when to use it

**User Story:** As an Evaluator, I want to see how the plugin compares with the tools I already know, so that I can tell whether it fits my work.

#### Acceptance Criteria

1. THE Front_Door SHALL hold a "when to use it" list that names Claude Code without the plugin and Kiro as Neighbours, each in one or two sentences.
2. THE Front_Door SHALL describe each Neighbour by what it does well as well as by where the plugin differs.
3. IF a statement about a Neighbour cannot be traced to the Neighbour's own documentation or to the author's own use of it, THEN THE System SHALL leave the statement out.
4. WHERE the author later uses a further tool, such as GitHub Spec Kit, THE System SHALL allow it to be added as a Neighbour under the same rule.

### Requirement 4: Show the evidence

**User Story:** As an Evaluator or AI_Assistant who needs more convincing, I want to see how the plugin is tested, how it scores against Claude Code without it, and why it was built, so that I can trust it before installing it.

#### Acceptance Criteria

1. THE Evidence_Page SHALL say, in plain words, what the free checks and the evals each test and how a Reader runs them.
2. THE Evidence_Page SHALL show Eval_Results for the rules and skill descriptions with the no-plugin baseline beside them.
3. THE System SHALL report every Eval_Result with the date of the run, the plugin version and the exact `make` command that produced it.
4. IF a component has no Eval_Result measured against the no-plugin baseline, THEN THE Evidence_Page SHALL say that it is not measured rather than imply a comparison.
5. THE Evidence_Page SHALL give the Origin_Story in the author's words, with spelling and grammar corrected and no claim added.
6. THE Evidence_Page SHALL link at least one merged spec in `.ponderly/specs/` as a real example of what the plugin writes.

### Requirement 5: Guide the real jobs

**User Story:** As a Teammate or Evaluator, I want a guide for each job I would use the plugin for, so that I can do it the first time without reading the Reference.

#### Acceptance Criteria

1. THE System SHALL provide five Guides, in this order: plan a year with `strategy`, `hld` and `lld`; spec and build a feature with `start-task`, `implement-spec` and `pr`; fix a bug with `bugfix` and `pr`; make one contained change through the `task-executor` agent; and tune a template for one repository.
2. THE Guide SHALL open with the job, what the Reader has at the end and what they need before starting.
3. THE Guide SHALL give each step as the exact command or request the Reader types, followed by what the plugin shows and what it writes.
4. THE Guide SHALL show each point where the plugin stops for the Reader, such as an approval question, and the answers it offers.
5. THE Guide for building a feature SHALL show a point where an agent stopped because the design did not fit the code, and what the Reader did next.
6. THE Guide SHALL close with links to the next Guide and to the Reference sections it used.
7. IF a step in a Guide cannot be shown from a Session_Capture, THEN THE Guide SHALL describe the step in words and show no invented output.

### Requirement 6: Show it in pictures

**User Story:** As an Evaluator, I want images and diagrams of the plugin at work, so that I can see what it does without reading every word.

#### Acceptance Criteria

1. THE Front_Door SHALL show one image near its top: a Session_Capture of a hand-back that lists problems first, then what was done, then the next step.
2. THE Front_Door SHALL hold a Diagram of how the skills hand off to one another.
3. WHERE a Guide's job involves more than one agent, such as an `implement-spec` wave with its executors and reviewer, THE Guide SHALL hold a sequence Diagram of it.
4. THE System SHALL use only Session_Captures of real sessions, each labelled with its date and plugin version.
5. WHERE a Session_Capture is rendered from a transcript, THE System SHALL show the transcript's text as recorded, changing nothing but the redactions criterion 9 requires and the plugin's former names, each replaced by its current one.
6. WHERE a Session_Capture is rendered from a transcript, THE System SHALL keep the rendering reproducible from a file in the repository, so that it can be regenerated when the plugin changes.
7. IF rendering a Session_Capture needs a tool the repository does not already use, THEN THE System SHALL add it only on the author's yes.
8. THE System SHALL give every image alt text that says what the image shows.
9. IF a Session_Capture holds a credential, a token, a private repository name or a personal email address, THEN THE System SHALL leave it out until that content is removed.

### Requirement 7: Hold the detail in a Reference

**User Story:** As a Teammate, I want one page with every skill, agent, rule and hook in detail, so that I can look up exactly what a component does.

#### Acceptance Criteria

1. THE Reference SHALL describe every skill, agent, rule and hook under `plugins/ponderly/`, each in a section of its own.
2. THE Reference SHALL open with a table of contents that links each section.
3. THE Reference SHALL give each skill's command, its arguments, when it applies, what it writes and the skill it hands off to.
4. WHEN detail moves from the Listing_Page or the Front_Door to the Reference, THE System SHALL leave a one-line pointer to the new section where the detail was.

### Requirement 8: Serve AI assistants

**User Story:** As an AI_Assistant, I want a short machine-readable summary of the plugin, so that I can describe, recommend or install it correctly without reading every page.

#### Acceptance Criteria

1. THE System SHALL provide an `llms.txt` at the repository root, in the format of llmstxt.org: a title, a one-paragraph summary, then sections of links with one line each.
2. THE `llms.txt` SHALL name every skill and agent with one line saying when to use it.
3. THE `llms.txt` SHALL state the install commands, what the plugin needs (Claude Code, and `gh` for `pr` and `bugfix`), the license, and what the plugin runs and sends.
4. THE `llms.txt` SHALL link the Front_Door, each Guide, the Reference and the Evidence_Page.
5. IF a skill, agent or rule exists under `plugins/ponderly/` and `llms.txt` does not name it, THEN THE Integrity_Check SHALL fail.

### Requirement 9: Keep the pages true to the code

**User Story:** As the author, I want a free check that fails when a page names something that is not there, so that the documentation cannot drift from the plugin.

#### Acceptance Criteria

1. THE Integrity_Check SHALL run under `make validate`, with the standard library only and no model call.
2. WHEN a Doc_Page names a skill, an agent, a rule, a `/ponderly:` command, a `make` target, a repository path or a relative link, THE Integrity_Check SHALL confirm that it exists on disk.
3. THE Integrity_Check SHALL confirm that every skill, agent and rule under `plugins/ponderly/` appears in the Listing_Page, the Reference and `llms.txt`.
4. THE Integrity_Check SHALL confirm that every image a Doc_Page references exists in the repository.
5. IF the Integrity_Check finds a name that does not exist or a component no page names, THEN THE Integrity_Check SHALL fail with the page, the line number and the name.

### Requirement 10: Align the metadata

**User Story:** As an Evaluator searching GitHub or the plugin listing, I want the repository's short descriptions to say what the plugin does, so that I find it and recognise it.

#### Acceptance Criteria

1. THE Repo_Metadata SHALL describe the plugin in the words of the Pitch, each description at most 350 characters, GitHub's limit for a repository description.
2. THE GitHub repository SHALL carry topics that name what the plugin is for, such as `claude-code` and `claude-code-plugin`.
3. WHEN the System changes the GitHub description, topics or homepage, THE System SHALL show the new values to the author and change them only on the author's yes.
4. IF the homepage has no page other than the repository itself, THEN THE System SHALL leave the homepage empty.
