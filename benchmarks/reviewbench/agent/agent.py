"""ReviewBench entrypoint: run the ponderly review skill and write the Findings_File.

Reads the contract's RB_* variables and /work/pr/pr.json, runs Claude Code
headlessly on /work/repo with the plugin at /opt/ponderly, and writes the
Findings_File at RB_OUT. Exits 0 with the file when the review file parses,
1 with no file otherwise, so that ReviewBench retries, and 2 when a required
variable or input is missing. The credential is ANTHROPIC_API_KEY or, on a
Claude subscription, CLAUDE_CODE_OAUTH_TOKEN; one of the two must be set.
"""

import json
import os
import pwd
import signal
import subprocess
import sys
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
FINDINGS_SHAPE = (
    '{"pass": "first" or "final", "verdict": "holds", "findings" or null, '
    '"second_pass": true or false, "counts": {"candidates": integer, '
    '"removed_by_merge": integer, "removed_by_review": integer, '
    '"failed_arms": [string]}, "findings": [{"file": string, '
    '"start_line": integer, "end_line": integer, '
    '"severity": "high", "medium" or "low", "category": string, '
    '"message": string}]}'
)


def log(message):
    print(message, file=sys.stderr, flush=True)


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


def claude_account(env):
    """Return the passwd entry Claude Code runs as, or None to run it as the adapter's own user.

    Raises KeyError when the adapter is root and the user RB_CLAUDE_USER names does not exist.
    """
    if os.getuid() != 0:
        log("adapter is not root; running claude as the adapter's own user and ignoring RB_CLAUDE_USER")
        return None
    return pwd.getpwnam(env.get("RB_CLAUDE_USER") or DEFAULT_CLAUDE_USER)


def run_claude(arguments, prompt, cwd, env, timeout_seconds, account=None):
    """Run Claude Code with the prompt on stdin, as account when given; return (exit code, stdout, killed)."""
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
        cwd=cwd,
        env=env,
        start_new_session=True,
        **account_arguments,
    )
    try:
        stdout, _ = process.communicate(prompt.encode("utf-8"), timeout=timeout_seconds)
        return process.returncode, stdout, False
    except subprocess.TimeoutExpired:
        # Claude Code spawns sub-agents and tools; killing only the child would leave them running.
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        # A tool that left the process group can hold stdout open long after the kill.
        try:
            stdout, _ = process.communicate(timeout=KILLED_OUTPUT_WAIT_SECONDS)
        except subprocess.TimeoutExpired as error:
            stdout = error.output or b""
        return process.poll(), stdout, True


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
    missing = first_missing_variable(env)
    if missing:
        log("missing required variable {}".format(missing))
        return 2

    settings = read_settings(env)
    log("model={model} effort={effort} budget_usd={budget_usd}".format(**settings))

    pr_json_path = env.get("RB_PR_JSON") or "/work/pr/pr.json"
    pr_text = read_text(pr_json_path)
    try:
        pull_request = json.loads(pr_text) if pr_text is not None else None
    except ValueError:
        pull_request = None
    if not isinstance(pull_request, dict):
        log("missing or unreadable pull request file {}".format(pr_json_path))
        return 2

    claude_bin = env.get("RB_CLAUDE_BIN") or "claude"
    review_path = env.get("RB_REVIEW_PATH") or "/tmp/review.json"
    repo_dir = env.get("RB_REPO_DIR") or "/work/repo"
    timeout_seconds = float(env.get("RB_TIMEOUT_SECONDS") or 1500)
    repair_timeout_seconds = float(env.get("RB_REPAIR_TIMEOUT_SECONDS") or 180)
    total_seconds = float(env.get("RB_TOTAL_SECONDS") or 1770)
    review_dir = os.path.dirname(review_path) or "."

    # A review file left from an earlier attempt would pass for this run's output.
    if os.path.exists(review_path):
        os.remove(review_path)

    try:
        account = claude_account(env)
    except KeyError:
        log("no such user {} for RB_CLAUDE_USER".format(env.get("RB_CLAUDE_USER") or DEFAULT_CLAUDE_USER))
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
        "--no-session-persistence",
        "--add-dir", review_dir,
    ]
    exit_code, stdout, killed = run_claude(
        review_arguments,
        build_prompt(env, pull_request, review_path),
        repo_dir,
        claude_env,
        timeout_seconds,
        account,
    )
    usage = usage_of(stdout)
    # Claude Code's duration_ms has reported 40 seconds for an eleven-minute review, so the
    # adapter's own clock is the floor and the larger of the two is recorded.
    elapsed_ms = int((time.monotonic() - started) * 1000)
    usage["time_in_ms"] = max(usage.get("time_in_ms", 0), elapsed_ms)
    if killed:
        log("claude killed after {:.0f} seconds; reading the interim review file".format(timeout_seconds))
    elif exit_code != 0:
        log("claude exited {}".format(exit_code))
        return 1
    if not os.path.exists(review_path):
        log("no review file at {}".format(review_path))
        return 1

    candidates, refused, error = parse_review_file(review_path)
    if error is not None or refused:
        log("review file needs repair: {}".format(error or "{} refused entries".format(len(refused))))
        repair_arguments = [
            claude_bin,
            "-p",
            "--output-format", "json",
            "--permission-mode", "bypassPermissions",
            "--model", settings["model"],
            "--effort", settings["effort"],
            "--max-budget-usd", REPAIR_BUDGET_USD,
            "--no-session-persistence",
            "--add-dir", review_dir,
        ]
        seconds_left = total_seconds - (time.monotonic() - started)
        repair_limit_seconds = min(repair_timeout_seconds, seconds_left)
        if repair_limit_seconds > 0:
            _, repair_stdout, _ = run_claude(
                repair_arguments,
                repair_prompt(review_path, read_text(review_path) or "", error, refused),
                review_dir,
                claude_env,
                repair_limit_seconds,
                account,
            )
            add_usage(usage, usage_of(repair_stdout))
        else:
            log("no time left for the repair run; reading the review file as it is")
        candidates, refused, error = parse_review_file(review_path)
        if error is not None:
            log("review file still does not parse after repair: {}".format(error))
            return 1

    file_lists_no_findings = not candidates and not refused
    failed_arms = failed_arms_of(review_path)
    if file_lists_no_findings and failed_arms:
        log("review lists no findings and names failed arms: {}".format(
            ", ".join(str(lens) for lens in failed_arms)
        ))
        return 1

    kept, dropped = findings.validate(candidates, line_counter(repo_dir))
    dropped["refused"] = len(refused)
    log(" ".join("dropped_{}={}".format(reason, count) for reason, count in dropped.items()))

    findings.write_atomically(env["RB_OUT"], findings.build_findings_file(kept, env, usage))
    log("wrote {} findings to {}".format(len(kept), env["RB_OUT"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
