# finds-planted-defects

Tests that the review finds two defects planted in an uncommitted change: one
for the security lens and one for the correctness lens, each on a line the
graders name.

## What the scaffold builds

The `shop` fixture, built by `evals/fixtures/setup.sh shop shop-search`, which
commits the fixture on main and checks out branch `shop-search`. The scaffold
must copy this case's `files/` in after that call, as
`evals/skills/readable-code/*/scaffold.sh` does, and not before it: a `files/`
overlay present before `setup.sh` runs is committed on main with the fixture,
which leaves the branch with no diff. Unlike the readable-code scaffold, it
commits nothing after the copy, so the planted change is an uncommitted diff
against main.

`files/shop/handlers.py` replaces the fixture's handlers with one that adds
`search_products`, carrying the two planted defects:

- line 14: the SQL is built by concatenating `term` into the string
  (security: SQL injection).
- line 16: the page slices `offset + size + 1` items, one more than the page
  size (correctness: off-by-one).

These line numbers live here, outside the fixture tree, because `setup.sh`
copies the whole fixture into the reviewed workspace: an answer key there
would let the review read the defects instead of finding them.
