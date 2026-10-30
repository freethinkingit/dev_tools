# Implementation Plan

## Overview

The three instruction files change first and independently, since each is its own file and they meet only through the Repository_Bar sentence, which the design fixes verbatim: the review skill's steps 5 to 7, the `wave-reviewer`'s Standard, and the `review-arm`'s description. The reference entries and the existing review eval's wording follow, once the text they describe is in, together with the two new eval cases. Instruction text has no unit tests here: each code-free task is proved by `make validate` and a dry run of the text on the chunk 2 pull request's evidence, and the eval cases are written but not run until the Owner asks, since every eval run is a paid model call.

## Tasks

- [x] 1. Fold the reviewer's findings and narrow the second pass
  - [x] 1.1 Rewrite steps 5, 6 and 7 of `plugins/ponderly/skills/review/SKILL.md`
    - Step 5: replace "No requirement or design excerpt applies to these changes; review them against the team rules." with the design's Repository_Bar sentence, verbatim. Step 6 becomes the settle step: 6a sort each Reviewer_Finding into a Contradiction or new and give it a Lens by `lenses.md`'s words; 6b the budget allows a Second_Pass when no Budget_Note was shown or the latest one's Remaining is at least its Spent; 6c relaunch only the arms with a contradicted finding, when the budget allows, with today's second-pass prompt and one relaunch of a failed arm; 6d Fold every Reviewer_Finding not left to a relaunched arm, anchored from its quote at the head with blocker to high, should-fix to medium, nit to low, a category its Lens carries and its problem as the message, count one not found as not anchored, settle each Contradiction no arm covers by reading the quoted code, and for an arm that failed its relaunch keep its first-pass list and Fold its Lens's findings; 6e merge as step 4 says. Keep "one second pass, no second wave review", and say the skill skips neither the Fold nor an allowed Second_Pass for its own reasons of cost or time. Step 7: append the Folded count, the not-anchored count, the relaunched Lenses or none, and whether a Budget_Note stopped the Second_Pass to the count line; `second_pass` true only when an arm was relaunched; candidates include Folded findings. Update the frontmatter description and the opening paragraph to match. Manual check: `make validate` passes, and a dry run of the new step 6 on the chunk 2 evidence (`benchmarks/reviewbench/runs/2026-10-30T12-51-00-prs5-9/logs/DisciplinedSoftware_Codebase-Conversion_1-4b46d68c/`, read only) says which Reviewer_Findings would be Folded, which are Contradictions, and that the budget at $6.05 spent and $1.95 remaining stops the relaunch
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 3.2, 3.3, 4.1_
  - [x] 1.2 Count the cap's drops in `plugins/ponderly/skills/review/SKILL.md`
    - Steps 4 and 6e count the findings the cap of 40 drops as `removed_by_cap`, apart from removed by the merge, summed over both merges; the findings object gains `counts.removed_by_cap` in step 4's JSON example and step 7's final object; the count line names it. Make the four counts disjoint so `candidates` = final + removed by the merge + by the cap + by the review, with `removed_by_review` the first-pass findings removed in step 6 (an upheld Contradiction or a relaunched arm's withdrawal) and candidates counting each finding once, as the design's Data Models say. In step 6d, write each `'` in the quote's line as `'\''` inside the single-quoted awk word. Manual check: `make validate` passes; a dry run on the chunk 2 evidence shows the cap's count apart from the merge's and the four counts adding up to the candidates; and an ephemeral check runs step 6d's command, as written in the skill, on a scratch file whose line holds a `'`, and prints its line number
    - _Requirements: 1.2, 3.2, 3.4, 3.5_

- [x] 2. Judge a pull request against the repository's bar
  - [x] 2.1 Add the review-skill branch to the Standard of `plugins/ponderly/agents/wave-reviewer.md`
    - When the launch holds the Repository_Bar sentence, read the repository's `CLAUDE.md`, contributing guide and the code around the change before judging style, structure, comments and tests; a Team_Rules departure the repository also shows, or with no Concrete_Cost, is a nit; one with a Concrete_Cost keeps the severity the Findings section gives that cost; with none of the three to read, judge by the Team_Rules and keep the nit rule. Every other launch keeps today's Standard word for word. Manual check: `make validate` passes, and a dry run of the Standard on the chunk 2 Wave_Review's five blockers sorts each into nit or kept
    - _Requirements: 4.2, 4.3, 4.4, 4.5_
  - [x] 2.2 Correct the frontmatter description of `plugins/ponderly/agents/review-arm.md`
    - Replace "and once more per lens with the wave-reviewer's Findings for a second pass" with "and once more, for a lens whose findings the wave-reviewer contradicted, with its Findings for a second pass"; nothing else in the file changes. Manual check: `make validate` passes
    - _Requirements: 5.1_

- [x] 3. Document the change
  - [x] 3.1 Update the `review`, `wave-reviewer` and `review-arm` entries of `docs/reference.md`
    - `review`: the Fold, the Second_Pass only for contradicted arms and only within budget, and the extended count line; `wave-reviewer`: the Repository_Bar sentence and its nit rule beside the spec-wave sentence; `review-arm`: relaunched only for a contradicted lens. Manual check: `make validate` passes and each entry agrees with the file it describes
    - _Requirements: 5.1_
  - [x] 3.2 Reword the `finds-planted-defects` and `clean-diff` eval cases of `evals/skills/review/`
    - `finds-planted-defects`'s `prompt.md` description and expected outcome say the arms run again whenever the reviewer finds something; reword them to the Fold and the narrowed Second_Pass. `clean-diff`'s name the wave-reviewer and nothing after it; reword them to say the reviewer's findings are Folded, so a reviewer blocker would reach the reply as high. Change no grader. Manual check: `make validate` passes; the case is not run
    - _Requirements: 5.1_
  - [x] 3.3 Reword the Review health paragraph of `benchmarks/reviewbench/README.md`
    - "how often a second pass ran" becomes how often a second pass relaunched arms; nothing else in the file changes. This is the one file under `benchmarks/` the spec changes, a documentation edit that a running chunk does not read; edit nothing else there. Manual check: `make validate` passes and the sentence agrees with the review skill's step 7
    - _Requirements: 5.1_
  - [x] 3.4 Relabel the Review health line and print the cap count in `benchmarks/reviewbench/report.py`
    - The line "Second pass ran: N" becomes a label saying arms were relaunched, still counted from `second_pass`; update the three assertions of that line in `checks/test_reviewbench_report.py` to the new label. Review health also prints the mean findings cut by the cap from `counts.removed_by_cap`, beside the merge's and the review's; a review file without that count stays readable and is left out of that mean only; add the test assertions for that line in the file's style, one for a run with the count and one for an older review file without it. Run no `make report`. Manual check: `python3 -m unittest checks.test_reviewbench_report` and `make validate` pass
    - _Requirements: 5.1_
  - [x] 3.5 Add `removed_by_cap` to the repair prompt's shape in `benchmarks/reviewbench/agent/agent.py`
    - `FINDINGS_SHAPE`'s counts gain `"removed_by_cap": integer` after `removed_by_merge`; nothing else in the file changes. Manual check: `python3 -m unittest checks.test_reviewbench_agent` and `make validate` pass
    - _Requirements: 3.2_

- [x] 4. Prove it with an eval case, not run until the Owner asks
  - [x]* 4.2 Write the `judges-by-the-repository-bar` eval case under `evals/agents/wave-reviewer/`
    - A fixture repository whose own modules use divider comments, and a change that adds a module with them and one real defect; the prompt launches the reviewer with the Repository_Bar sentence; graders: no divider-comment finding above nit, and the defect reported as should-fix or blocker. Follow the existing wave-reviewer cases' layout and scaffold. Manual check: `make validate` passes and the scaffold builds the fixture in a scratch directory; the case is not run
    - _Requirements: 4.1, 4.2, 4.3, 5.3_

## Notes

- Tasks 4.1 (`folds-the-reviewer-finding`) and 4.3 (`budget-stops-the-relaunch`) were written in wave 2 and then dropped with the author's approval: neither path can be forced by an eval fixture, as the design's Testing Strategy records.

- Sub-tasks marked `*` are optional tests; implementation sub-tasks are never optional.
- Under `benchmarks/`, only task 3.3's README sentence, task 3.4's report changes and task 3.5's repair shape change: a ReviewBench chunk may be running from this tree. The chunk 2 evidence is read, never written.
- No eval target runs in this spec; each eval case is proved only by `make validate` and its scaffold, until the Owner asks for a run.
- A skill or agent names another and hands off; it never recites the other's steps. The Repository_Bar sentence is the one text two files share, and it is copied verbatim from the design.
- Commit nothing; the author commits.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1", "2.1", "2.2"] },
    { "id": 1, "tasks": ["1.2"] },
    { "id": 2, "tasks": ["3.1", "3.2", "3.3", "3.4", "3.5", "4.2"] }
  ]
}
```
