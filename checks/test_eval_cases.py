"""Every eval case is reachable by its make target, has graders the harness can score, and runs the scaffold it carries. An llm grader needs no field: its prompt is the body after the closing fence."""

import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"

KNOWN_TYPES = {
    "regex": ["pattern"],
    "tool_used": ["tool"],
    "file_exists": ["path", "exists"],
    "llm": [],
}

FENCE = "---"
SCAFFOLD_SCRIPT = re.compile(r"^\s*scaffold_script:\s*(?P<name>[^\s#]+)\s*(?:#.*)?$", re.MULTILINE)
TAGS = re.compile(r"^tags:(?P<value>.*)$")


def cases():
    """Yield ``(case_dir, component)`` for every ``prompt.md`` under ``evals/``.

    ``evals/<kind>/<name>/<case>/`` names component ``name``; ``evals/hook/<case>/`` names ``hook``.
    A ``prompt.md`` under neither names component ``None``.
    """
    for prompt in sorted(EVALS_DIR.glob("**/prompt.md")):
        case_dir = prompt.parent
        parts = case_dir.relative_to(EVALS_DIR).parts
        if parts[:1] == ("hook",):
            yield case_dir, "hook"
        else:
            yield case_dir, parts[1] if len(parts) >= 2 else None


def fenced(path):
    """Return ``(lines, body)``: the lines between the first two ``---`` lines of ``path`` and the text after them.

    Raises ``ValueError`` naming the file when either fence is missing.
    """
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != FENCE:
        raise ValueError("{}: no opening --- fence".format(path.name))
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == FENCE)
    except StopIteration:
        raise ValueError("{}: no closing --- fence".format(path.name)) from None
    return lines[1:end], "\n".join(lines[end + 1 :])


def frontmatter(path):
    """Return ``(fields, body)`` from the ``key: value`` lines between the first two ``---`` lines of ``path``.

    Values are kept as raw strings, an inline map such as ``target: { ... }`` included.
    Raises ``ValueError`` naming the file when the fences are missing or a line is not ``key: value``.
    """
    lines, body = fenced(path)
    fields = {}
    for line in lines:
        if not line.strip():
            continue
        key, sep, value = line.partition(":")
        if not sep or not key.strip() or " " in key.strip():
            raise ValueError("{}: not a key: value line: {!r}".format(path.name, line))
        fields[key.strip()] = value.strip()
    return fields, body


def unquote(value):
    """Return ``value`` stripped, without one matching pair of surrounding single or double quotes."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def tags(value):
    """Return the entries of a ``[a, b]`` frontmatter list."""
    return [unquote(tag) for tag in value.strip().strip("[]").split(",") if tag.strip()]


def prompt_tags(path):
    """Return the ``tags`` in the frontmatter of ``path``, an inline ``[a, b]`` or one ``- a`` per line.

    Returns an empty list when there is no ``tags:`` line. Raises ``ValueError`` when a fence is missing.
    """
    lines, _ = fenced(path)
    for i, line in enumerate(lines):
        match = TAGS.match(line)
        if match is None:
            continue
        if match.group("value").strip():
            return tags(match.group("value"))
        items = []
        for item in lines[i + 1 :]:
            if not item.strip().startswith("-"):
                break
            items.append(unquote(item.strip()[1:]))
        return items
    return []


def relative(path):
    return path.relative_to(ROOT)


class EvalCasesTest(unittest.TestCase):
    """The eval cases under evals/ are tagged, gradable and scaffolded as the harness expects."""

    def assertNoProblems(self, problems):
        if problems:
            self.fail("\n".join(problems))

    def test_there_are_cases(self):
        self.assertTrue(list(cases()), "no eval cases found")

    def test_every_case_is_tagged_with_its_component(self):
        problems = []
        for case_dir, component in cases():
            if component is None:
                problems.append(
                    "{}: not under evals/<kind>/<name>/ or evals/hook/".format(relative(case_dir / "prompt.md"))
                )
                continue
            try:
                found = prompt_tags(case_dir / "prompt.md")
            except ValueError as error:
                problems.append("{}/{}".format(relative(case_dir), error))
                continue
            if component not in found:
                problems.append("{}: expected tag {}".format(relative(case_dir), component))
        self.assertNoProblems(problems)

    def test_every_case_has_valid_graders(self):
        problems = []
        for case_dir, _ in cases():
            graders_dir = case_dir / "graders"
            graders = sorted(p for p in graders_dir.glob("*.md") if p.is_file()) if graders_dir.is_dir() else []
            if not graders:
                problems.append("{}: no graders".format(relative(case_dir)))
            for grader in graders:
                try:
                    fields, body = frontmatter(grader)
                except ValueError as error:
                    problems.append("{}/{}".format(relative(grader.parent), error))
                    continue
                kind = unquote(fields["type"]) if "type" in fields else None
                if kind is None:
                    problems.append("{}: no type".format(relative(grader)))
                elif kind not in KNOWN_TYPES:
                    problems.append(
                        "{}: unknown type {}; add it to KNOWN_TYPES with its required fields".format(
                            relative(grader), kind
                        )
                    )
                else:
                    for field in KNOWN_TYPES[kind]:
                        if not fields.get(field):
                            problems.append("{}: {} grader has no {}".format(relative(grader), kind, field))
                    if kind == "llm" and not body.strip():
                        problems.append("{}: llm grader has an empty body".format(relative(grader)))
        self.assertNoProblems(problems)

    def test_scaffolds_are_wired_and_executable(self):
        problems = []
        for case_dir, _ in cases():
            case_yaml = case_dir / "case.yaml"
            named = None
            if case_yaml.is_file():
                match = SCAFFOLD_SCRIPT.search(case_yaml.read_text(encoding="utf-8"))
                if match is not None:
                    named = unquote(match.group("name"))
            if named is not None:
                script = case_dir / named
                if not (script.exists() or script.is_symlink()):
                    problems.append("{}: scaffold {} does not exist".format(relative(case_dir), named))
                elif script.is_symlink():
                    problems.append("{}: scaffold {} is a symlink".format(relative(case_dir), named))
                elif not script.is_file():
                    problems.append("{}: scaffold {} is not a regular file".format(relative(case_dir), named))
                elif not os.access(script, os.X_OK):
                    problems.append("{}: scaffold {} is not executable".format(relative(case_dir), named))
            scaffold = case_dir / "scaffold.sh"
            if (scaffold.exists() or scaffold.is_symlink()) and (
                named is None or (case_dir / named).resolve() != scaffold.resolve()
            ):
                problems.append("{}: scaffold.sh is not named by case.yaml".format(relative(case_dir)))
        self.assertNoProblems(problems)


if __name__ == "__main__":
    unittest.main()
