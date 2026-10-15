"""Every skill's and agent's frontmatter description is present and at most 1,024 characters.

Claude Code rejects a skill description over 1,024 characters, and the validator
gives no warning on the way there. Agent descriptions have no documented limit
but load into every session's context, so they are held to the same ceiling.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
SKILLS_DIR = ROOT / "skills"

DESCRIPTION_LIMIT = 1024


def read_frontmatter(path):
    """Return the flat ``key: value`` pairs between the leading ``---`` fences, or None if there is no block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return fields
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return None


class DescriptionLengthTest(unittest.TestCase):
    def test_descriptions_are_present_and_within_the_limit(self):
        paths = sorted(SKILLS_DIR.glob("*/SKILL.md")) + sorted(AGENTS_DIR.glob("*.md"))
        self.assertTrue(paths, "no skills/*/SKILL.md or agents/*.md found")
        for path in paths:
            with self.subTest(file=str(path.relative_to(ROOT))):
                fields = read_frontmatter(path)
                self.assertIsNotNone(fields, "no frontmatter block between --- fences")
                description = fields.get("description", "")
                self.assertTrue(description, "description is empty or missing")
                self.assertLessEqual(
                    len(description),
                    DESCRIPTION_LIMIT,
                    "description has {} characters; the limit is {}".format(len(description), DESCRIPTION_LIMIT),
                )


if __name__ == "__main__":
    unittest.main()
