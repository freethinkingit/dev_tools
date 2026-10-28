"""The report skill stays cheap to invoke: its text loads into the session each time it runs.

skills/report/templates/ holds exactly one Template per mode and nothing else.
skills/report/SKILL.md, frontmatter included, stays under 4,000 characters and
each Template under 3,000, both counted as decoded UTF-8 characters.
"""

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "ponderly"
REPORT_DIR = PLUGIN / "skills" / "report"
SKILL = REPORT_DIR / "SKILL.md"
TEMPLATES_DIR = REPORT_DIR / "templates"

MODES = ("handback", "decision", "status", "answer")
SKILL_LIMIT = 4000
TEMPLATE_LIMIT = 3000


class ReportSkillTest(unittest.TestCase):
    """The Templates match the modes, and the skill and its Templates stay under their character limits."""

    def test_templates_are_named_after_the_modes(self):
        expected = sorted(mode + ".md" for mode in MODES)
        found = (
            sorted(path.name for path in TEMPLATES_DIR.iterdir() if not path.name.startswith("."))
            if TEMPLATES_DIR.is_dir()
            else []
        )
        self.assertEqual(found, expected, "skills/report/templates/ holds %s; expected %s" % (found, expected))

    def test_skill_is_under_the_limit(self):
        self.assertTrue(SKILL.is_file(), "skills/report/SKILL.md is missing")
        count = len(SKILL.read_text(encoding="utf-8"))
        self.assertLess(
            count, SKILL_LIMIT, "skills/report/SKILL.md has %d characters; the limit is %d" % (count, SKILL_LIMIT)
        )

    def test_each_template_is_under_the_limit(self):
        for mode in MODES:
            path = TEMPLATES_DIR / (mode + ".md")
            with self.subTest(file=str(path.relative_to(ROOT))):
                self.assertTrue(path.is_file(), "%s is missing" % path.relative_to(ROOT))
                count = len(path.read_text(encoding="utf-8"))
                self.assertLess(
                    count,
                    TEMPLATE_LIMIT,
                    "%s has %d characters; the limit is %d" % (path.relative_to(ROOT), count, TEMPLATE_LIMIT),
                )


if __name__ == "__main__":
    unittest.main()
