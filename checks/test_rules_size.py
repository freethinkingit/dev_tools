"""The rules fit both hooks: past 10,000 characters Claude Code replaces a hook's
output with a file path and a 2,000-character preview, so rules past that point
would not be seen.

The output of hooks/load-rules.sh and the decoded additionalContext of
hooks/load-rules-subagent.sh each stay under 10,000 characters, and each rule
named in RULE_LIMITS stays at or under its own limit, all counted as decoded
UTF-8 characters.
"""

import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "ponderly")
LOAD_RULES = os.path.join(PLUGIN, "hooks", "load-rules.sh")
LOAD_RULES_SUBAGENT = os.path.join(PLUGIN, "hooks", "load-rules-subagent.sh")
RULES = os.path.join(PLUGIN, "rules")

HOOK_LIMIT = 10000
RULE_LIMITS = {
    "collaboration": 1600,
    "communication": 1600,
    "tests": 1000,
    "code-changes": 2450,
    "comments": 1450,
}


class RulesSizeTest(unittest.TestCase):
    """The output of both hooks and each limited rule stay within their character limits."""

    def test_hook_output_is_under_the_limit(self):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=PLUGIN)
        run = subprocess.run([LOAD_RULES], env=env, capture_output=True, check=True)
        count = len(run.stdout.decode("utf-8"))
        self.assertLess(
            count, HOOK_LIMIT, "load-rules.sh prints %d characters; the limit is %d" % (count, HOOK_LIMIT)
        )

    def test_subagent_context_is_under_the_limit(self):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=PLUGIN)
        run = subprocess.run([LOAD_RULES_SUBAGENT], env=env, capture_output=True, check=True)
        context = json.loads(run.stdout.decode("utf-8"))["hookSpecificOutput"]["additionalContext"]
        count = len(context)
        self.assertLess(
            count,
            HOOK_LIMIT,
            "load-rules-subagent.sh gives %d characters of additionalContext; the limit is %d" % (count, HOOK_LIMIT),
        )

    def test_each_rule_is_within_its_limit(self):
        for name, limit in RULE_LIMITS.items():
            with self.subTest(rule=name):
                with open(os.path.join(RULES, name + ".md"), encoding="utf-8") as f:
                    count = len(f.read())
                self.assertLessEqual(
                    count, limit, "rules/%s.md has %d characters; the limit is %d" % (name, count, limit)
                )


if __name__ == "__main__":
    unittest.main()
