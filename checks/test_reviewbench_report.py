"""Proves the ReviewBench score report in benchmarks/reviewbench/report.py.

The report states each metric group of the judge's results, computes grounded
F1, sums the model cost Claude Code reported, names the run's settings from
``run.json`` or says they are unknown, and exits 1 naming the judge target when
the judge's results file is absent.
"""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "benchmarks", "reviewbench", "report.py")


def load_report():
    spec = importlib.util.spec_from_file_location("reviewbench_report", REPORT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


report = load_report()


def metrics(grounded_precision, grounded_recall, golden_tp_count):
    return {
        "grounded_precision": grounded_precision,
        "grounded_recall": grounded_recall,
        "augmented_precision": 0.25,
        "augmented_recall": 0.75,
        "candidate_count": 7,
        "golden_tp_count": golden_tp_count,
        "matched_count": 4,
        "matched_tp_count": 3,
        "novel_tp_count": 1,
    }


def results_with_every_group():
    overall = metrics(0.5, 0.5, 6)
    return {
        "pr_count": 2,
        "macro": {
            "overall": overall,
            "by_severity": {"high": metrics(0.5, 0.5, 2)},
            "by_category": {"logic": metrics(0.5, 0.5, 3)},
        },
        "micro": {
            "overall": overall,
            "by_severity": {"high": metrics(0.5, 0.5, 2)},
            "by_category": {"logic": metrics(0.5, 0.5, 3)},
        },
    }


RUN_RECORD = {
    "set": "test",
    "model": "claude-opus-5-5",
    "effort": "high",
    "budget_usd": 5,
    "image": "reviewbench-ponderly:latest",
    "plugin_version": "9.8.7",
    "started": "2026-10-29T10:00:00Z",
    "commands": ["make -C benchmarks/reviewbench test-set", "make -C benchmarks/reviewbench judge RUN=x"],
    "judge_model": "claude-sonnet-4-5",
    "judge_base_url": "https://api.anthropic.com/v1/",
}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def make_run(folder, results=None, findings=None, run_record=None):
    run_dir = Path(folder)
    (run_dir / "findings").mkdir(parents=True, exist_ok=True)
    if results is not None:
        write_json(run_dir / "scoring" / "results.json", results)
    for name, content in (findings or {}).items():
        write_json(run_dir / "findings" / name, content)
    if run_record is not None:
        write_json(run_dir / "run.json", run_record)
    return run_dir


def run_main(run_dir):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        status = report.main([str(run_dir)])
    return status, stdout.getvalue(), stderr.getvalue()


class ReviewBenchReportTest(unittest.TestCase):
    def test_a_results_file_with_every_group_prints_overall_severity_and_category_rows(self):
        with tempfile.TemporaryDirectory() as folder:
            run_dir = make_run(folder, results=results_with_every_group(), run_record=RUN_RECORD)
            status, printed, _ = run_main(run_dir)
            written = (run_dir / "report.md").read_text(encoding="utf-8")
        self.assertEqual(status, 0)
        self.assertEqual(printed, written)
        overall_row = "| macro | overall | 50.0% | 50.0% | 50.0% | 25.0% | 75.0% | 37.5% | 6 |"
        severity_row = "| micro | high | 50.0% | 50.0% | 50.0% | 25.0% | 75.0% | 37.5% | 2 |"
        category_row = "| macro | logic | 50.0% | 50.0% | 50.0% | 25.0% | 75.0% | 37.5% | 3 |"
        self.assertIn(overall_row, written)
        self.assertIn(severity_row, written.split("## By severity")[1].split("## By category")[0])
        self.assertIn(category_row, written.split("## By category")[1])
        self.assertLess(written.index("Grounded precision is the share"), written.index(overall_row))

    def test_a_missing_results_file_exits_1_naming_it_and_the_judge_target(self):
        with tempfile.TemporaryDirectory() as folder:
            run_dir = make_run(folder, run_record=RUN_RECORD)
            status, printed, error = run_main(run_dir)
            report_written = (run_dir / "report.md").exists()
        self.assertEqual(status, 1)
        self.assertEqual(printed, "")
        self.assertIn(os.path.join("scoring", "results.json"), error)
        self.assertIn("make -C benchmarks/reviewbench judge", error)
        self.assertFalse(report_written)

    def test_findings_without_usage_report_duration_and_cost_as_unknown(self):
        with tempfile.TemporaryDirectory() as folder:
            run_dir = make_run(
                folder,
                results=results_with_every_group(),
                findings={"pr-0.json": {"findings": []}},
                run_record=RUN_RECORD,
            )
            written = report.render_report(run_dir)
        self.assertIn("averaged over the 0 of 1 findings files that record it", written)
        self.assertIn("Mean review duration: unknown", written)
        self.assertIn("Total model cost: unknown", written)
        self.assertIn("Mean model cost per pull request: unknown", written)

    def test_findings_with_usage_report_total_and_mean_cost_and_mean_duration(self):
        with tempfile.TemporaryDirectory() as folder:
            run_dir = make_run(
                folder,
                results=results_with_every_group(),
                findings={
                    "pr-0.json": {"findings": [], "usage": {"time_in_ms": 10000, "cost_usd": 1.25}},
                    "pr-1.json": {"findings": [], "usage": {"time_in_ms": 20000, "cost_usd": 0.75}},
                },
                run_record=RUN_RECORD,
            )
            written = report.render_report(run_dir)
        self.assertIn("Mean review duration: 15.0 s", written)
        self.assertIn("Total model cost: $2.00", written)
        self.assertIn("Mean model cost per pull request: $1.00", written)

    def test_zero_grounded_precision_gives_a_grounded_f1_of_zero(self):
        results = {"pr_count": 1, "macro": {"overall": metrics(0.0, 0.5, 4)}, "micro": {}}
        with tempfile.TemporaryDirectory() as folder:
            run_dir = make_run(folder, results=results, run_record=RUN_RECORD)
            written = report.render_report(run_dir)
        self.assertIn("| macro | overall | 0.0% | 50.0% | 0.0% | 25.0% | 75.0% | 37.5% | 4 |", written)

    def test_a_run_record_names_the_version_model_effort_set_judge_date_and_commands(self):
        with tempfile.TemporaryDirectory() as folder:
            run_dir = make_run(folder, results=results_with_every_group(), run_record=RUN_RECORD)
            written = report.render_report(run_dir)
        self.assertIn("- Plugin version: 9.8.7 (recorded at run time)", written)
        self.assertIn("- Model: claude-opus-5-5", written)
        self.assertIn("- Effort: high", written)
        self.assertIn("- Set: test", written)
        self.assertIn("- Judge model: claude-sonnet-4-5", written)
        self.assertIn("- Date: 2026-10-29T10:00:00Z", written)
        self.assertIn(
            "```\nmake -C benchmarks/reviewbench test-set\nmake -C benchmarks/reviewbench judge RUN=x\n```",
            written,
        )

    def test_no_run_record_reports_settings_unknown_and_reads_the_version_from_plugin_json(self):
        manifest = json.loads(Path(report.PLUGIN_MANIFEST).read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as folder:
            run_dir = make_run(folder, results=results_with_every_group())
            written = report.render_report(run_dir)
        self.assertIn("- Plugin version: {} (read from plugin.json now)".format(manifest["version"]), written)
        self.assertIn("- Model: unknown", written)
        self.assertIn("- Effort: unknown", written)
        self.assertIn("- Set: unknown", written)
        self.assertIn("- Judge model: unknown", written)
        self.assertIn("- Date: unknown", written)
        self.assertIn("Commands that produced it:\n\nunknown", written)


if __name__ == "__main__":
    unittest.main()
