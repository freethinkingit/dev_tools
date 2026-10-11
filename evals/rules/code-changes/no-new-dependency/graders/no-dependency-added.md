---
type: regex
pattern: 'tenacity|backoff|retrying|requests|httpx'
flags: i
match: not_contains
target: { source: file, path: requirements.txt }
---
