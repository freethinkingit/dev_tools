"""Proves the hand-written awk JSON encoder in hooks/load-rules-subagent.sh.

For any rules folder holding at least one .md file, the subagent hook's
additionalContext, JSON-decoded, must be the exact bytes load-rules.sh prints
for the same folder, since a mis-escaped rule would reach a sub-agent garbled
or not at all. With no rules folder the session hook prints nothing, and with
an empty one only the header; in both cases the subagent hook fails loudly.
"""

import json
import os
import random
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN = os.path.join(ROOT, "plugins", "ponderly")
HOOK = os.path.join(PLUGIN, "hooks", "load-rules-subagent.sh")
LOAD_RULES = os.path.join(PLUGIN, "hooks", "load-rules.sh")

HEADER = (
    b"# Handbook rules\n\n"
    b"Team rules that apply in every repository. They are shipped by the handbook plugin;"
    b" to change one, open a PR against the rules/ folder of the handbook repository.\n\n"
)

# NUL is left out: awk cannot carry it as text and it never appears in a rule.
CONTROLS = [chr(c) for c in range(0x01, 0x20)]


def run_hook(script, folder):
    env = dict(os.environ)
    if folder is None:
        env.pop("CLAUDE_PLUGIN_ROOT", None)
    else:
        env["CLAUDE_PLUGIN_ROOT"] = folder
    return subprocess.run([script], capture_output=True, env=env)


class HookEncoderTest(unittest.TestCase):
    """Both hooks agree on hard inputs and on the real rules, and handle a missing rules folder."""

    def fail_check(self, part, why, text=None):
        where = "" if text is None else "\n  input: %r" % text
        self.fail("hook encoder: %s failed: %s%s" % (part, why, where))

    def session_output(self, part, folder, text=None):
        run = run_hook(LOAD_RULES, folder)
        if run.returncode != 0:
            why = run.stderr.decode("utf-8", "replace").strip()
            self.fail_check(part, "load-rules.sh exited %d: %s" % (run.returncode, why), text)
        return run.stdout

    def hook_json(self, part, folder, text=None):
        run = run_hook(HOOK, folder)
        if run.returncode != 0:
            why = run.stderr.decode("utf-8", "replace").strip()
            self.fail_check(part, "hook exited %d: %s" % (run.returncode, why), text)
        try:
            out = json.loads(run.stdout.decode("utf-8"))["hookSpecificOutput"]
        except (ValueError, KeyError, TypeError) as err:
            self.fail_check(part, "output is not the hook JSON (%s): %r" % (err, run.stdout), text)
        if out.get("hookEventName") != "SubagentStart":
            self.fail_check(part, "hookEventName is %r, not SubagentStart" % out.get("hookEventName"), text)
        return out

    def compare(self, part, folder, text=None):
        """Fails unless the decoded additionalContext is the session output byte for byte; returns both."""
        want = self.session_output(part, folder, text)
        got = self.hook_json(part, folder, text).get("additionalContext")
        if not isinstance(got, str) or got.encode("utf-8") != want:
            self.fail_check(part, "decoded additionalContext %r is not the load-rules.sh output %r" % (got, want), text)
        return want, got

    def roundtrip(self, part, text):
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, "rules"))
            with open(os.path.join(folder, "rules", "a.md"), "wb") as f:
                f.write(text.encode("utf-8"))
            want, got = self.compare(part, folder, text)
        if text not in got:
            self.fail_check(part, "decoded additionalContext does not contain the input", text)
        return want

    def roundtrip_batch(self, part, texts):
        """Writes each text as its own rule file, in name order, and checks the folder as one run."""
        with tempfile.TemporaryDirectory() as folder:
            os.makedirs(os.path.join(folder, "rules"))
            for i, text in enumerate(texts):
                with open(os.path.join(folder, "rules", "f%02d.md" % i), "wb") as f:
                    f.write(text.encode("utf-8"))
            _, got = self.compare(part, folder, texts)
        for text in texts:
            if text.endswith("\n") and text not in got:
                self.fail_check(part, "decoded additionalContext does not contain one of the inputs", text)

    def test_fixed_table(self):
        """The known-hard inputs give the same text from both hooks."""
        fixed = ["", "\"", "\\", "\\\"", "é", "no trailing newline", "one\r\ntwo\r\n"]
        fixed += ["first line\nlast line without a newline"]
        fixed += CONTROLS + ["line " + c + " end\n" for c in CONTROLS]
        for text in fixed:
            self.roundtrip("fixed table", text)
        framed = self.roundtrip("fixed table", "rule text\nno newline at end")
        if framed != HEADER + b"rule text\nno newline at end\n\n":
            self.fail_check("fixed table", "load-rules.sh output is not the header, the file, then a blank line: %r" % framed)

    def test_seeded_fuzz(self):
        """500 strings of 0 to 2,000 characters, weighted to the hard characters, give the same text from both hooks.

        The strings are written 20 to a rules folder, so the run stays short and
        the blank line between files is checked on fuzz data too.
        """
        pool = list("The quick brown fox 0123456789 .,;:!?-_/()[]{}")
        pool += list("\"\\\n\r") * 8 + CONTROLS * 2 + [chr(0x7f)]
        pool += list("éßñ日本語€🙂") * 2
        rng = random.Random(1)
        texts = ["".join(rng.choices(pool, k=rng.randint(0, 2000))) for _ in range(500)]
        for start in range(0, len(texts), 20):
            self.roundtrip_batch("fuzz", texts[start:start + 20])

    def test_real_run(self):
        """On the plugin folder both hooks give the same rules text."""
        want, _ = self.compare("real run", PLUGIN)
        if not want.startswith(HEADER) or len(want) <= len(HEADER) + 1:
            self.fail_check("real run", "load-rules.sh printed no rules after the header")

    def test_no_rules(self):
        """With CLAUDE_PLUGIN_ROOT unset or without rules/, the session hook prints nothing and the subagent hook fails with one line."""
        with tempfile.TemporaryDirectory() as empty:
            for case, folder in (("unset", None), ("no rules/", empty)):
                part = "no rules (%s)" % case
                session = run_hook(LOAD_RULES, folder)
                if session.returncode != 0 or session.stdout:
                    self.fail_check(part, "load-rules.sh exited %d with output %r" % (session.returncode, session.stdout))
                sub = run_hook(HOOK, folder)
                lines = sub.stderr.decode("utf-8", "replace").splitlines()
                if sub.returncode == 0 or sub.stdout or len(lines) != 1:
                    self.fail_check(part, "hook exited %d, stdout %r, stderr %r" % (sub.returncode, sub.stdout, sub.stderr))


if __name__ == "__main__":
    unittest.main()
