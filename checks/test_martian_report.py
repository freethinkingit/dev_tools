"""Proves benchmarks/martian/report.py keeps a failed judging out of the score.

Martian's judge counts a comparison whose model call failed as no match, so a
review whose judging had failed calls would score as if its findings missed.
The report leaves such a review out of the scores and names it under Judge
errors, and says there is no score when every review's judging failed.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "benchmarks", "martian", "report.py")

FAILED_URL = "https://github.com/calcom/cal.com/pull/8087"
JUDGED_URL = "https://github.com/getsentry/sentry/pull/1"


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


def judged_review():
    return {
        "skipped": False,
        "true_positives": [{"golden_comment": "Golden bug", "category": "bug"}],
        "false_negatives": [],
        "fp": 1,
        "errors": [],
        "errors_count": 0,
    }


def failed_review():
    return {
        "skipped": False,
        "true_positives": [],
        "false_negatives": [{"golden_comment": "Golden bug", "category": "bug"}],
        "fp": 8,
        "errors": [{"golden": "Golden bug", "candidate": "c", "error": "Error code: 400"}],
        "errors_count": 16,
    }


class ReportJudgeErrorsTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.run_folder = os.path.join(self.folder.name, "run")
        self.golden_folder = os.path.join(self.folder.name, "golden")
        write_json(os.path.join(self.golden_folder, "repo.json"),
                   [{"comments": [{"comment": "Golden bug", "category": "bug"}]}])

    def report(self, evaluations):
        write_json(os.path.join(self.run_folder, "scoring", "evaluations.json"), evaluations)
        result = subprocess.run([sys.executable, REPORT, self.run_folder, self.golden_folder],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def test_a_review_with_failed_judge_calls_is_named_and_left_out_of_the_score(self):
        text = self.report({FAILED_URL: {"ponderly": failed_review()},
                            JUDGED_URL: {"ponderly": judged_review()}})

        self.assertIn("## Judge errors", text)
        self.assertIn("16 judge calls failed in 1 reviews", text)
        self.assertIn("- {} (ponderly): 16 failed calls".format(FAILED_URL), text)
        self.assertIn("| ponderly | 1 | 50.0% | 100.0% | 66.7% | 1 | 1 | 0 |", text)

    def test_every_review_with_failed_judge_calls_gives_no_score_and_no_table(self):
        text = self.report({FAILED_URL: {"ponderly": failed_review()}})

        self.assertIn("No score: no review was judged without errors.", text)
        self.assertNotIn("| Tool |", text)

    def test_a_run_judged_without_errors_has_no_judge_errors_section(self):
        text = self.report({JUDGED_URL: {"ponderly": judged_review()}})

        self.assertNotIn("Judge errors", text)
        self.assertIn("| ponderly | 1 | 50.0% | 100.0% | 66.7% | 1 | 1 | 0 |", text)


if __name__ == "__main__":
    unittest.main()
