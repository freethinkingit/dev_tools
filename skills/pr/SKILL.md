---
name: pr
description: Open or update a GitHub pull request for the current branch using the team's PR standard. Use when asked to open, create, raise, or update a PR. Walks the diff between the branch and its target one change at a time, saying what each source change does and asking the author to say why in their own words, which become the description's Changes bullets; asks once for what the diff cannot answer, drafts the title and description from the repository's own pull request template or the skill's default one, and creates the PR with the gh CLI after the author approves.
argument-hint: "[base-branch]"
allowed-tools: Bash(git status *) Bash(git branch *) Bash(git remote *) Bash(git rev-parse *) Bash(git fetch *) Bash(git log *) Bash(git diff *) Bash(gh auth status *) Bash(gh repo view *) Bash(gh pr view *) Bash(gh pr list *)
---

# Open a pull request

Open a pull request for the current branch whose title and description meet the team standard. Before drafting anything, walk the changes with the author so that every source change in the branch is explained and understood. The author approves the draft before anything is pushed or created.

The author is accountable for every change in the branch and should be able to speak to each one. That holds for code Claude wrote, in this session or an earlier one, as much as for code they typed. Help them understand and explain the changes; do not vouch for a change on their behalf.

Base branch override, if the author gave one: $ARGUMENTS

## 1. Check the starting state

Run these and stop with a clear message if any check fails:

- `git remote get-url origin`: if there is no `origin`, or it is not a GitHub repository, stop and say so. The `gh` commands below fail with a misleading message otherwise.
- `gh auth status`: if the author is not signed in, tell them to run `gh auth login`. Note which account is active; when more than one is signed in, the active one opens the PR.
- `git branch --show-current`: if this is the repository's default branch, stop. A PR needs its own branch.
- `git status --short`: if there are uncommitted changes, tell the author they will not be in the PR and ask whether to continue. Do not commit for them unless they ask.
- `gh pr view --json url,title,body,state,isDraft`: if an open PR already exists for this branch, the last step updates it instead of creating a second one. Still walk the changes first. An error saying no pull request was found is the normal case for a new PR.

## 2. Find the base branch

Use the override above if one was given. Otherwise use the repository default from `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. If that comes back empty, the repository has no branches on GitHub yet: stop and tell the author to push a base branch first. Run `git fetch origin <base>` so the comparison uses the current base.

## 3. Read and sort the changes

- `git log --oneline origin/<base>..HEAD` for the commits.
- `git diff --name-status origin/<base>...HEAD` for the full list of changed files. This list is the checklist for the walkthrough.
- `git diff origin/<base>...HEAD -- <path>` to read each change.

Sort every changed file into one of three groups:

- **Source**: code, tests, configuration, schemas, migrations, infrastructure and documentation that a person wrote or would review. Every source change must be explained in the walkthrough.
- **Export glue**: an index or barrel file (`index.ts`, `index.js`, `__init__.py` and similar) whose change in this branch only adds, removes or reorders exports. Skip these. If the same file also changes logic, it is source.
- **Generated**: lockfiles, build output, snapshots and other machine-written files. Name them in one line; do not walk them.

When unsure whether a file is source, treat it as source.

Read every source change fully enough to explain it. While reading, note anything the author should see before review: leftover debug output, commented-out code, TODOs added in this branch, credentials or keys, and changes that look unrelated to the rest of the branch. Do not fix them unless asked.

## 4. Walk the changes with the author

Group the source changes into logical changes: files that changed together for one purpose form one group. Order the groups so they tell the story of the branch: the core behaviour change first, then what had to change around it, then tests. Number them.

Then go through them one at a time, in plain prose, not a form. Open with the list of groups, one line each, and the first group in the same message. For each group:

- Say what changed: the behaviour or structure that is different now, with the files involved, in a few sentences a reader of the PR could follow. Raise any finding from step 3 that belongs to it.
- Ask the author to say why, in their own words. Do not propose a reason for them to accept; a reason you inferred from the diff or the commit messages is not the author's, and the bullet has to be. If a commit message states one, quote it as context and still ask.
- Wait for the answer. One group per message; the next group goes in the message after the author answers.

The author's words are what goes into the PR. A group is settled when the author has described it, has said it is self-explanatory, or described it earlier in the session or in the request. For a self-explanatory group, tell the author its bullet will say what changed and nothing more, and move on. For a group the author described in advance, show what changed, quote their words as its why, and go straight on to the next group in the same message, since there is nothing to wait for.

"Not sure" or "just include it" does not settle a group. Tell the author the bullet will keep what changed with "Reason not provided by the author" in place of the why and be listed under Notes for reviewers, and that the alternatives are to explain it now or to remove the change from the branch. Wait for their choice. If they remove it, run step 3 again; if they accept the marker, the group is settled with it. Do not invent a reason to fill the gap.

During the walkthrough, use the author's corrections: their account replaces yours. If a change turns out to be unintended, ask whether it belongs in this PR, and do not remove it yourself unless asked.

Before leaving this step, check the list from `git diff --name-status` against the groups: every changed file is either covered by a group, skipped as export glue, or named as generated. Tell the author which files were skipped and why, in one line.

## 5. Ask what is still missing

Ask once, in plain prose in a single message, and only for what the walkthrough and the author's earlier answers have not already covered. Where an earlier answer covered part of a question, ask only for the missing part.

- **Why**: the problem or goal behind the branch, when the group reasons do not already say it.
- **Ticket**: the ticket if there is one, in whatever form the author has it: an issue number such as `#12`, an issue URL, or a key from another tracker such as `ENG-1234`. Say that any form works.
- **Testing**: what they ran or checked, and the result.
- **Risk and rollout**: anything that needs care on deploy, such as migrations, flags, config, infra, or a required order of deploys.
- **Review focus**: where reviewers should look hardest, whether this should open as a draft, and for a UI change the screenshots or recording to attach.

Never invent an answer. If the author did not test the change, the Testing section says "Not tested".

## 6. Draft the title and description

**Title.** PRs are squash-merged, so the title becomes the commit on the base branch.

- With a ticket: `[#12] Add retry to upload worker` or `[ENG-1234] Add retry to upload worker`, the ticket written the way its tracker writes it
- Without: `Add retry to upload worker`
- Imperative mood, under 70 characters, no trailing period, specific enough to make sense in `git log` a year from now.

**Description.** If the repository has its own template (`.github/pull_request_template.md`), use it: its sections and the comments inside them say what that repository wants in each, and they take precedence over the bullets below; when a comment asks for something the author's answers did not give, ask before drafting. Otherwise use the skill's default template at `${CLAUDE_PLUGIN_ROOT}/skills/pr/pull_request_template.md`.

- Write the Why section from the ticket and the group reasons, or from the author's step 5 answer when those do not give the goal. Name the ticket as its tracker writes it, and link it when the author gave a URL; add nothing the author's answers or the repository's own template did not call for. Write the Changes section from the settled groups: one bullet per logical change, saying what changed and, in the author's words, why. Every source change in the branch is covered by some bullet. Export glue and generated files are left out.
- A group the author called self-explanatory gets a bullet that says what changed and nothing more. A change the author did not explain keeps its bullet, with "Reason not provided by the author" in place of the why, and is repeated under Notes for reviewers.
- Fill every section. Write "None" where a section does not apply, except Notes for reviewers, which is removed when empty.
- Say only what the diff and the author's answers support. No filler, no claims about quality.
- Call out breaking changes and anything a reviewer must do, such as running a migration, at the top of the relevant section.
- Remove the template's HTML comments from the final text.

## 7. Show the draft and get approval

Show the author the title, the full description, the repository and base branch, the GitHub account that will open the PR, and whether it will open as a draft. Apply their edits. Do not push or create anything until they approve.

## 8. Create or update the PR

Write the description to a temporary file so quoting cannot corrupt it.

- If the branch has no upstream or is ahead of it, push with `git push -u origin HEAD`.
- New PR: `gh pr create --base <base> --title "<title>" --body-file <file>`, adding `--draft` if the author chose a draft.
- Existing PR: `gh pr edit --title "<title>" --body-file <file>`.

Finish by giving the author the PR URL.
