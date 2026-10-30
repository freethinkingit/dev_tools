"""ReviewBench entrypoint: run the ponderly review skill and write the Findings_File.

Reads the contract's RB_* variables and /work/pr/pr.json, runs Claude Code
headlessly on /work/repo with the plugin at /opt/ponderly, and writes the
Findings_File at RB_OUT. Exits 0 with the file when the review file parses,
1 with no file otherwise, so that ReviewBench retries, and 2 when a required
variable or input is missing. The credential is ANTHROPIC_API_KEY or, on a
Claude subscription, CLAUDE_CODE_OAUTH_TOKEN; one of the two must be set.
Beside the Findings_File it keeps a logs/ evidence folder: adapter.log,
claude.log, review.json and, unless RB_KEEP_TRANSCRIPTS is 0, transcripts/.
"""

import contextlib
import datetime
import json
import os
import pwd
import shutil
import signal
import subprocess
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import findings  # noqa: E402

REQUIRED_VARIABLES = (
    "RB_NWO",
    "RB_PR_NUMBER",
    "RB_BASE",
    "RB_HEAD",
    "RB_OUT",
    "RB_AGENT",
)
CREDENTIAL_VARIABLES = ("ANTHROPIC_API_KEY", "CLAUDE_CODE_OAUTH_TOKEN")
PLUGIN_DIR = "/opt/ponderly"
DEFAULT_CLAUDE_USER = "reviewer"
REPAIR_BUDGET_USD = "1"
TOKEN_FIELD_NAMES = (
    ("input_tokens", "inputTokens"),
    ("output_tokens", "outputTokens"),
    ("cache_creation_input_tokens", "cacheCreationInputTokens"),
    ("cache_read_input_tokens", "cacheReadInputTokens"),
)
KILLED_OUTPUT_WAIT_SECONDS = 5
POLL_SECONDS = 2
FINDINGS_SHAPE = (
    '{"pass": "first" or "final", "verdict": "holds", "findings" or null, '
    '"second_pass": true or false, "counts": {"candidates": integer, '
    '"removed_by_merge": integer, "removed_by_cap": integer, '
    '"removed_by_review": integer, '
    '"failed_arms": [string]}, "findings": [{"file": string, '
    '"start_line": integer, "end_line": integer, '
    '"severity": "high", "medium" or "low", "category": string, '
    '"message": string}]}'
)


def log(message):
    print(message, file=sys.stderr, flush=True)


class Evidence:
    """The evidence folder of one pull request's review, beside the Findings_File.

    A folder of None, or one that cannot be created or written, leaves a writer that
    only prints; the review goes on either way.
    """

    def __init__(self, folder, credentials, transcripts_kept=True):
        self.folder = folder
        self.credentials = [value for value in credentials if value]
        self.transcripts_kept = transcripts_kept
        self.writable = folder is not None
        if folder is None:
            return
        try:
            os.makedirs(folder, exist_ok=True)
        except OSError as error:
            self.disable("cannot create the evidence folder {}: {}".format(folder, error))

    def disable(self, reason):
        # The folder stays known so that redact still reaches the files already written.
        self.writable = False
        log("{}; keeping no further evidence".format(reason))

    def path(self, name):
        return os.path.join(self.folder, name)

    def log(self, message):
        log(message)
        if not self.writable:
            return
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        try:
            with open(self.path("adapter.log"), "a", encoding="utf-8") as handle:
                handle.write("{} {}\n".format(timestamp, message))
        except OSError as error:
            self.disable("cannot write adapter.log: {}".format(error))

    def claude_stderr(self):
        """Return a context manager giving the stderr= for Claude Code: claude.log, or None to inherit."""
        if self.writable:
            try:
                return open(self.path("claude.log"), "ab")
            except OSError as error:
                self.disable("cannot open claude.log: {}".format(error))
        return contextlib.nullcontext(None)

    def keep_review(self, review_path):
        if not self.writable or not os.path.isfile(review_path):
            return
        try:
            shutil.copyfile(review_path, self.path("review.json"))
        except OSError as error:
            self.log("cannot copy the review file to the evidence folder: {}".format(error))

    def keep_transcripts(self, home):
        if not self.writable or not self.transcripts_kept:
            return
        projects = os.path.join(home, ".claude", "projects") if home else None
        if projects is None or not os.path.isdir(projects):
            self.log("no session directory at {}; keeping no transcripts".format(projects))
            return
        try:
            shutil.copytree(projects, self.path("transcripts"), symlinks=True, dirs_exist_ok=True)
        except (OSError, shutil.Error) as error:
            self.log("cannot copy the transcripts to the evidence folder: {}".format(error))

    def redact(self):
        """Replace every credential value in every evidence file with [redacted]; return the files changed."""
        if self.folder is None:
            return 0
        secrets = [value.encode("utf-8") for value in self.credentials]
        changed = 0
        for directory, _, names in os.walk(self.folder):
            for name in names:
                if redact_file(os.path.join(directory, name), secrets):
                    changed += 1
        self.log("redacted credentials in {} evidence files".format(changed))
        return changed

    def redact_finding(self, finding):
        """Return a copy of the finding with every credential value in its text fields replaced by [redacted]."""
        redacted = dict(finding)
        for field, value in finding.items():
            if not isinstance(value, str):
                continue
            for secret in self.credentials:
                value = value.replace(secret, "[redacted]")
            redacted[field] = value
        return redacted

    def hand_over(self):
        """When the adapter is root, give the evidence folder and all under it to the owner of its parent folder.

        On a Linux host the bind-mounted output folder would otherwise hold root-owned files that the
        host user can neither read nor remove. File modes are left as they are.
        """
        if os.getuid() != 0 or self.folder is None or not os.path.isdir(self.folder):
            return
        try:
            owner = os.stat(os.path.dirname(self.folder) or ".")
            os.chown(self.folder, owner.st_uid, owner.st_gid, follow_symlinks=False)
            for directory, folders, names in os.walk(self.folder):
                for name in folders + names:
                    os.chown(os.path.join(directory, name), owner.st_uid, owner.st_gid, follow_symlinks=False)
        except OSError as error:
            self.log("cannot hand the evidence folder to the output folder's owner: {}".format(error))


def redact_file(path, secrets):
    """Return True when the file held a secret and now holds [redacted] in its place."""
    if os.path.islink(path):
        return False
    try:
        with open(path, "rb") as handle:
            content = handle.read()
        redacted = content
        for secret in secrets:
            redacted = redacted.replace(secret, b"[redacted]")
        if redacted == content:
            return False
        with open(path, "wb") as handle:
            handle.write(redacted)
        return True
    except OSError as error:
        # A file that cannot be rewritten may still hold the credential, so it goes.
        log("cannot redact {}, removing it: {}".format(path, error))
        with contextlib.suppress(OSError):
            os.remove(path)
        return False


def evidence_folder(env):
    findings_path = env.get("RB_OUT")
    if not findings_path:
        return None
    return os.path.join(os.path.dirname(findings_path) or ".", "logs")


def claude_home(env):
    """Return the home Claude Code runs with, where it keeps its sessions, or None when unknown."""
    if os.getuid() != 0:
        return env.get("HOME")
    try:
        return pwd.getpwnam(env.get("RB_CLAUDE_USER") or DEFAULT_CLAUDE_USER).pw_dir
    except KeyError:
        return None


def first_missing_variable(env):
    for name in REQUIRED_VARIABLES:
        if not env.get(name):
            return name
    if not any(env.get(name) for name in CREDENTIAL_VARIABLES):
        return " or ".join(CREDENTIAL_VARIABLES)
    return None


def read_settings(env):
    return {
        "model": env.get("RB_CONFIG_MODEL") or "opus",
        "effort": env.get("RB_CONFIG_EFFORT") or "high",
        "budget_usd": env.get("RB_CONFIG_BUDGET_USD") or "15",
    }


def text_or_none_given(value):
    # The skill reads the prompt's first non-empty line after the command as the title.
    if not isinstance(value, str) or not value.strip():
        return "none given"
    return value


def build_prompt(env, pull_request, review_path):
    command = "/ponderly:review {}...{} --json {}".format(
        env["RB_BASE"], env["RB_HEAD"], review_path
    )
    title = text_or_none_given(pull_request.get("title"))
    body = text_or_none_given(pull_request.get("body"))
    return "{}\n\n{}\n\n{}\n".format(command, title, body)


def child_environment(settings):
    env = dict(os.environ)
    env.update(
        {
            "DISABLE_TELEMETRY": "1",
            "DISABLE_AUTOUPDATER": "1",
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "CLAUDE_CODE_EFFORT_LEVEL": settings["effort"],
            "CLAUDE_CODE_SUBAGENT_MODEL": settings["model"],
            "CLAUDE_CODE_SUBAGENT_MODEL_FORCE": "1",
        }
    )
    return env


def claude_account(env, evidence):
    """Return the passwd entry Claude Code runs as, or None to run it as the adapter's own user.

    Raises KeyError when the adapter is root and the user RB_CLAUDE_USER names does not exist.
    """
    if os.getuid() != 0:
        evidence.log("adapter is not root; running claude as the adapter's own user and ignoring RB_CLAUDE_USER")
        return None
    return pwd.getpwnam(env.get("RB_CLAUDE_USER") or DEFAULT_CLAUDE_USER)


def run_claude(arguments, prompt, cwd, env, timeout_seconds, grace_seconds=None, review_path=None,
               stderr=None, account=None):
    """Run Claude Code with the prompt on stdin, as account when given; return (exit code, stdout, ended).

    ended is None when Claude Code exited on its own, "timeout" when it was killed at
    timeout_seconds, and "final" when it was killed after the review file at review_path had
    been final for grace_seconds. A grace_seconds of None never ends it early. stderr is where
    Claude Code's standard error goes; None leaves it on the adapter's.
    """
    account_arguments = {}
    if account is not None:
        # user= alone would leave the child in root's group and supplementary groups.
        account_arguments = {
            "user": account.pw_uid,
            "group": account.pw_gid,
            "extra_groups": [],
        }
    process = subprocess.Popen(
        arguments,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=stderr,
        cwd=cwd,
        env=env,
        start_new_session=True,
        **account_arguments,
    )
    chunks = []
    writer = threading.Thread(target=write_and_close, args=(process.stdin, prompt.encode("utf-8")), daemon=True)
    reader = threading.Thread(target=read_until_closed, args=(process.stdout, chunks), daemon=True)
    writer.start()
    reader.start()
    deadline = time.monotonic() + timeout_seconds
    first_final = None
    ended = None
    while process.poll() is None or reader.is_alive():
        now = time.monotonic()
        if now >= deadline:
            ended = "timeout"
            break
        claude_running = process.poll() is None
        if grace_seconds is not None and claude_running and review_is_final(review_path):
            if first_final is None:
                first_final = now
            if now - first_final >= grace_seconds:
                ended = "final"
                break
        else:
            first_final = None
        time.sleep(min(POLL_SECONDS, deadline - now))
    if ended is None:
        process.stdout.close()
        return process.returncode, b"".join(chunks), None
    # Claude Code spawns sub-agents and tools; killing only the child would leave them running.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    except PermissionError:
        # macOS refuses to signal a group whose only members are unreaped zombies.
        pass
    # A tool that left the process group can hold stdout open long after the kill.
    reader.join(KILLED_OUTPUT_WAIT_SECONDS)
    # A reader still blocked on the pipe holds its buffer lock, so closing it here would wait for that reader.
    if not reader.is_alive():
        process.stdout.close()
    exit_code = process.poll()
    # Claude Code can exit on its own between the poll that saw it running and the kill.
    exited_before_kill = exit_code is not None and exit_code != -signal.SIGKILL
    if ended == "final" and exited_before_kill:
        ended = None
    return exit_code, b"".join(chunks), ended


def write_and_close(stream, data):
    # Claude Code may exit, or be killed, before it reads the whole prompt.
    with contextlib.suppress(OSError):
        stream.write(data)
    with contextlib.suppress(OSError):
        stream.close()


def read_until_closed(stream, chunks):
    while True:
        chunk = stream.read1(65536)
        if not chunk:
            return
        chunks.append(chunk)


def review_is_final(path):
    """Return True when the review file at path parses and its pass is "final"."""
    text = read_text(path) if path else None
    if text is None:
        return False
    try:
        findings.parse_review_json(text)
    except ValueError:
        return False
    return json.loads(text).get("pass") == "final"


def usage_of(stdout):
    """Return the cost, duration and tokens of Claude Code's JSON result, or {} when absent."""
    try:
        result = json.loads(stdout.decode("utf-8", errors="replace"))
    except ValueError:
        return {}
    if not isinstance(result, dict):
        return {}
    usage = {}
    if isinstance(result.get("total_cost_usd"), (int, float)):
        usage["cost_usd"] = result["total_cost_usd"]
    if isinstance(result.get("duration_ms"), (int, float)):
        usage["time_in_ms"] = int(result["duration_ms"])
    # modelUsage covers the sub-agents' models; the top-level usage covers only the main session.
    model_usage = result.get("modelUsage")
    if isinstance(model_usage, dict):
        usage["total_tokens"] = sum(token_count(entry) for entry in model_usage.values())
    elif isinstance(result.get("usage"), dict):
        usage["total_tokens"] = token_count(result["usage"])
    return usage


def token_count(tokens):
    if not isinstance(tokens, dict):
        return 0
    total = 0
    for names in TOKEN_FIELD_NAMES:
        for name in names:
            value = tokens.get(name)
            if isinstance(value, int) and not isinstance(value, bool):
                total += value
                break
    return total


def add_usage(total, extra):
    for field, value in extra.items():
        total[field] = total.get(field, 0) + value


def read_text(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return None


def parse_review_file(path):
    """Return (candidates, refused, error) for the review file; error is None when it parses."""
    text = read_text(path)
    if text is None:
        return [], [], "review file missing or unreadable at {}".format(path)
    try:
        candidates, refused = findings.parse_review_json(text)
    except ValueError as error:
        return [], [], str(error)
    return candidates, refused, None


def failed_arms_of(path):
    """Return the lenses the review file names in counts.failed_arms, or [] when it names none."""
    try:
        counts = json.loads(read_text(path) or "").get("counts")
    except (ValueError, AttributeError):
        return []
    failed_arms = counts.get("failed_arms") if isinstance(counts, dict) else None
    return failed_arms if isinstance(failed_arms, list) else []


def repair_prompt(review_path, text, error, refused):
    if error is not None:
        problem = "It does not parse: {}".format(error)
    else:
        problem = "These entries were refused:\n" + "\n".join(
            "- {} in {}".format(item["error"], json.dumps(item["entry"])) for item in refused
        )
    return (
        "The JSON file at {path} should hold a findings object of this shape:\n"
        "{shape}\n\n"
        "{problem}\n\n"
        "Its text is:\n{text}\n\n"
        "Write the file again at {path} in that shape, keeping its findings, "
        "and do nothing else.\n"
    ).format(path=review_path, shape=FINDINGS_SHAPE, problem=problem, text=text)


def line_counter(repo_dir):
    root = os.path.realpath(repo_dir)

    def line_count_of(path):
        full_path = os.path.realpath(os.path.join(root, path))
        if not full_path.startswith(root + os.sep) or not os.path.isfile(full_path):
            return None
        with open(full_path, "rb") as handle:
            content = handle.read()
        unterminated_last_line = 1 if content and not content.endswith(b"\n") else 0
        return content.count(b"\n") + unterminated_last_line

    return line_count_of


def main():
    started = time.monotonic()
    env = os.environ
    transcripts_kept = env.get("RB_KEEP_TRANSCRIPTS") != "0"
    evidence = Evidence(
        evidence_folder(env),
        [env.get(name) for name in CREDENTIAL_VARIABLES],
        transcripts_kept,
    )
    review_path = env.get("RB_REVIEW_PATH") or "/tmp/review.json"
    # A review file left from an earlier attempt would pass for this run's output.
    if os.path.exists(review_path):
        os.remove(review_path)
    evidence.log("start {} #{}".format(env.get("RB_NWO"), env.get("RB_PR_NUMBER")))
    try:
        return review_pull_request(env, evidence, review_path, transcripts_kept, started)
    except Exception as error:
        evidence.log("no findings file written: {}: {}".format(type(error).__name__, error))
        raise
    finally:
        evidence.keep_review(review_path)
        evidence.keep_transcripts(claude_home(env))
        evidence.redact()
        evidence.hand_over()


def review_pull_request(env, evidence, review_path, transcripts_kept, started):
    missing = first_missing_variable(env)
    if missing:
        evidence.log("missing required variable {}".format(missing))
        return 2

    settings = read_settings(env)
    evidence.log("model={model} effort={effort} budget_usd={budget_usd}".format(**settings))

    pr_json_path = env.get("RB_PR_JSON") or "/work/pr/pr.json"
    pr_text = read_text(pr_json_path)
    try:
        pull_request = json.loads(pr_text) if pr_text is not None else None
    except ValueError:
        pull_request = None
    if not isinstance(pull_request, dict):
        evidence.log("missing or unreadable pull request file {}".format(pr_json_path))
        return 2

    claude_bin = env.get("RB_CLAUDE_BIN") or "claude"
    repo_dir = env.get("RB_REPO_DIR") or "/work/repo"
    timeout_seconds = float(env.get("RB_TIMEOUT_SECONDS") or 1500)
    repair_timeout_seconds = float(env.get("RB_REPAIR_TIMEOUT_SECONDS") or 180)
    total_seconds = float(env.get("RB_TOTAL_SECONDS") or 1770)
    grace_seconds = float(env.get("RB_FINAL_GRACE_SECONDS") or 60)
    review_dir = os.path.dirname(review_path) or "."
    session_arguments = [] if transcripts_kept else ["--no-session-persistence"]

    try:
        account = claude_account(env, evidence)
    except KeyError:
        evidence.log("no such user {} for RB_CLAUDE_USER".format(env.get("RB_CLAUDE_USER") or DEFAULT_CLAUDE_USER))
        return 2

    claude_env = child_environment(settings)
    if account is not None:
        claude_env["HOME"] = account.pw_dir
    review_arguments = [
        claude_bin,
        "-p",
        "--output-format", "json",
        "--plugin-dir", PLUGIN_DIR,
        "--permission-mode", "bypassPermissions",
        "--model", settings["model"],
        "--effort", settings["effort"],
        "--max-budget-usd", settings["budget_usd"],
        *session_arguments,
        "--add-dir", review_dir,
    ]
    evidence.log("claude started")
    with evidence.claude_stderr() as stderr:
        exit_code, stdout, ended = run_claude(
            review_arguments,
            build_prompt(env, pull_request, review_path),
            repo_dir,
            claude_env,
            timeout_seconds,
            grace_seconds,
            review_path,
            stderr,
            account,
        )
    usage = usage_of(stdout)
    # Claude Code's duration_ms has reported 40 seconds for an eleven-minute review, so the
    # adapter's own clock is the floor and the larger of the two is recorded.
    elapsed_ms = int((time.monotonic() - started) * 1000)
    usage["time_in_ms"] = max(usage.get("time_in_ms", 0), elapsed_ms)
    if ended == "final":
        evidence.log("ended claude {:.0f} s after the review file turned final".format(
            time.time() - os.path.getmtime(review_path)
        ))
    elif ended == "timeout":
        evidence.log("claude killed after {:.0f} seconds; reading the interim review file".format(timeout_seconds))
    elif exit_code != 0:
        evidence.log("claude exited {}".format(exit_code))
        return 1
    else:
        evidence.log("claude finished with exit code 0")
    if not os.path.exists(review_path):
        evidence.log("no review file at {}".format(review_path))
        return 1

    candidates, refused, error = parse_review_file(review_path)
    if error is not None or refused:
        evidence.log("review file needs repair: {}".format(error or "{} refused entries".format(len(refused))))
        repair_arguments = [
            claude_bin,
            "-p",
            "--output-format", "json",
            "--permission-mode", "bypassPermissions",
            "--model", settings["model"],
            "--effort", settings["effort"],
            "--max-budget-usd", REPAIR_BUDGET_USD,
            *session_arguments,
            "--add-dir", review_dir,
        ]
        seconds_left = total_seconds - (time.monotonic() - started)
        repair_limit_seconds = min(repair_timeout_seconds, seconds_left)
        if repair_limit_seconds > 0:
            evidence.log("repair started")
            with evidence.claude_stderr() as stderr:
                repair_exit_code, repair_stdout, repair_ended = run_claude(
                    repair_arguments,
                    repair_prompt(review_path, read_text(review_path) or "", error, refused),
                    review_dir,
                    claude_env,
                    repair_limit_seconds,
                    None,
                    None,
                    stderr,
                    account,
                )
            if repair_ended == "timeout":
                evidence.log("repair killed after {:.0f} seconds".format(repair_limit_seconds))
            else:
                evidence.log("repair finished with exit code {}".format(repair_exit_code))
            add_usage(usage, usage_of(repair_stdout))
        else:
            evidence.log("no time left for the repair run; reading the review file as it is")
        candidates, refused, error = parse_review_file(review_path)
        if error is not None:
            evidence.log("review file still does not parse after repair: {}".format(error))
            return 1

    file_lists_no_findings = not candidates and not refused
    failed_arms = failed_arms_of(review_path)
    if file_lists_no_findings and failed_arms:
        evidence.log("review lists no findings and names failed arms: {}".format(
            ", ".join(str(lens) for lens in failed_arms)
        ))
        return 1

    kept, dropped = findings.validate(candidates, line_counter(repo_dir))
    dropped["refused"] = len(refused)
    evidence.log(" ".join("dropped_{}={}".format(reason, count) for reason, count in dropped.items()))

    kept = [evidence.redact_finding(finding) for finding in kept]
    findings.write_atomically(env["RB_OUT"], findings.build_findings_file(kept, env, usage))
    evidence.log("wrote {} findings to {}".format(len(kept), env["RB_OUT"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
