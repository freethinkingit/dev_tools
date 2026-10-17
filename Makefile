# Checks for the handbook plugin.
#
#   make validate              free: check, manifests and skill frontmatter (CI runs this)
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
# change. A case that needs its own flags gets one line in the "Per-target
# flags" block below; those flags are kept in CASE_ARGS so EVAL_ARGS on the
# command line still adds to them. The cost ceiling is per invocation, so raise
# it for the whole suite: make eval EVAL_MAX_COST_USD=5. Results go to
# evals/results/<timestamp>/ (gitignored). Paste the table the command prints
# into the PR's Testing section.

EVAL_MAX_COST_USD ?= 2
EVAL_ARGS ?=
CASE_ARGS :=
EVAL = claude plugin eval . --trust-plugin --ablation none --no-publish \
        --max-cost-usd $(EVAL_MAX_COST_USD) $(EVAL_ARGS) $(CASE_ARGS)

SKILLS := $(notdir $(patsubst %/,%,$(wildcard evals/skills/*/)))
RULES  := $(notdir $(patsubst %/,%,$(wildcard evals/rules/*/)))
AGENTS := $(notdir $(patsubst %/,%,$(wildcard evals/agents/*/)))
SKILL_TARGETS := $(addprefix eval-skill-,$(SKILLS))
RULE_TARGETS  := $(addprefix eval-rule-,$(RULES))
AGENT_TARGETS := $(addprefix eval-agent-,$(AGENTS))

.PHONY: validate check help eval eval-hook $(SKILL_TARGETS) $(RULE_TARGETS) $(AGENT_TARGETS)

validate: check
	claude plugin validate . --strict
	claude plugin validate ./skills --strict

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
eval-skill-pr: CASE_ARGS += --allow-tools Bash --scaffold
eval-skill-pr: export PATH := bin:$(PATH)
eval-skill-start-task: CASE_ARGS += --allow-tools Write Edit --scaffold
eval-skill-bugfix: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-skill-bugfix: export PATH := bin:$(PATH)
eval-rule-code-changes: CASE_ARGS += --allow-tools Write Edit --scaffold
eval-rule-communication: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-rule-communication: export PATH := bin:$(PATH)
eval-rule-workflow: CASE_ARGS += --scaffold
eval-skill-report: CASE_ARGS += --allow-tools Bash Write Edit --scaffold
eval-skill-report: export PATH := bin:$(PATH)

# Runs all evals and needs all flags
eval: CASE_ARGS += --scaffold
eval: CASE_ARGS += --allow-tools Bash Write Edit
eval: export PATH := bin:$(PATH)

eval:
	$(EVAL)

eval-hook:
	$(EVAL) --tag hook

$(SKILL_TARGETS): eval-skill-%:
	$(EVAL) --tag $*

$(RULE_TARGETS): eval-rule-%:
	$(EVAL) --tag $*

$(AGENT_TARGETS): eval-agent-%:
	$(EVAL) --tag $*
