"""The component dropdown of every issue form lists exactly the skills, agents, rules and hooks on disk, in the same order."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "freethinking"
FORMS_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"
CATCH_ALL = "Something else"

COMPONENT_BLOCK = re.compile(r"^\s*id: component\n(?P<body>(?:^ {4,}.*\n?)+)", re.MULTILINE)
OPTION = re.compile(r"^ {8}- (?P<option>.+?)\s*$", re.MULTILINE)


def component_options(path):
    """Return the ``options`` of the dropdown whose id is ``component``, or None if the form has none."""
    match = COMPONENT_BLOCK.search(path.read_text(encoding="utf-8"))
    if match is None:
        return None
    return OPTION.findall(match.group("body"))


def components_on_disk():
    """Return the dropdown entries the repository's components call for, catch-all excluded."""
    skills = ["{} (skill)".format(p.parent.name) for p in sorted((PLUGIN / "skills").glob("*/SKILL.md"))]
    agents = ["{} (agent)".format(p.stem) for p in sorted((PLUGIN / "agents").glob("*.md"))]
    rules = ["{} (rule)".format(p.stem) for p in sorted((PLUGIN / "rules").glob("*.md"))]
    events = json.loads((PLUGIN / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
    hooks = ["{} hook".format(event) for event in sorted(events)]
    return set(skills + agents + rules + hooks)


class IssueFormComponentTest(unittest.TestCase):
    def forms(self):
        forms = sorted(p for p in FORMS_DIR.glob("*.yml") if p.name != "config.yml")
        self.assertTrue(forms, "no issue forms under .github/ISSUE_TEMPLATE/")
        return forms

    def test_every_form_has_a_component_dropdown_ending_in_the_catch_all(self):
        for path in self.forms():
            with self.subTest(form=path.name):
                options = component_options(path)
                self.assertIsNotNone(options, "no dropdown with id: component")
                self.assertTrue(options, "component dropdown has no options")
                self.assertEqual(options[-1], CATCH_ALL, "last option is not the catch-all")
                self.assertEqual(len(options), len(set(options)), "duplicate options")

    def test_component_options_match_the_components_on_disk(self):
        expected = components_on_disk()
        for path in self.forms():
            with self.subTest(form=path.name):
                listed = set(component_options(path) or []) - {CATCH_ALL}
                self.assertEqual(
                    sorted(listed - expected), [], "options that name no skill, agent, rule or hook on disk"
                )
                self.assertEqual(sorted(expected - listed), [], "components on disk missing from the dropdown")

    def test_forms_list_components_in_the_same_order(self):
        forms = self.forms()
        reference = component_options(forms[0])
        for path in forms[1:]:
            with self.subTest(form=path.name, reference=forms[0].name):
                self.assertEqual(component_options(path), reference)


if __name__ == "__main__":
    unittest.main()
