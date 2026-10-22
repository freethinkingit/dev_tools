"""Every frontmatter block in the eval cases, graders, skills and agents parses as YAML.

The eval harness skips a case whose frontmatter a YAML parser rejects, with only
"invalid YAML frontmatter" to show for it, and Claude Code does the same to a
skill or agent. There is no YAML parser in the standard library, so this checks
the subset these files use: ``key: value`` lines whose values are plain, single-
or double-quoted scalars, flow lists and flow maps, block scalars, ``- item``
lists and indented nested mappings.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FENCE = "---"
KEY = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?:\s+(?P<value>.*)|\s*)$")
BLOCK_INDICATOR = re.compile(r"^[|>][+-]?[1-9]?[+-]?(?:\s+#.*)?$")
RESERVED_START = "`@"
NODE_PROPERTY_START = "&*!%"
FLOW_CLOSERS = {"[": "]", "{": "}"}
DOUBLE_QUOTED_ESCAPE = re.compile(r'\\(?:[0abt\tnvfre "/\\N_LP]|x[0-9A-Fa-f]{2}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8}|$)')


def frontmatter_files():
    """Return every file in scope: eval prompts and graders, skills and agents, sorted within each kind."""
    plugin = ROOT / "plugins" / "freethinking"
    return (
        sorted(ROOT.glob("evals/**/prompt.md"))
        + sorted(ROOT.glob("evals/**/graders/*.md"))
        + sorted(plugin.glob("skills/*/SKILL.md"))
        + sorted(plugin.glob("agents/*.md"))
    )


class FrontmatterError(ValueError):
    """A frontmatter line a YAML parser would reject; ``line`` is its 1-based number in the file."""

    def __init__(self, line, reason):
        super().__init__(reason)
        self.line = line
        self.reason = reason


def frontmatter_lines(path):
    """Return ``[(line_number, text)]`` for the lines between the first two ``---`` fences of ``path``.

    Raises ``FrontmatterError`` when either fence is missing.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != FENCE:
        raise FrontmatterError(1, "no opening --- fence")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == FENCE:
            return [(number, text) for number, text in enumerate(lines[1:index], start=2)]
    raise FrontmatterError(len(lines), "no closing --- fence")


def single_quoted_end(text, start):
    """Return the index just past the single-quoted scalar opening at ``start``, or None if it does not close."""
    i = start + 1
    while i < len(text):
        if text[i] == "'":
            if text[i + 1 : i + 2] == "'":
                i += 2
                continue
            return i + 1
        i += 1
    return None


def double_quoted_end(text, start):
    """Return the index just past the double-quoted scalar opening at ``start``, or None if it does not close.

    Raises ``ValueError`` on a backslash escape YAML does not define.
    """
    i = start + 1
    while i < len(text):
        if text[i] == "\\":
            escape = DOUBLE_QUOTED_ESCAPE.match(text, i)
            if escape is None:
                raise ValueError(
                    "double-quoted value holds {}, an escape YAML does not define; "
                    "use single quotes for a regex".format(text[i : i + 2])
                )
            i = escape.end()
            continue
        if text[i] == '"':
            return i + 1
        i += 1
    return None


def check_rest(rest, what):
    """Raise ``ValueError`` unless ``rest``, the text after a closed value, is empty or a `` #`` comment."""
    if rest.strip() and not re.match(r"^\s+#", rest):
        raise ValueError("text after the closing {}: {!r}".format(what, rest.strip()))


def check_quoted(value):
    """Raise ``ValueError`` unless ``value`` is one closed quoted scalar, optionally followed by a comment."""
    quote = value[0]
    end = single_quoted_end(value, 0) if quote == "'" else double_quoted_end(value, 0)
    if end is None:
        raise ValueError("unbalanced {} quote".format(quote))
    rest = value[end:]
    if quote == "'" and rest.strip() and not re.match(r"^\s+#", rest):
        raise ValueError("single-quoted value holds an unescaped ' (write it as '')")
    check_rest(rest, "quote")


def check_plain(value, flow=False):
    """Raise ``ValueError`` if ``value`` cannot be a plain scalar; inside a flow collection ``,[]{}`` end it."""
    if value[0] in RESERVED_START:
        raise ValueError("plain value starts with the reserved character {!r}; quote it".format(value[0]))
    if value[0] in NODE_PROPERTY_START:
        raise ValueError(
            "plain value starts with {!r}, which YAML reads as an anchor, alias, tag or directive; quote it".format(
                value[0]
            )
        )
    if value[0] in "]}," or (not flow and value[0] in "[{"):
        raise ValueError("plain value starts with {!r}; quote it".format(value[0]))
    if value.startswith("- ") or value == "-":
        raise ValueError("plain value starts with '- '; quote it")
    if ": " in value or value.endswith(":"):
        raise ValueError("plain value holds ': '; quote it")
    if " #" in value or "\t#" in value:
        raise ValueError("plain value holds ' #', which starts a comment; quote it")


def flow_scalar_end(text, i):
    """Return the index just past the flow-collection scalar starting at ``text[i]``."""
    if text[i] in "'\"":
        end = single_quoted_end(text, i) if text[i] == "'" else double_quoted_end(text, i)
        if end is None:
            raise ValueError("unbalanced {} quote".format(text[i]))
        return end
    j = i
    while j < len(text) and text[j] not in ",[]{}" and not text.startswith(": ", j) and not text.startswith(" #", j):
        j += 1
    if j == i:
        raise ValueError("empty entry in a flow collection")
    check_plain(text[i:j].strip(), flow=True)
    return j


def skip_space(text, i):
    while i < len(text) and text[i] in " \t":
        i += 1
    return i


def flow_end(text, start):
    """Return the index just past the ``[...]`` or ``{...}`` opening at ``text[start]``."""
    opener = text[start]
    closer = FLOW_CLOSERS[opener]
    kind = "flow list" if opener == "[" else "flow map"
    i = skip_space(text, start + 1)
    if text[i : i + 1] == closer:
        return i + 1
    while True:
        if i >= len(text):
            raise ValueError("{} {} does not close with {}".format(kind, opener, closer))
        i = flow_end(text, i) if text[i] in FLOW_CLOSERS else flow_scalar_end(text, i)
        i = skip_space(text, i)
        if opener == "{" or text.startswith(": ", i):
            if not text.startswith(":", i):
                raise ValueError("flow map entry has no ': '")
            i = skip_space(text, i + 1)
            if i >= len(text):
                raise ValueError("{} {} does not close with {}".format(kind, opener, closer))
            i = flow_end(text, i) if text[i] in FLOW_CLOSERS else flow_scalar_end(text, i)
            i = skip_space(text, i)
        if i >= len(text):
            raise ValueError("{} {} does not close with {}".format(kind, opener, closer))
        if text[i] == closer:
            return i + 1
        if text[i] != ",":
            raise ValueError("unexpected {!r} in a {}".format(text[i], kind))
        i = skip_space(text, i + 1)
        if text[i : i + 1] == closer:
            return i + 1


def check_value(value):
    """Raise ``ValueError`` unless ``value``, the text after ``key: `` or ``- ``, is one YAML scalar or flow collection."""
    value = value.rstrip()
    if not value or value.startswith("#"):
        return
    if value[0] in "'\"":
        check_quoted(value)
    elif value[0] in FLOW_CLOSERS:
        check_rest(value[flow_end(value, 0) :], "flow collection")
    else:
        check_plain(value)


def parse_line(content):
    """Return ``(kind, value)`` for a line stripped of its indent: kind ``"item"`` for ``- x``, ``"key"`` for ``key: x``.

    Raises ``ValueError`` when the line is neither.
    """
    if content == "-" or content.startswith("- "):
        return "item", content[1:].strip()
    match = KEY.match(content)
    if match is None:
        raise ValueError("not a key: value line, a block scalar line or a list item: {!r}".format(content))
    return "key", match.group("value") or ""


def place(levels, indent, kind, opens_under):
    """Fit a line at ``indent`` into ``levels``, the open ``(indent, kind)`` blocks, or raise ``ValueError``.

    ``opens_under`` is the indent of the key above when that key had no value, else None.
    """
    if opens_under is not None and (indent > opens_under or (indent == opens_under and kind == "item")):
        levels.append((indent, kind))
        return
    while levels[-1][0] > indent:
        levels.pop()
    if levels[-1][0] != indent:
        raise ValueError("indentation does not match the lines above")
    if levels[-1][1] != kind and kind == "key" and len(levels) > 1 and levels[-2] == (indent, "key"):
        levels.pop()
    if levels[-1][1] != kind:
        raise ValueError("list item and key: value mixed at the same indentation")


def check_frontmatter(numbered_lines):
    """Raise ``FrontmatterError`` at the first line of ``numbered_lines`` a YAML parser would reject."""
    levels = [(0, "key")]
    block_scalar_indent = None
    opens_under = None
    for number, line in numbered_lines:
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        if line[indent : indent + 1] == "\t":
            raise FrontmatterError(number, "indented with a tab; YAML allows only spaces")
        if block_scalar_indent is not None and indent > block_scalar_indent:
            continue
        block_scalar_indent = None
        content = line.strip()
        if content.startswith("#"):
            continue
        try:
            kind, value = parse_line(content)
            place(levels, indent, kind, opens_under)
            opens_under = None
            if kind == "item" and KEY.match(value.strip()):
                indent += len(content) - len(value.lstrip())
                kind, value = parse_line(value.strip())
                levels.append((indent, kind))
            value = value.strip()
            if BLOCK_INDICATOR.match(value):
                block_scalar_indent = indent
            elif kind == "key" and (not value or value.startswith("#")):
                opens_under = indent
            else:
                check_value(value)
        except ValueError as error:
            raise FrontmatterError(number, str(error)) from None


def problem(path):
    """Return ``"<file>:<line>: <reason>"`` for the first YAML fault in the frontmatter of ``path``, or None."""
    try:
        check_frontmatter(frontmatter_lines(path))
    except FrontmatterError as error:
        return "{}:{}: {}".format(path.relative_to(ROOT), error.line, error.reason)
    return None


class FrontmatterYamlTest(unittest.TestCase):
    """The frontmatter of every eval prompt and grader, skill and agent is YAML a parser accepts."""

    def test_there_are_files(self):
        self.assertTrue(frontmatter_files(), "no prompt.md, grader, SKILL.md or agent file found")

    def test_every_frontmatter_block_parses_as_yaml(self):
        for path in frontmatter_files():
            with self.subTest(file=str(path.relative_to(ROOT))):
                fault = problem(path)
                if fault is not None:
                    self.fail(fault)


if __name__ == "__main__":
    unittest.main()
