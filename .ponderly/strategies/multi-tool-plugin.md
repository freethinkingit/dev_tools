# Multi-tool plugin

## Introduction and horizon

The freethinking plugin gives engineers a disciplined way to work: specs approved before code, bugs reproduced before fixes, tests with each change, and team rules in every session. Today it runs only in Claude Code. This strategy takes it to every coding agent its author and the engineers who use it work in, starting with Cursor and Codex, from one canonical source compiled into each agent's own format, rather than a copy per tool. It serves three people named in the spike, freethinkingit/dev_tools#61:
- the operator, an engineer who moves between agents;
- the user, who uses the software the operator builds;
- the owner, who maintains the plugin.

The horizon is this quarter, from 22 October to 31 December 2026. The plugin formats of these agents change month to month, so the author reviews this strategy every week and sets the next horizon at the quarter's end.

## Goals

The goals are listed in the order the author ranked them; the first takes the author's time when two compete.

This quarter the targets are each agent's command-line tool. The IDEs may become targets later. Parity means the plugin's three core parts work in the agent, each through whatever that agent supports for it, in its own format where it has one:
- its skills;
- its sub-agents, the plugin's named agents;
- its rules, in every session and sub-agent.

Other gaps, such as a question tool that does not block, are recorded and do not count against parity.

1. **Claude Code, Cursor and Codex at the closest parity each allows.** In Cursor and Codex, an operator installs the plugin with one command, and its rules reach every session and sub-agent. Its skills, agents and hand-offs then behave as they do in Claude Code, as far as the tool allows. Measure: every shared scenario for skills, sub-agents and rules that passes in Claude Code passes in each tool, with each part delivered through that tool's own support, such as Codex's agents as its own agent files; a failure caused by a recorded gap outside those three parts does not count. Worth: the author, as an operator, stops switching back to Claude Code for the plugin. Users get the plugin's discipline whichever of the three their engineer works in, except where an agent's question tool does not wait for approval, which is recorded as a gap.
2. **Kiro next, then every agent that gains a format.** Kiro is brought up to the closest parity it allows, measured as for goal 1. Every other agent with a plugin or skills format is installed for the weekly format watch and appears in its report with its gaps, whether or not it is brought up yet. No agent is ruled out, because their support changes quickly. Worth: the author built the plugin partly to stop switching between Kiro and Claude Code, and the next agent should cost less than the last.
3. **One canonical source, no hand-kept copies.** Every agent's layout, Claude Code's included, is generated at build time from one canonical source. A free check fails when a generated file is out of date or when a target leaves out part of the canonical source. Measure: no file an agent reads is edited by hand; each is generated. Worth: the owner keeps one plugin in step instead of several, and adding an agent means adding one target, not rewriting the plugin.
4. **Know within a week when a tool's support changes.** A weekly run reports which plugin parts each tool supports. It catches both a gap that opens, such as a broken hook, and one that closes, such as a tool gaining named agents. Measure: the weekly report runs, and it names any change from the week before. Worth: a target is updated as soon as an agent's support changes, and breakage is seen before an operator meets it.
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

It keeps hooks and agents Claude-only, leaves Claude-only syntax in its shared skill text, and gives Kiro a skills-only install. It also ships a Devin manifest, so Devin has a plugin format too, and it serves skills on demand from an MCP server through a `retrieve_skill` tool.

The author's dansabin project, a separate repository of theirs, has a Gherkin harness, `@freethinkingit/gherkin-harness`: it runs Cucumber Features through a library of ready-made steps for HTTP, browser, command and data checks, and records what each step did. It is TypeScript on Node, and it has no steps for driving a coding agent or reading its output.

## Principles and constraints

- Claude Code is the benchmark. Each other tool is measured against Claude Code's results on the same cases, and its target aims to bring it as close to them as it allows.
- One canonical source, compiled for every agent. A canonical folder holds the Markdown of every skill, rule and agent, with neutral markers where agents differ. One target folder per agent, as the author chose, holds the generator that writes that agent's native layout from it. Claude Code is a target like any other. A target generates every file its agent reads, copying unchanged whatever the agent already reads natively.
- Generated output is produced at build time and checked in. A free check in CI fails when it is out of date or when a target is incomplete, that is, when it leaves out part of the canonical source.
- No agent is excluded for what it cannot do today. Its gaps are recorded and revisited by the weekly run.
- One set of eval scenarios is shared by every agent. They run through one harness that drives each agent's command-line tool and checks both the final result and what happened along the way, such as which skill loaded, whether a question came before a write, and whether a sub-agent started. An agent may add scenarios of its own for behaviour only it has. Evals are a token cost: they run by hand, one target at a time, and never in CI.
- Free checks are stdlib Python `unittest` files under `checks/`. No check greps a skill's prompt text; a skill's behaviour is proven by an eval case.
- The author does the work alone, so one destination is brought up at a time.
- The weekly format watch is the one scheduled run that spends tokens, and it is kept to the three probe prompts.

## Streams of work

1. **Canonical source and the Claude Code target.** Moves the skills, rules and agents into the canonical folder, defines the neutral markers, and builds the compiler with its freshness and completeness check. Its first target is Claude Code: the generated output must match today's `plugins/freethinking/` byte for byte, so the migration changes no behaviour. Serves goals 1, 2 and 3. First; every stream but the format watch builds on it.
2. **Agent targets.** Adds one target folder per agent, one at a time. Each holds that agent's generator, manifest, hook format and install path. Cursor and Codex come first, then Kiro, then other agents as they gain a format, Devin among them, since it already has one. Serves goals 1, 2 and 3. Starts once the Claude Code target reproduces today's plugin.
3. **Cross-agent evals.** The shared scenarios and one harness that runs them against every agent, checking the final result and the events along the way, scored against Claude Code's results. It weighs the author's Gherkin harness against extending this repository's own tooling. An agent target is done when its scenarios show the plugin's skills, sub-agents and rules working in that agent. Serves goals 1 and 2. Runs alongside the agent targets stream: the scenarios for a target are written before or with that target.
4. **Format watch.** Rebuilds the spike's test plugin in the repository from its description in #61's result comment. Then a weekly automation re-runs its three probe prompts in every installed agent and reports what each supports and what changed since the week before. The automation runs in Superset, the author's agent workspace, which schedules agent tasks. Serves goals 2 and 4. Can start now.
5. **MCP delivery channel.** Designs and builds an MCP server that serves the plugin's parts MCP can carry: skill text, templates and possibly rules. It decides whether the server runs locally or is hosted on AWS, or records a decision not to build one. It settles four questions first:
   - do other agents add MCP server instructions to the session, as Claude Code does;
   - do sub-agents see them;
   - which CLIs render elicitation, MCP's way for a server to ask the user a question;
   - does the model pick skills as reliably through a fetch tool as through descriptions.

   Serves goal 5. Starts once the canonical source exists, since that is the text it would serve.

## Risks

- **A format changes under a shipped destination.** Likely: Cursor's CLI started running plugin hooks in August 2026, according to its changelog. Kiro moved its powers, its package format, to the open Agent Plugins format in August 2026, according to Kiro's blog; a power still carries only skills and MCP servers. Kiro's changelog says its V3 engine becomes the default at the end of October 2026. Costly when an operator meets it first. The weekly format watch is there to see it first.
- **The markers grow into a programming language.** Each agent's difference tempts a new marker, until the canonical source is harder to read than any one agent's text. Moderate likelihood, costly to unwind. Markers are added only for a difference the spike or the weekly report has measured, and the canonical source design sets how few markers there are.
- **Every change goes through a build.** Editing a skill means editing the canonical source and building, even for Claude Code. Certain, and a small cost on every edit. The freshness check in CI catches a forgotten build, and `make build` is one command.
- **The migration changes Claude Code's behaviour.** Moving the plugin into the canonical source could alter the text Claude Code reads. Possible, and costly to the benchmark. The Claude Code target must reproduce today's `plugins/freethinking/` byte for byte before any other target is added.
- **The plugin's approval gates do not hold in some tools.** None of the three has a blocking question tool in its normal mode. Cursor's does not block, so a skill can carry on before the author approves. Codex's question tool exists only in its plan mode, which the plugin's skills do not run in. Kiro has none. Certain today. A gate that does not hold is recorded as a gap in that tool's evals, not hidden by glue, because no glue can make a tool wait for an answer it does not wait for.
- **Eval costs multiply by the number of tools.** Each destination adds its own runs and a paid account for that tool, and the weekly format watch spends tokens in every installed agent each week. Certain, and a moderate cost. The shared cases start from the spike's three probe prompts; the cross-agent evals issue, #65, settles which of the existing cases under `evals/` join them. A tool's own cases are added only when a problem in that tool needs one.
- **The MCP server becomes a service to run.** An AWS-hosted server needs authentication and uptime, and every session depends on the network. A single maintainer then carries that alone. Moderate likelihood if hosting is chosen. The MCP design weighs a local server against a hosted one before anything is built.

## Out of scope

Anything this strategy does not name is out of scope this quarter. In particular:
- The IDEs: Codex's IDE extension, the Cursor IDE and the Kiro IDE. They may become targets once the command-line tools reach parity.
- Hand-kept copies of the plugin per tool, ruled out by goal 3.
- Running evals in CI, ruled out by the constraints above.

## High level designs

- `canonical-source`: the canonical folder, its neutral markers, the compiler with its freshness and completeness check, and the Claude Code target that reproduces today's plugin byte for byte.
- `agent-targets`: one target folder per agent, each with its generator, manifest, hook format and install path; Cursor and Codex first, then Kiro and the agents after.
- `cross-agent-evals`: the shared scenarios, one harness driving every agent's command-line tool with checks on the final result and the events along the way, and the choice between the Gherkin harness and this repository's own tooling.
- `format-watch`: the test plugin in the repository and the weekly Superset automation that re-runs it in each agent and reports changes.
- `mcp-delivery`: an MCP server for the parts MCP can carry, local or AWS-hosted, and the four questions it settles first.
