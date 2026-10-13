"""The rules fit the SessionStart hook: Claude Code truncates hook output past 10,000 characters.

The output of hooks/load-rules.sh stays under 10,000 characters and
rules/collaboration.md under 1,600, both counted as decoded UTF-8 characters.
"""

import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOAD_RULES = os.path.join(ROOT, "hooks", "load-rules.sh")
COLLABORATION = os.path.join(ROOT, "rules", "collaboration.md")

HOOK_LIMIT = 10000
COLLABORATION_LIMIT = 1600


class RulesSizeTest(unittest.TestCase):
    """The hook output and the collaboration rule stay under their character limits."""

    def test_hook_output_is_under_the_limit(self):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=ROOT)
        run = subprocess.run([LOAD_RULES], env=env, capture_output=True, check=True)
        count = len(run.stdout.decode("utf-8"))
        self.assertLess(
            count, HOOK_LIMIT, "load-rules.sh prints %d characters; the limit is %d" % (count, HOOK_LIMIT)
        )

    def test_collaboration_rule_is_under_the_limit(self):
        with open(COLLABORATION, encoding="utf-8") as f:
            count = len(f.read())
        self.assertLess(
            count,
            COLLABORATION_LIMIT,
            "rules/collaboration.md has %d characters; the limit is %d" % (count, COLLABORATION_LIMIT),
        )


if __name__ == "__main__":
    unittest.main()
