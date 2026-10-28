# Requirements Document

## Introduction

The plugin is moving from the `freethinkingit` organisation to Dan's personal account as `sabind/ponderly`, and it must arrive under its new names, so that nothing after the move carries the old organisation's names or identity. This task renames the plugin from `freethinking` to `ponderly` and the marketplace from `freethinkingit` to `sabind`, moves the working folder that skills read and write from `.freethinking/` to `.ponderly/`, points every absolute link at `github.com/sabind/ponderly`, gives the plugin Dan's own identity, and carries the open draft pull requests #73 and #71 onto the new names. The owner gets a repository ready to transfer; the operator types `/ponderly:<skill>` and installs `ponderly@sabind`; a reader sees one name throughout. The transfer itself, draft PR #72 on the `newcomer-docs` branch, removing the old install from Dan's machine and a migration release are not part of this task. Issue #76.

## Glossary

- **Repository**: This repository, today `freethinkingit/dev_tools`, transferred by hand to `sabind/ponderly` after this task merges.
- **Plugin**: The Claude Code plugin the Repository ships, today `freethinking` in `plugins/freethinking/`.
- **Marketplace**: The marketplace the Repository declares in `.claude-plugin/marketplace.json`, today `freethinkingit`.
- **Old_Names**: The strings `freethinking` (in any case, which covers `freethinkingit`, `.freethinking/` and `freethinking.it`) and `dev_tools`.
- **New_Names**: `ponderly` for the Plugin, its folder and its namespace; `sabind` for the Marketplace; `sabind/ponderly` for the Repository; `.ponderly/` for the Work_Folder.
- **Namespace**: The prefix by which skills and agents are invoked and named, `freethinking:<name>` today, as in `/freethinking:start-task` and `subagent_type: freethinking:task-executor`.
- **Work_Folder**: The folder at the root of any repository the Plugin works in, where skills keep specs, strategies, designs and template overrides; `.freethinking/` today.
- **Records**: The merged specs under the Work_Folder's `specs/` folder of this Repository, and its strategy under `strategies/`.
- **Identity**: The owner's details the Repository publishes: the author name, email and URL in `plugin.json`, the copyright holder in `LICENSE`, and the report contact in `.github/CODE_OF_CONDUCT.md`. The new Identity is Dan Sabin, `dan.sabin@gmail.com`, `https://dansabin.com`.
- **Issue_Forms**: The YAML forms under `.github/ISSUE_TEMPLATE/`, and their `config.yml`.
- **Type_Labels**: The labels `type: bug`, `type: feature`, `type: task` and `type: spike`, which already exist on the Repository.
- **Draft_PRs**: The open draft pull requests #73 (`56-experience-first-explanations`) and #71 (`63-canonical-source-hld`); #72 is not one of them.
- **Name_Search**: The command `rg -n -i --hidden -g '!.git' 'freethinking|dev_tools'` run at the root of a branch's working tree.
- **Validation**: `make validate` and `make check` at the root of the Repository.

## Requirements

### Requirement 1: The plugin answers to ponderly

**User Story:** As the operator, I want every skill and agent to answer to `ponderly`, so that each command I type and each hand-off between skills reaches a name that exists.

#### Acceptance Criteria

1. THE Plugin SHALL live in `plugins/ponderly/`, moved with its history, and SHALL be named `ponderly` in its `plugin.json`.
2. THE Plugin SHALL use the Namespace `ponderly:` in every skill, agent, rule, hook, README and template that names a skill or agent, including every hand-off between skills and every `subagent_type`.
3. IF any file under `plugins/ponderly/` still contains one of the Old_Names, THEN the Name_Search SHALL report it and the task SHALL not be done.
4. THE Plugin's `plugin.json` version SHALL be `1.0.0`, marking the new name as a fresh start, unless the owner chooses another version before the task is done.

### Requirement 2: The marketplace is sabind

**User Story:** As the operator, I want to install with `claude plugin marketplace add sabind/ponderly` and `claude plugin install ponderly@sabind`, so that the install matches where the Repository will live.

#### Acceptance Criteria

1. THE Marketplace SHALL be named `sabind` in `.claude-plugin/marketplace.json` and SHALL list one plugin, `ponderly`, with source `./plugins/ponderly`.
2. THE Repository's README and the Plugin's README SHALL give the install, update and marketplace-selection steps with `sabind/ponderly`, `ponderly@sabind` and the `sabind` Marketplace.
3. WHEN `claude plugin validate` runs on the Repository root, on `plugins/ponderly` and on `plugins/ponderly/skills` with `--strict`, THE validation SHALL pass.

### Requirement 3: The work folder is .ponderly/

**User Story:** As the operator, I want skills to keep their specs, strategies, designs and templates in `.ponderly/`, so that no repository the Plugin works in carries the old name.

#### Acceptance Criteria

1. THE Plugin's skills, agents, rules and templates SHALL read and write the Work_Folder as `.ponderly/`, and SHALL name no `.freethinking/` path.
2. THE Repository's own Work_Folder SHALL be moved from `.freethinking/` to `.ponderly/` with `git mv`, every Record included, so that each file keeps its history.
3. THE Plugin's README SHALL say that the Work_Folder is `.ponderly/`, and SHALL not keep the note about the 0.14.0 move from `.claude/specs/`.
4. THE eval cases and scaffolds that create or read a Work_Folder SHALL use `.ponderly/`.

### Requirement 4: Records are rewritten once to the new names

**User Story:** As the owner, I want the merged specs and the strategy to use the New_Names, so that the old names appear nowhere in the Repository, as a one-time exception, which I approve, to the rule that a merged spec is a record and is not edited.

#### Acceptance Criteria

1. THE Records SHALL have every Old_Name replaced by its New_Name: the Plugin, the Namespace, the Work_Folder, the Marketplace and the Repository.
2. THE rewrite of the Records SHALL change names only, and SHALL change no other word, decision, number or checkbox in them, except on a line where the New_Name would make the sentence false, which SHALL be reworded as little as keeps it true without an Old_Name.
3. IF an Old_Name in a Record names something outside the Repository, THEN THE rewrite SHALL use that thing's new name where the owner has renamed it, as with `@freethinkingit/gherkin-harness`, which becomes `@sabind/gherkin-harness`, and SHALL list any other case for the owner to decide.
4. THE workflow rule's sentence that a merged spec is a record SHALL keep its meaning, with its path changed to `.ponderly/specs/<task>/`.

### Requirement 5: Evals and checks follow the new names

**User Story:** As a maintainer, I want the checks and the eval suite to find the Plugin under its new name, so that `make validate` and the eval targets still run after the rename.

#### Acceptance Criteria

1. THE checks under `checks/` SHALL find the Plugin at `plugins/ponderly/`.
2. THE `Makefile` SHALL set `PLUGIN` to `plugins/ponderly` and SHALL name its temporary eval folder with `ponderly`, not `freethinking`.
3. THE eval cases' prompts, graders and scaffolds SHALL use the Namespace `ponderly:` and the Work_Folder `.ponderly/`, so that a grader that matches a name matches the new one.
4. WHEN the rename is complete, THE Validation SHALL pass.
5. THE task SHALL be proven by the Name_Search and the Validation, and SHALL run no eval target.

### Requirement 6: Links and issue forms point at sabind/ponderly

**User Story:** As a reader, I want every link to point at `github.com/sabind/ponderly` and every issue form to work on a personal account, so that links and forms keep working after the transfer.

#### Acceptance Criteria

1. THE Repository SHALL replace every `github.com/freethinkingit/dev_tools` URL with the matching `github.com/sabind/ponderly` URL, including the links in `.github/ISSUE_TEMPLATE/config.yml` and in `plugin.json`'s `homepage` and `repository`.
2. THE Issue_Forms SHALL apply their Type_Label through `labels:` in place of the organisation's `type:` key: the bug form `type: bug`, the proposal form `type: feature`, the eval-case form `type: task`, and the spike form `type: spike`.
3. IF an Issue_Form already sets other labels, THEN THE form SHALL keep them beside its Type_Label.
4. THE `.github/CONTRIBUTING.md` guide SHALL name `plugins/ponderly/` in its commands and paths.

### Requirement 7: The identity is Dan's

**User Story:** As the owner, I want the Plugin and the Repository to name me, so that the work is published under my own name rather than the organisation's.

#### Acceptance Criteria

1. THE `plugin.json` author SHALL be Dan Sabin, with email `dan.sabin@gmail.com` and URL `https://dansabin.com`.
2. THE `LICENSE` copyright holder SHALL be Dan Sabin, with the year kept.
3. THE `.github/CODE_OF_CONDUCT.md` report contact SHALL be `dan.sabin@gmail.com`.
4. THE Marketplace's `owner` SHALL be Dan Sabin.

### Requirement 8: Draft pull requests carry the new names

**User Story:** As the owner, I want draft PRs #73 and #71 moved onto the new names, so that they can be finished and merged after the rename without bringing the old names back.

#### Acceptance Criteria

1. WHEN this task's branch is ready, each Draft_PR's branch SHALL be rebased onto it, with the files the Draft_PR moved or added following the renamed paths.
2. THE files each Draft_PR adds or changes SHALL have every Old_Name replaced by its New_Name, as fixes committed on that Draft_PR's own branch.
3. WHEN a Draft_PR's branch is rebased and fixed, THE Name_Search on that branch SHALL find no Old_Name and its Validation SHALL pass.
4. IF a rebase hits a conflict whose resolution is not a name change, THEN THE work SHALL stop and show the conflict to the owner.
5. THE work SHALL commit or push nothing on any branch, including force-pushes of rebased Draft_PRs, until the owner says so.
6. THE work SHALL not touch the `newcomer-docs` branch or draft PR #72.

### Requirement 9: Done means no old name is left

**User Story:** As the owner, I want one search to prove the rename is complete, so that I can transfer the Repository knowing nothing carries the old names.

#### Acceptance Criteria

1. WHEN the task is done, THE Name_Search on this task's branch SHALL find no match, except in this task's own spec, which describes the rename and must name the Old_Names.
2. IF the Name_Search finds a match, THEN THE task SHALL not be reported done, and the match SHALL be listed with its file and line.
3. THE task SHALL not transfer or rename the GitHub Repository, change its settings, or remove the old Plugin or Marketplace from the owner's machine.
