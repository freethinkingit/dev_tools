"""Proves benchmarks/reviewbench/agent/findings.py, the adapter's pure functions.

Seeded property tests cover the design's Properties 1 to 3; the example tests
cover each path and boundary of parse_review_json, validate and
build_findings_file. The head tree is faked by HEAD_TREE, a map of path to
line count, whose get method is the line_count_of validate is given.
"""

import importlib.util
import json
import os
import random
import string
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINDINGS_PATH = os.path.join(ROOT, "benchmarks", "reviewbench", "agent", "findings.py")

_spec = importlib.util.spec_from_file_location("reviewbench_findings", FINDINGS_PATH)
findings = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(findings)

ITERATIONS = 100
LIMIT = 40
SEVERITIES = ("high", "medium", "low")

HEAD_TREE = {
    "src/app.py": 120,
    "src/lib/util.py": 30,
    "README.md": 8,
    "one_line.txt": 1,
}

ENV = {
    "RB_NWO": "octo/shop",
    "RB_PR_NUMBER": "17",
    "RB_BASE": "a" * 40,
    "RB_HEAD": "b" * 40,
    "RB_AGENT": "ponderly",
}


def candidate(file="src/app.py", start_line=1, end_line=1, severity="high", message="x"):
    return {
        "file": file,
        "start_line": start_line,
        "end_line": end_line,
        "severity": severity,
        "category": "correctness",
        "message": message,
    }


def review_text(candidates):
    return json.dumps(
        {
            "pass": "final",
            "verdict": "holds",
            "second_pass": False,
            "counts": {},
            "findings": candidates,
        }
    )


def validate(candidates):
    return findings.validate(candidates, HEAD_TREE.get)


def through_the_adapter(message):
    """Return the message as it comes out of parse, validate and build."""
    candidates, _refused = findings.parse_review_json(review_text([candidate(message=message)]))
    kept, _dropped = validate(candidates)
    return findings.build_findings_file(kept, ENV, {})["findings"][0]["message"]


def random_text(rng, alphabet=string.ascii_letters + string.digits + "-_/.", most=20):
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(1, most)))


def random_spelling(rng, path):
    """Return path as the skill might write it, with ./, / or backslashes."""
    form = rng.choice(("plain", "dot_slash", "slash", "backslash"))
    if form == "dot_slash":
        return "./" + path
    if form == "slash":
        return "/" + path
    if form == "backslash":
        return path.replace("/", "\\")
    return path


def random_candidate(rng):
    """Return (candidate, is_valid): the generator knows whether it aimed inside the tree."""
    severity = rng.choice(SEVERITIES)
    if rng.random() < 0.2:
        return candidate(file="missing/" + random_text(rng), severity=severity), False
    path = rng.choice(sorted(HEAD_TREE))
    line_count = HEAD_TREE[path]
    if rng.random() < 0.25:
        start_line = rng.choice((0, -1, line_count + 1, line_count + rng.randint(1, 50)))
        end_line = max(start_line, 1)
        return (
            candidate(random_spelling(rng, path), start_line, end_line, severity),
            False,
        )
    start_line = rng.randint(1, line_count)
    end_line = rng.randint(start_line, line_count)
    return candidate(random_spelling(rng, path), start_line, end_line, severity), True


class EveryFindingIsAnchoredInTheHeadTree(unittest.TestCase):
    """Property 1: Every finding is anchored in the head tree."""

    def test_every_returned_finding_names_a_tree_file_and_lines_inside_it(self):
        rng = random.Random(0)
        for _ in range(ITERATIONS):
            candidates = [random_candidate(rng)[0] for _ in range(rng.randint(0, 60))]
            kept, _dropped = validate(candidates)
            for finding in kept:
                self.assertIn(finding["file"], HEAD_TREE)
                self.assertFalse(finding["file"].startswith("./"))
                self.assertFalse(finding["file"].startswith("/"))
                self.assertLessEqual(1, finding["start_line"])
                self.assertLessEqual(finding["start_line"], finding["end_line"])
                self.assertLessEqual(finding["end_line"], HEAD_TREE[finding["file"]])


class TheOutputIsBoundedAndOrdered(unittest.TestCase):
    """Property 2: The output is bounded and ordered."""

    def test_at_most_forty_in_severity_order_with_the_lowest_dropped_first(self):
        rng = random.Random(0)
        for _ in range(ITERATIONS):
            generated = [random_candidate(rng) for _ in range(rng.randint(0, 90))]
            candidates = [item for item, _is_valid in generated]
            valid = [item for item, is_valid in generated if is_valid]
            kept, _dropped = validate(candidates)
            ranks = [SEVERITIES.index(finding["severity"]) for finding in kept]
            self.assertLessEqual(len(kept), LIMIT)
            self.assertEqual(ranks, sorted(ranks))
            if len(valid) > LIMIT:
                self.assertEqual(len(kept), LIMIT)
                lowest_kept = max(ranks)
                for severity in SEVERITIES[:lowest_kept]:
                    valid_of_severity = [item for item in valid if item["severity"] == severity]
                    kept_of_severity = [item for item in kept if item["severity"] == severity]
                    self.assertEqual(len(kept_of_severity), len(valid_of_severity))


class TheFindingsFileEchoesTheContractsIdentity(unittest.TestCase):
    """Property 3: The findings file echoes the contract's identity."""

    def test_head_pr_number_agent_and_every_producer_come_from_the_environment(self):
        rng = random.Random(0)
        for _ in range(ITERATIONS):
            pr_number = rng.randint(1, 10**6)
            env = {
                "RB_NWO": random_text(rng) + "/" + random_text(rng),
                "RB_PR_NUMBER": str(pr_number),
                "RB_BASE": random_text(rng, string.hexdigits.lower(), 40),
                "RB_HEAD": random_text(rng, string.hexdigits.lower(), 40),
                "RB_AGENT": random_text(rng),
            }
            generated = [random_candidate(rng)[0] for _ in range(rng.randint(0, 45))]
            kept, _dropped = validate(generated)
            result = findings.build_findings_file(kept, env, {"time_in_ms": rng.randint(0, 10**7)})
            self.assertEqual(result["pr"]["head"], env["RB_HEAD"])
            self.assertEqual(result["pr"]["pr_number"], pr_number)
            self.assertEqual(result["agent"], env["RB_AGENT"])
            self.assertEqual(len(result["findings"]), len(kept))
            for entry in result["findings"]:
                self.assertEqual(entry["producer"], env["RB_AGENT"])


class ValidatePaths(unittest.TestCase):
    def test_a_leading_dot_slash_is_removed_and_the_finding_kept(self):
        kept, _dropped = validate([candidate(file="./src/app.py")])
        self.assertEqual([finding["file"] for finding in kept], ["src/app.py"])

    def test_a_leading_slash_is_removed_and_the_finding_kept(self):
        kept, _dropped = validate([candidate(file="/src/app.py")])
        self.assertEqual([finding["file"] for finding in kept], ["src/app.py"])

    def test_a_backslash_path_becomes_a_forward_slash_path_and_is_kept(self):
        kept, _dropped = validate([candidate(file="src\\lib\\util.py")])
        self.assertEqual([finding["file"] for finding in kept], ["src/lib/util.py"])

    def test_a_file_absent_at_head_is_dropped_and_counted_as_absent(self):
        kept, dropped = validate([candidate(file="src/gone.py")])
        self.assertEqual(kept, [])
        self.assertEqual(dropped["absent_file"], 1)


class ValidateLines(unittest.TestCase):
    def test_a_start_line_of_zero_is_dropped_and_counted_out_of_range(self):
        kept, dropped = validate([candidate(start_line=0, end_line=1)])
        self.assertEqual(kept, [])
        self.assertEqual(dropped["lines_out_of_range"], 1)

    def test_an_end_line_past_the_file_is_dropped_and_counted_out_of_range(self):
        kept, dropped = validate([candidate(file="README.md", start_line=1, end_line=9)])
        self.assertEqual(kept, [])
        self.assertEqual(dropped["lines_out_of_range"], 1)

    def test_line_one_of_a_one_line_file_is_kept(self):
        kept, _dropped = validate([candidate(file="one_line.txt", start_line=1, end_line=1)])
        self.assertEqual(len(kept), 1)


class ValidateLimit(unittest.TestCase):
    def test_forty_valid_findings_are_all_kept_and_none_counted_over_the_limit(self):
        kept, dropped = validate([candidate(start_line=line, end_line=line) for line in range(1, 41)])
        self.assertEqual(len(kept), 40)
        self.assertEqual(dropped["over_limit"], 0)

    def test_forty_one_valid_findings_drop_the_one_of_lowest_severity(self):
        highs = [candidate(start_line=line, end_line=line) for line in range(1, 41)]
        low = candidate(start_line=99, end_line=99, severity="low")
        kept, dropped = validate([low] + highs)
        self.assertEqual(len(kept), 40)
        self.assertNotIn(low, kept)
        self.assertEqual(dropped["over_limit"], 1)

    def test_an_empty_list_gives_no_findings_and_no_drops(self):
        kept, dropped = validate([])
        self.assertEqual(kept, [])
        self.assertEqual(sum(dropped.values()), 0)


class AwkwardMessages(unittest.TestCase):
    def test_a_message_of_joined_emoji_reaches_the_findings_file_unchanged(self):
        message = "\U0001F469‍\U0001F469‍\U0001F467‍\U0001F466"
        self.assertEqual(through_the_adapter(message), message)

    def test_a_message_with_a_byte_order_mark_reaches_the_findings_file_unchanged(self):
        message = "﻿null dereference"
        self.assertEqual(through_the_adapter(message), message)

    def test_a_whitespace_only_message_reaches_the_findings_file_unchanged(self):
        message = " \t\n "
        self.assertEqual(through_the_adapter(message), message)

    def test_a_very_long_message_reaches_the_findings_file_unchanged(self):
        message = "overflow " * 20000
        self.assertEqual(through_the_adapter(message), message)

    def test_a_message_in_a_non_latin_script_reaches_the_findings_file_unchanged(self):
        message = "\u3053\u306e\u95a2\u6570\u306f\u5931\u6557\u3059\u308b"
        self.assertEqual(through_the_adapter(message), message)

    def test_a_message_with_zero_width_characters_reaches_the_findings_file_unchanged(self):
        message = "null\u200bcheck\u200dmissing"
        self.assertEqual(through_the_adapter(message), message)

    def test_a_message_with_control_characters_reaches_the_findings_file_unchanged(self):
        message = "bad\u0001input\tfound"
        self.assertEqual(through_the_adapter(message), message)


class ParseReviewJson(unittest.TestCase):
    def test_a_candidate_missing_a_field_is_refused_naming_it_and_the_rest_kept(self):
        good = candidate()
        lacking = candidate(file="README.md")
        del lacking["severity"]
        candidates, refused = findings.parse_review_json(review_text([lacking, good]))
        self.assertEqual(candidates, [good])
        self.assertEqual([entry["entry"] for entry in refused], [lacking])
        self.assertIn("severity", refused[0]["error"])

    def test_a_text_that_is_not_a_findings_object_raises(self):
        with self.assertRaises(ValueError):
            findings.parse_review_json('{"pass": "final", "verdict": "holds"}')


if __name__ == "__main__":
    unittest.main()
