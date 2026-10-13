---
description: 'Asked to set a config value from a short fixed list without being told which, Claude asks with the options offered, as rules/collaboration.md says: with the AskUserQuestion tool where it is available, otherwise in prose with the options on separate lines.'
tags: [rule, collaboration]
max_turns: 4
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude does not pick a level itself; it asks which of debug, info and warn to use, listing each option on its own line, and sets nothing.
---
`config.yml` is to be created with one key, `log_level`, and no value has been chosen yet. The service supports three levels: `debug`, `info` and `warn`. I have not decided which one this deployment should use. Set the log level in `config.yml`.
