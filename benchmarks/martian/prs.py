"""Resolve the Martian benchmark's pull requests into prs.json.

Usage: python3 prs.py [<golden folder>]

Reads every `*.json` golden file in `<golden folder>`, by default the
`.martian/offline/golden_comments` the setup target clones beside this script,
in file-name order and in each file's own order, asks
`gh api repos/{owner}/{repo}/pulls/{n}` for each golden `url`, and writes
`prs.json` beside this script: an array of
`{nwo, pr_number, title, body, base, head, golden_url}`. A missing or empty
golden folder, a golden URL that is not a pull request, or a `gh` call that
fails stops with exit status 1 and writes nothing.
"""

import glob
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_GOLDEN_FOLDER = os.path.join(HERE, ".martian", "offline", "golden_comments")
OUTPUT = os.path.join(HERE, "prs.json")


def golden_urls(golden_folder):
    """Return every golden pull request URL in `golden_folder`, in the golden files' order.

    Raises LookupError when the folder is missing or holds no `*.json`.
    """
    paths = sorted(glob.glob(os.path.join(golden_folder, "*.json")))
    if not paths:
        raise LookupError("golden folder %s not found or empty; run the setup target" % golden_folder)
    urls = []
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            urls.extend(entry["url"] for entry in json.load(handle))
    return urls


def split_pull_url(url):
    """Return `(owner/repo, number)` for a `https://github.com/<owner>/<repo>/pull/<n>` URL.

    Raises LookupError when the URL is not a GitHub pull request URL.
    """
    parts = url.rstrip("/").split("github.com/", 1)[-1].split("/")
    if len(parts) != 4 or parts[2] != "pull" or not parts[3].isdigit():
        raise LookupError("%s is not a GitHub pull request URL" % url)
    return "%s/%s" % (parts[0], parts[1]), int(parts[3])


def resolve(url):
    """Return the prs.json entry for one golden pull request URL, read from the GitHub API.

    Raises LookupError naming the URL when `gh api` fails, or naming `gh` when it is not installed.
    """
    nwo, number = split_pull_url(url)
    try:
        result = subprocess.run(
            ["gh", "api", "repos/%s/pulls/%d" % (nwo, number)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except FileNotFoundError:
        raise LookupError("missing: gh")
    if result.returncode != 0:
        raise LookupError("gh api failed for %s: %s" % (url, result.stderr.strip()))
    pull = json.loads(result.stdout)
    return {
        "nwo": nwo,
        "pr_number": number,
        "title": pull.get("title") or "",
        "body": pull.get("body") or "",
        "base": pull["base"]["sha"],
        "head": pull["head"]["sha"],
        "golden_url": url,
    }


def main(argv):
    """Write prs.json; return the exit status."""
    if len(argv) > 2:
        print("usage: python3 prs.py [<golden folder>]", file=sys.stderr)
        return 2
    golden_folder = argv[1] if len(argv) == 2 else DEFAULT_GOLDEN_FOLDER
    try:
        entries = [resolve(url) for url in golden_urls(golden_folder)]
    except LookupError as error:
        print("prs.py: %s" % error.args[0], file=sys.stderr)
        return 1
    with open(OUTPUT, "w", encoding="utf-8") as handle:
        json.dump(entries, handle, indent=2)
        handle.write("\n")
    print("wrote %d pull requests to %s" % (len(entries), OUTPUT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
