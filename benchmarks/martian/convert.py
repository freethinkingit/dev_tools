"""Convert a run folder's findings files into Martian's benchmark_data.json.

Usage: python3 convert.py <run folder> <golden folder>

Each `<run folder>/findings/*.json` is a ReviewBench findings file. It is
matched to the golden pull request whose `url` or `original_url` is
`<pr.repo>/pull/<pr.pr_number>`, and becomes one record of
`<run folder>/benchmark_data.json`, keyed by the golden URL, holding the golden
comments and one `ponderly` review with one comment per finding. A findings
file with no golden pull request, two findings files for the same golden pull
request, or a golden folder that is missing or holds no `*.json` stops the
conversion with exit status 1 and writes nothing.
"""

import glob
import json
import os
import sys

TOOL = "ponderly"


def load_golden(golden_folder):
    """Return the golden records of every `*.json` file in `golden_folder`.

    Each record is the golden file's entry plus `source_file`, the name of the
    file it came from, and is reachable under its `url` and, when present, its
    `original_url`.

    Raises LookupError when `golden_folder` is missing or holds no `*.json`.
    """
    paths = sorted(glob.glob(os.path.join(golden_folder, "*.json")))
    if not paths:
        raise LookupError("golden folder %s not found or empty; run the setup target" % golden_folder)
    golden = {}
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            entries = json.load(handle)
        for entry in entries:
            record = dict(entry, source_file=os.path.basename(path))
            golden[entry["url"]] = record
            if entry.get("original_url"):
                golden[entry["original_url"]] = record
    return golden


def pull_request_url(findings):
    """Return the pull request URL a findings file names in `pr`."""
    return "%s/pull/%d" % (findings["pr"]["repo"].rstrip("/"), findings["pr"]["pr_number"])


def repository_name(url):
    """Return the `<repo>` part of a `https://github.com/<owner>/<repo>/...` URL."""
    return url.split("github.com/", 1)[1].split("/")[1]


def to_record(findings, golden_record):
    """Return the Martian_Data_File record for one findings file and its golden record."""
    golden_url = golden_record["url"]
    nwo = findings["pr"]["repo"].rstrip("/").split("github.com/", 1)[1]
    comments = [
        {"path": finding["file"], "line": finding["start_line"], "body": finding["message"]}
        for finding in findings["findings"]
    ]
    return {
        "pr_title": golden_record.get("pr_title"),
        "original_url": golden_record.get("original_url"),
        "source_repo": repository_name(golden_url),
        "golden_comments": golden_record.get("comments", []),
        "golden_source_file": golden_record["source_file"],
        "az_comment": None,
        "reviews": [
            {
                "tool": TOOL,
                "repo_name": nwo,
                "pr_url": golden_url,
                "review_comments": comments,
            }
        ],
    }


def convert(run_folder, golden_folder):
    """Return the Martian_Data_File for a run folder, keyed by golden URL.

    Raises LookupError naming the first findings file with no golden record,
    or the two findings files that match the same golden record.
    """
    golden = load_golden(golden_folder)
    data = {}
    matched_by = {}
    for path in sorted(glob.glob(os.path.join(run_folder, "findings", "*.json"))):
        with open(path, encoding="utf-8") as handle:
            findings = json.load(handle)
        url = pull_request_url(findings)
        if url not in golden:
            raise LookupError("%s: no golden record for %s" % (path, url))
        golden_url = golden[url]["url"]
        if golden_url in matched_by:
            raise LookupError(
                "%s and %s both match the golden record %s" % (matched_by[golden_url], path, golden_url)
            )
        matched_by[golden_url] = path
        data[golden_url] = to_record(findings, golden[url])
    return data


def main(argv):
    """Write `<run folder>/benchmark_data.json`; return the exit status."""
    if len(argv) != 3:
        print("usage: python3 convert.py <run folder> <golden folder>", file=sys.stderr)
        return 2
    run_folder, golden_folder = argv[1], argv[2]
    try:
        data = convert(run_folder, golden_folder)
    except LookupError as error:
        print("convert.py: %s" % error.args[0], file=sys.stderr)
        return 1
    with open(os.path.join(run_folder, "benchmark_data.json"), "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
