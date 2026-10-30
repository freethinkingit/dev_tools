# ReviewBench harness for the review skill. Run by hand, never in CI: the run
# and judge targets are real model calls. A run takes ANTHROPIC_API_KEY or a
# Claude subscription's CLAUDE_CODE_OAUTH_TOKEN; the judge needs ANTHROPIC_API_KEY.
#
#   make check-tools          stop naming the first of docker, node, jq that is missing, or that neither
#                             ANTHROPIC_API_KEY nor CLAUDE_CODE_OAUTH_TOKEN is set
#   make setup                clone ReviewBench at REVIEWBENCH_COMMIT into .reviewbench/ and npm ci there
#   make image                build $(IMAGE) from the repository root
#   make pr PR=<n>            run the image on Test_Set pull request <n> into runs/<timestamp>-pr<n>/
#   make prs PRS="<n> ..."    run the image on each listed Test_Set pull request into runs/<timestamp>-prs<first>-<last>/
#   make test-set             run the image on the Test_Set into runs/<timestamp>-test/
#   make full-set             run the image on the Full_Set into runs/<timestamp>-full/
#   make collect RUNS="<dir> ..."  copy the listed run folders' findings into runs/<timestamp>-collected/ for one judge
#   make judge RUN=<dir>      judge <dir>/findings into <dir>/scoring/results.json with JUDGE_MODEL at JUDGE_BASE_URL
#   make report RUN=<dir>     write and print <dir>/report.md
#   make manifest             validate ponderly.json with the clone's schema/validate-manifest.mjs
#
# The run targets and collect print the run folder to pass as RUN. RB_CONFIG_MODEL,
# RB_CONFIG_EFFORT and RB_CONFIG_BUDGET_USD in the environment reach the
# adapter in the image, and run.json records them.

REVIEWBENCH_COMMIT ?= 228f2a8d662c9c1c12d25757e23c52c9a6170d5a
IMAGE ?= ponderly-review:dev
JUDGE_MODEL ?= claude-sonnet-5
JUDGE_BASE_URL ?= https://api.anthropic.com
RUN ?=
PRS ?=
RUNS ?=

export REVIEWBENCH_COMMIT IMAGE JUDGE_MODEL JUDGE_BASE_URL

REPO_ROOT := ../..

.PHONY: check-tools setup image pr prs test-set full-set collect judge report manifest require-run require-runs require-pr require-prs require-judge-key

check-tools:
	@./run.sh check-tools

setup:
	./run.sh setup

image:
	cd $(REPO_ROOT) && docker build --platform linux/amd64 -f benchmarks/reviewbench/Dockerfile -t $(IMAGE) .

pr: require-pr check-tools setup image
	./run.sh run pr "make pr PR=$(PR)" "$(PR)"

prs: require-prs check-tools setup image
	./run.sh run prs 'make prs PRS="$(PRS)"' $(PRS)

test-set: check-tools setup image
	./run.sh run test "make test-set"

full-set: check-tools setup image
	./run.sh run full "make full-set"

judge: require-run check-tools require-judge-key setup
	./run.sh judge "$(RUN)" "make judge RUN=$(RUN) JUDGE_MODEL=$(JUDGE_MODEL) JUDGE_BASE_URL=$(JUDGE_BASE_URL)"

collect: require-runs
	./run.sh collect 'make collect RUNS="$(RUNS)"' $(RUNS)

report: require-run
	./run.sh record "$(RUN)" "make report RUN=$(RUN)"
	python3 report.py "$(RUN)"

manifest: setup
	node .reviewbench/schema/validate-manifest.mjs ponderly.json

require-pr:
	@case "$(PR)" in '' | *[!0-9]*) echo "PR=<n> is required, a Test_Set pull request index such as 0" >&2; exit 2 ;; esac

require-prs:
	@test -n "$(strip $(PRS))" || { echo 'PRS="<n> ..." is required, Test_Set pull request indices such as "0 1 2"' >&2; exit 2; }
	@for index in $(PRS); do case "$$index" in *[!0-9]*) echo "PRS lists Test_Set pull request indices such as \"0 1 2\", not '$$index'" >&2; exit 2 ;; esac; done

# ReviewBench's judge client reads ANTHROPIC_API_KEY itself; a subscription token does not serve it.
require-judge-key:
	@test -n "$$ANTHROPIC_API_KEY" || { echo "missing: ANTHROPIC_API_KEY is not set; the judge needs it" >&2; exit 1; }

require-run:
	@test -n "$(RUN)" || { echo "RUN=<run folder> is required, as make pr, prs, test-set, full-set or collect printed it" >&2; exit 2; }

require-runs:
	@test -n "$(strip $(RUNS))" || { echo 'RUNS="<run folder> ..." is required, the run folders make pr, prs, test-set or full-set printed' >&2; exit 2; }
