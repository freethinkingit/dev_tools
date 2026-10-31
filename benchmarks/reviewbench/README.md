# ReviewBench harness

This folder scores the `review` skill on
[ReviewBench](https://github.com/review-bench/ReviewBench), a public code review
benchmark. It builds a Docker image that runs the skill on one pull request at
a time, as ReviewBench's agent contract asks, runs that image with
ReviewBench's own runner, judges the findings with ReviewBench's own judge, and
writes a score report. It also holds the manifest, `ponderly.json`, that puts
the image on ReviewBench's leaderboard.

## What it costs

Every run and every judge is a real model call on your own account, so the
harness runs by hand and never in CI, and `make validate` never calls it.
A run bills `ANTHROPIC_API_KEY` in dollars, or, when only
`CLAUDE_CODE_OAUTH_TOKEN` is set, your Claude subscription's usage windows;
on the token the report's cost column is a list-price estimate, not a bill.

- Each pull request is one Claude Code session in the image, capped at
  `RB_CONFIG_BUDGET_USD`, fifteen dollars by default. When the review's
  findings file needs repair, the adapter runs a repair session with its own
  one-dollar cap, so one pull request can cost the cap plus one dollar.
- The test set is 25 pull requests, so a test-set run can cost up to 25 times
  that. The full set is 219 pull requests.
- The test set can also be run as chunks, a few pull requests at a time with
  `make prs`, so each chunk's cost is seen before the next is started. `make
  collect` then gathers the chunks' findings into one run folder, so the
  judge runs once over all of them; collect itself makes no model call.
- The judge is a second model cost, always billed to `ANTHROPIC_API_KEY`, on
  top of the runs.

Start with `make pr PR=0`, one pull request, before a whole set.

## What you need

- `docker`, `node`, `jq`, `git` and `python3` on your `PATH`. `make
  check-tools` names the first of `docker`, `node` and `jq` that is missing,
  or that neither credential below is set; `setup` clones with `git` and
  `report` runs with `python3`.
- For the runs, either `ANTHROPIC_API_KEY` or, on a Claude subscription, the
  token `claude setup-token` prints, exported in your shell as
  `CLAUDE_CODE_OAUTH_TOKEN`. The image reads whichever is set for the review.
- For the judge, `ANTHROPIC_API_KEY` in every case: ReviewBench's judge client
  reads it for the scoring, and `make judge` stops when it is unset. The
  leaderboard steps below use the key too.

## Run it

Run each target from this folder, or with `make -C benchmarks/reviewbench`
from the repository root, in this order:

```bash
make check-tools          # stop naming the first missing tool or key
make setup                # clone ReviewBench at REVIEWBENCH_COMMIT into .reviewbench/ and install it
make image                # build IMAGE from the repository root
make pr PR=0              # run the image on one test-set pull request
make prs PRS="0 1 2 3 4"  # run the image on each listed test-set pull request, into one run folder
make test-set             # run the image on the 25 test-set pull requests
make full-set             # run the image on the 219 full-set pull requests
make collect RUNS="<dir> <dir>"  # copy the listed run folders' findings and evidence folders into one new run folder
make judge RUN=<dir>      # judge <dir>/findings into <dir>/scoring/results.json
make report RUN=<dir>     # write and print <dir>/report.md
make manifest             # validate ponderly.json with ReviewBench's validator
```

`pr`, `prs`, `test-set` and `full-set` run `check-tools`, `setup` and `image`
first, and print the run folder under `runs/` to pass as `RUN`. `prs` runs
every listed pull request even when one fails, and fails at the end if any
did. `collect` prints its new run folder, `runs/<timestamp>-collected/`, to
pass to `judge` and `report`. It stops when two folders hold findings for the
same pull request, or when their model, effort, budget, image or plugin
version differ, since those findings would not be one run. Each target that works
on a run folder appends its command to the folder's `run.json`, so the report
names the commands that made it.

## What a run folder holds

A run folder under `runs/` holds `findings/`, one findings file per pull
request, which is all ReviewBench reads; `scoring/`, the judge's output;
`run.json`, the run's settings and commands; `report.md`; and
`logs/try-agent.log`, the output of ReviewBench's `try-agent.sh` for every
attempt run into the folder. Beside them,
`logs/<PR_Key>/` keeps each pull request's evidence for working out what the
review did: `adapter.log`, the adapter's lines, each with a UTC timestamp;
`claude.log`, Claude Code's standard error, for the review session and then
any repair session; `review.json`, the review file as the skill left it; and
`transcripts/`, Claude Code's session transcripts, left out when
`RB_KEEP_TRANSCRIPTS` is `0`. When a pull request is run again into the same
folder, the earlier attempt's findings file and evidence move to
`logs/<PR_Key>.before-<UTC timestamp>/`, so the judge sees only the latest.
`collect` carries the evidence along: the source folder that holds the pull
request's findings keeps `logs/<PR_Key>/`, or, when none holds them, the last
source listed that has the folder; the other sources' copies go to
`logs/<PR_Key>.before-<source folder name>/`.

`report.md` has a header naming the run and its commands, then the sections
Overall, By severity, By category, Duration and cost, and Review health. Review
health counts, from the `review.json` files, the readable and unreadable review
files and the findings files, how often the wave review held the findings,
returned findings or gave no verdict, how often a second pass relaunched
arms, which lenses lost an arm, the mean and largest number of candidates, and
the mean number of findings removed by the merge, by the cap and by the wave
review.

## Variables

Set any of these on the `make` command line or in your environment.

- `REVIEWBENCH_COMMIT`: the ReviewBench commit `setup` checks out.
- `IMAGE`: the image tag to build and run, `ponderly-review:dev` by default.
- `PR`: the test-set pull request index for `make pr`, counting from 0.
- `PRS`: the test-set pull request indices for `make prs`, separated by
  spaces.
- `RUN`: the run folder for `judge` and `report`.
- `RUNS`: the run folders for `make collect`, separated by spaces.
- `JUDGE_MODEL`: the judge model, `claude-sonnet-5` by default.
- `JUDGE_BASE_URL`: the judge's API base URL, `https://api.anthropic.com` by
  default. `judge` declares the model at this URL in
  `.reviewbench/.judge/models.json` and points the judge there with
  `PI_CODING_AGENT_DIR`, since the pinned ReviewBench does not list the model.
- `TRY_AGENT_WORK`: where ReviewBench's runner keeps its repository caches,
  `.reviewbench/.try-agent` by default.

These three reach the image and are recorded in `run.json`:

- `RB_CONFIG_MODEL`: the Claude model the review runs on, `opus` by default.
- `RB_CONFIG_EFFORT`: its effort level, `high` by default.
- `RB_CONFIG_BUDGET_USD`: the cost cap of one pull request's session in
  dollars, `15` by default.

These two reach the image too, and are not recorded in `run.json`:

- `RB_KEEP_TRANSCRIPTS`: `1` by default, which copies Claude Code's session
  transcripts into the evidence; `0` runs Claude Code with
  `--no-session-persistence` and copies none.
- `RB_FINAL_GRACE_SECONDS`: the seconds Claude Code may keep running after the
  review file turns final before the adapter ends it, `60` by default.

## Put it on the leaderboard

A leaderboard row needs steps only the Owner can take, in GitHub and in
ReviewBench's portal. Nothing publishes the image, registers it or starts a
run on its own: each is a step the Owner takes by hand, after the Owner's own
yes, even where a workflow here does the work. The steps follow ReviewBench's
onboarding guide, `docs/ONBOARDING.md` in the clone, in its order.

1. **Publish the image.** Run the "Publish review image" workflow by hand from
   the repository's Actions tab. It builds the image for `linux/amd64`, pushes
   `ghcr.io/sabind/ponderly-review:<sha>` and writes the digest to the run's
   summary. Put that digest in `ponderly.json`'s `image` in place of the
   placeholder, and run `make manifest`.

   A new GitHub Container Registry package is private, and ReviewBench cannot
   pull a private package anonymously. Either make the package public in its
   settings on GitHub, or keep it private and declare a pull token: choose
   "private package" when you register, which adds `GHCR_PULL_TOKEN` to the
   manifest's secret names and `"image_visibility": "private"` to the
   manifest, as the other private reviewers' files in the clone's `agents/`
   folder show, and enter the token in step 3. Then change `ponderly.json` to
   match before the ReviewBench pull request merges, so the file here stays
   the one ReviewBench's `agents/` folder holds. The manifest declares one
   secret, `ANTHROPIC_API_KEY`, only for a public package.
2. **Register the image.** Sign in to the portal with GitHub and fill the form
   from `ponderly.json`: the display name, the image digest, the
   configuration labels `model` and `effort`, the model API URL
   `https://api.anthropic.com` and the secret name `ANTHROPIC_API_KEY`. The
   form also asks for a contact email, which the file does not hold; it holds
   the GitHub login `sabind` under `contacts`. The model API URL cannot be
   edited in the portal afterwards. Leave the optional seconds an agent may
   spend on one pull request blank, which means 1800: the adapter's 25-minute
   review limit and its 29 minute 30 second limit with the repair assume that
   default, and a lower value would cut reviews short. The portal opens a
   pull request with the manifest in ReviewBench's repository, and a
   maintainer's merge of it is the approval.
3. **Enter the credentials.** The portal shows a credentials form as soon as
   the image is registered. Enter the value of `ANTHROPIC_API_KEY` and, for a
   private package, `GHCR_PULL_TOKEN`: a GitHub classic personal access token
   with the single scope `read:packages`.
4. **Start the test run.** It runs the 25 test-set pull requests with detail
   for each, and it is not on the leaderboard. Use it to check the image works
   in the portal before the final run. Its reviews are billed to the key
   entered in step 3, as a local test-set run is.
5. **Start the final run.** It runs three fresh rounds over the 219 full-set
   pull requests, 657 sessions billed to the same key. The mean of the three
   becomes the leaderboard row after a maintainer merges the publication.
   Both runs start from the portal once a maintainer has merged the manifest;
   only the credentials of step 3 can go in before that. Start the final run
   only after the test run reads well: its per-pull-request detail shows
   findings judged false and golden findings missed, and a run whose reviews
   failed or cost far more than the local test set is not ready.
