"""Write the score report of one judged ReviewBench run.

    python3 benchmarks/reviewbench/report.py <run folder>

Reads the judge's ``scoring/results.json``, the ``usage`` of every
``findings/*.json``, and the ``run.json`` the harness writes, then writes
``report.md`` into the run folder and prints it. A field ``run.json`` lacks is
reported as "unknown", except the plugin version, which is then read from
``plugin.json`` and marked so. Exits 1 naming the file when ``scoring/results.json``
is absent, since the ``judge`` target writes it.
"""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
PLUGIN_MANIFEST = ROOT / "plugins" / "ponderly" / ".claude-plugin" / "plugin.json"

UNKNOWN = "unknown"
NOT_DEFINED = "—"

METRIC_HEADER = (
    "| Average | {} | Grounded P | Grounded R | Grounded F1 | Augmented P | Augmented R | Augmented F1 | Golden TPs |\n"
    "|---|---|---|---|---|---|---|---|---|"
)


def f1(precision, recall):
    """Return the harmonic mean of precision and recall, None when either is None, 0.0 when both are zero."""
    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def percent(value):
    if value is None:
        return NOT_DEFINED
    return "{:.1f}%".format(value * 100)


def read_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def read_run_info(run_dir):
    path = run_dir / "run.json"
    if not path.is_file():
        return {}
    return read_json(path)


def plugin_version_line(run_info):
    recorded = run_info.get("plugin_version")
    if recorded is not None:
        return "{} (recorded at run time)".format(recorded)
    if not PLUGIN_MANIFEST.is_file():
        return UNKNOWN
    return "{} (read from plugin.json now)".format(read_json(PLUGIN_MANIFEST).get("version", UNKNOWN))


def count(metrics, key):
    value = metrics.get(key)
    if value is None:
        return UNKNOWN
    return str(value)


def read_usages(run_dir):
    usages = []
    for path in sorted((run_dir / "findings").glob("*.json")):
        usage = read_json(path).get("usage")
        if isinstance(usage, dict):
            usages.append(usage)
    return usages


def metric_row(average, name, metrics):
    grounded_precision = metrics.get("grounded_precision")
    grounded_recall = metrics.get("grounded_recall")
    augmented_precision = metrics.get("augmented_precision")
    augmented_recall = metrics.get("augmented_recall")
    cells = [
        average,
        name,
        percent(grounded_precision),
        percent(grounded_recall),
        percent(f1(grounded_precision, grounded_recall)),
        percent(augmented_precision),
        percent(augmented_recall),
        percent(f1(augmented_precision, augmented_recall)),
        count(metrics, "golden_tp_count"),
    ]
    return "| " + " | ".join(cells) + " |"


def stratum_table(results, group, label):
    rows = []
    for average in ("macro", "micro"):
        strata = results.get(average, {}).get(group, {})
        for name in sorted(strata):
            rows.append(metric_row(average, name, strata[name]))
    if not rows:
        return "The judge reported no {} split for this run.".format(label.lower())
    return METRIC_HEADER.format(label) + "\n" + "\n".join(rows)


def overall_section(results):
    rows = []
    for average in ("macro", "micro"):
        overall = results.get(average, {}).get("overall")
        if overall is not None:
            rows.append(metric_row(average, "overall", overall))
    micro = results.get("micro", {}).get("overall", {})
    return "\n".join([
        "## Overall",
        "",
        "Grounded precision is the share of the review's findings matched to the golden set whose golden entry is "
        "a true problem; grounded recall is the share of the golden set's true problems the review found; grounded "
        "F1 is their harmonic mean, so it is high only when both are. Augmented precision is the share of all the "
        "review's findings that are real problems, counting a finding outside the golden set that the judge "
        "classed as one; augmented recall adds those findings to the problems there were to find. Macro averages each pull "
        "request's score, so every pull request weighs the same; micro pools every finding first, so pull "
        "requests with more findings weigh more. A dash means the ratio is undefined because its denominator "
        "was zero.",
        "",
        METRIC_HEADER.format("Set"),
        "\n".join(rows),
        "",
        "Across the run, pooled: the review made {} findings; the golden set holds {} true problems; the judge "
        "matched {} findings to the golden set, of which {} were true problems; and {} findings outside the golden "
        "set were classed as real problems.".format(
            count(micro, "candidate_count"),
            count(micro, "golden_tp_count"),
            count(micro, "matched_count"),
            count(micro, "matched_tp_count"),
            count(micro, "novel_tp_count"),
        ),
    ])


def usage_section(usages, findings_count):
    durations = [usage["time_in_ms"] for usage in usages if usage.get("time_in_ms") is not None]
    costs = [usage["cost_usd"] for usage in usages if usage.get("cost_usd") is not None]
    if durations:
        mean_duration = "{:.1f} s".format(sum(durations) / len(durations) / 1000)
    else:
        mean_duration = UNKNOWN
    if costs:
        total_cost = "${:.2f}".format(sum(costs))
        mean_cost = "${:.2f}".format(sum(costs) / len(costs))
    else:
        total_cost = UNKNOWN
        mean_cost = UNKNOWN
    return "\n".join([
        "## Duration and cost",
        "",
        "Mean review duration is the wall-clock time Claude Code took to review one pull request, averaged over "
        "the {} of {} findings files that record it.".format(len(durations), findings_count),
        "",
        "Mean review duration: {}".format(mean_duration),
        "",
        "Model cost is what Claude Code's own usage output reports the reviews cost, summed over the {} of {} "
        "findings files that record it, then divided by that count for the mean.".format(len(costs), findings_count),
        "",
        "Total model cost: {}".format(total_cost),
        "",
        "Mean model cost per pull request: {}".format(mean_cost),
    ])


def header_section(run_info, results):
    commands = run_info.get("commands") or []
    if commands:
        command_lines = ["```"] + [str(command) for command in commands] + ["```"]
    else:
        command_lines = [UNKNOWN]
    return "\n".join([
        "# ReviewBench score report",
        "",
        "- Plugin version: {}".format(plugin_version_line(run_info)),
        "- Model: {}".format(run_info.get("model", UNKNOWN)),
        "- Effort: {}".format(run_info.get("effort", UNKNOWN)),
        "- Set: {}".format(run_info.get("set", UNKNOWN)),
        "- Judge model: {}".format(run_info.get("judge_model", UNKNOWN)),
        "- Image: {}".format(run_info.get("image", UNKNOWN)),
        "- Date: {}".format(run_info.get("started", UNKNOWN)),
        "- Pull requests judged: {}".format(results.get("pr_count", UNKNOWN)),
        "",
        "Commands that produced it:",
        "",
    ] + command_lines)


def render_report(run_dir):
    """Return the text of ``report.md`` for the run folder ``run_dir``; raises FileNotFoundError without ``scoring/results.json``."""
    results_path = run_dir / "scoring" / "results.json"
    if not results_path.is_file():
        raise FileNotFoundError(str(results_path))
    results = read_json(results_path)
    findings_count = len(list((run_dir / "findings").glob("*.json")))
    sections = [
        header_section(read_run_info(run_dir), results),
        overall_section(results),
        "## By severity\n\nThe same numbers for the golden set's problems of each severity alone.\n\n"
        + stratum_table(results, "by_severity", "Severity"),
        "## By category\n\nThe same numbers for the golden set's problems of each category alone.\n\n"
        + stratum_table(results, "by_category", "Category"),
        usage_section(read_usages(run_dir), findings_count),
    ]
    return "\n\n".join(sections) + "\n"


def report(run_dir):
    """Write ``report.md`` into ``run_dir`` and return its path; raises FileNotFoundError without ``scoring/results.json``."""
    run_dir = Path(run_dir)
    text = render_report(run_dir)
    target = run_dir / "report.md"
    target.write_text(text, encoding="utf-8")
    return target


def main(argv=None):
    """Write and print the report of the run folder named on the command line; exit 1 when the judge has not run."""
    parser = argparse.ArgumentParser(description="Write the score report of one judged ReviewBench run.")
    parser.add_argument("run_dir", help="the run folder, such as benchmarks/reviewbench/runs/<timestamp>-<set>")
    arguments = parser.parse_args(argv)
    try:
        target = report(arguments.run_dir)
    except FileNotFoundError as missing:
        print(
            "{} is missing; run the judge first: make -C benchmarks/reviewbench judge RUN={}".format(
                missing, Path(arguments.run_dir).resolve()
            ),
            file=sys.stderr,
        )
        return 1
    sys.stdout.write(target.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
