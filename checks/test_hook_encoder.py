"""Proves the hand-written awk JSON encoder in hooks/load-rules-subagent.sh.

The encoder must round-trip any rule text byte for byte, since a mis-escaped
rule would reach a sub-agent garbled or not at all.
"""

import json
import os
import random
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, "hooks", "load-rules-subagent.sh")
LOAD_RULES = os.path.join(ROOT, "hooks", "load-rules.sh")

# NUL is left out: it cannot cross a shell pipeline as text and never appears in a rule.
CONTROLS = [chr(c) for c in range(0x01, 0x20)]


class HookEncoderTest(unittest.TestCase):
    """The encoder round-trips hard inputs and wraps the real rules for SubagentStart."""

    def fail_check(self, part, why, text=None):
        where = "" if text is None else "\n  input: %r" % text
        self.fail("hook encoder: %s failed: %s%s" % (part, why, where))

    def hook_json(self, part, args, stdin=None, text=None):
        run = subprocess.run(args, input=stdin, capture_output=True)
        if run.returncode != 0:
            why = run.stderr.decode("utf-8", "replace").strip()
            self.fail_check(part, "hook exited %d: %s" % (run.returncode, why), text)
        try:
            return json.loads(run.stdout.decode("utf-8"))["hookSpecificOutput"]
        except (ValueError, KeyError, TypeError) as err:
            self.fail_check(part, "output is not the hook JSON (%s): %r" % (err, run.stdout), text)

    def roundtrip(self, part, text):
        want = text.encode("utf-8")
        got = self.hook_json(part, [HOOK, "-"], want, text).get("additionalContext")
        if not isinstance(got, str) or got.encode("utf-8") != want:
            self.fail_check(part, "decoded text differs: %r" % got, text)

    def test_fixed_table(self):
        """The known-hard inputs round-trip."""
        fixed = ["", "\"", "\\", "\\\"", "é", "no trailing newline", "one\r\ntwo\r\n"]
        fixed += CONTROLS + ["line " + c + " end\n" for c in CONTROLS]
        for text in fixed:
            self.roundtrip("fixed table", text)

    def test_seeded_fuzz(self):
        """500 strings of 0 to 2,000 characters, weighted to the hard characters, round-trip."""
        pool = list("The quick brown fox 0123456789 .,;:!?-_/()[]{}")
        pool += list("\"\\\n\r") * 8 + CONTROLS * 2 + [chr(0x7f)]
        pool += list("éßñ日本語€🙂") * 2
        rng = random.Random(1)
        for _ in range(500):
            self.roundtrip("fuzz", "".join(rng.choices(pool, k=rng.randint(0, 2000))))

    def test_real_run(self):
        """With no argument the hook wraps the load-rules.sh output for SubagentStart."""
        rules = subprocess.run([LOAD_RULES], capture_output=True, check=True).stdout
        real = self.hook_json("real run", [HOOK])
        if real.get("hookEventName") != "SubagentStart":
            self.fail_check("real run", "hookEventName is %r, not SubagentStart" % real.get("hookEventName"))
        got = real.get("additionalContext")
        if not isinstance(got, str) or got.encode("utf-8") != rules:
            self.fail_check("real run", "additionalContext is not the load-rules.sh output")


if __name__ == "__main__":
    unittest.main()
