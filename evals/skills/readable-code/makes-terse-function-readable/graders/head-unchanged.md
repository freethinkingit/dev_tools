---
type: regex
pattern: '^[^\n]*\tcommit \(initial\): Initial commit\n[^\n]*\tcheckout: moving from main to add-median\n[^\n]*\tcommit: Add median to calc\.stats\n?$'
target: { source: file, path: .git/logs/HEAD }
---
