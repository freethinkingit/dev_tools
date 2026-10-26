# uploadq

A small job queue. The upload worker takes one job at a time: a file the uploader has sent, which it stores and indexes. When a job fails, the worker retries it at once, and the jobs behind it wait in the queue until it succeeds or is dropped.

## Open decision: the retry ceiling

The worker needs a ceiling on retries for a failed job, and it has not been chosen. The candidates are 3, 5 and 10 attempts.

What we have seen over the last month of failed jobs:

| Ceiling | Failures that succeed by this attempt | Added queue delay for each job behind a failing one |
| --- | --- | --- |
| 3 | 80% | about 6 seconds |
| 5 | 95% | about 15 seconds |
| 10 | 97% | about 45 seconds |

Who waits: the uploader. When a job is dropped after its last attempt, the uploader's file is lost and the uploader has to send it again. While retries run, every uploader whose job is behind the failing one waits for their file to appear.
