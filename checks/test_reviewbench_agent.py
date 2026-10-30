"""Proves benchmarks/reviewbench/agent/agent.py, the ReviewBench adapter, end to end.

Each test runs the adapter as a subprocess with python3 -I, as the image does,
and fakes Claude Code at its boundary with the stub STUB_SOURCE, written into
a temporary directory and named by RB_CLAUDE_BIN. STUB_PLAN tells the stub
what each call does, one action per call separated by commas, the last action
repeating; the stub appends a line per call to STUB_LOG with the
CLAUDE_CODE_* variables, ANTHROPIC_API_KEY and HOME it was given and the uid it ran as. The time limits are scaled down to
seconds through RB_TIMEOUT_SECONDS and RB_TOTAL_SECONDS.
"""

import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT = os.path.join(ROOT, "benchmarks", "reviewbench", "agent", "agent.py")
ADAPTER_WAIT_SECONDS = 30
API_KEY = "sk-ant-test-4f9c2e"

STUB_SOURCE = '''
import json
import os
import subprocess
import sys
import time

sys.stdin.read()
log_path = os.environ["STUB_LOG"]
with open(log_path, "a", encoding="utf-8") as log:
    variables = {
        name: value for name, value in os.environ.items()
        if name.startswith("CLAUDE_CODE_") or name in ("ANTHROPIC_API_KEY", "HOME")
    }
    variables["uid"] = os.getuid()
    log.write(json.dumps(variables) + "\\n")
with open(log_path, encoding="utf-8") as log:
    call = len(log.readlines())
actions = os.environ["STUB_PLAN"].split(",")
action = actions[min(call, len(actions)) - 1]
review_path = os.environ["RB_REVIEW_PATH"]

GOOD = {"file": "src/app.py", "start_line": 1, "end_line": 2, "severity": "high",
        "category": "correctness", "message": "off by one"}
WITHOUT_MESSAGE = {"file": "src/app.py", "start_line": 3, "end_line": 3, "severity": "low",
                   "category": "style"}
RESULT = {"total_cost_usd": 0.5, "duration_ms": 1234, "usage": {"input_tokens": 10, "output_tokens": 5}}


def write_review(findings, failed_arms=()):
    review = {"pass": "final", "verdict": "holds", "second_pass": False,
              "counts": {"candidates": len(findings), "removed_by_merge": 0,
                         "removed_by_review": 0, "failed_arms": list(failed_arms)},
              "findings": findings}
    with open(review_path, "w", encoding="utf-8") as handle:
        json.dump(review, handle)


def write_unparseable():
    with open(review_path, "w", encoding="utf-8") as handle:
        handle.write('{"findings": [')


def finish(result=RESULT):
    print(json.dumps(result), flush=True)
    sys.exit(0)


if action == "good":
    write_review([GOOD])
    finish()
if action == "no_file":
    finish()
if action == "fail":
    sys.exit(1)
if action == "sleep":
    time.sleep(60)
if action == "interim_then_sleep":
    write_review([GOOD])
    time.sleep(60)
if action == "unparseable":
    write_unparseable()
    finish()
if action == "unparseable_then_sleep":
    write_unparseable()
    time.sleep(60)
if action == "refused":
    write_review([GOOD, WITHOUT_MESSAGE])
    finish()
if action == "empty":
    write_review([])
    finish()
if action == "empty_with_failed_arm":
    write_review([], failed_arms=["security"])
    finish()
if action == "two_models":
    write_review([GOOD])
    finish({"total_cost_usd": 0.5, "duration_ms": 1234,
            "usage": {"input_tokens": 1, "output_tokens": 1},
            "modelUsage": {
                "claude-opus": {"inputTokens": 1, "outputTokens": 2,
                                "cacheReadInputTokens": 3, "cacheCreationInputTokens": 4},
                "claude-sonnet": {"inputTokens": 10, "outputTokens": 20,
                                  "cacheReadInputTokens": 30, "cacheCreationInputTokens": 40},
            }})
if action == "grandchild_then_sleep":
    grandchild = subprocess.Popen(["sleep", "60"], stdin=subprocess.DEVNULL, stdout=sys.stdout,
                                  stderr=subprocess.DEVNULL, start_new_session=True)
    with open(os.environ["STUB_GRANDCHILD_PID"], "w", encoding="utf-8") as handle:
        handle.write(str(grandchild.pid))
    time.sleep(60)
sys.exit(3)
'''


class AdapterTestCase(unittest.TestCase):
    """Runs the adapter against the stub in a fresh temporary directory per test."""

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = temporary.name
        repo_dir = os.path.join(self.directory, "repo")
        os.makedirs(os.path.join(repo_dir, "src"))
        with open(os.path.join(repo_dir, "src", "app.py"), "w", encoding="utf-8") as handle:
            handle.write("a = 1\nb = 2\nc = 3\n")
        review_dir = os.path.join(self.directory, "review")
        os.makedirs(review_dir)
        pr_json = os.path.join(self.directory, "pr.json")
        with open(pr_json, "w", encoding="utf-8") as handle:
            json.dump({"title": "Fix pagination", "body": "Slices one too many."}, handle)
        stub = os.path.join(self.directory, "claude")
        with open(stub, "w", encoding="utf-8") as handle:
            handle.write("#!{} -I\n{}".format(sys.executable, STUB_SOURCE))
        os.chmod(stub, 0o755)
        self.log_path = os.path.join(self.directory, "stub.log")
        self.out_path = os.path.join(self.directory, "findings.json")
        self.grandchild_pid_path = os.path.join(self.directory, "grandchild.pid")
        self.env = {
            "PATH": os.environ.get("PATH", ""),
            "RB_NWO": "octo/shop",
            "RB_PR_NUMBER": "17",
            "RB_BASE": "a" * 40,
            "RB_HEAD": "b" * 40,
            "RB_OUT": self.out_path,
            "RB_AGENT": "ponderly",
            "ANTHROPIC_API_KEY": API_KEY,
            "RB_CLAUDE_BIN": stub,
            "RB_REVIEW_PATH": os.path.join(review_dir, "review.json"),
            "RB_REPO_DIR": repo_dir,
            "RB_PR_JSON": pr_json,
            "RB_TIMEOUT_SECONDS": "10",
            "STUB_LOG": self.log_path,
            "STUB_GRANDCHILD_PID": self.grandchild_pid_path,
        }

    def run_adapter(self, plan, **overrides):
        env = dict(self.env, STUB_PLAN=plan)
        env.update(overrides)
        return subprocess.run(
            [sys.executable, "-I", AGENT],
            env=env,
            capture_output=True,
            timeout=ADAPTER_WAIT_SECONDS,
        )

    def stub_calls(self):
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, encoding="utf-8") as log:
            return [json.loads(line) for line in log]

    def findings_file(self):
        with open(self.out_path, encoding="utf-8") as handle:
            return json.load(handle)


class AFindingsFileExistsExactlyWhenTheReviewProducedParseableFindings(AdapterTestCase):
    """Property 4: A findings file exists exactly when the review produced parseable findings."""

    def test_a_parseable_review_file_exits_0_and_writes_the_findings_file(self):
        completed = self.run_adapter("good")
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(os.path.exists(self.out_path))

    def test_exit_0_without_a_review_file_exits_1_and_writes_nothing(self):
        completed = self.run_adapter("no_file")
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(os.path.exists(self.out_path))

    def test_a_non_zero_claude_exit_exits_1_and_writes_nothing(self):
        completed = self.run_adapter("fail")
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(os.path.exists(self.out_path))

    def test_a_kill_at_the_time_limit_with_no_interim_file_exits_1_and_writes_nothing(self):
        completed = self.run_adapter("sleep", RB_TIMEOUT_SECONDS="1")
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(os.path.exists(self.out_path))

    def test_a_kill_at_the_time_limit_with_a_parseable_interim_file_exits_0_and_writes_it(self):
        completed = self.run_adapter("interim_then_sleep", RB_TIMEOUT_SECONDS="1")
        self.assertEqual(completed.returncode, 0)
        findings = self.findings_file()["findings"]
        written = [(finding["start_line"], finding["message"]) for finding in findings]
        self.assertEqual(written, [(1, "off by one")])

    def test_an_unparseable_file_the_repair_run_fixes_exits_0_and_writes_the_findings_file(self):
        completed = self.run_adapter("unparseable,good")
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(os.path.exists(self.out_path))
        self.assertEqual(len(self.stub_calls()), 2)

    def test_a_file_still_unparseable_after_the_one_repair_run_exits_1_and_writes_nothing(self):
        completed = self.run_adapter("unparseable,unparseable")
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(os.path.exists(self.out_path))
        self.assertEqual(len(self.stub_calls()), 2)

    def test_an_entry_the_repair_leaves_refused_is_dropped_and_the_rest_written_with_exit_0(self):
        completed = self.run_adapter("refused,refused")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(len(self.stub_calls()), 2)
        findings = self.findings_file()["findings"]
        written = [(finding["start_line"], finding["message"]) for finding in findings]
        self.assertEqual(written, [(1, "off by one")])

    def test_a_review_file_with_no_findings_and_a_failed_arm_exits_1_and_writes_nothing(self):
        completed = self.run_adapter("empty_with_failed_arm")
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(os.path.exists(self.out_path))

    @unittest.skipIf(os.getuid() == 0, "the adapter switches user only when it runs as root")
    def test_a_non_root_adapter_ignores_an_unknown_claude_user_and_runs_claude_as_its_own_user(self):
        own_home = os.path.expanduser("~")
        completed = self.run_adapter("good", HOME=own_home, RB_CLAUDE_USER="no-such-user-4f9c2e")
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(os.path.exists(self.out_path))
        [variables] = self.stub_calls()
        self.assertEqual(variables["HOME"], own_home)
        self.assertEqual(variables["uid"], os.getuid())
        self.assertIn(b"ignoring RB_CLAUDE_USER", completed.stderr)


class TheAdapterChecksItsInputs(AdapterTestCase):
    def test_a_missing_required_variable_exits_2_naming_it_before_calling_claude(self):
        del self.env["RB_NWO"]
        completed = self.run_adapter("good")
        self.assertEqual(completed.returncode, 2)
        self.assertIn(b"RB_NWO", completed.stderr)
        self.assertFalse(os.path.exists(self.out_path))
        self.assertEqual(self.stub_calls(), [])


class TheFindingsFile(AdapterTestCase):
    def test_an_empty_findings_list_exits_0_and_writes_a_file_with_no_findings(self):
        completed = self.run_adapter("empty")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(self.findings_file()["findings"], [])

    def test_model_usage_for_two_models_gives_total_tokens_as_the_sum_over_both(self):
        completed = self.run_adapter("two_models")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(self.findings_file()["usage"]["total_tokens"], 1 + 2 + 3 + 4 + 10 + 20 + 30 + 40)


class ClaudeCodeIsGivenTheSettings(AdapterTestCase):
    def test_the_child_environment_carries_the_effort_and_a_forced_subagent_model(self):
        self.run_adapter("good", RB_CONFIG_MODEL="sonnet", RB_CONFIG_EFFORT="medium")
        [variables] = self.stub_calls()
        self.assertEqual(variables["CLAUDE_CODE_EFFORT_LEVEL"], "medium")
        self.assertEqual(variables["CLAUDE_CODE_SUBAGENT_MODEL"], "sonnet")
        self.assertEqual(variables["CLAUDE_CODE_SUBAGENT_MODEL_FORCE"], "1")

    def test_the_api_key_reaches_claude_code_and_is_printed_on_neither_stdout_nor_stderr(self):
        completed = self.run_adapter("good")
        [variables] = self.stub_calls()
        self.assertEqual(variables["ANTHROPIC_API_KEY"], API_KEY)
        self.assertNotIn(API_KEY.encode("utf-8"), completed.stdout)
        self.assertNotIn(API_KEY.encode("utf-8"), completed.stderr)


class TheAdapterStaysInsideItsTimeLimits(AdapterTestCase):
    def test_a_repair_started_with_little_time_left_is_killed_before_the_total_limit(self):
        total_seconds = 4
        started = time.monotonic()
        completed = self.run_adapter(
            "unparseable_then_sleep,sleep",
            RB_TIMEOUT_SECONDS="2",
            RB_TOTAL_SECONDS=str(total_seconds),
            RB_REPAIR_TIMEOUT_SECONDS="30",
        )
        elapsed = time.monotonic() - started
        self.assertEqual(len(self.stub_calls()), 2)
        self.assertLess(elapsed, total_seconds + 5)
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(os.path.exists(self.out_path))

    def test_a_grandchild_holding_stdout_after_the_kill_does_not_hang_the_adapter(self):
        self.addCleanup(self.kill_grandchild)
        completed = self.run_adapter("grandchild_then_sleep", RB_TIMEOUT_SECONDS="1")
        self.assertTrue(os.path.exists(self.grandchild_pid_path))
        self.assertEqual(completed.returncode, 1)
        self.assertFalse(os.path.exists(self.out_path))

    def kill_grandchild(self):
        if not os.path.exists(self.grandchild_pid_path):
            return
        with open(self.grandchild_pid_path, encoding="utf-8") as handle:
            pid = int(handle.read())
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


if __name__ == "__main__":
    unittest.main()
