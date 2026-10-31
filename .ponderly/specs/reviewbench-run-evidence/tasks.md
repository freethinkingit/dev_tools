# Implementation Plan

## Overview

Three files change independently first, the adapter's evidence writer, the run script's copy and set-aside, and the report's health section, since they meet only through the run folder's layout, which the design fixes. The runner's early finish follows in the adapter once the evidence writer is in, because both edit `agent.py` and the early finish logs through the writer. Tests come after the code they prove, in the two existing `checks/` files and in their style: the adapter tests run `agent.py` as a subprocess against the stub Claude Code with scaled-down time limits, and the report tests build a run folder in a temporary directory. `run.sh` has no unit tests and is proved by hand with the fake image. The last task is the author's: the next chunk of the test set on the rebuilt image, with the evidence read back.

## Tasks

- [x] 1. Keep the evidence and finish on a final review file
  - [x] 1.1 Add the evidence writer to `benchmarks/reviewbench/agent/agent.py`
    - An `Evidence` class owning `<dirname(RB_OUT)>/logs/`: `log` tees each line to stderr and `adapter.log` with a UTC timestamp; `claude_stderr` returns an append handle on `claude.log` passed as `stderr=` to both `run_claude` calls; `keep_review` copies the review file; `keep_transcripts` copies `$HOME/.claude/projects/` of the Claude Code environment to `transcripts/` unless `RB_KEEP_TRANSCRIPTS` is `0`, in which case `--no-session-persistence` stays on the command lines and otherwise comes off; `redact` replaces every credential value present in the environment with `[redacted]` in every file under the folder and logs the count. A folder that cannot be created or written logs the reason and the writer prints only. `main` wraps its body so keep, keep and redact run on every return. Phase lines: start, claude started, claude finished or ended with the reason, repair started and finished, findings written or why not. Ephemeral check: a scratch run of the adapter against a stub that writes to stderr and to a fake `projects/` file, then `ls -R` of the folder and `grep` for the stub's fake key
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9_
  - [x] 1.2 Make `run_claude` poll and end Claude Code a grace period after the review file turns final
    - Drain stdout on a thread; loop every `POLL_SECONDS = 2` over `poll()`, the time limit and `review_is_final(review_path)`; kill the process group as the timeout path does when the file has been final for `RB_FINAL_GRACE_SECONDS` (default 60); return `(exit_code, stdout, ended)` with `ended` in `None`, `"timeout"`, `"final"`; the repair run passes no grace and no review path; the caller treats `"final"` as `"timeout"` and logs how long after the file turned final it ended Claude Code. Ephemeral check: a stub that writes a final file then sleeps, run with a one-second grace, ends within a few seconds and writes the findings
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_
  - [x]* 1.3 Write the evidence tests in `checks/test_reviewbench_agent.py`
    - Stub actions that write to stderr, write a fake transcript under `$HOME/.claude/projects/` holding the API key and the OAuth token, and write both into stderr. One test per path: `claude.log` holds the stub's stderr and the repair run's after it; `transcripts/` holds the fake transcript with both values replaced by `[redacted]`; `claude.log` likewise; `adapter.log` lines carry a timestamp and the phase lines; `review.json` is the review file; `RB_KEEP_TRANSCRIPTS=0` keeps `--no-session-persistence` and writes no `transcripts/`; an unwritable `logs/` still produces the findings file; a non-zero exit still leaves `adapter.log` and `review.json`. The existing stdout and stderr credential tests must also scan every file under `logs/`
    - **Property 1: No credential in the evidence**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9**
  - [x]* 1.4 Write the early-finish tests in `checks/test_reviewbench_agent.py`
    - Stub actions `final_then_sleep` and `first_then_sleep`. One test per path, with `RB_FINAL_GRACE_SECONDS=1` and the scaled-down limits: a final file then a sleep gives exit 0, the same findings as `good`, and an `adapter.log` line saying Claude Code was ended after the file turned final; a `pass: "first"` file then a sleep is not ended by the grace and is killed at the time limit as today; a final file written and an exit within the grace is not killed and the log has no grace line; a cost reported by the ended run reaches the findings file; a Claude Code that exits on its own between the final-file check and the kill is not counted as a grace end, forced by calling `run_claude` in-process with `review_is_final` replaced by a stand-in that waits for the stub's exit before answering yes
    - **Property 2: The findings do not depend on how Claude Code ended**
    - **Property 3: The grace end never comes early**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

- [x] 2. Carry the evidence into the run folder
  - [x] 2.1 Add `copy_evidence` and `set_aside_earlier_attempt` to `benchmarks/reviewbench/run.sh`, and carry `logs/` through `collect`
    - `copy_evidence <run_dir> <set> [<index>...]` derives each PR_Key from the set's manifest with the runner's own `jq` expression and copies `$TRY_AGENT_WORK/out/<PR_Key>/logs` to `<run_dir>/logs/<PR_Key>/`, printing `no evidence for <PR_Key>` when there is none; `set_aside_earlier_attempt <run_dir> <PR_Key>` moves an existing `findings/<PR_Key>.json` and `logs/<PR_Key>/` into `logs/<PR_Key>.before-<UTC timestamp>/`, the findings as `findings.json`; `run_set` calls set-aside before and copy after each `try_agent` for `pr` and `prs`, and copy once after `test` and `full`, whatever the status; `collect` copies each source's `logs/<PR_Key>/` folders. Hazard: a chunk may be running `run.sh`, so write the new file to a temporary path and `mv` it over `run.sh`, never edit it in place. Manual check with the fake image from the `prs` task: a `prs` run of two indices leaves `logs/<PR_Key>/` for each; the same index run again into that folder leaves a `.before-` folder with `findings.json`; `collect` of two folders carries both `logs/` folders; a cache with no `logs/` prints the line and continues
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 3. Report the review's health
  - [x] 3.1 Add `read_reviews` and `health_section` to `benchmarks/reviewbench/report.py`
    - `read_reviews` returns one entry per `logs/*/review.json`, the parsed object or `None` when it does not parse or lacks `pass`, `verdict`, `second_pass` or `counts`; `health_section` renders the "Review health" section after "Duration and cost" with the counts and averages of the design's table, the one-sentence form when there are no review files, and the unreadable count. Ephemeral check: a scratch run folder with three review files and `report.py` printed
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [x]* 3.2 Write the health-section tests in `checks/test_reviewbench_report.py`
    - One test per path: three review files, `holds`, `findings` with a second pass and a failed `security` arm, and `null`, print the verdict counts, the second-pass count, the lens with its count and the candidate mean and largest; no review files print the sentence; one unreadable file is counted as such and left out of the other counts; a `.before-` folder's review file is not counted
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 4. Document the evidence in `benchmarks/reviewbench/README.md`
  - A "What a run folder holds" paragraph with `findings/`, `scoring/`, `logs/<PR_Key>/` and its four entries, the `.before-` folders, `run.json` and `report.md`, and that ReviewBench reads only the findings file; `RB_KEEP_TRANSCRIPTS` and `RB_FINAL_GRACE_SECONDS` in the variables list with defaults; the "Review health" section beside the report's other sections. Manual check: `make validate` passes and the README's command list and variables list read in order
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 5. Run the next chunk on the rebuilt image (the author, by hand)
  - `make prs` for the next chunk of the test set on the API key, then `judge` and `report`; read `logs/<PR_Key>/adapter.log` of each pull request for the phase lines and any grace end, `review.json` for the verdict, and the report's "Review health" section. Record in the conversation how many reviews ended on the grace and whether any wave review was missing; a missing wave review goes to a new ticket against the review skill, not this spec
  - _Requirements: 1.4, 2.5, 3.1, 4.2_

- [x] 6. Carry the evidence through the Martian harness
  - In `benchmarks/martian/run.sh`, pass `-e RB_KEEP_TRANSCRIPTS -e RB_FINAL_GRACE_SECONDS` to `docker run` beside the `RB_CONFIG_` variables, and after each container, whatever its status, copy `$out/logs` to `$run_dir/logs/<key>/` when it exists, printing `no evidence for <key>` otherwise; a failed copy prints a line and the run goes on. In `benchmarks/martian/README.md`, name the two variables with their defaults and say each pull request's evidence lands in `logs/<key>/`. `run.sh` is replaced by a temporary file and `mv`. Manual check with a fake image built from alpine, deleted afterwards
  - _Requirements: 1.7, 2.3, 3.1, 3.3_

- [x] 7. Redact credentials from the findings file
  - In `benchmarks/reviewbench/agent/agent.py`, replace every credential value present in the environment with `[redacted]` in each finding's text before the findings file is written, using the evidence writer's credential list; one test in `checks/test_reviewbench_agent.py` with the existing `leaks_credentials` stub asserts the findings file holds `[redacted]` and neither fake value
  - _Requirements: 1.8_

## Notes

- Sub-tasks marked `*` are optional tests; implementation sub-tasks are never optional.
- One test per path, one input per test, in the two files' existing style: the adapter tests extend the stub's `STUB_PLAN` actions and read the evidence folder from the temporary output directory; the report tests build the run folder under `tempfile`.
- No credential value is ever printed, logged or written to a run folder; the tests use the fake values the test file already defines.
- `run.sh` is replaced by a temporary file and `mv`, never edited in place, while a chunk may be running it.
- Every leaf task cites the requirements it implements.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1", "3.1"] },
    { "id": 1, "tasks": ["1.2", "3.2", "4"] },
    { "id": 2, "tasks": ["1.3", "1.4", "6"] },
    { "id": 3, "tasks": ["5", "7"] }
  ]
}
```
