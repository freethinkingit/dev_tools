"""Tests for evals/keep_traces.py, which copies each eval run's trace and last
message into the results folder and deletes the runner's kept sandbox."""
import importlib.util
import json
import os
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "evals", "keep_traces.py")


def load_script():
    spec = importlib.util.spec_from_file_location("keep_traces", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_trace(path, events):
    with open(path, "w", encoding="utf-8") as trace:
        for event in events:
            trace.write(json.dumps(event) + "\n")


def assistant(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


class LastMessageTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()
        self.dir = tempfile.TemporaryDirectory()
        self.trace = os.path.join(self.dir.name, "trace.jsonl")

    def tearDown(self):
        self.dir.cleanup()

    def test_the_last_assistant_text_wins_over_earlier_ones(self):
        write_trace(self.trace, [assistant("first"), {"type": "user"}, assistant("final")])
        self.assertEqual(self.module.last_message_of(self.trace), "final")

    def test_a_trace_with_no_assistant_text_gives_an_empty_message(self):
        write_trace(self.trace, [{"type": "user"}, {"type": "assistant", "message": {"content": [{"type": "tool_use"}]}}])
        self.assertEqual(self.module.last_message_of(self.trace), "")

    def test_a_line_that_is_not_json_is_skipped(self):
        with open(self.trace, "w", encoding="utf-8") as trace:
            trace.write("not json\n" + json.dumps(assistant("kept")) + "\n")
        self.assertEqual(self.module.last_message_of(self.trace), "kept")


class KeepTracesTest(unittest.TestCase):
    def setUp(self):
        self.module = load_script()
        self.dir = tempfile.TemporaryDirectory()
        self.results = os.path.join(self.dir.name, "results")
        os.makedirs(self.results)

    def tearDown(self):
        self.dir.cleanup()

    def make_sandbox(self, text):
        sandbox = tempfile.mkdtemp(prefix="e-", dir=self.dir.name)
        os.makedirs(os.path.join(sandbox, "out"))
        trace = os.path.join(sandbox, "out", "trace.jsonl")
        write_trace(trace, [assistant(text)])
        return sandbox, trace

    def write_aggregate(self, cases):
        with open(os.path.join(self.results, "aggregate-result.json"), "w", encoding="utf-8") as aggregate:
            json.dump({"cases": cases}, aggregate)

    def test_a_run_s_trace_and_last_message_are_kept_and_its_sandbox_removed(self):
        sandbox, trace = self.make_sandbox("the review's reply")
        self.write_aggregate([{"name": "clean-diff", "arms": {"with": [{"tracePath": trace}]}}])
        self.module.keep_traces(self.results)
        traces = os.path.join(self.results, "traces")
        self.assertTrue(os.path.exists(os.path.join(traces, "clean-diff-with-run1.jsonl")))
        with open(os.path.join(traces, "clean-diff-with-run1.md"), encoding="utf-8") as last:
            self.assertEqual(last.read(), "the review's reply")
        self.assertFalse(os.path.exists(sandbox))

    def test_a_results_folder_without_an_aggregate_file_is_left_alone(self):
        self.module.keep_traces(self.results)
        self.assertEqual(os.listdir(self.results), [])

    def test_a_run_whose_trace_is_already_gone_is_skipped(self):
        self.write_aggregate([{"name": "gone", "arms": {"with": [{"tracePath": os.path.join(self.dir.name, "missing", "out", "trace.jsonl")}]}}])
        self.module.keep_traces(self.results)
        self.assertFalse(os.path.exists(os.path.join(self.results, "traces")))


if __name__ == "__main__":
    unittest.main()
