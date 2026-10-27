---
type: regex
target: trace
pattern: '(?:demo/__init__\.py|0\.[12]\.0)[^\n]{0,300}?(?:anything a reviewer should know|(?:took|taken|from (?:your|the) request)[^\n]{0,150}?nothing a reviewer needs|nothing a reviewer needs[^\n]{0,150}?(?:took|taken|from (?:your|the) request))|(?:anything a reviewer should know|(?:took|taken|from (?:your|the) request)[^\n]{0,150}?nothing a reviewer needs|nothing a reviewer needs[^\n]{0,150}?(?:took|taken|from (?:your|the) request))[^\n]{0,300}?(?:demo/__init__\.py|0\.[12]\.0)'
flags: i
---
