"""Proves benchmarks/reviewbench/agent/agent.py, the ReviewBench adapter, end to end.

Each test runs the adapter as a subprocess with python3 -I, as the image does,
except one that calls run_claude in-process, and fakes Claude Code at its
boundary with the stub STUB_SOURCE, written into a temporary directory and
named by RB_CLAUDE_BIN. STUB_PLAN tells the stub what each call does, one
action per call separated by commas, the last action repeating; the stub
appends a line per call to STUB_LOG with the CLAUDE_CODE_* variables,
CLAUDE_CODE_OAUTH_TOKEN among them, ANTHROPIC_API_KEY and HOME it was given,
the uid it ran as and its arguments. The time limits are scaled down to
seconds through RB_TIMEOUT_SECONDS and RB_TOTAL_SECONDS.
"""

import datetime
import importlib.util
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
OAUTH_TOKEN = "sk-ant-oat-test-7d1b3a"

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
    variables["argv"] = sys.argv[1:]
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
if action == "slow_with_a_short_duration":
    time.sleep(2)
    write_review([GOOD])
    finish({"total_cost_usd": 0.5, "duration_ms": 50,
            "usage": {"input_tokens": 1, "output_tokens": 1}})
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
if action == "leaks_credentials":
    credentials = "{} {}".format(os.environ.get("ANTHROPIC_API_KEY", ""),
                                 os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", ""))
    session_dir = os.path.join(os.environ["HOME"], ".claude", "projects", "-work-repo")
    os.makedirs(session_dir, exist_ok=True)
    with open(os.path.join(session_dir, "session.jsonl"), "w", encoding="utf-8") as handle:
        handle.write(json.dumps({"type": "user", "text": "credentials " + credentials}) + "\\n")
    print("credentials " + credentials, file=sys.stderr, flush=True)
    write_review([dict(GOOD, message="credentials " + credentials)])
    finish()
if action == "unparseable_with_stderr":
    print("review run stderr", file=sys.stderr, flush=True)
    write_unparseable()
    finish()
if action == "good_with_stderr":
    print("repair run stderr", file=sys.stderr, flush=True)
    write_review([GOOD])
    finish()
if action == "good_then_fail":
    write_review([GOOD])
    sys.exit(1)
if action == "final_then_sleep":
    write_review([GOOD])
    print(json.dumps(RESULT), flush=True)
    time.sleep(60)
if action == "first_then_sleep":
    with open(review_path, "w", encoding="utf-8") as handle:
        json.dump({"pass": "first", "verdict": "holds", "second_pass": False,
                   "counts": {"candidates": 1, "removed_by_merge": 0,
                              "removed_by_review": 0, "failed_arms": []},
                   "findings": [GOOD]}, handle)
    time.sleep(60)
if action == "final_then_exit_shortly":
    write_review([GOOD])
    time.sleep(3)
    finish()
if action == "marker_then_exit_5":
    with open(os.environ["STUB_EXIT_MARKER"], "w", encoding="utf-8"):
        pass
    sys.exit(5)
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

    def evidence_path(self, *names):
        return os.path.join(self.directory, "logs", *names)

    def evidence_bytes(self, *names):
        with open(self.evidence_path(*names), "rb") as handle:
            return handle.read()

    def every_evidence_file(self):
        """Return the bytes of every file under logs/, joined."""
        contents = []
        for directory, _, names in os.walk(self.evidence_path()):
            for name in names:
                with open(os.path.join(directory, name), "rb") as handle:
                    contents.append(handle.read())
        return b"".join(contents)


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
        completed = self.run_adapter("good", HOME=own_home, RB_CLAUDE_USER="no-such-user-4f9c2e", RB_KEEP_TRANSCRIPTS="0")
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

    def test_neither_the_api_key_nor_the_oauth_token_exits_2_naming_both_before_calling_claude(self):
        del self.env["ANTHROPIC_API_KEY"]
        completed = self.run_adapter("good")
        self.assertEqual(completed.returncode, 2)
        self.assertIn(b"ANTHROPIC_API_KEY or CLAUDE_CODE_OAUTH_TOKEN", completed.stderr)
        self.assertFalse(os.path.exists(self.out_path))
        self.assertEqual(self.stub_calls(), [])


class TheFindingsFile(AdapterTestCase):
    def test_an_empty_findings_list_exits_0_and_writes_a_file_with_no_findings(self):
        completed = self.run_adapter("empty")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(self.findings_file()["findings"], [])

    def test_a_duration_claude_code_under_reports_is_raised_to_the_adapters_own_clock(self):
        completed = self.run_adapter("slow_with_a_short_duration")
        self.assertEqual(completed.returncode, 0)
        self.assertGreaterEqual(self.findings_file()["usage"]["time_in_ms"], 2000)

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
        self.assertNotIn(API_KEY.encode("utf-8"), self.every_evidence_file())

    def test_the_oauth_token_alone_reaches_claude_code_unprinted_and_the_findings_file_is_written(self):
        del self.env["ANTHROPIC_API_KEY"]
        completed = self.run_adapter("good", CLAUDE_CODE_OAUTH_TOKEN=OAUTH_TOKEN)
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(os.path.exists(self.out_path))
        [variables] = self.stub_calls()
        self.assertEqual(variables["CLAUDE_CODE_OAUTH_TOKEN"], OAUTH_TOKEN)
        self.assertNotIn(OAUTH_TOKEN.encode("utf-8"), completed.stdout)
        self.assertNotIn(OAUTH_TOKEN.encode("utf-8"), completed.stderr)
        self.assertNotIn(OAUTH_TOKEN.encode("utf-8"), self.every_evidence_file())


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


class NoCredentialInTheEvidence(AdapterTestCase):
    """Property 1: No credential in the evidence."""

    def setUp(self):
        super().setUp()
        self.env["HOME"] = os.path.join(self.directory, "home")
        self.env["CLAUDE_CODE_OAUTH_TOKEN"] = OAUTH_TOKEN

    def test_the_copied_transcript_holds_redacted_in_place_of_the_api_key_and_the_oauth_token(self):
        self.run_adapter("leaks_credentials")
        transcript = self.evidence_bytes("transcripts", "-work-repo", "session.jsonl")
        self.assertIn(b"credentials [redacted] [redacted]", transcript)
        self.assertNotIn(API_KEY.encode("utf-8"), transcript)
        self.assertNotIn(OAUTH_TOKEN.encode("utf-8"), transcript)

    def test_claude_log_holds_redacted_in_place_of_the_api_key_and_the_oauth_token(self):
        self.run_adapter("leaks_credentials")
        claude_log = self.evidence_bytes("claude.log")
        self.assertIn(b"credentials [redacted] [redacted]", claude_log)
        self.assertNotIn(API_KEY.encode("utf-8"), claude_log)
        self.assertNotIn(OAUTH_TOKEN.encode("utf-8"), claude_log)

    def test_review_json_holds_redacted_and_no_evidence_file_holds_the_api_key_or_the_oauth_token(self):
        self.run_adapter("leaks_credentials")
        self.assertIn(b"credentials [redacted] [redacted]", self.evidence_bytes("review.json"))
        evidence = self.every_evidence_file()
        self.assertNotIn(API_KEY.encode("utf-8"), evidence)
        self.assertNotIn(OAUTH_TOKEN.encode("utf-8"), evidence)

    def test_the_findings_file_holds_redacted_in_place_of_the_api_key_and_the_oauth_token(self):
        self.run_adapter("leaks_credentials")
        with open(self.out_path, "rb") as handle:
            findings_file = handle.read()
        self.assertIn(b"credentials [redacted] [redacted]", findings_file)
        self.assertNotIn(API_KEY.encode("utf-8"), findings_file)
        self.assertNotIn(OAUTH_TOKEN.encode("utf-8"), findings_file)

    def test_a_default_run_does_not_pass_no_session_persistence_to_claude(self):
        self.run_adapter("good")
        [variables] = self.stub_calls()
        self.assertNotIn("--no-session-persistence", variables["argv"])

    def test_rb_keep_transcripts_0_runs_claude_without_session_persistence_and_keeps_no_transcripts(self):
        self.run_adapter("leaks_credentials", RB_KEEP_TRANSCRIPTS="0")
        [variables] = self.stub_calls()
        self.assertIn("--no-session-persistence", variables["argv"])
        self.assertTrue(os.path.exists(self.evidence_path("adapter.log")))
        self.assertFalse(os.path.exists(self.evidence_path("transcripts")))


class TheEvidenceFolder(AdapterTestCase):
    def test_claude_log_holds_the_review_runs_stderr_and_then_the_repair_runs(self):
        completed = self.run_adapter("unparseable_with_stderr,good_with_stderr")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(self.evidence_bytes("claude.log"), b"review run stderr\nrepair run stderr\n")

    def test_adapter_log_lines_carry_a_utc_timestamp_and_name_each_phase_in_order(self):
        self.run_adapter("unparseable,good")
        lines = self.evidence_bytes("adapter.log").decode("utf-8").splitlines()
        messages = []
        for line in lines:
            timestamp, message = line.split(" ", 1)
            datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            messages.append(message)
        phases = [
            "start octo/shop #17",
            "claude started",
            "claude finished with exit code 0",
            "repair started",
            "repair finished with exit code 0",
            "wrote 1 findings to {}".format(self.out_path),
        ]
        self.assertEqual([message for message in messages if message in phases], phases)

    def test_review_json_is_a_copy_of_the_review_file(self):
        self.run_adapter("good")
        with open(self.env["RB_REVIEW_PATH"], "rb") as handle:
            review = handle.read()
        self.assertEqual(self.evidence_bytes("review.json"), review)

    @unittest.skipIf(os.getuid() == 0, "root writes into a read-only folder")
    def test_an_unwritable_evidence_folder_still_exits_0_and_writes_the_findings_file(self):
        os.makedirs(self.evidence_path(), mode=0o500)
        self.addCleanup(os.chmod, self.evidence_path(), 0o700)
        completed = self.run_adapter("good")
        self.assertEqual(completed.returncode, 0)
        self.assertTrue(os.path.exists(self.out_path))
        self.assertEqual(os.listdir(self.evidence_path()), [])

    def test_a_non_zero_claude_exit_still_leaves_adapter_log_and_review_json(self):
        completed = self.run_adapter("good_then_fail")
        self.assertEqual(completed.returncode, 1)
        self.assertTrue(os.path.exists(self.evidence_path("adapter.log")))
        self.assertTrue(os.path.exists(self.evidence_path("review.json")))


class TheFindingsDoNotDependOnHowClaudeCodeEnded(AdapterTestCase):
    """Property 2: The findings do not depend on how Claude Code ended."""

    def test_a_final_file_then_a_sleep_is_ended_after_the_grace_with_exit_0_the_findings_of_good_and_a_log_line(self):
        self.run_adapter("good")
        findings_of_good = self.findings_file()["findings"]
        completed = self.run_adapter("final_then_sleep", RB_FINAL_GRACE_SECONDS="1", RB_TIMEOUT_SECONDS="8")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(self.findings_file()["findings"], findings_of_good)
        adapter_log = self.evidence_bytes("adapter.log").decode("utf-8")
        self.assertRegex(adapter_log, r"ended claude \d+ s after the review file turned final")

    def test_the_cost_reported_by_a_run_ended_after_the_grace_reaches_the_findings_file(self):
        completed = self.run_adapter("final_then_sleep", RB_FINAL_GRACE_SECONDS="1", RB_TIMEOUT_SECONDS="8")
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(self.findings_file()["usage"]["cost_usd"], 0.5)
        adapter_log = self.evidence_bytes("adapter.log").decode("utf-8")
        self.assertRegex(adapter_log, r"ended claude \d+ s after the review file turned final")


class TheGraceEndNeverComesEarly(AdapterTestCase):
    """Property 3: The grace end never comes early."""

    def test_a_first_pass_file_then_a_sleep_is_not_ended_by_the_grace_and_is_killed_at_the_time_limit(self):
        started = time.monotonic()
        completed = self.run_adapter("first_then_sleep", RB_FINAL_GRACE_SECONDS="1", RB_TIMEOUT_SECONDS="5")
        elapsed = time.monotonic() - started
        self.assertEqual(completed.returncode, 0)
        self.assertGreaterEqual(elapsed, 5)
        adapter_log = self.evidence_bytes("adapter.log").decode("utf-8")
        self.assertIn("claude killed after 5 seconds; reading the interim review file", adapter_log)
        self.assertNotIn("turned final", adapter_log)

    def test_a_final_file_and_an_exit_within_the_grace_is_not_killed_and_logs_no_grace_line(self):
        completed = self.run_adapter("final_then_exit_shortly", RB_FINAL_GRACE_SECONDS="6", RB_TIMEOUT_SECONDS="10")
        self.assertEqual(completed.returncode, 0)
        adapter_log = self.evidence_bytes("adapter.log").decode("utf-8")
        self.assertIn("claude finished with exit code 0", adapter_log)
        self.assertNotIn("turned final", adapter_log)

    def test_claude_code_exiting_on_its_own_between_the_final_check_and_the_kill_is_not_a_grace_end(self):
        spec = importlib.util.spec_from_file_location("reviewbench_agent", AGENT)
        agent = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent)
        marker = os.path.join(self.directory, "exited")
        checks = []

        def final_once_the_stub_has_exited(path):
            checks.append(path)
            deadline = time.monotonic() + 10
            while not os.path.exists(marker) and time.monotonic() < deadline:
                time.sleep(0.05)
            # The stub writes the marker just before it exits.
            time.sleep(1)
            return True

        original = agent.review_is_final
        agent.review_is_final = final_once_the_stub_has_exited
        self.addCleanup(setattr, agent, "review_is_final", original)
        env = dict(self.env, STUB_PLAN="marker_then_exit_5", STUB_EXIT_MARKER=marker)
        exit_code, _, ended = agent.run_claude(
            [self.env["RB_CLAUDE_BIN"]], "prompt", self.directory, env, 10,
            grace_seconds=0, review_path=self.env["RB_REVIEW_PATH"],
        )
        self.assertEqual(len(checks), 1)
        self.assertEqual(exit_code, 5)
        self.assertIsNone(ended)


if __name__ == "__main__":
    unittest.main()
