# Tests

How tests are written in any repository this handbook applies to.

- **One test per path.** One per code path, corner case or gotcha.
- **One input per test.** No loop, `subTest` or `parametrize`; only a seeded property test a spec names may loop.
- **Test the boundaries.** Zero, one, the limit, one past it, empty, NaN and negative; no exhaustive tables.
- **Test behaviour, not values.** No test restates an internal constant, checks its own input or a library, or asserts a parameter nothing relies on.
- **Pin contracts.** A value others rely on is a literal, not its constant, and the test's name says who relies on it.
- **Parsers get awkward input.** Joined emoji, non-Latin script, a long string, whitespace only, zero-width and control characters and a byte-order mark get their contract's outcome; none throws.
- **The name is a promise.** A test's name is a behaviour sentence it fully asserts.
- **Fake at the boundary.** Small shared in-memory fakes enforce the real contract.
