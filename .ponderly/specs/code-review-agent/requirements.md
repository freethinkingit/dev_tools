# Requirements Document

## Introduction

The `ponderly` plugin reviews code today only inside its own workflows: the `wave-reviewer` agent reads a spec's wave or a readable-code pass against the requirements and design behind it. Nothing in the plugin reviews an ordinary pull request that has no spec, and nothing measures how good the plugin's review is against anyone else's. This task adds a pull request review to the plugin, a `review` skill that runs several review arms as sub-agents, has the `wave-reviewer` read their work, and runs the arms once more when the `wave-reviewer` has something to say, and then measures that review against ReviewBench, GitHub's open benchmark of 219 real pull requests with human-audited golden findings, first on the author's own machine and then on the public leaderboard, and against Martian's offline benchmark of 50 pull requests, run on the author's machine with the same image. Three people use it: the Reviewer, who asks for a review of a branch in a Claude Code session and reads the findings; the Operator, who runs the benchmark by hand and reads the score; and the Owner, who pays for the runs and decides when the numbers justify a leaderboard submission.

## Glossary

- **Reviewer**: A person who asks the plugin to review a pull request in a Claude Code session and reads the findings it returns.
- **Operator**: A person who builds the Image, runs the Harness by hand and reads the Score_Report.
- **Owner**: The person who pays for model calls and decides whether a Score_Report justifies a Leaderboard_Submission.
- **Review_Skill**: The plugin skill, `review`, that reviews one Pull_Request and returns its Findings.
- **Pull_Request**: One set of changes identified by a base commit and a head commit in a git repository, with a title and a body that may be empty.
- **Diff**: The three-dot diff from a Pull_Request's base to its head, the text GitHub shows on the pull request page.
- **Review_Arm**: One launch of a sub-agent by the Review_Skill that reads the Pull_Request through one Lens and returns Candidate_Findings.
- **Lens**: The kind of problem one Review_Arm looks for, such as correctness, reliability, security, maintainability or testing.
- **Candidate_Finding**: One problem a Review_Arm reports, with a file path relative to the repository root, a start line and an end line in the file at the head commit, a message that says what is wrong and why it matters, a severity of high, medium or low, and a category.
- **Finding**: A Candidate_Finding that survived the Review_Skill's merge and the Wave_Review and is returned to the Reviewer or written to the Findings_File.
- **Wave_Review**: One launch of the plugin's existing `wave-reviewer` agent by the Review_Skill over the Pull_Request, in the form the agent already accepts, returning its Findings block.
- **Second_Pass**: One more launch of every Review_Arm, each given the Wave_Review's Findings block, that the Review_Skill runs only when the Wave_Review's verdict is `findings`.
- **Findings_File**: The one JSON file ReviewBench's agent contract requires, holding the Pull_Request's repository URL, number, base and head, the agent name, and the Findings as entries with `file`, `start_line`, `end_line`, `message` and `producer`.
- **Contract**: ReviewBench's `AGENT_CONTRACT.md`: the mounts, environment variables, output file, exit codes, time limit and network rules a review image must obey.
- **Image**: The `linux/amd64` Docker image that runs the Review_Skill headlessly on one Pull_Request under the Contract.
- **Adapter**: The program inside the Image that reads the Contract's inputs, runs Claude Code with the plugin, and writes the Findings_File.
- **Harness**: The scripts and `make` targets in this repository that build the Image, run it on a Set with ReviewBench's own runner, judge the Findings_Files with ReviewBench's own judge, and write the Score_Report.
- **Set**: Either the Test_Set, ReviewBench's 25 representative pull requests, or the Full_Set, all 219.
- **Judge**: ReviewBench's `npm run judge` command, which matches Findings to the golden set with a model and classifies the unmatched ones with the same model.
- **Score_Report**: The Harness's summary of one judged run: grounded and augmented precision, recall and F1, the same split by severity and by category, mean review duration, the model cost of the run, and the plugin version, model, effort, date and commands that produced it.
- **Leaderboard_Submission**: The published Image on GitHub Container Registry, the manifest pull request to the ReviewBench repository, and the portal runs that put the plugin on the public leaderboard.
- **Martian_Benchmark**: Martian's open offline code review benchmark, `withmartian/code-review-benchmark`, 50 pull requests from Sentry, Grafana, Cal.com, Discourse and Keycloak with 173 human-curated golden comments, judged by its own Python pipeline.
- **Martian_PR_List**: The Harness's record of the Martian_Benchmark's 50 pull requests, each with its repository, number, title, base commit and head commit, resolved once from GitHub and stored in the repository.
- **Martian_Data_File**: The Martian_Benchmark's `benchmark_data.json`, one record per golden pull request holding its golden comments and a list of reviews, each review a list of comments with a path, a line and a body.
- **System**: The Review_Skill, its Review_Arms, the Image, the Adapter and the Harness described by this document.

## Requirements

### Requirement 1: Review a pull request in a session

**User Story:** As a Reviewer, I want to ask the plugin to review the pull request on my branch, so that I get the problems a senior reviewer would raise before I open or merge it.

#### Acceptance Criteria

1. WHEN a Reviewer invokes the Review_Skill with no argument, THE System SHALL review the Pull_Request from the branch's merge base with the default branch to the working tree, found the way the `wave-reviewer` agent already finds it.
2. WHERE a Reviewer passes a base and a head, or a `base...head` range, THE System SHALL review that Pull_Request instead.
3. WHEN the review is done, THE System SHALL return the Findings to the Reviewer ordered by severity, high first, each with its file, line range, severity, category and message, and say how many Candidate_Findings the Review_Arms produced and how many the merge and Wave_Review removed.
4. WHILE the Pull_Request has no Diff, THE System SHALL say so and return no Findings rather than review nothing.
5. THE Review_Skill SHALL change no file in the repository, commit nothing and leave no scratch file, so a Reviewer's working tree is as it was.
6. IF a Review_Arm or the Wave_Review fails to return, THEN THE System SHALL return the Findings of the launches that did return and name the launch that did not, rather than return nothing.

### Requirement 2: Review through several lenses

**User Story:** As a Reviewer, I want the review to look for correctness, reliability, security, maintainability and testing problems at once, so that no one kind of problem is missed because the model was thinking about another.

#### Acceptance Criteria

1. THE Review_Skill SHALL launch one Review_Arm per Lens, all in one message so they run at the same time, each with the Diff, the Pull_Request's title and body, and read access to the repository at the head commit.
2. THE System SHALL include a security Lens among the Review_Arms, covering at least injection, authentication and authorisation, secrets in code, unsafe deserialisation and path traversal.
3. THE System SHALL keep the set of Lenses in one place, so the Operator can add, remove or reword a Lens without changing the Review_Skill's steps.
4. WHEN two Candidate_Findings in the same file name the same defect and the same fix, THE System SHALL keep the one with the fuller message, with its own line range, so that the Findings hold no duplicates and no anchor is widened by a neighbour; WHERE the Reviewer passes `--duplicates keep`, THE System SHALL collapse none, and WHERE `--duplicates overlap`, THE System SHALL also collapse two Candidate_Findings whose line ranges overlap in the same file.
5. THE System SHALL verify each Candidate_Finding's file exists at the head commit and its line range lies within that file, and drop any that does not.
6. THE System SHALL return at most 40 Findings for one Pull_Request, keeping the highest severities, so that no output is truncated.
7. IF a Review_Arm returns text that is not in the shape its launch asked for, THEN THE System SHALL treat that Review_Arm as having failed under Requirement 1.6, rather than guess at its findings.

### Requirement 3: Hold the findings to a second reader

**User Story:** As a Reviewer, I want a second reader to check what the arms found before I see it, so that I get fewer wrong or vague findings.

#### Acceptance Criteria

1. WHEN every Review_Arm has returned, THE Review_Skill SHALL run one Wave_Review over the Pull_Request, launched the way `implement-spec` launches it, with no requirement or design excerpt and the merged Candidate_Findings quoted in the launch as the files that cite the changes.
2. WHEN the Wave_Review's verdict is `findings`, THE Review_Skill SHALL run one Second_Pass and merge its Candidate_Findings with the first pass's under Requirement 2.4 and 2.5.
3. WHEN the Wave_Review's verdict is `holds`, THE Review_Skill SHALL run no Second_Pass.
4. THE Review_Skill SHALL run at most one Second_Pass per Pull_Request, so the review always ends.
5. THE Review_Skill SHALL say in its result whether a Second_Pass ran and what the Wave_Review's verdict was.

### Requirement 4: Write findings a judge can match

**User Story:** As an Operator, I want each finding written so that ReviewBench's judge recognises the problem, so that a real catch is scored as one.

#### Acceptance Criteria

1. THE System SHALL write each Finding's message as what is wrong, why it matters and what would fix it, in at most 120 words.
2. THE System SHALL anchor each Finding to the smallest line range at the head commit that holds the problem, never one entry per line of a multi-line problem.
3. THE System SHALL report no Finding that is a style or formatting preference below the project's own review bar, no Finding it cannot verify against the code at the head commit, and no Finding whose suggested change would not improve the Pull_Request.
4. WHERE a problem lies in code the Pull_Request did not change but is in a file it touches and is factually verifiable, THE System SHALL report it, because ReviewBench labels such findings true when they are correct.
5. THE Findings_File SHALL carry `pr.head` equal to the head commit and `pr.pr_number` equal to the pull request number given, and `agent` and every `producer` equal to the agent name given.

### Requirement 5: Run under ReviewBench's contract

**User Story:** As an Operator, I want an image that runs the plugin's review on one pull request exactly as ReviewBench invokes it, so that the benchmark measures what a Reviewer gets.

#### Acceptance Criteria

1. THE Image SHALL run Claude Code headlessly with the plugin from this repository's working tree built in at image build time, so that no network call to GitHub or to a marketplace happens at run time.
2. WHEN the Image starts, THE Adapter SHALL read the Contract's inputs from the environment variables and mounted files the Contract names, run the Review_Skill on the mounted repository, and write the Findings_File at the path `RB_OUT` names.
3. THE Adapter SHALL read the model from `RB_CONFIG_MODEL` and the effort from `RB_CONFIG_EFFORT`, with defaults when unset, and print the settings it applies on standard error, as the Contract asks.
4. THE Adapter SHALL read the credential from `ANTHROPIC_API_KEY` or, for a local run on a Claude subscription, the token from `CLAUDE_CODE_OAUTH_TOKEN`, require that one of the two is set, send it nowhere but Claude Code, and print it nowhere.
5. THE Adapter SHALL end the review run within 25 minutes of starting and, when a repair run follows it, end that run before 29 minutes 30 seconds from the start, writing a Findings_File with the Findings it has, so the Contract's 30-minute limit is never hit.
6. IF Claude Code exits non-zero, or its output holds no Findings in the expected shape, THEN THE Adapter SHALL exit non-zero without writing a Findings_File, so that ReviewBench retries rather than scores an empty review.
7. IF the Review_Skill returns no Findings, THEN THE Adapter SHALL write a Findings_File with an empty `findings` array and exit 0.
8. THE Image SHALL build for `linux/amd64`, start with no arguments, and reach only `api.anthropic.com` over the network.

### Requirement 6: Run the benchmark by hand

**User Story:** As an Operator, I want one command to build the image, run it on a set and judge the findings, so that I can measure a change to the review without learning ReviewBench's tooling.

#### Acceptance Criteria

1. THE Harness SHALL live in `benchmarks/reviewbench/` in this repository, with `make` targets that build the Image, run it on one pull request by index, run it on the Test_Set or the Full_Set, judge a run's Findings_Files, and print the Score_Report.
2. THE Harness SHALL clone ReviewBench at a commit pinned in the Harness, outside the repository's tracked tree, and use ReviewBench's own `scripts/try-agent.sh` and `npm run judge` rather than copies of them.
3. THE Harness SHALL write each run to its own folder under `benchmarks/reviewbench/runs/`, gitignored, holding the Findings_Files, the judge's results and the Score_Report.
4. THE Harness SHALL judge with the Anthropic provider and a model the Operator names, defaulting to the Claude Sonnet model the leaderboard uses, read from the environment.
5. THE Harness SHALL run only by hand and never in CI, as the evals do, and `make validate` SHALL stay free of model calls.
6. WHEN a run on a Set ends, THE Harness SHALL print the Score_Report with each number's meaning stated before it, including the model cost of the run from Claude Code's own usage output.
7. IF `docker`, `node` or `jq` is missing, or neither `ANTHROPIC_API_KEY` nor `CLAUDE_CODE_OAUTH_TOKEN` is set for a run, or `ANTHROPIC_API_KEY` is unset for the judge, which ReviewBench's judge client reads, THEN THE Harness SHALL stop before any model call and name what is missing.

### Requirement 7: Record the evidence

**User Story:** As an Owner, I want each benchmark run recorded with what produced it, so that I can see whether a change to the review helped and decide when to submit.

#### Acceptance Criteria

1. THE Score_Report SHALL name the plugin version, the model, the effort, the Set, the judge model, the date and the commands that produced it.
2. THE System SHALL record the Test_Set Score_Report of the first working review and of each later change to the review in `docs/evidence.md`, next to the eval results already there, with the leaderboard's headline for comparison, which on 2026-10-28 is GitHub Copilot's grounded F1 of 40.1% on the Full_Set.
3. THE Harness SHALL keep the per-PR judge output of each run, so the Operator can read which golden findings were missed and which Findings were judged false.

### Requirement 8: Submit to the leaderboard

**User Story:** As an Owner, I want the review on the public ReviewBench leaderboard once it runs well, so that the plugin's review is measured against the field by the same judge.

#### Acceptance Criteria

1. WHERE the Owner has accepted a Test_Set Score_Report, THE System SHALL provide a GitHub Actions workflow in this repository that builds the Image on demand and publishes it to GitHub Container Registry under the `sabind` owner, printing its digest.
2. THE System SHALL provide the ReviewBench manifest for the plugin, with `name` `ponderly`, the published digest, `model` and `effort` configuration labels, `ANTHROPIC_API_KEY` as its one secret, `api.anthropic.com` as its model API host, and `sabind` as its contact, valid under ReviewBench's `schema/validate-manifest.mjs`.
3. THE System SHALL document in `benchmarks/reviewbench/README.md` the portal steps the Owner takes by hand: registering the Image, entering the API key, the test run and the final run of three rounds.
4. THE System SHALL make no Leaderboard_Submission, publish no Image and open no pull request to ReviewBench without the Owner's explicit yes.

### Requirement 9: Prove it

**User Story:** As an Owner, I want the review proven the way the plugin's other skills are, so that a change to it cannot silently break it.

#### Acceptance Criteria

1. THE System SHALL cover the Adapter's parsing of Claude Code's output, its validation of Candidate_Findings and its writing of the Findings_File with tests that need no model call, run by `make validate`.
2. THE System SHALL provide eval cases under `evals/skills/review/` that run the Review_Skill on a fixture pull request with a planted correctness defect and a planted security defect and grade that each is found with its file and line range.
3. THE System SHALL provide an eval case that grades the Review_Skill on a clean fixture pull request and expects no high-severity Finding.
4. THE System SHALL describe the Review_Skill in the plugin README and the Reference, and add it to the workflow diagram, so the plugin's documentation checks pass.

### Requirement 10: Run Martian's offline benchmark with the same image

**User Story:** As an Operator, I want to run the Martian_Benchmark on the same Image with one command, so that the review is measured by a second judge and a second golden set without a second way of running the plugin.

#### Acceptance Criteria

1. THE Harness SHALL hold the Martian_PR_List in `benchmarks/martian/`, with a `make` target that resolves it once from the Martian_Benchmark's golden files and the GitHub API, so a run needs no GitHub call.
2. WHEN the Operator runs the Martian target, THE Harness SHALL run the same Image on every pull request of the Martian_PR_List with the mounts and variables the Contract names, one container per pull request, writing each Findings_File to a run folder under `benchmarks/martian/runs/`, gitignored.
3. THE Harness SHALL convert the run's Findings_Files into a Martian_Data_File, each Finding becoming one comment with its file as the path, its start line as the line and its message as the body, under the tool name `ponderly`.
4. THE Harness SHALL clone the Martian_Benchmark at a commit pinned in the Harness, outside the tracked tree, and run its extract, deduplicate and judge steps on the Martian_Data_File with its own `uv` toolchain and an OpenAI-compatible judge endpoint and model the Operator names.
5. WHEN the Martian judge ends, THE Harness SHALL print a Score_Report with precision, recall and F1 under the Martian_Benchmark's Strict, Core and All profiles, with each number's meaning stated before it, the judge model, the Image settings and the date.
6. IF `uv`, `gh` or the judge key is missing, THEN THE Harness SHALL stop before any model call and name what is missing.
7. THE System SHALL record the Martian Score_Report in `docs/evidence.md` beside the ReviewBench one, with the Martian leaderboard's published top score for comparison on the day of the run.
