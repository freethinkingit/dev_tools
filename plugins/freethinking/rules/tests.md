# Tests

How tests are written in any repository this handbook applies to.

- **One test per path.** Write one for each code path, corner case or gotcha.
- **One input per test.** No loop, `subTest` or `parametrize`; only a seeded property test a spec names may loop.
- **Test the boundaries.** Use zero, one, the limit, the limit plus one, empty, NaN and negative, not exhaustive tables or cross products.
- **Test behaviour, not values.** No test restates an implementation constant, checks its own input or checks a library.
- **Parsers get awkward input.** Feed joined emoji, non-Latin scripts, a very long string, whitespace only, zero-width and control characters and a byte-order mark. Each gets the outcome the input's contract defines, accepted or refused with a clear error, and none throws.
- **The name is a promise.** A test's name is a behaviour sentence the test fully asserts.
- **Fake at the boundary.** Small in-memory fakes, shared in one place, enforce the real contract.
