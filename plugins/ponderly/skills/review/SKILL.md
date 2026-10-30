---
name: review
description: Review a pull request and return line-anchored findings. Use when asked to review this branch, review this pull request, review these commits or review a base...head range. Takes the range from the argument, or the branch's merge base with the default branch up to the working tree when there is none, launches one review-arm agent per lens in its lenses file, all at once, and merges what they return. The merge relaunches once an arm whose block is missing or malformed, then drops it and names its arm, checks every finding's file and lines at the head, collapses duplicates as --duplicates says, orders high, medium, low and keeps at most 40. Has the wave-reviewer agent read the change with the merged findings quoted, and runs the arms once more when it returns findings. Returns the findings with their counts, the wave review's verdict and whether a second pass ran, or writes them as JSON to a path outside the repository with --json. Changes no file in the repository and commits nothing.
argument-hint: "[base...head] [--json <path>] [--duplicates same-defect|keep|overlap]"
allowed-tools: Bash(git status *) Bash(git rev-parse *) Bash(git merge-base *) Bash(git diff *) Bash(git show *) Bash(git ls-files *) Bash(git log *) Bash(git cat-file *) Bash(awk *)
---

# Review a pull request

Review one pull request: find its range, have one `review-arm` read it through each lens of `${CLAUDE_SKILL_DIR}/lenses.md`, all at the same time, merge their findings into one list anchored to lines at the head, have the `wave-reviewer` read the change with that list quoted, run the arms once more when it finds something, and return the final list with its counts.

The skill reads; it changes no file in the repository, commits nothing and leaves no scratch file, so the working tree is as it was. The one file it writes is the JSON a `--json` path names, and only when that path is outside the repository.

The text after the command: $ARGUMENTS

Terms used below:

- An **arm** is the plugin's `review-arm` agent, launched as `ponderly:review-arm`, one per lens. Its own definition holds its procedure and the shape of its arm block, so the launch carries only the review's inputs; it gathers the diff itself.
- The **reviewer** is the plugin's `wave-reviewer` agent, launched as `ponderly:wave-reviewer`, once per review. Its own definition holds its procedure and the shape of its Findings.
- A **lens** is one `##` section of `lenses.md`. The **shared standard** is the three sentences of that file's opening paragraph from "Across every lens" to the paragraph's end.

## Working with the author

- **Stops.** Only when something is wrong: a `base...head` side that names no commit, a range with only one of its first two words naming a commit, a `--json` without a path or with a path inside the repository, a `--duplicates` whose word is not `same-defect`, `keep` or `overlap`, a range with no diff, a missing `lenses.md`, and a missing `review-arm` agent. A missing `wave-reviewer` agent does not stop the review; step 5 says what follows.
- **How it asks.** It does not ask; every input comes from the arguments and the repository.
- **Hand-backs.** The report of step 7, or the stop that ends the run.
- **Hand-offs.** None; the author decides what to do with the findings.

## 1. Read the arguments

The arguments are on the first line of the text above; everything after that line is the pull request's title, its first non-empty line, and its body, the rest. When the first line holds neither a range nor `--json` nor `--duplicates`, there is no argument, and the whole text is the title and body.

- **Range.** A word resolves when `git rev-parse --verify --quiet <word>^{commit}` succeeds. A word of the form `base...head` is the range, and both sides must resolve: when one does not, say which names no commit, and stop. Otherwise, when the first two words both resolve, they are the base and the head. When exactly one of the first two words resolves, say that a range needs a base and a head, or a `base...head`, and stop. When neither resolves, there is no range, and unless the first line holds `--json` or `--duplicates`, the whole text is the title and body.
- **`--json <path>`.** The word after `--json` is the path. Missing: say that `--json` needs a path, and stop. Find the repository root with `git rev-parse --show-toplevel` and make the path absolute against the working directory. When it is the root or lies under it, say that the `--json` path must be outside the repository, naming both, and stop. When the path already exists, from an earlier review, read it with the Read tool before the first write, so the Write tool may overwrite it.
- **`--duplicates <mode>`.** The word after `--duplicates` is the mode of step 4's duplicate collapse: `same-defect`, the default when the argument is absent, `keep` or `overlap`. Any other word, or none: say that `--duplicates` takes `same-defect`, `keep` or `overlap`, and stop.

A title or body that is not given is passed on as "none given".

## 2. Resolve the range

With a base and a head from the arguments, the base is `git merge-base <base> <head>`, so that commits the base branch gained after the branch left it are not reviewed, or the base as given when there is no merge base; the head is `git rev-parse <head>`. The changed files are `git diff --name-only <base> <head>`.

With no range, the head is the working tree and the base is the branch's merge base with the default branch: the default branch is `git rev-parse --abbrev-ref origin/HEAD` with the `origin/` prefix removed, or `main` when that command fails, as it does when `origin/HEAD` is unset, even though it still prints `origin/HEAD`; the base is `git merge-base origin/<default> HEAD`; when there is no `origin`, it is `git merge-base <default> HEAD` with the local default branch, if that branch exists and is not the current one; when neither exists, or the merge base cannot be found, the base is `HEAD`. The changed files are those `git diff --name-only <base>` lists, which compares the working tree with the base, with the new files `git ls-files --others --exclude-standard` lists.

When the list of changed files is empty, say "no diff" with the base and head it was measured between, return no findings, and stop. With `--json`, write the findings object of step 4 with `pass` `"final"`, `verdict` `null`, `second_pass` `false`, every count 0 and `findings` `[]` before stopping.

## 3. Launch the arms

Read `${CLAUDE_SKILL_DIR}/lenses.md`. If it is missing, say that the skill's `lenses.md` is missing, naming its path, and stop.

Launch one arm per lens, all in one message so they run at the same time, each with the Agent tool as `subagent_type: ponderly:review-arm` and a prompt that holds:

- the shared standard, quoted;
- the lens: its `##` heading and its text, quoted;
- the range: the base commit, and the head commit or the words "the working tree";
- the changed files, one per line;
- the pull request's title and body.

Nothing more, and never the diff: each arm runs `git diff` and reads the files itself. If the Agent tool cannot find `ponderly:review-arm`, say that the plugin's `review-arm` agent is missing and stop. Wait for every arm.

## 4. Merge

Read each arm's final text as an arm block. An arm **failed** when it did not return, when its text is not an arm block (a `lens:` line, a `findings:` list whose every entry has a `file`, integer `start_line` and `end_line`, a `severity` of `high`, `medium` or `low` and a `category` and `message`, then an `unsure:` list), or when its block has `findings: []` and an `unsure` entry beginning `review not done:`, since that arm did not review. Once every arm of the pass has returned, relaunch each failed arm once, all failed ones in one message, with the prompt it had, and read the relaunch's text by the same rule. An arm that fails again is dropped: take none of its entries, and name its lens as failed. This holds for the second pass too, and a relaunch is not the second pass. Every entry of the blocks that remain is a candidate.

Then, in order:

1. **Normalise** each candidate's `file` to forward slashes, with no leading `./` or `/`.
2. **Check it at the head.** For a head commit, the file exists when `git cat-file -e <head>:<file>` succeeds, and its line count is `git show <head>:<file> | awk 'END{print NR}'`; for the working tree, the file exists when it is in the working tree, and its line count is `awk 'END{print NR}' <file>`. Drop a candidate whose file is absent, or whose lines are not 1 ≤ `start_line` ≤ `end_line` ≤ that line count.
3. **Collapse duplicates**, as `--duplicates` says. `same-defect`, the default: two candidates in the same file become one only when they name the same defect and the same fix; a different `category` is a sign they do not, since each lens reports its own kind of problem, so a correctness finding on a line and a performance finding spanning it stay two findings. `overlap`: two candidates in the same file whose line ranges overlap also become one. `keep`: no candidate is collapsed. When two become one, keep the one whose message is fuller, with its own `start_line` and `end_line`, never a union of the two ranges, and drop the other.
4. **Order** high, then medium, then low, keeping the lenses' order within a severity.
5. **Cap** at 40, dropping from the lowest severity.

The merged list is what is left. **Removed by the merge** is the number of candidates minus the number of findings in the merged list; **removed by the review** is 0 until step 6.

With `--json`, write the interim findings object to the path with the Write tool, after this first merge and before the wave review:

```json
{
  "pass": "first",
  "verdict": null,
  "second_pass": false,
  "counts": {"candidates": 0, "removed_by_merge": 0, "removed_by_review": 0, "failed_arms": []},
  "findings": [
    {"file": "path/at/head.py", "start_line": 1, "end_line": 1, "severity": "high", "category": "correctness", "message": "..."}
  ]
}
```

`failed_arms` holds the lens name of each failed arm; `findings` holds the merged list, each entry with the six fields of its arm-block entry.

## 5. Wave review

Launch the reviewer once, with the Agent tool as `subagent_type: ponderly:wave-reviewer` and a prompt that holds:

- the range in place of a file list: the base commit, and the head commit or the words "the working tree";
- the sentence, verbatim, "No requirement or design excerpt applies to these changes; review them against the team rules.";
- the merged list, quoted in the arm block's shape, as the text that cites the changed files: every place where a finding and the code at the head disagree is a finding, and so is a problem in the changes the list does not hold.

Nothing more, and never the diff. If the Agent tool cannot find `ponderly:wave-reviewer`, say that the plugin's `wave-reviewer` agent is missing, and go on as for a wave review that did not return: the merged list is the final list, the verdict is that the wave review did not run, and there is no second pass; go to step 7.

Its Findings' `verdict` line decides what follows. `findings`: go to step 6. `holds`: the merged list is the final list; go to step 7 with no second pass. No Findings with a `verdict` line, because the reviewer did not return or returned something else: the merged list is the final list, the verdict is that the wave review did not return, and there is no second pass; go to step 7.

## 6. Second pass

Launch every arm again, all in one message, each with the prompt of step 3 and, added to it:

- the reviewer's Findings block, quoted whole;
- the whole merged list from step 4, quoted in the arm block's shape, from which the arm takes as its own the entries whose category its lens carries.

Each arm returns the whole list for its lens, which replaces its first-pass list. Merge as step 4 says, over the second-pass block of each arm that returned one in the right shape and, for an arm that failed this time, its relaunch included, its first-pass block if it had one; name each lens that failed in this pass as failed. The counts then cover both passes: **candidates** is every entry the arms returned across both passes; **removed by the merge** is the sum of what the two merges removed, each merge's candidates minus its merged list; **removed by the review** is the number of first-pass findings with no entry in the final list at the same file with an overlapping line range. The three need not add up to the final count, since the second pass replaces lists.

This is the one second pass: no third launch of the arms and no second wave review, whatever the second merge holds.

## 7. Report

Without `--json`, reply with the final list, high first, one finding per line as `<severity> <category> <file>:<start_line>-<end_line> <message>`, or "No findings." when the list is empty. After it, one count line: the candidates the arms produced, the number the merge removed, the number removed after the wave review, the wave review's verdict (`holds`, `findings`, or that it did not return or did not run), whether a second pass ran, and each failed arm by its lens and pass, or that none failed.

With `--json`, write the final findings object to the path, in step 4's shape with `pass` `"final"`, `verdict` `"holds"`, `"findings"` or `null` when the wave review did not return or did not run, `second_pass` `true` or `false`, and the final counts and list; then reply with the path and the count line alone.
