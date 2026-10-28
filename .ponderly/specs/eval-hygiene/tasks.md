# Implementation Plan

## Overview

The check comes first, since the README names it. Then the documentation edits in one wave, since they touch different files. The Linux run and the issue comments come last, since the run proves nothing about this branch and the comments describe the finished state. The handbook's test framework is the stdlib `unittest` files under `checks/`, so the check is both the deliverable and its own proof against the live suite; its correctness on broken input is proved by an ephemeral check. Every command runs in the worktree at `/Users/dansabin/autohdr/developer-handbook-evals`.

## Tasks

- [x] 1. The check
  - [x] 1.1 Write `checks/test_eval_cases.py`
    - Module docstring in the style of `checks/test_issue_forms.py`: one sentence saying what the check keeps true. `ROOT` from the file's location. `KNOWN_TYPES` as the design's table, with a comment-free structure: a dict from type to its required frontmatter fields, and `llm` handled by a non-empty body. `cases()` yields `(case_dir, component)` for every `evals/**/prompt.md`, component from the path (`evals/<kind>/<name>/<case>/` gives `name`; `evals/hook/<case>/` gives `hook`). `frontmatter(path)` returns the `key: value` pairs between the first two `---` lines and the body after, raising `ValueError` with the file name when the fences are missing or a line is not `key: value`; an inline-map value such as `target: { ... }` is kept as its raw string. Three test methods: `test_every_case_is_tagged_with_its_component`, `test_every_case_has_valid_graders`, `test_scaffolds_are_wired_and_executable`, each looping over all cases, collecting every problem as `path: reason`, and failing once with the list joined by newlines; a fourth, `test_there_are_cases`, fails if none are found. The scaffold test reads `scaffold_script:` from `case.yaml` by a line match, checks the named file exists, `is_file()`, not `is_symlink()`, and `os.access(path, os.X_OK)`, and separately that a `scaffold.sh` present without `case.yaml` is a problem. Run `make check` and `time make check`
    - **Property 1: Every case is reachable by its target**
    - **Property 2: Every grader can score**
    - **Property 3: Scaffolds run when named and are named when present**
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_
  - [x] 1.2 Prove the check on broken input
    - Ephemeral: copy `evals/agents/task-executor/standalone-mode/` into a scratch tree under the scratchpad shaped `evals/agents/task-executor/standalone-mode/`, make the check accept an alternative root (an `EVAL_CHECK_ROOT` environment variable read at import, defaulting to `ROOT`, is the smallest way; keep it only if it stays under three lines, otherwise monkeypatch `ROOT` from the scratch script), then break the copy four ways in turn and assert the matching message: remove `task-executor` from `tags`; change a grader's `type` to `regx`; remove `pattern` from a regex grader; `chmod -x scaffold.sh`. Delete the scratch tree. Record the four messages in the Summary
    - _Requirements: 1.3, 1.5, 1.6, 1.9_

- [x] 2. Documentation and the twin
  - [x] 2.1 Rewrite the cadence paragraph in `evals/README.md`, Running
    - Replace the paragraph beginning "A single run is noisy" with the design's cadence rule text: run only the `make` target of the component touched, the whole suite only for a change to `hooks/` or the Makefile; iterate at `--runs 1`; confirm at two runs when every grader is `regex`, `tool_used` or `file_exists`, at three when any grader is `llm`; `--case` takes one glob and the last `--case` flag wins, so several named cases need one invocation each. Keep the example commands block; drop the `--case` example's claim if it implies more than one. Read back
    - _Requirements: 2.1, 2.2, 2.3_
  - [x] 2.2 Name the check in `evals/README.md`, Writing a case
    - One or two sentences at the end of the section: `checks/test_eval_cases.py`, run by `make validate`, keeps tags, graders and scaffolds valid, without listing its assertions. Read back
    - _Requirements: 2.5_
  - [x] 2.3 Make the Makefile header agree
    - In the Makefile's header comment, the lines about defaults and runs say the same cadence as the README in one or two lines; nothing else in the Makefile changes. `make help` unchanged
    - _Requirements: 2.4_

- [x] 3. The Linux run and the issues
  - [x] 3.1 Run the hook eval under Linux once, done by the author with Claude driving
    - In the scratchpad, write a Dockerfile from a tagged Node LTS image (`node:22-bookworm` or the current LTS tag) that installs `@anthropic-ai/claude-code` globally and `make`; copy the worktree's checkout into the build context without `.git`, `evals/results` and `.claude/settings.json`; run the container with `-e ANTHROPIC_API_KEY` or `-e CLAUDE_CODE_OAUTH_TOKEN` from the author's shell, never written to a file, executing `make eval-hook EVAL_ARGS="--runs 1"` in the copied checkout; capture the result table, `claude --version` and the image tag. Then remove the image, the container and the scratch build context. Stop and say so if Docker is not running or neither token is set
    - _Requirements: 3.1, 3.2, 3.4, 3.5_
  - [x] 3.2 Record the run on issue #4
    - A `gh issue comment 4` with the table, the image tag, the Claude Code version and the exact `docker build` and `docker run` commands with the token shown as a placeholder, so the run can be repeated by hand. No token in the comment
    - _Requirements: 3.3_
  - [x] 3.3 Note on issues #3 and #13 what shipped and what was dropped
    - A `gh issue comment 3` saying the rules-size half shipped in #21 as `checks/test_rules_size.py` and the tag half ships with this branch's PR; a `gh issue comment 13` saying the fewer-variants item was dropped by decision on 2026-10-13 and the rest ships with this branch's PR
    - _Requirements: 4.2_
  - [x] 3.4 Validate the finished branch
    - `make validate` green; `make help` lists the same targets as before; `git status` shows only the intended files. Record the result for the PR's Testing section
    - _Requirements: 4.3_

## Notes

- Every command runs in the worktree at `/Users/dansabin/autohdr/developer-handbook-evals`, never in the main checkout, which another session is using.
- The check follows `checks/test_issue_forms.py` for docstring style, root discovery and failure messages; standard library only.
- Model calls happen only in task 3.1, once, at one run per case; nothing else in this plan costs a seat.
- The PR closes #3, #13 and #4 (Requirement 4.1), through the `pr` skill.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["1.2", "2.1", "2.2", "2.3"] },
    { "id": 2, "tasks": ["3.1", "3.3"] },
    { "id": 3, "tasks": ["3.2", "3.4"] }
  ]
}
```
