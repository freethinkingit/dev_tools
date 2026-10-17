# Requirements Document

## Introduction

The plugin is submitted to Anthropic's plugin directory, which scans every file in the folder that holds the manifest. Today that folder is the repository root, so the scan reads the eval suite and the spec records as if an installed plugin ran them, and holds the submission for a reviewer on each version. This task moves the plugin into a folder of its own, leaves the test and design material outside it, gives the manifest the fields the listing shows, writes down what the plugin runs and sends, and keeps every check and eval target working from the new layout. Contributors keep the same commands; users keep the same install id; the directory's reviewer sees only the plugin.

## Glossary

- **Plugin_Folder**: The folder `plugins/freethinking/` at the repository root that holds the Manifest and every file an installed plugin loads: `skills/`, `agents/`, `rules/`, `hooks/`, the plugin README and the Icon.
- **Repository_Root**: The top folder of the repository, holding the Marketplace_File, `evals/`, `checks/`, `.claude/specs/`, the Makefile, the CI workflow, the contributing guide, the LICENSE and the root README.
- **Manifest**: The file `plugins/freethinking/.claude-plugin/plugin.json`.
- **Marketplace_File**: The file `.claude-plugin/marketplace.json` at the Repository_Root, whose one entry names the plugin and points at the Plugin_Folder.
- **Listing_Fields**: The Manifest fields the Directory shows: `displayName`, `homepage`, `repository`, `icon`, `keywords`, `author` and `version`.
- **Icon**: The square PNG at `plugins/freethinking/.claude-plugin/icon.png`, 1024 pixels on each side.
- **Directory**: Anthropic's plugin directory, submitted to from the developer portal at claude.ai/directory/manage.
- **Validator_Shape**: The form of a hook script that the Directory's validator follows when the Plugin_Folder is a subfolder: every path written in full from `${CLAUDE_PLUGIN_ROOT}`, no other shell variable, no command substitution, no package launcher, and no call to another file in the plugin.
- **Hook_Script**: One of `hooks/load-rules.sh` and `hooks/load-rules-subagent.sh` in the Plugin_Folder.
- **Run_Tree**: A temporary folder, built by the Makefile for one eval invocation, holding a copy of the Plugin_Folder's contents with a copy of `evals/` inside it and a git repository initialised at its top.
- **Results_Folder**: The folder `evals/results/<timestamp>/` at the Repository_Root where one eval invocation writes `aggregate-result.json` and `report.html`.
- **Free_Check**: A `unittest` file under `checks/`, run by `make check` and `make validate` with no model call.
- **Disclosure_Section**: The last section of the plugin README, titled "What the plugin runs and sends", written for the Directory's reviewer.
- **Listing_Check**: The Free_Check `checks/test_listing.py` that proves the directory's mechanical listing rules on the Plugin_Folder: the README length, the license and the Icon.
- **Eval_Target**: Any of `make eval`, `make eval-hook`, `make eval-skill-<name>`, `make eval-rule-<name>` and `make eval-agent-<name>`.

## Requirements

### Requirement 1: The plugin lives in its own folder

**User Story:** As the plugin's maintainer, I want every file an installed plugin loads in one folder and nothing else in it, so that the Directory scans the plugin and not the repository.

#### Acceptance Criteria

1. THE Plugin_Folder SHALL hold the Manifest, the Icon, `skills/`, `agents/`, `rules/`, `hooks/` and a `README.md`, each moved from the Repository_Root with its content otherwise unchanged except where a later requirement says.
2. THE Repository_Root SHALL keep the Marketplace_File, `evals/`, `checks/`, `.claude/specs/`, `Makefile`, `.github/`, `LICENSE` and `.gitignore` where they are.
3. THE Plugin_Folder SHALL contain no file under `evals/`, `checks/` or `.claude/specs/`, and no symbolic link.
4. THE Marketplace_File SHALL keep its `name` `freethinkingit` and its entry's `name` `freethinking`, and SHALL point the entry's `source` at `./plugins/freethinking`.
5. WHEN `claude plugin validate . --strict` runs at the Repository_Root and `claude plugin validate ./plugins/freethinking --strict` runs, THE System SHALL print `Validation passed` for each with no warning.
6. WHEN a machine with the plugin installed from this marketplace runs `claude plugin update freethinking@freethinkingit`, THE System SHALL install the new version under the same install id, with every skill, agent, rule and hook loaded.

### Requirement 2: The manifest carries the listing fields

**User Story:** As a developer browsing the Directory, I want the listing to show the plugin's name, publisher, icon, links and tags, so that I can judge it before installing.

#### Acceptance Criteria

1. THE Manifest SHALL set `displayName` to `Freethinking`, `homepage` and `repository` to `https://github.com/freethinkingit/dev_tools`, `icon` to `./.claude-plugin/icon.png`, and `license` to `MIT`.
2. THE Manifest SHALL set `author` to name `FreeThinking IT`, email `hello@freethinking.it` and url `https://freethinking.it`.
3. THE Manifest SHALL set `keywords` to `developer-workflow`, `feature-development`, `bug-fixing`, `pull-requests`, `code-review`, `spec-driven`, `engineering-standards` and `accountability`.
4. THE Manifest SHALL set `version` to `0.12.0`.
5. THE Icon SHALL be a PNG of 1024 by 1024 pixels at the path the Manifest names.
6. IF a Listing_Field is absent, misspelt or not of the type the manifest reference gives, THEN `claude plugin validate ./plugins/freethinking --strict` SHALL fail, and THE System SHALL not be submitted.

### Requirement 3: The plugin README discloses what runs and sends

**User Story:** As the Directory's reviewer, I want the README to say what the plugin runs, reads and sends, so that the security scan's holds can be confirmed against a stated behaviour.

#### Acceptance Criteria

1. THE plugin README SHALL end with the Disclosure_Section.
2. THE Disclosure_Section SHALL state that the `pr` and `bugfix` skills read issues and open pull requests through the `gh` command already signed in on the user's machine and run `git` on the current repository; that the `SessionStart` and `SubagentStart` hooks read only the files under the plugin's `rules/`; that no skill, agent or hook reads a credential, runs a package launcher or sends anything anywhere else; and that the repository's `evals/` and `.claude/specs/` folders are the test suite and the design records, outside the plugin and never run by an installed plugin.
3. THE plugin README's Install section SHALL describe a public repository: no mention of read access, `gh auth login` or `gh auth setup-git`.
4. THE root README SHALL say what the repository holds, link to the plugin README and the contributing guide, and carry the Testing section that the plugin README holds today, since the checks and evals belong to the repository and not to the installed plugin.
5. THE plugin README SHALL keep the Install, Stay up to date, Skills, Rules, Agents and "Tune the plugin for a repository" sections as they are today.

### Requirement 4: The hook scripts take the validator's shape

**User Story:** As the plugin's maintainer, I want the two hook scripts to be ones the Directory's validator follows, so that a submission from a subfolder carries no hold for an unfollowed script.

#### Acceptance Criteria

1. THE Hook_Scripts SHALL each be in Validator_Shape.
2. WHEN `hooks/load-rules.sh` runs with `CLAUDE_PLUGIN_ROOT` set to the Plugin_Folder, THE System SHALL print the "Handbook rules" heading and its introductory sentence followed by the content of every `rules/*.md` file, in name order, each followed by a newline, exactly as the script prints today.
3. WHEN `hooks/load-rules-subagent.sh` runs with `CLAUDE_PLUGIN_ROOT` set to the Plugin_Folder, THE System SHALL print one JSON object whose `hookSpecificOutput.additionalContext` is the exact text of criterion 2, with every byte of it reproduced after JSON decoding, trailing newlines and non-ASCII text included.
4. IF `CLAUDE_PLUGIN_ROOT` is unset or names a folder with no `rules/`, THEN `hooks/load-rules.sh` SHALL exit 0 and print nothing, and `hooks/load-rules-subagent.sh` SHALL exit non-zero with one line on stderr saying the sub-agent gets no rules.
5. THE Free_Check for the JSON encoder SHALL prove criterion 3 by running the subagent Hook_Script against a fixture rules folder it writes itself, covering quotes, backslashes, control characters, non-ASCII text and trailing newlines, in place of feeding the script on stdin.
6. THE Free_Check for the rules size SHALL keep its limit on the session Hook_Script's output and on each rule file, run against the Plugin_Folder.

### Requirement 5: The eval targets run from a copy

**User Story:** As a contributor, I want `make eval-<kind>-<name>` to keep working with the evals outside the plugin, so that moving them costs no change to a case.

#### Acceptance Criteria

1. WHEN an Eval_Target runs, THE Makefile SHALL build a Run_Tree, run `claude plugin eval` against it with the same flags, tags and `EVAL_ARGS` as today, and delete the Run_Tree afterwards, whether the eval passed or failed.
2. WHEN an Eval_Target runs, THE System SHALL write the run's `aggregate-result.json` and `report.html` to a Results_Folder at the Repository_Root, and nothing to `evals/` inside the Run_Tree that survives it.
3. WHEN a case's scaffold runs in the Run_Tree, THE System SHALL resolve `git rev-parse --show-toplevel` to the Run_Tree, so that `$ROOT/evals/fixtures/setup.sh` is the copy inside it and no scaffold or fixture file changes.
4. THE Eval_Targets SHALL keep their names, the enumeration from the `evals/` folders, the per-target flags, `EVAL_MAX_COST_USD`, `EVAL_ARGS` and `make help`'s output.
5. IF the Run_Tree cannot be built, THEN THE Makefile SHALL stop with the failing command's error and run no eval.
6. THE Free_Check for eval cases SHALL keep reading the cases under `evals/` at the Repository_Root.

### Requirement 6: The free checks and the guides follow the layout

**User Story:** As a contributor, I want `make validate` and the guides to describe the repository as it is, so that a change to one part still reaches every part it must.

#### Acceptance Criteria

1. THE Free_Checks that read `skills/`, `agents/`, `rules/`, `hooks/` or the Manifest SHALL read them under the Plugin_Folder, and `make validate` SHALL pass.
2. THE `validate` target SHALL run `make check`, then `claude plugin validate . --strict` for the Marketplace_File and `claude plugin validate ./plugins/freethinking --strict` for the plugin.
3. THE CI workflow SHALL keep running `make validate` unchanged.
4. THE contributing guide, the root README, the plugin README and `evals/README.md` SHALL name paths as they are after the move, including that the plugin loads for one session with `claude --plugin-dir ./plugins/freethinking`, and SHALL say that `evals/` sits outside the plugin and how an Eval_Target runs it.
5. THE Makefile SHALL name the Plugin_Folder in one `PLUGIN` variable, and each Free_Check that reads the Plugin_Folder SHALL name it in one constant at its top, so that adding a second plugin under `plugins/` is one edit per file.
6. IF a backticked repository path in the contributing guide, the root README, the plugin README or `evals/README.md` names a file or folder that does not exist after the move, THEN the wave review SHALL report it as a finding to fix in this task.

### Requirement 7: The portal confirms the result

**User Story:** As the plugin's maintainer, I want the developer portal's validation of the new layout to carry no hold, so that each version goes live without a reviewer wait.

#### Acceptance Criteria

1. WHEN the author validates the repository in the Directory's developer portal with the plugin path `plugins/freethinking` after the change merges, THE report SHALL show no finding with the result "Policy hold" and no finding with the result "Blocks".
2. WHILE a warning remains in that report, THE System SHALL record the warning's title and cause as a comment on issue #43, so the next change knows what is left.

### Requirement 8: The listing rules are checked before the portal

**User Story:** As the plugin's maintainer, I want the directory's mechanical listing rules checked by `make validate`, so that a wrong icon, which the portal takes only once, never reaches a submission.

#### Acceptance Criteria

1. THE Listing_Check SHALL fail when the Plugin_Folder has no `README.md`, or when that README holds fewer than 40 words outside fenced code blocks.
2. THE Listing_Check SHALL fail when the Plugin_Folder has no `LICENSE` file and the Manifest has no `license` field.
3. THE Listing_Check SHALL fail when the Manifest's `icon` names no file, or names a file that is not a PNG, not square, or not between 512 and 2048 pixels on each side, read from the PNG header with the standard library only.
4. THE Listing_Check SHALL pass on the Plugin_Folder as this task leaves it, and `make validate` SHALL run it with the other Free_Checks.
