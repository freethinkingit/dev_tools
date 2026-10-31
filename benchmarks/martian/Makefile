# Martian's offline code review benchmark on the ponderly review image.
#
#   make check-tools       stop naming the first of docker, gh, uv, jq, MARTIAN_API_KEY that is missing
#   make setup             clone withmartian/code-review-benchmark at MARTIAN_COMMIT into .martian/ and uv sync
#   make prs               resolve the golden pull requests through gh api into prs.json
#   make run [ONLY=<n>]    run IMAGE on every pull request of prs.json, or entry <n>, into runs/<timestamp>/
#   make convert RUN=<dir> write <dir>/benchmark_data.json from <dir>/findings/
#   make judge RUN=<dir>   run Martian's steps 2, 2.5 and 3 and copy evaluations.json into <dir>/scoring/
#   make report RUN=<dir>  write <dir>/report.md
#
# RUN defaults to the newest folder under runs/, so `make run convert judge
# report` works on the folder the run target just made. run and judge make
# model calls on your own keys (ANTHROPIC_API_KEY or a Claude subscription's
# CLAUDE_CODE_OAUTH_TOKEN for the image, MARTIAN_API_KEY for the judge) and
# never run in CI; each target stops first, naming the tool or key it needs
# that is missing. The judge reads MARTIAN_BASE_URL and
# MARTIAN_MODEL; override both for an OpenAI judge. Each target that works on
# a run folder appends its command to the folder's run.json.

MARTIAN_REPO := https://github.com/withmartian/code-review-benchmark.git
MARTIAN_COMMIT ?= e616e849755441da38f18bf3adba2c9583b03803
IMAGE ?= ponderly-review:dev
MARTIAN_BASE_URL ?= https://api.anthropic.com/v1/
MARTIAN_MODEL ?= claude-opus-4-5-20251101
ONLY ?=
RUN ?= $(shell ls -d runs/*/ 2>/dev/null | tail -n 1 | sed 's:/$$::')

export MARTIAN_BASE_URL MARTIAN_MODEL

OFFLINE := .martian/offline
MODEL_DIR := $(OFFLINE)/results/$(subst /,_,$(strip $(MARTIAN_MODEL)))

# $(1) is a list of commands and environment variables, each one stopping the target when missing.
define REQUIRE
@for name in $(1); do \
	case $$name in \
		*_KEY) test -n "$$(printenv $$name)" ;; \
		*) command -v $$name >/dev/null 2>&1 ;; \
	esac || { echo "missing: $$name" >&2; exit 1; }; \
done
endef

# $(1) is a list of environment variables, the target stopping when none of them is set.
define REQUIRE_ONE_OF
@for name in $(1); do test -n "$$(printenv $$name)" && exit 0; done; \
	echo "missing: one of $(1)" >&2; exit 1
endef

define REQUIRE_RUN
@test -n "$(RUN)" -a -f "$(RUN)/run.json" || { echo "RUN=$(RUN) is not a run folder; run the run target first or name one with RUN=<dir>" >&2; exit 1; }
endef

# $(1) is a jq filter applied to run.json with $$command bound to the target's command.
define RECORD
@jq --arg command "$(2)" '$(1) | .commands += [$$command]' "$(RUN)/run.json" > "$(RUN)/run.json.tmp" && mv "$(RUN)/run.json.tmp" "$(RUN)/run.json"
endef

.PHONY: check-tools setup prs run convert judge report

check-tools:
	$(call REQUIRE,docker gh uv jq MARTIAN_API_KEY)

setup:
	$(call REQUIRE,git uv)
	@test -d .martian/.git || git clone -q $(MARTIAN_REPO) .martian
	@git -C .martian cat-file -e "$(MARTIAN_COMMIT)^{commit}" 2>/dev/null || git -C .martian fetch -q origin
	git -C .martian checkout -q --detach $(MARTIAN_COMMIT)
	cd $(OFFLINE) && uv sync --frozen

prs:
	$(call REQUIRE,gh)
	python3 prs.py

run:
	$(call REQUIRE,docker git jq)
	$(call REQUIRE_ONE_OF,ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN)
	./run.sh "$(IMAGE)" $(ONLY)

convert:
	$(REQUIRE_RUN)
	python3 convert.py "$(RUN)" $(OFFLINE)/golden_comments
	$(call RECORD,.,make convert RUN=$(RUN))

judge:
	$(call REQUIRE,uv jq MARTIAN_API_KEY)
	$(REQUIRE_RUN)
	@test -f "$(RUN)/benchmark_data.json" || { echo "$(RUN)/benchmark_data.json not found; run the convert target first" >&2; exit 1; }
	cp "$(RUN)/benchmark_data.json" $(OFFLINE)/results/benchmark_data.json
	cd $(OFFLINE) && uv run --frozen python -m code_review_benchmark.step2_extract_comments --tool ponderly --force
	cd $(OFFLINE) && uv run --frozen python -m code_review_benchmark.step2_5_dedup_candidates --tool ponderly --force
	cd $(OFFLINE) && uv run --frozen python -m code_review_benchmark.step3_judge_comments --tool ponderly --force \
		--dedup-groups results/$(notdir $(MODEL_DIR))/dedup_groups.json
	mkdir -p "$(RUN)/scoring"
	cp $(MODEL_DIR)/evaluations.json "$(RUN)/scoring/evaluations.json"
	$(call RECORD,.judge_model = "$(MARTIAN_MODEL)" | .judge_base_url = "$(MARTIAN_BASE_URL)",make judge RUN=$(RUN) MARTIAN_MODEL=$(MARTIAN_MODEL) MARTIAN_BASE_URL=$(MARTIAN_BASE_URL))

report:
	$(REQUIRE_RUN)
	$(call RECORD,.,make report RUN=$(RUN))
	python3 report.py "$(RUN)"
