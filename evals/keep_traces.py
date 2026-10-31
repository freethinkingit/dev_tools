"""Copy each eval run's trace and last message into the results folder, then
delete the runner's kept sandboxes.

Run by the Makefile's eval targets after ``claude plugin eval --keep-temp``:
``python3 evals/keep_traces.py <results dir>``. Reads ``aggregate-result.json``
there, writes ``traces/<case>-<arm>-run<n>.jsonl`` and ``.md`` beside it, and
removes the sandbox folder that held each trace. A results folder without the
aggregate file, as a run that stopped early leaves, is reported and skipped.
"""
import json
import os
import shutil
import sys


def last_message_of(trace_path):
    """Return the final assistant text of a trace, or '' when it has none."""
    text = ""
    with open(trace_path, encoding="utf-8") as trace:
        for line in trace:
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            message = event.get("message") if event.get("type") == "assistant" else None
            if not isinstance(message, dict):
                continue
            parts = [
                block.get("text", "")
                for block in message.get("content", [])
                if isinstance(block, dict) and block.get("type") == "text"
            ]
            if parts:
                text = "\n".join(parts)
    return text


def sandbox_of(trace_path):
    """Return the sandbox folder a trace lives in: the parent of its out/ folder."""
    out_dir = os.path.dirname(trace_path)
    return os.path.dirname(out_dir) if os.path.basename(out_dir) == "out" else out_dir


def remove_sandbox(sandbox):
    """Delete a kept sandbox; the runner seals parts of it read-only, so open them first."""
    for folder, subfolders, files in os.walk(sandbox):
        os.chmod(folder, 0o700)
        for name in subfolders + files:
            path = os.path.join(folder, name)
            if not os.path.islink(path):
                os.chmod(path, 0o700)
    shutil.rmtree(sandbox, ignore_errors=True)


def keep_traces(results_dir):
    aggregate_path = os.path.join(results_dir, "aggregate-result.json")
    if not os.path.exists(aggregate_path):
        print("keep_traces: no aggregate-result.json in {}; nothing kept".format(results_dir))
        return
    with open(aggregate_path, encoding="utf-8") as aggregate_file:
        aggregate = json.load(aggregate_file)
    traces_dir = os.path.join(results_dir, "traces")
    sandboxes = set()
    kept = 0
    for case in aggregate.get("cases", []):
        for arm, runs in case.get("arms", {}).items():
            for number, run in enumerate(runs, 1):
                trace_path = run.get("tracePath")
                if not trace_path or not os.path.exists(trace_path):
                    continue
                os.makedirs(traces_dir, exist_ok=True)
                stem = "{}-{}-run{}".format(case["name"], arm, number)
                shutil.copyfile(trace_path, os.path.join(traces_dir, stem + ".jsonl"))
                with open(os.path.join(traces_dir, stem + ".md"), "w", encoding="utf-8") as last:
                    last.write(last_message_of(trace_path))
                sandboxes.add(sandbox_of(trace_path))
                kept += 1
    for sandbox in sandboxes:
        remove_sandbox(sandbox)
    print("keep_traces: kept {} trace(s) under {}".format(kept, traces_dir))


if __name__ == "__main__":
    keep_traces(sys.argv[1])
