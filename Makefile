# Checks for the handbook plugin.
#
#   make validate              free: check, marketplace, plugin manifest and skill frontmatter (CI runs this)
#   make check                 free: the Python checks under checks/, such as the hook's JSON encoder
#   make help                  list the eval targets that exist
#   make eval                  every eval case
#   make eval-skill-<name>     cases under evals/skills/<name>/
#   make eval-rule-<name>      cases under evals/rules/<name>/
#   make eval-agent-<name>     cases under evals/agents/<name>/
#   make eval-hook             cases under evals/hook/
#
# Evals are real model calls on your own Claude seat, so they run by hand, not
# in CI. Defaults: one arm (plugin on), the case's own runs count, list-price
# ceiling $(EVAL_MAX_COST_USD). Add flags with EVAL_ARGS, for example
#   make eval-skill-pr EVAL_ARGS="--runs 2 --ablation with-without"
# Iterate at --runs 1; confirm at 2 when every grader of the case is
# deterministic, 3 when any is llm or the target mixes both. --case takes one
# glob and the last --case wins, so run one invocation per named case.
# The eval-skill-*, eval-rule-* and eval-agent-* targets are enumerated from
# the evals/ directories and select their cases with --tag, so every case
# carries its component's name as a tag and a new case needs no Makefile
# change. The runner reads cases only from inside the plugin root, and the
# plugin lives in $(PLUGIN) with evals/ beside it at the repository root, so
# each eval target runs claude plugin eval against a temporary copy of the
# plugin with evals/ copied inside it and a git repository initialised at its
# top, for the scaffolds that find evals/fixtures/ through git rev-parse. The
# pr scaffold also reads .github/pull_request_template.md from that top, so
# that one file is copied in too. The copy is deleted when the run ends, pass or fail. A case that needs its own
# flags gets one line in the "Per-target flags" block below; those flags are
# kept in CASE_ARGS so EVAL_ARGS on the command line still adds to them. The
# cost ceiling is per invocation, so raise it for the whole suite: make eval
# EVAL_MAX_COST_USD=5. Results go to evals/results/<timestamp>/ at the
# repository root (gitignored), and every run's trace.jsonl and last message
# are copied there as traces/<case>-<arm>-run<n>.jsonl and .md by
# evals/keep_traces.py, which then deletes the runner's kept sandboxes, so a
# failed grader can be read without a paid rerun. Paste the table the command
# prints into the PR's Testing section.

PLUGIN := plugins/ponderly
EVAL_MAX_COST_USD ?= 2
EVAL_ARGS ?=
CASE_ARGS :=

define RUN_EVAL
set -eu; \
results=$$(pwd)/evals/results/$$(date +%Y-%m-%dT%H-%M-%S); \
run=$$(mktemp -d "$${TMPDIR:-/tmp}/ponderly-eval.XXXXXX"); \
trap 'rm -rf "$$run"' EXIT; trap 'exit 130' HUP INT TERM; \
cp -R $(PLUGIN)/. "$$run"/; \
tar -C . --exclude=evals/results -cf "$$run/evals.tar" evals; \
tar -C "$$run" -xf "$$run/evals.tar"; \
rm "$$run/evals.tar"; \
mkdir -p "$$run/.github"; \
cp .github/pull_request_template.md "$$run/.github/"; \
git -C "$$run" init -q; \
mkdir -p "$$results"; \
status=0; \
claude plugin eval "$$run" --trust-plugin --ablation none --no-publish --keep-temp \
	--max-cost-usd $(EVAL_MAX_COST_USD) --output-dir "$$results" \
	$(EVAL_ARGS) $(CASE_ARGS) $(1) || status=$$?; \
python3 evals/keep_traces.py "$$results"; \
exit $$status
endef

SKILLS := $(notdir $(patsubst %/,%,$(wildcard evals/skills/*/)))
RULES  := $(notdir $(patsubst %/,%,$(wildcard evals/rules/*/)))
AGENTS := $(notdir $(patsubst %/,%,$(wildcard evals/agents/*/)))
SKILL_TARGETS := $(addprefix eval-skill-,$(SKILLS))
RULE_TARGETS  := $(addprefix eval-rule-,$(RULES))
AGENT_TARGETS := $(addprefix eval-agent-,$(AGENTS))

.PHONY: validate check help eval eval-hook $(SKILL_TARGETS) $(RULE_TARGETS) $(AGENT_TARGETS)

validate: check
	claude plugin validate . --strict
	claude plugin validate ./$(PLUGIN) --strict
	claude plugin validate ./$(PLUGIN)/skills --strict

check:
	python3 -m unittest discover -s checks

help:
	@printf '  %s\n' eval eval-hook $(SKILL_TARGETS) $(RULE_TARGETS) $(AGENT_TARGETS)

# Per-target flags. The scaffold flag runs the case's own scaffold script
# (evals/skills/implement-spec/invalid-graph-stops/scaffold.sh) as you.
# Bash is used by some skills, and Path is needed because some tools modify git and gh shims.
eval-skill-implement-spec: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-skill-implement-spec: export PATH := bin:$(PATH)
eval-agent-task-executor: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-agent-task-executor: export PATH := bin:$(PATH)
eval-agent-wave-reviewer: CASE_ARGS += --allow-tools Bash --scaffold
eval-agent-wave-reviewer: export PATH := bin:$(PATH)
eval-agent-document-reviewer: CASE_ARGS += --scaffold
eval-skill-pr: CASE_ARGS += --allow-tools Bash --scaffold
eval-skill-pr: export PATH := bin:$(PATH)
eval-skill-start-task: CASE_ARGS += --allow-tools Write Edit --scaffold
eval-skill-strategy: CASE_ARGS += --allow-tools Write Edit --scaffold
eval-skill-hld: CASE_ARGS += --allow-tools Write Edit --scaffold
eval-skill-lld: CASE_ARGS += --allow-tools Write Edit --scaffold
eval-skill-readable-code: CASE_ARGS += --allow-tools Bash Write Edit Agent --scaffold
eval-skill-readable-code: export PATH := bin:$(PATH)
eval-skill-bugfix: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-skill-bugfix: export PATH := bin:$(PATH)
eval-skill-tighten-tests: CASE_ARGS += --allow-tools Bash Write Edit Agent --scaffold
eval-skill-tighten-tests: export PATH := bin:$(PATH)
eval-rule-code-changes: CASE_ARGS += --allow-tools Write Edit --scaffold
eval-rule-tests: CASE_ARGS += --allow-tools Bash Write Edit Agent --scaffold
eval-rule-tests: export PATH := bin:$(PATH)
eval-rule-communication: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-rule-communication: export PATH := bin:$(PATH)
eval-rule-workflow: CASE_ARGS += --allow-tools Bash --scaffold
eval-rule-workflow: export PATH := bin:$(PATH)
eval-skill-report: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-skill-report: export PATH := bin:$(PATH)
eval-skill-review: CASE_ARGS += --allow-tools Bash --scaffold
eval-skill-review: EVAL_MAX_COST_USD = 10
eval-skill-review: export PATH := bin:$(PATH)
eval-agent-review-arm: CASE_ARGS += --allow-tools Bash --scaffold
eval-agent-review-arm: export PATH := bin:$(PATH)

# Runs all evals and needs all flags
eval: CASE_ARGS += --scaffold
eval: CASE_ARGS += --allow-tools Bash Write Edit
eval: export PATH := bin:$(PATH)

eval:
	$(call RUN_EVAL)

eval-hook:
	$(call RUN_EVAL,--tag hook)

$(SKILL_TARGETS): eval-skill-%:
	$(call RUN_EVAL,--tag $*)

$(RULE_TARGETS): eval-rule-%:
	$(call RUN_EVAL,--tag $*)

$(AGENT_TARGETS): eval-agent-%:
	$(call RUN_EVAL,--tag $*)
