"""Write a Martian offline run's score report.

    python3 benchmarks/martian/report.py <run folder> [<golden folder>]

Reads ``<run folder>/scoring/evaluations.json``, the judge's output, and the
golden comment files in ``<golden folder>``, by default the
``.martian/offline/golden_comments`` the setup target clones beside this
script, and writes and prints
``<run folder>/report.md``: precision, recall and F1 for each reviewed tool
under Martian's Strict, Core and All profiles, scored as Martian's dashboard
scores them, with the judge model, the image settings and the date taken from
``<run folder>/run.json`` ("unknown" for any field it lacks). Exits 1 naming
the file or folder that is missing.
"""

import json
import sys
from pathlib import Path

PROFILES = (
    ("Strict", frozenset({"bug", "security", "concurrency", "data", "api"})),
    ("Core", frozenset({
        "bug", "security", "concurrency", "data", "api",
        "perf", "test_gap", "doc_defect",
    })),
    ("All", frozenset({
        "bug", "security", "concurrency", "data", "api",
        "perf", "test_gap", "doc_defect", "style", "speculative",
    })),
)

UNKNOWN = "unknown"
NOT_DEFINED = "—"
DEFAULT_GOLDEN_DIR = Path(__file__).resolve().parent / ".martian" / "offline" / "golden_comments"


def load_golden_categories(golden_dir):
    """Return a map from each golden comment's text to its category."""
    if not golden_dir.is_dir():
        sys.exit("golden folder {} not found; run the setup target".format(golden_dir))
    categories = {}
    for golden_file in sorted(golden_dir.glob("*.json")):
        records = json.loads(golden_file.read_text(encoding="utf-8"))
        for record in records:
            for comment in record.get("comments", []):
                if comment.get("comment") and comment.get("category"):
                    categories[comment["comment"]] = comment["category"]
    if not categories:
        sys.exit("no golden comments with a category in {}".format(golden_dir))
    return categories


def category_of(entry, golden_categories):
    return entry.get("category") or golden_categories.get(entry.get("golden_comment", ""), "")


def ratio(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator


def f1(precision, recall):
    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def score(evaluations, golden_categories):
    """Return ``{tool: {profile: {tp, fp, fn, prs, precision, recall, f1}}}``.

    A match to a golden comment outside a profile's categories counts as
    neither a true nor a false positive under that profile; false positives
    are the same under every profile.
    """
    totals = {}
    for tool_evals in evaluations.values():
        for tool, review in tool_evals.items():
            if review.get("skipped"):
                continue
            tool_totals = totals.setdefault(
                tool, {name: {"tp": 0, "fp": 0, "fn": 0, "prs": 0} for name, _ in PROFILES})
            for name, profile_categories in PROFILES:
                counts = tool_totals[name]
                counts["tp"] += sum(
                    1 for match in review.get("true_positives", [])
                    if category_of(match, golden_categories) in profile_categories)
                counts["fn"] += sum(
                    1 for miss in review.get("false_negatives", [])
                    if category_of(miss, golden_categories) in profile_categories)
                counts["fp"] += review.get("fp", 0)
                counts["prs"] += 1
    for tool_totals in totals.values():
        for counts in tool_totals.values():
            counts["precision"] = ratio(counts["tp"], counts["tp"] + counts["fp"])
            counts["recall"] = ratio(counts["tp"], counts["tp"] + counts["fn"])
            counts["f1"] = f1(counts["precision"], counts["recall"])
    return totals


def percent(value):
    if value is None:
        return NOT_DEFINED
    return "{:.1f}%".format(value * 100)


def render(totals, run):
    """Return the report's Markdown text for ``score``'s totals and the run settings."""
    commands = run.get("commands") or []
    lines = [
        "# Martian Code Review Bench, offline",
        "",
        "- Date: {}".format(run.get("started", UNKNOWN)),
        "- Judge model: {}".format(run.get("judge_model", UNKNOWN)),
        "- Judge endpoint: {}".format(run.get("judge_base_url", UNKNOWN)),
        "- Image settings: image {}, model {}, effort {}".format(
            run.get("image", UNKNOWN), run.get("model", UNKNOWN), run.get("effort", UNKNOWN)),
        "- Commands: {}".format("; ".join("`{}`".format(c) for c in commands) or UNKNOWN),
        "",
        "Martian's judge matched each review's findings against the human golden comments "
        "of its pull request. Precision is the share of findings that matched a golden "
        "comment the profile counts, so a lower number means more noise. Recall is the "
        "share of the profile's golden comments that a finding matched, so a lower number "
        "means more missed issues. F1 is the harmonic mean of the two, high only when both "
        "are. A finding that matched a golden comment outside the profile's categories "
        "counts neither for nor against the score. TP, FP and FN are the counts of matched "
        "golden comments, unmatched findings and missed golden comments. A dash means the "
        "ratio is undefined because its denominator was zero.",
    ]
    for name, profile_categories in PROFILES:
        lines += [
            "",
            "## {}".format(name),
            "",
            "Golden comments counted: {}.".format(", ".join(sorted(profile_categories))),
            "",
            "| Tool | Pull requests | Precision | Recall | F1 | TP | FP | FN |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for tool in sorted(totals):
            counts = totals[tool][name]
            lines.append("| {} | {} | {} | {} | {} | {} | {} | {} |".format(
                tool, counts["prs"], percent(counts["precision"]), percent(counts["recall"]),
                percent(counts["f1"]), counts["tp"], counts["fp"], counts["fn"]))
    return "\n".join(lines) + "\n"


def main(argv=None):
    """Write and print ``report.md`` for the run folder and optional golden folder in ``argv``."""
    args = sys.argv[1:] if argv is None else argv
    if len(args) not in (1, 2):
        sys.exit("usage: python3 report.py <run folder> [<golden folder>]")
    run_dir = Path(args[0])
    evaluations_path = run_dir / "scoring" / "evaluations.json"
    if not evaluations_path.is_file():
        sys.exit("{} not found; run the judge target first".format(evaluations_path))
    golden_categories = load_golden_categories(
        Path(args[1]) if len(args) == 2 else DEFAULT_GOLDEN_DIR)
    run_path = run_dir / "run.json"
    run = json.loads(run_path.read_text(encoding="utf-8")) if run_path.is_file() else {}
    text = render(score(json.loads(evaluations_path.read_text(encoding="utf-8")), golden_categories), run)
    (run_dir / "report.md").write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
