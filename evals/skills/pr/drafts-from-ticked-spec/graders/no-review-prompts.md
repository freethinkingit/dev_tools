---
type: regex
pattern: '^\s*(\d+[.)]\s+|[-*]\s+)?(\*\*)?What would break it(\*\*)?\?'
flags: m
match: not_contains
---
None of the five review prompts is put: "What would break it?" at the start of a line or list item, with a capital W and its question mark, is the prompt; the phrase inside a sentence about the prompts, or as a label such as "What would break it:", is not counted.
