"""Proves benchmarks/martian/convert.py turns findings files into Martian's data file.

For any findings files that each match a golden pull request, the
benchmark_data.json convert.py writes holds one record per matched pull
request, one `ponderly` review per record and one comment per finding, with
the finding's file, start line and message. A findings file with no golden
record, two findings files for one golden pull request and a missing or empty
golden folder each exit 1, name what is wrong and write nothing.
"""

import json
import os
import random
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONVERT = os.path.join(ROOT, "benchmarks", "martian", "convert.py")

MESSAGE_PIECES = ["plain", "café", "日本語", "👩‍👩‍👧", "﻿", "​", "  ", "\t", "<tag>", '"q"', "x" * 300]


def golden_entry(owner, repo, number, original=None):
    entry = {
        "pr_title": "Change %s %d" % (repo, number),
        "url": "https://github.com/%s/%s/pull/%d" % (owner, repo, number),
        "comments": [{"comment": "Golden %d" % number, "severity": "High", "category": "Bug"}],
    }
    if original is not None:
        entry["original_url"] = "https://github.com/%s/%s/pull/%d" % (original[0], original[1], original[2])
    return entry


def findings_file(nwo, number, findings):
    return {
        "pr": {"repo": "https://github.com/%s" % nwo, "pr_number": number, "base": "b" * 40, "head": "h" * 40},
        "agent": "ponderly",
        "findings": findings,
    }


def finding(path, start_line, message):
    return {"file": path, "start_line": start_line, "end_line": start_line, "message": message, "producer": "ponderly"}


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


def run_convert(run_folder, golden_folder):
    return subprocess.run([sys.executable, CONVERT, run_folder, golden_folder], capture_output=True, text=True)


def read_data(run_folder):
    with open(os.path.join(run_folder, "benchmark_data.json"), encoding="utf-8") as handle:
        return json.load(handle)


def random_findings(generator):
    findings = []
    for _ in range(generator.choice([0, 1, 2, 5, 12])):
        path = "/".join(generator.choice(["src", "lib", "a b", "日本", "x"]) for _ in range(generator.randint(1, 3))) + ".py"
        message = "".join(generator.choice(MESSAGE_PIECES) for _ in range(generator.randint(1, 4)))
        findings.append(finding(path, generator.randint(1, 5000), message))
    return findings


def random_case(generator):
    """Return golden files, findings files and the comments expected under each golden URL."""
    golden_files = {}
    entries = []
    for file_index in range(generator.randint(1, 3)):
        file_entries = []
        for _ in range(generator.randint(1, 4)):
            number = len(entries) + 1
            original = None
            if generator.random() < 0.5:
                original = ("upstream", "project%d" % number, generator.randint(1, 99999))
            entry = golden_entry("bench", "repo%d" % number, number, original)
            file_entries.append(entry)
            entries.append(entry)
        golden_files["golden_%d.json" % file_index] = file_entries
    covered = generator.sample(entries, generator.randint(1, len(entries)))
    findings_files = {}
    expected = {}
    for index, entry in enumerate(covered):
        target = entry["url"]
        if "original_url" in entry and generator.random() < 0.5:
            target = entry["original_url"]
        nwo, number = target.split("github.com/", 1)[1].split("/pull/")
        findings = random_findings(generator)
        findings_files["%03d.json" % index] = findings_file(nwo, int(number), findings)
        expected[entry["url"]] = (nwo, [{"path": f["file"], "line": f["start_line"], "body": f["message"]} for f in findings])
    return golden_files, findings_files, expected


class MartianDataFileKeepsEveryFindingOnceTest(unittest.TestCase):
    """Property 6: The Martian data file keeps every finding once."""

    def test_each_matched_pull_request_gets_one_ponderly_review_with_one_comment_per_finding(self):
        generator = random.Random(0)
        for iteration in range(100):
            golden_files, findings_files, expected = random_case(generator)
            with self.subTest(iteration=iteration), tempfile.TemporaryDirectory() as folder:
                run_folder = os.path.join(folder, "run")
                golden_folder = os.path.join(folder, "golden")
                for name, entries in golden_files.items():
                    write_json(os.path.join(golden_folder, name), entries)
                for name, content in findings_files.items():
                    write_json(os.path.join(run_folder, "findings", name), content)

                result = run_convert(run_folder, golden_folder)

                self.assertEqual(result.returncode, 0, result.stderr)
                data = read_data(run_folder)
                self.assertEqual(sorted(data), sorted(expected))
                for golden_url, (nwo, comments) in expected.items():
                    reviews = data[golden_url]["reviews"]
                    self.assertEqual(len(reviews), 1)
                    self.assertEqual(reviews[0]["tool"], "ponderly")
                    self.assertEqual(reviews[0]["repo_name"], nwo)
                    self.assertEqual(reviews[0]["pr_url"], golden_url)
                    self.assertEqual(reviews[0]["review_comments"], comments)


class ConvertExampleTest(unittest.TestCase):
    """One example per path convert.py takes outside the property."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.run_folder = os.path.join(self.folder.name, "run")
        self.golden_folder = os.path.join(self.folder.name, "golden")
        os.makedirs(os.path.join(self.run_folder, "findings"))

    def tearDown(self):
        self.folder.cleanup()

    def assert_refused_without_writing(self, result, *names):
        self.assertEqual(result.returncode, 1)
        for name in names:
            self.assertIn(name, result.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.run_folder, "benchmark_data.json")))

    def test_a_findings_file_with_no_golden_record_exits_1_naming_the_file_and_writes_nothing(self):
        write_json(os.path.join(self.golden_folder, "golden.json"), [golden_entry("bench", "repo1", 1)])
        stray = os.path.join(self.run_folder, "findings", "stray.json")
        write_json(stray, findings_file("bench/repo1", 2, [finding("a.py", 3, "m")]))

        self.assert_refused_without_writing(run_convert(self.run_folder, self.golden_folder), stray)

    def test_two_findings_files_for_one_golden_pull_request_exit_1_naming_both_and_write_nothing(self):
        entry = golden_entry("bench", "repo1", 1, original=("upstream", "project1", 77))
        write_json(os.path.join(self.golden_folder, "golden.json"), [entry])
        by_url = os.path.join(self.run_folder, "findings", "by_url.json")
        by_original = os.path.join(self.run_folder, "findings", "by_original.json")
        write_json(by_url, findings_file("bench/repo1", 1, []))
        write_json(by_original, findings_file("upstream/project1", 77, []))

        self.assert_refused_without_writing(run_convert(self.run_folder, self.golden_folder), by_url, by_original)

    def test_a_missing_golden_folder_exits_1_naming_the_setup_target_and_writes_nothing(self):
        write_json(os.path.join(self.run_folder, "findings", "one.json"), findings_file("bench/repo1", 1, []))

        self.assert_refused_without_writing(run_convert(self.run_folder, self.golden_folder), "setup target")

    def test_an_empty_golden_folder_exits_1_naming_the_setup_target_and_writes_nothing(self):
        os.makedirs(self.golden_folder)
        write_json(os.path.join(self.run_folder, "findings", "one.json"), findings_file("bench/repo1", 1, []))

        self.assert_refused_without_writing(run_convert(self.run_folder, self.golden_folder), "setup target")

    def test_an_empty_findings_list_gives_a_ponderly_review_with_no_comments(self):
        write_json(os.path.join(self.golden_folder, "golden.json"), [golden_entry("bench", "repo1", 1)])
        write_json(os.path.join(self.run_folder, "findings", "one.json"), findings_file("bench/repo1", 1, []))

        result = run_convert(self.run_folder, self.golden_folder)

        self.assertEqual(result.returncode, 0, result.stderr)
        reviews = read_data(self.run_folder)["https://github.com/bench/repo1/pull/1"]["reviews"]
        self.assertEqual([(review["tool"], review["review_comments"]) for review in reviews], [("ponderly", [])])

    def test_a_golden_pull_request_no_findings_file_covers_gets_no_record(self):
        covered = golden_entry("bench", "repo1", 1)
        uncovered = golden_entry("bench", "repo2", 2)
        write_json(os.path.join(self.golden_folder, "golden.json"), [covered, uncovered])
        write_json(os.path.join(self.run_folder, "findings", "one.json"), findings_file("bench/repo1", 1, []))

        result = run_convert(self.run_folder, self.golden_folder)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(list(read_data(self.run_folder)), [covered["url"]])


if __name__ == "__main__":
    unittest.main()
