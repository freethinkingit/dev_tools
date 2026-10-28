# Implementation Plan

## Overview

Two tasks: the function, then its test. Tests run with `python3 -m unittest`.

## Tasks

- [x] 1. Add `subtract(a, b)` to `calc/ops.py`, returning a minus b, in the style of `add`
  - _Requirements: 1.1_

- [x] 2. Add `test_subtract` to `OpsTest` in `tests/test_ops.py`, asserting subtract(5, 3) == 2
  - _Requirements: 1.2_

## Notes

- Task numbers identify tasks; the graph decides the order.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2"] }
  ]
}
```
