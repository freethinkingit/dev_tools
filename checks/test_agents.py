"""Agent frontmatter is well formed and every ponderly:<name> the skills reference exists."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "ponderly"
AGENTS_DIR = PLUGIN / "agents"
SKILLS_DIR = PLUGIN / "skills"

# The allowlist of tool names the handbook's agents may declare; extend it here when an agent needs another.
KNOWN_TOOLS = {
    "Read",
    "Glob",
    "Grep",
    "Edit",
    "Write",
    "Bash",
    "Agent",
    "WebFetch",
    "WebSearch",
    "NotebookEdit",
    "TodoWrite",
    "Skill",
    "AskUserQuestion",
    "LSP",
}
MODEL_ALIASES = {"sonnet", "opus", "haiku", "fable", "inherit"}
EFFORTS = {"low", "medium", "high", "xhigh", "max"}

HANDBOOK_REFERENCE = re.compile(r"ponderly:([a-z0-9]+(?:-[a-z0-9]+)*)")


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


class AgentFrontmatterTest(unittest.TestCase):
    def test_agents_exist(self):
        self.assertTrue(sorted(AGENTS_DIR.glob("*.md")), "no agents/*.md found")

    def test_each_agent_frontmatter(self):
        for path in sorted(AGENTS_DIR.glob("*.md")):
            with self.subTest(agent=path.name):
                fields = read_frontmatter(path)
                self.assertIsNotNone(fields, "no frontmatter block between --- fences")
                self.assertEqual(fields.get("name"), path.stem)
                self.assertTrue(fields.get("description"), "description is empty or missing")

                if "tools" in fields:
                    tools = [tool.strip() for tool in fields["tools"].split(",") if tool.strip()]
                    self.assertTrue(tools, "tools is present but empty")
                    self.assertLessEqual(set(tools), KNOWN_TOOLS, "unknown tool names")

                model = fields.get("model", "")
                self.assertTrue(
                    model in MODEL_ALIASES or model.startswith("claude-"),
                    "model {!r} is not an alias or a claude- model id".format(model),
                )
                self.assertIn(fields.get("effort"), EFFORTS)


class HandbookReferenceTest(unittest.TestCase):
    def test_every_reference_names_an_agent_or_skill(self):
        for path in sorted(SKILLS_DIR.rglob("*.md")):
            for name in sorted(set(HANDBOOK_REFERENCE.findall(path.read_text(encoding="utf-8")))):
                with self.subTest(file=str(path.relative_to(ROOT)), reference=name):
                    self.assertTrue(
                        (AGENTS_DIR / (name + ".md")).is_file()
                        or (SKILLS_DIR / name / "SKILL.md").is_file(),
                        "ponderly:{} names no agents/{}.md and no skills/{}/SKILL.md".format(name, name, name),
                    )


if __name__ == "__main__":
    unittest.main()
