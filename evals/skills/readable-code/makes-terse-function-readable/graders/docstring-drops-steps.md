---
type: llm
focus: { source: file, path: calc/stats.py }
---

The file shown is `calc/stats.py` after a readability pass over a branch whose one source file it is. Before the pass, the docstring of `median` in that file walked through the algorithm in numbered steps: sort the values, take the count and the middle index, return the middle value for an odd count and otherwise the average of the two middle values.

PASS if the docstring of `median` in the file shown states only the function's intent, its parameters, what it returns and what it raises, for example "Return the median of values; for an even count, the mean of the two middle values." Saying what the result is for an even count is part of what it returns, not a step.
FAIL if the docstring still describes how the result is computed, in steps or in reworded prose, such as sorting the values, finding or taking the middle index or element, or averaging the elements around the middle as an action the function performs; or if `median` has no docstring left at all or the file has no `median`.
