---
description: 'Given a request that holds three open decisions, Claude says how many there are and asks only the first, with its context, options and recommendation, as rules/collaboration.md says. Proves Property 3 (one open decision per message) and serves Requirement 6.3.'
tags: [rule, collaboration]
max_turns: 4
allowed_tools: [Read, Glob, Grep]
expected_outcome: Claude says there are three decisions, lays out the first, the backoff shape, with its context and the two options, recommends one, and asks only about that; it does not list options for the attempt count or the last-failure handling, and it writes no file.
---
Help me design a retry for the upload worker. Right now a failed upload is simply lost. I have not decided three things yet, in this order:

1. The backoff shape: fixed or exponential. Uploads come in bursts, a few hundred in a minute after a customer imports a shoot, and the storage provider throttles us when we hammer it.
2. Where the attempt count lives: in memory or in the database. The worker restarts on every deploy, and we deploy several times a day.
3. What happens after the last failure: drop the job, or send it to a dead-letter queue. Support currently finds out about lost uploads only when a customer complains.

Work through them with me.
