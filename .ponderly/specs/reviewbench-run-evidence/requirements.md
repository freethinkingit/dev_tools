# Requirements Document

## Introduction

A ReviewBench run today keeps one file per pull request, the findings with their cost, and throws away everything that explains them: Claude Code's transcripts, its error output, the review file with its verdict and arm counts, and the time each phase took. When a review hangs or a wave review never runs, the owner has nothing to read. This feature keeps that evidence beside the findings for every pull request of a run, ends a review as soon as its file is final instead of waiting out the whole time limit, and adds a review-health section to the report, so the owner can see how the review skill behaved across a set and tune it from what happened rather than from guesses. The benchmark's own view, the findings file, does not change.

## Glossary

- **Adapter**: The Python program in the benchmark image that runs Claude Code once per pull request and writes the Findings_File.
- **Findings_File**: The JSON file at the path `RB_OUT` names, the only file ReviewBench reads.
- **Output_Mount**: The directory holding the Findings_File, mounted from the runner's cache for one pull request.
- **Evidence_Folder**: The `logs/` directory the Adapter writes in the Output_Mount, holding the evidence of one pull request's review.
- **Review_File**: The JSON file the review skill writes with `--json`, holding `pass`, `verdict`, `second_pass`, `counts` and `findings`.
- **Final_Review_File**: A Review_File that parses and whose `pass` is `"final"`.
- **Session_Directory**: The directory under the reviewer account's home where Claude Code keeps a session's transcript and its sub-agents' transcripts when session persistence is on.
- **Grace_Period**: The number of seconds the Adapter waits after first seeing a Final_Review_File before ending Claude Code.
- **Run_Folder**: The directory under `runs/` that one `make pr`, `prs`, `test-set`, `full-set` or `collect` creates, with `findings/`, `scoring/`, `logs/` and `run.json`.
- **PR_Key**: The pull request's identifier in the runner, its repository `owner/name` with `/` replaced by `_`, then `_`, the pull request number, `-` and the first eight characters of its head commit.
- **Report**: The `report.md` that `make report` writes into a Run_Folder.
- **Credential**: The value of `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN`.
- **System**: The Adapter, `run.sh`, `report.py` and their documentation under `benchmarks/reviewbench/`.

## Requirements

### Requirement 1: Keep the evidence of every review

**User Story:** As the owner, I want every pull request's review to leave its transcripts, error output, review file and timing beside its findings, so that a hang, a missing wave review or a lost arm can be read instead of guessed at.

#### Acceptance Criteria

1. WHEN the Adapter runs, THE System SHALL create the Evidence_Folder in the Output_Mount before Claude Code starts.
2. THE System SHALL write Claude Code's standard error output to `claude.log` in the Evidence_Folder, for the review run and, when one runs, the repair run.
3. THE System SHALL write every line the Adapter logs to `adapter.log` in the Evidence_Folder, each prefixed with a UTC timestamp, while still printing it to standard error as today.
4. THE System SHALL log one line at each phase: the start, Claude Code started, Claude Code finished or was ended with the reason, the repair run started and finished when one runs, and the Findings_File written or the reason it was not.
5. WHEN the Adapter finishes, whatever its exit code, THE System SHALL copy the Review_File, when one exists, to `review.json` in the Evidence_Folder.
6. WHEN the Adapter finishes, whatever its exit code, THE System SHALL copy the Session_Directory, when one exists, to `transcripts/` in the Evidence_Folder, main transcript and sub-agent transcripts included.
7. WHERE the environment sets `RB_KEEP_TRANSCRIPTS` to `0`, THE System SHALL run Claude Code without session persistence and write no `transcripts/`, and SHALL otherwise run it with session persistence on.
8. THE System SHALL write no Credential into any file of the Evidence_Folder.
9. IF the Evidence_Folder cannot be created or a file in it cannot be written, THEN THE System SHALL log the reason and go on to produce the Findings_File as today.

### Requirement 2: Finish when the review is final

**User Story:** As the owner, I want a review whose file is already final to end after a short Grace_Period instead of sitting idle until the time limit, so that a hung session costs a minute and not a quarter of an hour on every pull request.

#### Acceptance Criteria

1. WHILE Claude Code is running, THE System SHALL check the Review_File at least every 5 seconds.
2. WHEN the Review_File first becomes a Final_Review_File and Claude Code is still running after the Grace_Period, THE System SHALL end Claude Code and every process it started, and treat the result as it treats its own time-limit kill, reading the Final_Review_File and writing the Findings_File from it.
3. THE System SHALL take the Grace_Period from `RB_FINAL_GRACE_SECONDS`, with a default of 60 seconds.
4. WHEN Claude Code exits on its own within the Grace_Period, THE System SHALL proceed as today, with no kill.
5. WHEN the System ends Claude Code after the Grace_Period, THE System SHALL log that it did so and how long after the Final_Review_File appeared.
6. IF the Review_File is final but Claude Code's exit after the Grace_Period kill reports a cost, THEN THE System SHALL record that cost in the Findings_File as it does for a kill today.

### Requirement 3: Carry the evidence into the run folder

**User Story:** As the owner, I want each pull request's Evidence_Folder copied into the Run_Folder, so that a run is one folder I can read, archive or hand to someone else.

#### Acceptance Criteria

1. WHEN a pull request's run ends, whether the runner reports it passed or failed, THE System SHALL copy its Evidence_Folder from the runner's cache to `logs/<PR_Key>/` in the Run_Folder.
2. THE System SHALL derive the PR_Key from the corpus entry exactly as the runner does.
3. IF a pull request has no Evidence_Folder in the cache, THEN THE System SHALL log that none was found and continue with the next pull request.
4. WHEN `make collect` builds a Run_Folder from several runs, THE System SHALL copy each source's `logs/<PR_Key>/` folders along with its findings, so the collected folder's Report can read them.
5. IF a pull request runs again into a Run_Folder that already holds its findings file or its `logs/<PR_Key>/`, THEN THE System SHALL move both into `logs/<PR_Key>.before-<UTC timestamp>/` before the run, the findings as `findings.json` inside it, so that the judge reads only the latest attempt and no earlier attempt is lost.

### Requirement 4: Report the review's health

**User Story:** As the owner, I want the Report to say how the review skill behaved across the set, so that I can tell a skill problem from a benchmark result.

#### Acceptance Criteria

1. WHEN `make report` runs on a Run_Folder, THE System SHALL add a "Review health" section to the Report that reads every `logs/<PR_Key>/review.json`.
2. THE System SHALL state, as counts over the pull requests of the run: how many have a review file; how many of those have a `verdict` of `holds` or `findings`, and how many have none; how many ran a second pass; and how many list at least one failed arm, naming each failed lens with the number of pull requests it failed on.
3. THE System SHALL state, for the pull requests with a review file, the mean and the largest `candidates` count, and the mean number of findings removed by the merge and by the wave review.
4. WHILE no pull request of the run has a review file, THE System SHALL print the section with a sentence saying no review files were found, not an error.
5. IF a `review.json` does not parse or lacks a field the section needs, THEN THE System SHALL count that pull request as unreadable, say how many were, and leave it out of the other counts.

### Requirement 5: Document the evidence

**User Story:** As a new operator, I want the README to say what a Run_Folder holds and how to turn the evidence off or shorten the wait, so that I can read a run without this conversation.

#### Acceptance Criteria

1. THE System SHALL document in the harness README the Evidence_Folder's files, where they land in the Run_Folder, and that ReviewBench reads none of them.
2. THE System SHALL document `RB_KEEP_TRANSCRIPTS` and `RB_FINAL_GRACE_SECONDS` in the README's variables list, with their defaults.
3. THE System SHALL document the Report's "Review health" section in the README beside the Report's other sections.
