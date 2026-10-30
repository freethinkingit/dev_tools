"""Turn the review skill's findings object into a ReviewBench Findings_File.

Pure functions the adapter calls: parse the skill's JSON, keep only findings
that land inside a file at the head commit, build the Contract object and
write it so that a reader never sees a half-written file.
"""

import json
import os

SEVERITY_ORDER = ("high", "medium", "low")
MAX_FINDINGS = 40
FINDING_STRING_FIELDS = ("file", "category", "message")
FINDING_INTEGER_FIELDS = ("start_line", "end_line")
USAGE_FIELDS = ("time_in_ms", "cost_usd", "total_tokens")


def parse_review_json(text):
    """Return the candidate findings of the skill's findings object and the refused ones.

    The first value is the list of findings with every field present and of
    the right type. The second is a list of {"index", "entry", "error"} for
    each finding refused, where error names the field it lacks or mistypes.
    Raises ValueError only when the text is not JSON, not an object, or has
    no "findings" array.
    """
    try:
        review = json.loads(text)
    except json.JSONDecodeError as error:
        raise ValueError("review: not valid JSON ({})".format(error)) from error
    if not isinstance(review, dict):
        raise ValueError("review: expected an object")
    if "findings" not in review:
        raise ValueError("findings: missing")
    if not isinstance(review["findings"], list):
        raise ValueError("findings: expected an array")
    accepted = []
    refused = []
    for index, candidate in enumerate(review["findings"]):
        try:
            check_candidate(candidate, "findings[{}]".format(index))
        except ValueError as error:
            refused.append({"index": index, "entry": candidate, "error": str(error)})
            continue
        accepted.append(candidate)
    return accepted, refused


def check_candidate(candidate, where):
    if not isinstance(candidate, dict):
        raise ValueError("{}: expected an object".format(where))
    for field in FINDING_STRING_FIELDS + FINDING_INTEGER_FIELDS + ("severity",):
        if field not in candidate:
            raise ValueError("{}.{}: missing".format(where, field))
    for field in FINDING_STRING_FIELDS:
        if not isinstance(candidate[field], str):
            raise ValueError("{}.{}: expected a string".format(where, field))
    for field in FINDING_INTEGER_FIELDS:
        value = candidate[field]
        # bool is a subclass of int, so true would otherwise pass as line 1.
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError("{}.{}: expected an integer".format(where, field))
    if candidate["severity"] not in SEVERITY_ORDER:
        raise ValueError(
            "{}.severity: expected one of {}".format(where, ", ".join(SEVERITY_ORDER))
        )


def normalise_path(path):
    path = path.replace("\\", "/")
    while path.startswith("./") or path.startswith("/"):
        path = path[2:] if path.startswith("./") else path[1:]
    return path


def validate(candidates, line_count_of):
    """Return the findings that land inside a file at head, and the drop counts.

    line_count_of(path) gives the file's line count at head, or None when the
    file is absent; it is never asked for a path that is empty or only dots
    and slashes, which counts as an absent file. The findings come back with
    normalised paths, ordered high, medium, low with input order kept inside
    a severity, and at most 40 of them. The second value maps each reason,
    "absent_file", "lines_out_of_range" and "over_limit", to how many were
    dropped for it.
    """
    dropped = {"absent_file": 0, "lines_out_of_range": 0, "over_limit": 0}
    kept = []
    for candidate in candidates:
        path = normalise_path(candidate["file"])
        # git show head: with no path lists the root tree, so it would count lines.
        if not path.strip("./"):
            dropped["absent_file"] += 1
            continue
        line_count = line_count_of(path)
        if line_count is None:
            dropped["absent_file"] += 1
            continue
        if not 1 <= candidate["start_line"] <= candidate["end_line"] <= line_count:
            dropped["lines_out_of_range"] += 1
            continue
        finding = dict(candidate)
        finding["file"] = path
        kept.append(finding)
    kept.sort(key=lambda finding: SEVERITY_ORDER.index(finding["severity"]))
    dropped["over_limit"] = max(0, len(kept) - MAX_FINDINGS)
    return kept[:MAX_FINDINGS], dropped


def build_findings_file(findings, env, usage):
    """Return the ReviewBench Contract object for one pull request.

    env holds RB_NWO, RB_PR_NUMBER, RB_BASE, RB_HEAD and RB_AGENT; usage holds
    any of time_in_ms, cost_usd and total_tokens, and only those are copied.
    Raises KeyError when an RB_* value is missing and ValueError when
    RB_PR_NUMBER is not a whole number.
    """
    agent = env["RB_AGENT"]
    return {
        "pr": {
            "repo": "https://github.com/{}".format(env["RB_NWO"]),
            "pr_number": int(env["RB_PR_NUMBER"]),
            "base": env["RB_BASE"],
            "head": env["RB_HEAD"],
        },
        "agent": agent,
        "findings": [
            {
                "file": finding["file"],
                "start_line": finding["start_line"],
                "end_line": finding["end_line"],
                "message": finding["message"],
                "producer": agent,
            }
            for finding in findings
        ],
        "usage": {field: usage[field] for field in USAGE_FIELDS if field in usage},
    }


def write_atomically(path, obj):
    """Write obj as JSON to path + ".tmp", then rename it over path."""
    temporary_path = str(path) + ".tmp"
    with open(temporary_path, "w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2)
        handle.write("\n")
    os.replace(temporary_path, path)
