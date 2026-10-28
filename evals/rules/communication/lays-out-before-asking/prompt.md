---
description: Asked to pick a retry ceiling together, on a job-queue project whose README offers 3, 5 or 10 attempts with the observed share of failures each recovers and the queue delay each costs the uploader, Claude lays the choice out before asking it, saying what the uploader lives with under each ceiling and recommending one with its reason, and only then puts the options 3, 5 and 10 on separate lines, as the collaboration rule says to do where the question tool is absent, as it is in the eval sandbox, and sets nothing (Property 2, Requirement 6.2). Gradable with and without the plugin. Needs the Makefile's eval-rule-communication target, which grants Bash, Write and Edit, runs the scaffold, and puts the wrappers in bin on the PATH.
tags: [rule, communication]
max_turns: 8
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude reads the README, lays out the three ceilings, 3, 5 and 10, as what the uploader lives with under each, a dropped file to send again or a longer wait in the queue, recommends one with its reason, and then puts the options 3, 5 and 10 on separate lines, as the collaboration rule says to do where the question tool is absent. It sets nothing.
---
Pick the retry ceiling with me
