# Requirements Document

## Introduction

The handbook's evals are real model calls, run by hand per component, and three things make them costlier or less trustworthy than they need to be. A case that loses its component tag, a grader whose frontmatter does not parse, or a scaffold that is not a regular executable file is silently never run or never scored, and nothing free catches it. The eval README still says three runs is the confirmation and does not say that `--case` takes one glob, so contributors over-run and mis-select. And the SubagentStart hook has only ever been seen firing inside a sub-agent on macOS, while CI runs on Linux. This task adds free structural checks under `checks/` that `make validate` runs, records the cheaper cadence and the case-selection rule in the README, and runs the hook eval once under Linux in a scratch container, recording the result on the issue. Issues #3, #13 and #4.

## Glossary

- **Case**: A directory under `evals/` holding a `prompt.md` with frontmatter, a `graders/` directory, and optionally `case.yaml` and `scaffold.sh`.
- **Component**: A skill, agent, rule or hook of the plugin, named by the directory under `skills/`, `agents/` or `rules/`, or `hook`.
- **Tag**: An entry in a Case's `tags` frontmatter list; `make eval-*` selects Cases with `--tag <component>`.
- **Grader**: A file under a Case's `graders/` directory whose frontmatter holds a `type` and that type's fields.
- **Known_Type**: One of the grader types the harness supports and the repository uses: `regex`, `tool_used`, `file_exists`, `llm`.
- **Required_Fields**: The fields a Grader of a Known_Type must carry: `pattern` for `regex`; `tool` for `tool_used`; `path` and `exists` for `file_exists`; `prompt` or the field the harness documents for `llm`.
- **Scaffold**: A Case's `scaffold.sh`, named by `case.yaml`'s `context.scaffold_script`, which builds the Case's workspace before the run.
- **Free_Check**: A standard-library `unittest` file under `checks/`, discovered by `make check` and run by `make validate` and CI, making no model call.
- **Cadence**: The number of runs per Case a contributor uses: one while iterating, and a confirmation count before trusting a change.
- **Deterministic_Grader**: A Grader of type `regex`, `tool_used` or `file_exists`, whose verdict depends only on the transcript and the workspace.
- **Hook_Eval**: The two Cases tagged `hook`, run by `make eval-hook`, which show the handbook rules loaded into a session and into a sub-agent.
- **Linux_Run**: A one-off run of the Hook_Eval inside a scratch Linux container on the contributor's machine, with the plugin loaded from a copy of the checkout.
- **Token**: The credential the container needs to call the model: an `ANTHROPIC_API_KEY` or a `CLAUDE_CODE_OAUTH_TOKEN` from `claude setup-token`, passed as an environment variable and never written to disk in the repository.

## Requirements

### Requirement 1: Free checks on case structure

**User Story:** As a contributor, I want a case that cannot run or cannot be scored to fail `make validate`, so that a silent gap in the suite is caught before merge rather than discovered when a change goes untested.

#### Acceptance Criteria

1. THE plugin SHALL ship a Free_Check `checks/test_eval_cases.py` in the style of `checks/test_issue_forms.py`.
2. THE Free_Check SHALL discover every Case under `evals/` by its `prompt.md`, and SHALL fail if there are none.
3. THE Free_Check SHALL assert that every Case's `tags` list contains the Component name derived from the Case's path (`evals/skills/<name>/`, `evals/agents/<name>/`, `evals/rules/<name>/` give `<name>`; `evals/hook/` gives `hook`), naming the Case and the missing Tag on failure.
4. THE Free_Check SHALL assert that every Case has at least one Grader.
5. THE Free_Check SHALL assert that every Grader's frontmatter parses as `key: value` lines between `---` fences, that its `type` is a Known_Type, and that its Required_Fields are present, naming the Grader file and the problem on failure.
6. WHEN a Case has a `case.yaml` naming a `scaffold_script`, THE Free_Check SHALL assert that the named file exists beside it, is a regular file (not a symlink), and is executable by its owner.
7. THE Free_Check SHALL assert that a Case with a `scaffold.sh` also has a `case.yaml` naming it, so a scaffold is never silently skipped.
8. THE Free_Check SHALL use only the standard library, and SHALL run in under five seconds on the current suite.
9. IF a Grader uses a `type` the repository has not used before, THEN THE Free_Check SHALL fail with a message saying to add the type and its Required_Fields to the check, so the list stays deliberate.

### Requirement 2: The README records the cheaper cadence

**User Story:** As a contributor, I want the eval README to tell me how many runs to make and how to select cases, so that I spend the least on my own seat for a trustworthy answer.

#### Acceptance Criteria

1. THE eval README SHALL say to run only the `make` target of the Component the change touched, never the whole suite, unless the change is to the hooks or the Makefile.
2. THE eval README SHALL say to iterate at `--runs 1` and to confirm at two runs when every Grader of the Case is a Deterministic_Grader, and at three runs when any Grader is an `llm` judge.
3. THE eval README SHALL say that `--case` takes one glob and that the last `--case` flag wins, so several named Cases need one invocation each.
4. THE Makefile's header comment SHALL agree with the README on Cadence and on `--case`.
5. THE eval README SHALL name the Free_Check of Requirement 1 as what keeps Tags, Graders and Scaffolds valid, in the "Writing a case" section, without listing its individual assertions.

### Requirement 3: The hook eval is seen under Linux once

**User Story:** As a maintainer, I want to see the SubagentStart hook fire inside a sub-agent on Linux once, so that the one behaviour CI cannot exercise is confirmed on the platform CI uses, without adding anything to the repository for it.

#### Acceptance Criteria

1. THE Linux_Run SHALL be performed once in this task from a scratch Docker container on the contributor's Mac: a tagged Node LTS image with Claude Code installed, the checkout copied in, and `make eval-hook` run with the plugin loaded from that copy.
2. THE container SHALL receive the Token only as an environment variable, and the Token SHALL appear in no file, no shell history the task writes, and no issue comment.
3. THE Linux_Run's result table, the image tag, the Claude Code version and the exact command used SHALL be recorded as a comment on issue #4, so the run can be repeated by hand.
4. THE task SHALL add no file to the repository for the Linux_Run; the scratch container, its image build context and any copied checkout SHALL be removed when the run is done.
5. IF Docker is not running or the Token is unset, THEN THE task SHALL stop and say so rather than run the eval elsewhere.

### Requirement 4: Issue housekeeping

**User Story:** As a maintainer, I want the three issues to reflect what shipped where, so that the board is honest.

#### Acceptance Criteria

1. THE pull request for this task SHALL close #3, #13 and #4.
2. A comment on #3 SHALL note that its rules-size half shipped in #21 as `checks/test_rules_size.py`, and a comment on #13 SHALL note that its fewer-variants item was dropped by decision, before this task's PR closes them.
3. THE `make validate` target SHALL pass, and the existing Cases SHALL all pass the new Free_Check without modification; where one does not, the Case is fixed in this task and the fix named in the PR.
