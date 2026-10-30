# ReviewBench harness for the review skill. Run by hand, never in CI: the run
# and judge targets are real model calls. A run takes ANTHROPIC_API_KEY or a
# Claude subscription's CLAUDE_CODE_OAUTH_TOKEN; the judge needs ANTHROPIC_API_KEY.
#
#   make check-tools          stop naming the first of docker, node, jq that is missing, or that neither
#                             ANTHROPIC_API_KEY nor CLAUDE_CODE_OAUTH_TOKEN is set
#   make setup                clone ReviewBench at REVIEWBENCH_COMMIT into .reviewbench/ and npm ci there
#   make image                build $(IMAGE) from the repository root
#   make pr PR=<n>            run the image on Test_Set pull request <n> into runs/<timestamp>-pr<n>/
#   make test-set             run the image on the Test_Set into runs/<timestamp>-test/
#   make full-set             run the image on the Full_Set into runs/<timestamp>-full/
#   make judge RUN=<dir>      judge <dir>/findings into <dir>/scoring/results.json with JUDGE_MODEL at JUDGE_BASE_URL
#   make report RUN=<dir>     write and print <dir>/report.md
#   make manifest             validate ponderly.json with the clone's schema/validate-manifest.mjs
#
# The run targets print the run folder to pass as RUN. RB_CONFIG_MODEL,
# RB_CONFIG_EFFORT and RB_CONFIG_BUDGET_USD in the environment reach the
# adapter in the image, and run.json records them.

REVIEWBENCH_COMMIT ?= 228f2a8d662c9c1c12d25757e23c52c9a6170d5a
IMAGE ?= ponderly-review:dev
JUDGE_MODEL ?= claude-sonnet-5
JUDGE_BASE_URL ?= https://api.anthropic.com
RUN ?=

export REVIEWBENCH_COMMIT IMAGE JUDGE_MODEL JUDGE_BASE_URL

REPO_ROOT := ../..

.PHONY: check-tools setup image pr test-set full-set judge report manifest require-run require-pr require-judge-key

check-tools:
	@./run.sh check-tools

setup:
	./run.sh setup

image:
	cd $(REPO_ROOT) && docker build --platform linux/amd64 -f benchmarks/reviewbench/Dockerfile -t $(IMAGE) .

pr: require-pr check-tools setup image
	./run.sh run pr "make pr PR=$(PR)" "$(PR)"

test-set: check-tools setup image
	./run.sh run test "make test-set"

full-set: check-tools setup image
	./run.sh run full "make full-set"

judge: require-run check-tools require-judge-key setup
	./run.sh judge "$(RUN)" "make judge RUN=$(RUN) JUDGE_MODEL=$(JUDGE_MODEL) JUDGE_BASE_URL=$(JUDGE_BASE_URL)"

report: require-run
	./run.sh record "$(RUN)" "make report RUN=$(RUN)"
	python3 report.py "$(RUN)"

manifest: setup
	node .reviewbench/schema/validate-manifest.mjs ponderly.json

require-pr:
	@case "$(PR)" in '' | *[!0-9]*) echo "PR=<n> is required, a Test_Set pull request index such as 0" >&2; exit 2 ;; esac

# ReviewBench's judge client reads ANTHROPIC_API_KEY itself; a subscription token does not serve it.
require-judge-key:
	@test -n "$$ANTHROPIC_API_KEY" || { echo "missing: ANTHROPIC_API_KEY is not set; the judge needs it" >&2; exit 1; }

require-run:
	@test -n "$(RUN)" || { echo "RUN=<run folder> is required, as make pr, test-set or full-set printed it" >&2; exit 2; }
