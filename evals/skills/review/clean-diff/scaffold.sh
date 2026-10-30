#!/usr/bin/env bash
# Builds the workspace for this case: the calc fixture on branch calc-subtract,
# with the bin wrappers the Makefile's review target puts on the PATH, then an
# uncommitted calc/ops.py that adds a correct subtract, a - b, and an
# uncommitted tests/test_ops.py that tests it like add and multiply.
set -euo pipefail
ROOT=$(git -C "$(dirname "$0")" rev-parse --show-toplevel)
bash "$ROOT/evals/fixtures/setup.sh" calc calc-subtract wrappers
printf 'def add(a, b):\n    return a + b\n\n\ndef subtract(a, b):\n    return a - b\n\n\ndef multiply(a, b):\n    return a * b\n' > calc/ops.py
printf 'import unittest\n\nfrom calc.ops import add, multiply, subtract\n\n\nclass OpsTest(unittest.TestCase):\n    def test_add(self):\n        self.assertEqual(add(2, 3), 5)\n\n    def test_subtract(self):\n        self.assertEqual(subtract(5, 3), 2)\n\n    def test_multiply(self):\n        self.assertEqual(multiply(2, 3), 6)\n' > tests/test_ops.py
