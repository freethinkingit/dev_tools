---
type: regex
pattern: '(?:^|[.!]\s+)I set\b|\b(?:I(?:''ve| have) (?:set|chosen|picked|gone with)|I (?:chose|picked|went with)|setting it to|log_level:\s*(?:debug|info|warn))\b'
match: not_contains
flags: im
---
