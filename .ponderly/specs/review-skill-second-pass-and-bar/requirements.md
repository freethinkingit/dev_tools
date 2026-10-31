# Requirements Document

## Introduction

The `review` skill reviews a pull request with one review arm per lens, has the `wave-reviewer` read the change with the merged findings quoted, and today relaunches every arm when the reviewer returns findings. On the first pull request of ReviewBench chunk 2 the session saw it had spent $6.05 of its $8 budget, skipped that second pass on its own, and returned the first-pass list, so the reviewer's real code findings (a row-major versus column-major contradiction, an entry point that cannot import its module, a crash on a cargo timeout) never reached the findings; and the reviewer, told to judge against the team rules, returned five blockers that were all style departures the repository's own code shares. This task makes the reviewer's findings reach the final list on every review, relaunches only the arms whose findings the reviewer contradicted and only when the budget allows, and has the reviewer judge a pull request against the repository's own bar while still flagging team-rule departures at low weight. It serves the Reviewer, who reads the findings in a session, and the Owner, who pays for every review and reads its score on the benchmarks.

## Glossary

- **Reviewer**: A person who runs the Review_Skill on a pull request and reads its Final_List.
- **Owner**: The person who pays for each review's model calls and reads its benchmark score.
- **Review_Skill**: The plugin skill `review`, `plugins/ponderly/skills/review/SKILL.md`.
- **Review_Arm**: One launch of the plugin's `review-arm` agent by the Review_Skill, reading the pull request through one Lens.
- **Lens**: One `##` section of the Review_Skill's `lenses.md`, naming the categories its Review_Arm's findings carry.
- **Merged_List**: The findings left after the Review_Skill's first merge of every Review_Arm's block, before the Wave_Review.
- **Wave_Reviewer**: The plugin's `wave-reviewer` agent, `plugins/ponderly/agents/wave-reviewer.md`.
- **Wave_Review**: The one launch of the Wave_Reviewer by the Review_Skill, with the Merged_List quoted.
- **Reviewer_Finding**: One entry of the Wave_Review's Findings block: a file, an exact quote, a problem and a severity of blocker, should-fix or nit.
- **Contradiction**: A Reviewer_Finding that says a Merged_List finding is wrong, in its claim, its lines or its severity.
- **Fold**: Turning a Reviewer_Finding into a finding of the Final_List without relaunching a Review_Arm.
- **Second_Pass**: The relaunch of some Review_Arms, each given the Wave_Review's Findings block and the Merged_List, after the Wave_Review.
- **Budget_Note**: The line Claude Code shows the session when it runs with a spending cap, of the form `USD budget: $<spent>/$<cap>; $<remaining> remaining`.
- **Spent**: The dollar amount a Budget_Note gives as used so far.
- **Remaining**: The dollar amount a Budget_Note gives as left.
- **Final_List**: The findings the Review_Skill returns, or writes to the Findings_File.
- **Findings_File**: The JSON file the Review_Skill writes when run with `--json`, in the shape its step 4 gives.
- **Team_Rules**: The handbook rules the plugin puts in every agent's context.
- **Repository_Bar**: What the reviewed repository's `CLAUDE.md`, its contributing guide and the code around the change already do about style, structure, comments and tests.
- **Concrete_Cost**: A harm a departure causes in this change that the finding can show, such as a test that cannot fail or a comment that contradicts the code.
- **Spec_Wave_Review**: Any launch of the Wave_Reviewer other than the Wave_Review: by `implement-spec`, `readable-code`, `tighten-tests` or an author directly.
- **System**: The Review_Skill, the Wave_Reviewer and their documentation and evals.

## Requirements

### Requirement 1: Fold the reviewer's findings into the final list

**User Story:** As a Reviewer, I want every problem the Wave_Review finds to reach the Final_List, so that a real defect the arms missed is not lost because a second pass did not run.

#### Acceptance Criteria

1. WHEN the Wave_Review returns a verdict of `findings`, THE System SHALL Fold each Reviewer_Finding that is not a Contradiction and whose lens's Review_Arm is not relaunched in the Second_Pass.
2. WHEN the System Folds a Reviewer_Finding, THE System SHALL anchor it at the smallest line range at the head that holds its quote, whatever characters the quote contains, give it severity high for blocker, medium for should-fix and low for nit, a category from the Lens whose kind of problem it names, and its problem as the message.
3. IF a Reviewer_Finding's file is absent at the head or its quote is not found in that file, THEN THE System SHALL leave it out of the Final_List and count it as not anchored.
4. WHEN a Folded finding names the same defect at an overlapping line range as a Merged_List finding, THE System SHALL keep one of the two, as the Review_Skill's duplicate collapse already decides.
5. WHEN the System Folds Reviewer_Findings, THE System SHALL pass them through the Review_Skill's head check, ordering and cap of 40, so that a low finding is the first to be cut.
6. WHEN a Contradiction's lens has no Review_Arm relaunched, THE System SHALL read the code at the head the Contradiction quotes and remove or correct the contradicted finding only when that code bears the Contradiction out.

### Requirement 2: Relaunch only the arms the reviewer contradicted, and only within budget

**User Story:** As an Owner, I want a second pass only where it can change a finding and only when the budget allows it, so that a review costs close to its first pass and never ends without the reviewer's findings.

#### Acceptance Criteria

1. WHEN the Wave_Review returns a verdict of `findings`, THE System SHALL relaunch in the Second_Pass only the Review_Arms with at least one Merged_List finding that a Contradiction names.
2. WHILE the latest Budget_Note shows a Remaining smaller than its Spent, THE System SHALL relaunch no Review_Arm and SHALL Fold every Reviewer_Finding, settling each Contradiction as criterion 1.6 says.
3. WHERE the session has shown no Budget_Note, THE System SHALL treat the budget as allowing a Second_Pass.
4. THE System SHALL keep the first-pass list of every Review_Arm it does not relaunch.
5. IF a relaunched Review_Arm fails again after its one relaunch, THEN THE System SHALL keep that arm's first-pass list and Fold the Reviewer_Findings of its Lens.
6. THE System SHALL run at most one Second_Pass and one Wave_Review per review.
7. THE System SHALL skip neither the Fold nor a Second_Pass that criteria 2.1 to 2.3 call for, for any reason of its own about cost or time.

### Requirement 3: Say how the review ended

**User Story:** As an Owner, I want the report and the Findings_File to say which findings came from where and why a second pass did or did not run, so that I can tell a budget decision from a skill problem.

#### Acceptance Criteria

1. THE System SHALL end its report with one count line naming the candidates, the number removed by the merge, the number removed after the Wave_Review, the Wave_Review's verdict, the number of Reviewer_Findings Folded and the number not anchored, each Review_Arm relaunched by its Lens or that none was, and whether a Budget_Note stopped a Second_Pass.
2. WHEN run with `--json`, THE System SHALL write the Findings_File in its existing shape with one added count, `removed_by_cap`, and with `second_pass` true when at least one Review_Arm was relaunched and false otherwise.
3. IF the Wave_Review did not return or did not run, THEN THE System SHALL return the Merged_List as the Final_List, Fold nothing and say so in the count line, as it does today.
4. THE System SHALL count the findings the cap of 40 drops as `removed_by_cap`, separate from the number removed by the merge, and SHALL name that count in the count line.
5. THE System SHALL count so that the candidates equal the Final_List plus the numbers removed by the merge, by the cap and by the review, each finding counted in exactly one of them.

### Requirement 4: Judge a pull request against the repository's own bar

**User Story:** As a Reviewer, I want the Wave_Review to weigh style, comments, structure and tests by what my repository already does, so that a style habit my codebase shares is flagged lightly and never as a blocker, while a real defect keeps its weight.

#### Acceptance Criteria

1. WHEN the Review_Skill launches the Wave_Review, THE System SHALL tell the Wave_Reviewer to judge style, structure, comments and tests against the Repository_Bar and to report a Team_Rules departure as this requirement says.
2. WHEN judging for the Review_Skill, THE Wave_Reviewer SHALL report a Team_Rules departure with no Concrete_Cost in the change as a nit, whether or not the Repository_Bar also shows it.
3. WHEN judging for the Review_Skill, THE Wave_Reviewer SHALL report a Team_Rules departure with a Concrete_Cost at the severity its Standard gives that cost, even when the Repository_Bar also shows it.
4. WHILE judging a Spec_Wave_Review, THE Wave_Reviewer SHALL hold the changes to the Team_Rules as it does today.
5. IF the Repository_Bar cannot be read, because the repository has no `CLAUDE.md`, no contributing guide and no code around the change, THEN THE Wave_Reviewer SHALL judge by the Team_Rules and still report a departure without a Concrete_Cost as a nit.

### Requirement 5: Document and prove the change

**User Story:** As an Owner, I want the reference docs to describe the new behaviour and an eval for each change, so that a reader knows what a review does and a regression shows up before a benchmark run.

#### Acceptance Criteria

1. THE System SHALL describe in `docs/reference.md`, in the `review`, `wave-reviewer` and `review-arm` entries, the Fold, the narrowed and budget-bounded Second_Pass, the count line and the Repository_Bar, and SHALL keep the `review-arm` agent's description and the ReviewBench README's description and report's label of the Review health section true to that behaviour, with the report printing the `removed_by_cap` count beside the merge's and the review's.
2. THE System SHALL record in the design that the Fold has no eval case of its own, because any defect the Wave_Review can catch a Review_Arm can catch first, so no fixture forces the Fold, and SHALL prove the Fold by the `finds-planted-defects` case's expected outcome and the next ReviewBench chunk's count line.
3. THE System SHALL include an eval case for the Wave_Reviewer in which a repository whose own code uses divider comments gets no divider-comment finding above nit for a change that adds one.
4. THE System SHALL record in the design that the budget rule has no eval case, because the eval runner never gives Claude Code a spending cap and a Budget_Note written into a prompt only bites when the Wave_Review contradicts an arm, and SHALL prove the rule by step 6b's text and the next ReviewBench chunk, which runs every review under a real cap.
5. THE System SHALL run no eval case until the Owner asks for it.
