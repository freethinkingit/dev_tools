# Multi-tool plugin

## Introduction and horizon

The freethinking plugin gives engineers a disciplined way to work: specs approved before code, bugs reproduced before fixes, tests with each change, and team rules in every session. Today it runs only in Claude Code. This strategy takes it to every coding agent its author and its users work in, starting with Cursor and Codex, from one source rather than a copy per tool. It serves three readers named in the spike, freethinkingit/dev_tools#61:
- the operator, an engineer who moves between agents;
- the user, who uses the software the operator builds;
- the owner, who maintains the plugin.

The plugin formats of these agents change month to month, so the strategy is open-ended rather than dated. The author reviews this strategy every week.

## Goals

The goals are listed in the order the author ranked them; the first takes the author's time when two compete.

1. **Claude Code, Cursor and Codex at the closest parity each allows.** In Cursor and Codex, an operator installs the plugin with one command, and its rules reach every session and sub-agent. Its skills, agents and hand-offs then behave as they do in Claude Code, as far as the tool allows. Measure: the shared eval cases, run in each tool and scored against Claude Code's results on the same cases. Worth: the author stops switching back to Claude Code for the plugin. Users get the plugin's discipline whichever of the three their engineer works in.
2. **Kiro next, then every agent that gains a format.** Kiro is brought up to the closest parity it allows, measured as for goal 1. Every other agent with a plugin or skills format is installed for the weekly format watch and appears in its report with its gaps, whether or not it is brought up yet. No agent is ruled out, because their support changes quickly. Worth: the author built the plugin partly to stop switching between Kiro and Claude Code, and the next agent should cost less than the last.
3. **One source, no hand-kept copies.** Each tool's packaging comes from the one source, either read as it is or generated from it at build time. A free check fails when a generated file is out of date. Measure: no file a tool reads is edited by hand outside the source. Worth: the owner keeps one plugin in step instead of several.
4. **Know within a week when a tool's support changes.** A weekly run reports which plugin parts each tool supports. It catches both a gap that opens, such as a broken hook, and one that closes, such as a tool gaining named agents. Measure: the weekly report runs, and it names any change from the week before. Worth: glue is retired as soon as a tool no longer needs it, and breakage is seen before an operator meets it.
5. **One delivery channel every agent shares, where it helps.** An MCP server serves the plugin's parts that MCP can carry, in whichever agent connects to it. MCP, the Model Context Protocol, is a standard way for an agent to connect to tools served by another program. All four tools accept MCP servers, Codex, Cursor and Kiro even inside their own plugin or package formats, according to the documentation read in the spike. Measure: the parts served this way work in each target, by that target's eval cases. Worth: one install line and one place to update for the parts it serves, in every agent, including ones with no plugin format.

## Current state

The plugin is at version 0.16.0. It holds, in `plugins/freethinking/`:
- eight skills;
- three agents, `task-executor`, `wave-reviewer` and `document-reviewer`;
- five rule files, loaded into every session and sub-agent by a session-start hook and a sub-agent-start hook;
- one manifest, `.claude-plugin/plugin.json`, and a marketplace that installs it in Claude Code.

Two kinds of test run against it. Eval cases run on `claude plugin eval`, by hand, one target at a time. Free checks are stdlib Python `unittest` files under `checks/`, run by `make validate`.

The spike, #61, built a small test plugin in the plugin's shape: a rule with a codeword, an agent, skills that use each Claude-only feature, and a pair of skills where one hands off to the other. It loaded that plugin into Codex CLI 0.163.0, Cursor CLI 2026.10.22 and kiro-cli 2.33.1, and ran three probe prompts in each: what the session loaded, a skill called with arguments, and a hand-off followed by a sub-agent. It found the following:

- **Codex** installs the plugin from its `.claude-plugin` marketplace unchanged. It runs both rule hooks unchanged, so the rules reach every session and sub-agent. It does not offer the plugin's agents, and its IDE extension loads no plugins.
- **Cursor** loads the plugin's `.claude-plugin` layout, skills, agents and hooks. The rules reach sessions and sub-agents only when the hook prints them as JSON. It ignores an agent's tool list. Its question tool does not block, so the agent keeps working while it waits for an answer.
- **Kiro** needs its own `.kiro/` layout. Its steering files carry rules to every session and sub-agent with no hook, and its Markdown agents keep their tool lists. Kiro's package format, called a power, carries only skills and MCP servers. Steering, agents and hooks must be copied into `~/.kiro/` by an install step.
- **In all three**, one skill hands off to another, which works. Four things do not:
  - skill arguments arrive as literal text;
  - `!` shell prefetch lines arrive as literal text;
  - `${CLAUDE_SKILL_DIR}` arrives as literal text;
  - none has Claude Code's blocking fixed-option question.

AWS's [agent-toolkit-for-aws](https://github.com/aws/agent-toolkit-for-aws) is the nearest prior art:
- one folder per plugin, with a manifest per tool;
- a CI check that the manifests agree;
- shared skills copied from one canonical folder by a sync script with a CI check.

It keeps hooks and agents Claude-only, leaves Claude-only syntax in its shared skill text, and gives Kiro a skills-only install. It also serves skills on demand from an MCP server through a `retrieve_skill` tool.

## Principles and constraints

- Claude Code is the benchmark. Each other tool is measured against Claude Code's results on the same cases, and its glue aims to bring it as close to them as it allows.
- Converge first, compile at the edges. Where a tool reads the plugin's own structure, it reads the source as it is. Where it cannot, the gap is closed by glue generated at build time. Generation is never a first resort.
- Generated output is produced at build time and checked in, and a free check in CI fails when it is out of date.
- No agent is excluded for what it cannot do today. Its gaps are recorded and revisited by the weekly run.
- One set of eval cases is shared by every tool. Each tool has its own runner, plus cases of its own for behaviour only it has. Evals are a token cost: they run by hand, one target at a time, and never in CI.
- Free checks are stdlib Python `unittest` files under `checks/`. No check greps a skill's prompt text; a skill's behaviour is proven by an eval case.
- The author does the work alone, so one destination is brought up at a time.
- The weekly format watch is the one scheduled run that spends tokens, and it is kept to the three probe prompts.

## Streams of work

1. **Core and glue.** Separates the tool-neutral text of skills, rules and agents from what is specific to one tool. It defines the glue each tool needs, such as reading arguments from the request, running prefetch commands as a first step, and naming files relative to the skill. It also adds the build step and its free check for anything generated. Serves goals 1, 2 and 3. First; every other stream builds on it.
2. **Tool packaging and install.** Brings up one destination at a time, each with its own manifest, its hook format and its install path. Cursor and Codex come first, beside Claude Code, then Kiro, then other agents as they gain a format. Serves goals 1 and 2. Starts once the core and glue stream has its first tool-neutral skill.
3. **Cross-tool evals.** The shared eval cases, a runner per tool, and each tool's own cases, scored against Claude Code's results. A destination is done when its runner's results meet the parity bar for that tool. Serves goals 1 and 2. Runs alongside the packaging stream, one destination ahead of or with it.
4. **Format watch.** Rebuilds the spike's test plugin in the repository from its description in #61's result comment. Then a weekly automation re-runs its three probe prompts in every installed agent and reports what each supports and what changed since the week before. The automation runs in Superset, the author's agent workspace, which schedules agent tasks. Serves goals 2 and 4. Can start now.
5. **MCP delivery channel.** Designs an MCP server that serves the plugin's parts MCP can carry: skill text, templates and possibly rules. It decides whether the server runs locally or is hosted on AWS. It settles four questions first:
   - do other agents add MCP server instructions to the session, as Claude Code does;
   - do sub-agents see them;
   - which CLIs render elicitation, MCP's way for a server to ask the user a question;
   - does the model pick skills as reliably through a fetch tool as through descriptions.

   Serves goal 5. Starts once the core and glue stream has defined the tool-neutral text.

## Risks

- **A format changes under a shipped destination.** Likely: Cursor's CLI started running plugin hooks in August 2026, according to its changelog. Kiro moved its powers, its package format, to the open Agent Plugins format in August 2026, according to Kiro's blog; a power still carries only skills and MCP servers. Kiro's changelog says its V3 engine becomes the default at the end of October 2026. Costly when an operator meets it first. The weekly format watch is there to see it first.
- **Glue grows into a fork.** The Claude Code text and a tool's generated text could drift until they are two plugins. Moderate likelihood, costly to unwind. The core and glue stream keeps glue to measured gaps, the spike's for the first three tools and the weekly report's for the rest, and the weekly report retires glue a tool no longer needs.
- **The plugin's approval gates do not hold in some tools.** Cursor's question tool does not block, so a skill can carry on before the author approves. Kiro has no question tool at all. Certain today. A gate that does not hold is recorded as a gap in that tool's evals, not hidden by glue, because no glue can make a tool wait for an answer it does not wait for.
- **Eval costs multiply by the number of tools.** Each destination adds its own runs and a paid account for that tool, and the weekly format watch spends tokens in every installed agent each week. Certain. The shared cases start from the spike's three probe prompts. A tool's own cases are added only when a problem in that tool needs one.
- **The MCP server becomes a service to run.** An AWS-hosted server needs authentication and uptime, and every session depends on the network. A single maintainer then carries that alone. Moderate likelihood if hosting is chosen. The MCP design weighs a local server against a hosted one before anything is built.

## Out of scope

- Hand-kept copies of the plugin per tool, ruled out by goal 3.
- Running evals in CI, ruled out by the constraints above.

## High level designs

- `core-and-glue`: the split between tool-neutral text and per-tool glue, the build step that generates per-tool output, and its free check.
- `tool-packaging`: per-destination manifests, hook formats and install paths, Cursor and Codex first, then Kiro and the agents after.
- `cross-tool-evals`: the shared eval cases, a runner per tool, each tool's own cases, and scoring against Claude Code.
- `format-watch`: the test plugin in the repository and the weekly Superset automation that re-runs it in each agent and reports changes.
- `mcp-delivery`: an MCP server for the parts MCP can carry, local or AWS-hosted, and the four questions it settles first.
