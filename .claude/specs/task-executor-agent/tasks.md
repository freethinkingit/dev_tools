# Implementation Plan

## Overview

The hook script and the agent file come first, because the checks, the evals and the skill change all depend on them. Then the free checks and the eval cases, then the skill change, then wiring and the runs. The handbook has no code and no unit-test framework beyond `make validate`, which gains the encoder round-trip check in this plan; behaviour is proved by eval cases, run by hand at the task that says so, and by one direct use of the agent by the author.

## Tasks

- [x] 1. The Rules hook for sub-agents
  - [x] 1.1 Write `hooks/load-rules-subagent.sh`
    - POSIX shell plus awk: with no argument, run `load-rules.sh` and wrap its output as `{"hookSpecificOutput": {"hookEventName": "SubagentStart", "additionalContext": "<escaped text>"}}`; with `-`, encode stdin the same way. The awk escapes backslash, double quote and every control character. Exit non-zero on any failure. Prove it with an ephemeral check: pipe a string holding a quote, a backslash, a tab, a newline and a carriage return through `-`, parse with `python3 -c json.loads`, compare
    - _Requirements: 1.2, 1.3, 1.5_
  - [x] 1.2 Register the hook
    - Add a `SubagentStart` entry with no matcher to `hooks/hooks.json`, running the new script with the same quoting as the SessionStart entry. Run `make validate`
    - _Requirements: 1.1_
  - [x] 1.3 Add the encoder checks to `make validate`: fixed table, seeded fuzz, real run
    - A `check-hook` target that `validate` depends on, driven by one `python3 -c` block so there is no test directory or helper script. (a) Fixed table: empty input; a lone quote; a lone backslash; a backslash before a quote; each ASCII control character 0x01 to 0x1f on its own and inside a line; a non-ASCII character; a line with no trailing newline; CRLF line endings. (b) Fuzz: 500 random strings from a fixed seed, each 0 to 2,000 characters drawn from a pool that over-represents quotes, backslashes, control characters, non-ASCII and newlines. (c) The real run: `hookEventName` is `SubagentStart` and `additionalContext` equals the current `load-rules.sh` output. For (a) and (b) each input is piped through `load-rules-subagent.sh -`, the output parsed with `json.loads`, and the decoded `additionalContext` compared byte for byte; the first mismatch prints the input as a Python literal and fails. NUL is excluded from the pools, since it cannot cross a shell pipeline as text and never appears in a rule. Free, no model call. Run `make validate`
    - _Requirements: 1.2_
  - [x] 1.4 Hook eval: a sub-agent sees the rules
    - `evals/hook/subagent-rules-loaded/`: `allowed_tools: [Agent]`, a prompt that launches one general-purpose sub-agent asking it to list the handbook rule headings it sees without tools and paste the reply; graders: regex `Code changes`, regex `Workflow`, regex `NO RULES` not_contains. Tag `hook`
    - _Requirements: 1.4, 5.3_
  - [x] 1.5 Move the encoder check into `checks/`
    - `checks/test_hook_encoder.py`: the same fixed table, seeded fuzz and real run as the Makefile block, as three test methods with the same failure messages. The Makefile loses the `define` block and its comment; `validate` depends on a `check` target that runs `python3 -m unittest discover -s checks`; the header comment names it. Supersedes the shape chosen in 1.3. Run `make validate`
    - _Requirements: 1.2_

- [x] 2. The agent
  - [x] 2.1 Write `agents/task-executor.md`
    - Frontmatter: `name`, `description` (one well-specified change, from a spec task or a single change you describe; use directly for a contained task), `tools: Read, Glob, Grep, Edit, Write, Bash`, `model: opus`, `effort: medium`. Body in the design's parts: Role, Mode, Procedure, Never, Stop and ask, Summary shape, one line on the rules already in context. Run `make validate`
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10, 2.11, 2.12, 3.1, 3.2, 3.3_
  - [x] 2.2 Agent eval, Spec_Mode, and the Makefile target
    - `evals/agents/task-executor/spec-mode/`: scaffold copied from the implement-spec work-loop case (calc package on a branch, bin wrappers; no spec files needed); `allowed_tools: [Read, Glob, Grep, Agent]`; prompt launches `freethinking:task-executor` with the mode sentence and the task text "Add subtract(a, b) to calc/ops.py returning a minus b, in the style of add"; graders: `def subtract` in `calc/ops.py`, `test_subtract` absent from `tests/test_ops.py`, final message contains `status: done`, `checks run:` and `ephemeral check:`. Makefile: `eval-agent-task-executor: CASE_ARGS += --allow-tools Bash Write Edit --scaffold` and `export PATH := bin:$(PATH)`. Tag `task-executor`
    - _Requirements: 5.2_
  - [x] 2.3 Agent eval, Standalone_Mode
    - `evals/agents/task-executor/standalone-mode/`: same scaffold and task text, no mode sentence; graders: `def subtract` in `calc/ops.py`, `test_subtract` in `tests/test_ops.py`, `status: done`
    - _Requirements: 5.2_
  - [x]* 2.4 Agent eval, stop on Drift
    - `evals/agents/task-executor/stops-when-unclear/`: same scaffold; task text names a module that does not exist; graders: `status: stopped` in the final message, `file_exists` `**/*` false
    - **Property 4: A stop changes nothing more**
    - **Validates: Requirements 2.11, 3.1**
  - [x] 2.5 Agent frontmatter check
    - `checks/test_agents.py`: for each `agents/*.md`, a frontmatter block, `name` equal to the file stem, a non-empty `description`, `tools` a subset of the known tool names, `model` and `effort` in their sets; and every `freethinking:<name>` referenced under `skills/` names an existing agent or skill. Flat `key: value` parse, no PyYAML. Run `make validate`
    - _Requirements: 2.1, 4.1, 6.1_

- [x] 6. The reviewer agent
  - [x] 6.1 Write `agents/wave-reviewer.md`
    - Frontmatter per the design's table (`model: opus`, `effort: high`, read-only tools plus Bash for git). Body in the design's parts: Role, Procedure (gather the diff itself, classify, dry-run or reason or cross-check, return Findings), Standard (team rules are the bar; a spec-wave code task correctly lacks a test), the Findings shape, the blocker-on-missing-input rule. No restated rules. Run `make validate`
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_
  - [x] 6.2 Reviewer evals and the Makefile target
    - `evals/agents/wave-reviewer/finds-the-contradiction/` and `passes-a-clean-diff/` per the design's Testing Strategy, sharing a fixture that builds the calc project and writes an uncommitted `subtract` diff (wrong in one case, right in the other); Makefile: `eval-agent-wave-reviewer: CASE_ARGS += --allow-tools Bash --scaffold` and `export PATH := bin:$(PATH)`
    - **Property 6: The Reviewer's verdict follows the diff**
    - **Validates: Requirements 6.4, 6.6, 6.7**
    - _Requirements: 5.6_
  - [x] 6.3 One source tree per fixture project, one setup script, no symlinks
    - `evals/fixtures/setup.sh <tree> <branch> [wrappers]` copies `evals/fixtures/<tree>/` into the workspace, inits git with one commit as Example and checks out the branch, resolving its own location with `cd` and `pwd`; with the third argument `wrappers` it also writes the bin wrappers and the `bin/` exclude, which only the cases that grant Bash and put `bin` on the PATH need. `evals/fixtures/calc/` holds the clean calc package; `evals/fixtures/calc-smells/` holds the code-changes project. Every case that used a symlinked `scaffold.sh` gets its own regular one: the code-changes cases call `setup.sh calc-smells main`; the task-executor cases call `setup.sh calc calc-subtract wrappers`; the wave-reviewer cases do the same and then append `subtract` with `b - a` or `a - b`, uncommitted; works-one-wave calls it with `wrappers`, copies the spec from its own `files/` folder and commits it. Delete `evals/agents/task-executor/fixture.sh`, `evals/agents/wave-reviewer/fixture.sh`, `evals/rules/code-changes/fixture.sh` and every scaffold symlink. Rewrite the evals README's fixture note: trees under `evals/fixtures/`, one `setup.sh`, each case's scaffold its own file, no symlinks. Prove it by building each of the nine converted cases with the old and the new scaffold in the scratchpad and comparing: same files byte for byte outside `.git`, same branch, same commit count, same `git status`. Run `make validate`
    - _Requirements: 5.2, 5.4, 5.6_

- [x] 3. implement-spec launches the agent
  - [x] 3.1 Change step 5 of `skills/implement-spec/SKILL.md`
    - Launch with `subagent_type: freethinking:task-executor`; the launch bullets become the mode sentence, the task text and cited requirements quoted, the design sections quoted, the siblings in flight, the property tag; remove the procedure, the rules excerpt, the Summary shape and the stop instruction from the launch; "When a task comes back" reads `status` first and sends `stopped` to step 6 as Drift. Run `make validate`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [x] 3.3 Name both agents and add the wave review to `skills/implement-spec/SKILL.md`
    - Terms: replace the single **sub-agent** entry with two. The **executor**, `freethinking:task-executor`, one per leaf task, keeping the current sentences on what the launch carries and what the summary holds. The **reviewer**, `freethinking:wave-reviewer`, one per wave: read-only, gathers the diff itself, returns Findings, a `verdict` of `holds` or `findings`, each finding with file, exact quote, problem and severity, then `unsure`. Say that "sub-agent" below means either. The description and the opening paragraph say each task is built by the executor and each wave is read by the reviewer before anything is ticked.
    - Step 5: a new "Reviewing the wave" sub-step between "When a task comes back" and "Ending a wave". Once every executor of the wave has returned and each task's own checks have passed, and before any tick, launch `freethinking:wave-reviewer` once with the sentence "These changes come from a spec wave", the list of files the wave changed or created taken from the Summaries, the requirement and design excerpts the wave's tasks cite, and the files that cite the changed ones; it runs the diff itself. Collect every `unsure` item from the Summaries. A `blocker` or `should-fix`, and any `unsure` item that is a defect, goes to the executor that owns the file, or a new one given the finding, as a fix within the same two attempts, and its check is re-run; a `nit` is fixed the same way or carried; anything carried goes to the report's follow-ups with the reason. Tick only after that. At task cadence, the review runs once when the wave's last task has passed its checks and before its tick. "Ending a wave" then opens with the review done and runs the full suite. The step 6 report gains one line under Tests with the review's verdict and what was carried. One reviewer per wave, no repeated lenses, no refuters. Run `make validate`
    - _Requirements: 4.6, 4.7_
  - [x] 3.2 Re-run the implement-spec evals
    - `make eval-skill-implement-spec`: all three cases at three runs, the work-loop case now executed by the agent
    - _Requirements: 5.4_

- [x] 4. Wire into the handbook
  - [x] 4.1 README Agents section
    - After Rules: what `task-executor` and `wave-reviewer` are, how to launch each directly, the executor's two modes, what each returns; one line each in the Evals section for `make eval-agent-task-executor` and `make eval-agent-wave-reviewer`. Rename `## Evals` to `## Testing`, with the free checks first (`make validate`, what it covers, that it needs make and python3) and the evals after, plus one sentence on the split: using the plugin needs only Claude Code, developing it needs make, python3 and Claude Code, and CI adds Node only to install Claude Code
    - _Requirements: 5.1, 5.7_
  - [x] 4.2 Bump the plugin version
    - `.claude-plugin/plugin.json` to `0.5.0`; `make validate`
    - _Requirements: 5.5_
  - [x] 4.3 Run the hook and agent evals
    - After 6.3 has landed, `make eval-hook`, `make eval-agent-task-executor` and `make eval-agent-wave-reviewer` at three runs each. Keep one Spec_Mode run (`--keep-temp`) and read the sub-agent's model and effort from its trace; record them in the PR, since no grader can see them. Record the tables for the PR's Testing section
    - _Requirements: 1.4, 2.1, 5.2, 5.3_

- [x] 5. Manual check: use the agent directly
  - In a session started with `claude --plugin-dir .`, address `@agent-freethinking:task-executor` with one small contained change in a scratch copy of a project, without the mode sentence. Confirm it gathers context, makes the change with a test, returns the Summary shape with `status: done`, and leaves no scratch files. Record the transcript summary for the PR
  - _Requirements: 2.3, 2.7, 2.10, 3.1_

## Notes

- Sub-tasks marked `*` are optional; implementation sub-tasks are never optional.
- `make validate` is the unit test and the full suite for this repository, after task 1.3 it includes the encoder round-trip check, and after task 1.5 the free checks live under `checks/` as standard-library Python 3.9 unittest files, never a venv or a requirements file. Run it after every change under `hooks/`, `agents/`, `skills/`, `checks/` or `.claude-plugin/`, and at the end of every wave.
- Evals cost real model calls. Run them only at tasks 3.2 and 4.3.
- Task numbers identify tasks; the graph below decides the order. Review happens at the end of each task or each wave, by the author's cadence.
- Work on the `task-executor-agent` branch, never on main.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "1.2", "2.1"] },
    { "id": 1, "tasks": ["1.3", "1.4", "2.2", "2.3", "2.4", "3.1"] },
    { "id": 2, "tasks": ["6.1"] },
    { "id": 3, "tasks": ["1.5", "2.5", "6.2", "3.3", "3.2", "4.2"] },
    { "id": 4, "tasks": ["4.1", "6.3", "4.3", "5"] }
  ]
}
```
