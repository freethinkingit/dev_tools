"""Every skill's frontmatter name matches the name of the folder that holds its SKILL.md.

A skill copied from another and left with the old name loads under that name,
and the validator does not compare the two.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "plugins" / "ponderly" / "skills"


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


class SkillNameTest(unittest.TestCase):
    def test_each_skill_name_matches_its_folder(self):
        paths = sorted(SKILLS_DIR.glob("*/SKILL.md"))
        self.assertTrue(paths, "no skills/*/SKILL.md found")
        for path in paths:
            with self.subTest(file=str(path.relative_to(ROOT))):
                fields = read_frontmatter(path)
                self.assertIsNotNone(fields, "no frontmatter block between --- fences")
                found = fields.get("name")
                expected = path.parent.name
                self.assertEqual(
                    found,
                    expected,
                    "{} has name {!r}; expected {!r}, the folder's name".format(
                        path.relative_to(ROOT), found, expected
                    ),
                )


if __name__ == "__main__":
    unittest.main()
