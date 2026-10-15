# Design Document

## Overview

One function in `calc/ops.py`, next to `add` and `multiply`, and one test method in `tests/test_ops.py`, in the existing `OpsTest` class. Tests run with `python3 -m unittest`.

## Components and Interfaces

| Component | Responsibility | Requirements |
|-----------|----------------|--------------|
| `calc/ops.py` `subtract(a, b)` | returns a minus b | 1.1 |
| `tests/test_ops.py` `test_subtract` | asserts subtract(5, 3) == 2 | 1.2 |
