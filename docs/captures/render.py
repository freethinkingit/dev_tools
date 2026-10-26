"""Turn excerpts of real Claude Code sessions into terminal-window SVGs.

    python3 docs/captures/render.py extract <transcript> --from <uuid> --to <uuid> --name <name>
    python3 docs/captures/render.py render <name>

``extract`` copies the text of a range of messages from a session's ``.jsonl``
into ``docs/captures/<name>.txt``, a header of ``key: value`` lines, a blank
line, then the excerpt. ``render`` draws ``docs/images/<name>.svg`` from that
source with ``render_svg``, which gives the same bytes for the same input.
A tool call is drawn with its whole input, since the text may not be trimmed,
so choose ranges that hold no Write or Edit of a large file.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

CAPTURES = Path(__file__).resolve().parent
IMAGES = CAPTURES.parent / "images"

HEADER_FIELDS = ("title", "date", "plugin", "source", "alt")

AUTHOR = "> "
TEXT = "● "
TOOL = "⏺ "
CONTINUATION = "  "

# The skill loader's message is the one record that names the plugin version a session ran;
# other mentions of the plugin cache are commands and their output.
SKILL_BASE = re.compile(r"^Base directory for this skill: \S*/freethinking/(\d[\w.\-]*)/skills/")

# The harness wraps what it adds to a user turn in hyphenated tags, such as task notifications,
# shell output and system reminders; the author typed none of it. A paste is <pasted_content>.
HARNESS_ONLY = re.compile(r"\s*(?:<([a-z]+(?:-[a-z]+)+)>.*?</\1>\s*)+", re.DOTALL)
COMMAND_TAG = re.compile(r"<(command-name|command-args|command-message)>(.*?)</\1>", re.DOTALL)
BASH_INPUT = re.compile(r"\s*<bash-input>(.*)</bash-input>\s*", re.DOTALL)
# A subagent's final report reaches its launcher as a meta user record: a frame line, the
# harness's preamble, the report with every line indented, then the harness's notes.
HAND_BACK = re.compile(
    r"Another Claude session sent a message:\n<agent-message from=\"[^\"]*\">\n\[Subagent hand-back\][^\n]*\n(.*?)\n</agent-message>",
    re.DOTALL,
)
# The three ways the harness records the author's answer to an AskUserQuestion call:
# a chosen option, free text, and a question turned down with a note.
QUESTION_ANSWERS = ("Your questions have been answered:", "The user answered:", "To tell you how to proceed, the user said:")
# When a hand-back looks like instructions, the harness adds this note and writes "<" as "<\".
HARNESS_NOTE = "[harness: "

COLUMNS = 100
CHAR_WIDTH = 9
LINE_HEIGHT = 20
FONT_SIZE = 15
PAD = 20
TITLE_BAR = 36
FOOTER = 36
WIDTH = COLUMNS * CHAR_WIDTH + 2 * PAD

COLOURS = {
    AUTHOR: "#7fc8f8",
    TEXT: "#e6e6e6",
    TOOL: "#a6e3a1",
}
BACKGROUND = "#1e1e2e"
BAR = "#2a2a3c"
MUTED = "#8a8aa0"
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"


def read_records(transcript):
    with open(transcript, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def prefixed(prefix, text):
    lines = text.split("\n")
    return [prefix + lines[0]] + [CONTINUATION + line if line else "" for line in lines[1:]]


def tool_call(part):
    arguments = []
    for key, value in part.get("input", {}).items():
        shown = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        arguments.append("{}: {}".format(key, shown))
    return "{}({})".format(part.get("name", ""), ", ".join(arguments))


def typed(text):
    if not HARNESS_ONLY.fullmatch(text):
        return text
    tags = dict(COMMAND_TAG.findall(text))
    if "command-name" in tags:
        name = tags["command-name"].strip()
        command = name if name.startswith("/") else "/" + name
        arguments = tags.get("command-args", "").strip()
        return "{} {}".format(command, arguments) if arguments else command
    bash = BASH_INPUT.fullmatch(text)
    if bash:
        return "! " + bash.group(1)
    return None


def part_text(content):
    if isinstance(content, str):
        return content
    return "".join(part.get("text", "") for part in content or [] if part.get("type") == "text")


def hand_back(text):
    match = HAND_BACK.match(text)
    if not match:
        return None
    lines = [line[len(CONTINUATION):] if line.startswith(CONTINUATION) else line for line in match.group(1).split("\n")]
    if lines and lines[0].startswith(HARNESS_NOTE):
        lines = lines[2:] if len(lines) > 1 and not lines[1].strip() else lines[1:]
        lines = [line.replace("<\\", "<") for line in lines]
    return "\n".join(lines)


def message_blocks(record):
    if record.get("type") not in ("user", "assistant") or record.get("isCompactSummary"):
        return []
    content = (record.get("message") or {}).get("content")
    if isinstance(content, str):
        content = [{"type": "text", "text": content}]
    if record.get("isMeta"):
        reports = [hand_back(part.get("text", "")) for part in content or [] if part.get("type") == "text"]
        return [prefixed(TOOL, report) for report in reports if report is not None]
    blocks = []
    for part in content or []:
        kind = part.get("type")
        if kind == "tool_result":
            answer = part_text(part.get("content"))
            if answer.startswith(QUESTION_ANSWERS):
                blocks.append(prefixed(CONTINUATION, answer))
        elif kind == "text" and record["type"] == "user":
            text = typed(part.get("text", ""))
            if text is not None:
                blocks.append(prefixed(AUTHOR, text))
        elif kind == "text":
            blocks.append(prefixed(TEXT, part.get("text", "")))
        elif kind == "tool_use":
            blocks.append(prefixed(TOOL, tool_call(part)))
    return blocks


def skill_versions(record):
    if record.get("type") != "user" or not record.get("isMeta"):
        return []
    content = (record.get("message") or {}).get("content")
    texts = [content] if isinstance(content, str) else [part.get("text", "") for part in content or [] if part.get("type") == "text"]
    return [match.group(1) for text in texts for match in [SKILL_BASE.match(text)] if match]


def extract(transcript, first, last, name, force=False):
    """Write ``docs/captures/<name>.txt`` from the records ``first`` to ``last``.

    Exits non-zero, writing nothing, when an id is not in the transcript or the
    source already exists and ``force`` is not set.
    """
    target = CAPTURES / "{}.txt".format(name)
    if target.exists() and not force:
        sys.exit("{} exists; pass --force to overwrite it and its redactions".format(target))
    records = read_records(transcript)
    index = {record["uuid"]: position for position, record in enumerate(records) if "uuid" in record}
    missing = [uuid for uuid in (first, last) if uuid not in index]
    if missing:
        sys.exit("not in {}: {}".format(transcript, ", ".join(missing)))
    start, end = index[first], index[last]
    if start > end:
        sys.exit("--from {} comes after --to {} in {}".format(first, last, transcript))

    versions = [version for record in records[: end + 1] for version in skill_versions(record)]
    header = {
        "title": "",
        "date": records[start].get("timestamp", "")[:10],
        "plugin": versions[-1] if versions else "",
        "source": "session {}".format(records[start].get("sessionId", "")),
        "alt": "",
    }
    body = []
    for record in records[start : end + 1]:
        for block in message_blocks(record):
            if body:
                body.append("")
            body.extend(block)

    lines = ["{}: {}".format(key, header[key]).rstrip() for key in HEADER_FIELDS]
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines + [""] + body) + "\n")
    print(target)


def parse_source(source_text):
    head, _, body = source_text.partition("\n\n")
    fields = dict.fromkeys(HEADER_FIELDS, "")
    for line in head.split("\n"):
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    lines = body.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return fields, lines


def break_at(text, width, keep):
    # A break inside the prefix or a run of leading spaces would leave a screen line with no text.
    space = text.rfind(" ", keep, width)
    return space + 1 if space >= 0 and text[:space].strip() else width


def wrap(text, width, keep=0):
    pieces = []
    while len(text) > width:
        cut = break_at(text, width, keep)
        pieces.append(text[:cut])
        text = text[cut:]
        keep = 0
    pieces.append(text)
    return pieces


def screen_lines(body):
    colour = COLOURS[TEXT]
    shown = []
    for line in body:
        prefix = line[:2]
        if prefix in COLOURS:
            colour = COLOURS[prefix]
        indent = 2 if prefix in COLOURS or prefix == CONTINUATION else 0
        first = wrap(line, COLUMNS, indent)[0]
        shown.append((0, colour, first))
        if len(first) < len(line):
            shown.extend((indent, colour, piece) for piece in wrap(line[len(first):], COLUMNS - indent))
    return shown


def text_element(x, y, fill, text, extra=""):
    return '<text x="{}" y="{}" fill="{}"{} xml:space="preserve">{}</text>'.format(x, y, fill, extra, escape(text))


def render_svg(source_text):
    """Return the SVG for a capture source as a string; the same input always gives the same bytes."""
    fields, body = parse_source(source_text)
    shown = screen_lines(body)
    height = TITLE_BAR + PAD + len(shown) * LINE_HEIGHT + FOOTER
    attribute = {'"': "&quot;"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="{0}" height="{1}" viewBox="0 0 {0} {1}" role="img">'.format(WIDTH, height),
        "<title>{}</title>".format(escape(fields["alt"])),
        '<rect width="{}" height="{}" rx="8" fill="{}"/>'.format(WIDTH, height, BACKGROUND),
        '<rect width="{}" height="{}" rx="8" fill="{}"/>'.format(WIDTH, TITLE_BAR, BAR),
        '<rect y="{}" width="{}" height="8" fill="{}"/>'.format(TITLE_BAR - 8, WIDTH, BAR),
        '<circle cx="20" cy="18" r="6" fill="#ff5f57"/>',
        '<circle cx="40" cy="18" r="6" fill="#febc2e"/>',
        '<circle cx="60" cy="18" r="6" fill="#28c840"/>',
        '<g font-family="{}" font-size="{}">'.format(escape(FONT, attribute), FONT_SIZE),
        text_element(WIDTH // 2, 23, MUTED, fields["title"], ' text-anchor="middle"'),
    ]
    top = TITLE_BAR + PAD + FONT_SIZE
    for row, (column, colour, text) in enumerate(shown):
        parts.append(text_element(PAD + column * CHAR_WIDTH, top + row * LINE_HEIGHT, colour, text))
    footer = "{} · freethinking {}".format(fields["date"], fields["plugin"])
    parts.append(text_element(WIDTH - PAD, height - 14, MUTED, footer, ' text-anchor="end"'))
    parts.append("</g>")
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def render(name):
    """Write ``docs/images/<name>.svg`` from ``docs/captures/<name>.txt``."""
    source = CAPTURES / "{}.txt".format(name)
    if not source.is_file():
        sys.exit("no capture source {}".format(source))
    IMAGES.mkdir(exist_ok=True)
    target = IMAGES / "{}.svg".format(name)
    with open(target, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_svg(source.read_text(encoding="utf-8")))
    print(target)


def main(argv=None):
    """Run the ``extract`` or ``render`` command given on the command line."""
    parser = argparse.ArgumentParser(description="Turn excerpts of real Claude Code sessions into terminal-window SVGs.")
    commands = parser.add_subparsers(dest="command", required=True)
    extract_command = commands.add_parser("extract", help="copy a range of a transcript's messages into docs/captures/<name>.txt")
    extract_command.add_argument("transcript")
    extract_command.add_argument("--from", dest="first", required=True, help="uuid of the first record")
    extract_command.add_argument("--to", dest="last", required=True, help="uuid of the last record")
    extract_command.add_argument("--name", required=True)
    extract_command.add_argument("--force", action="store_true", help="overwrite an existing source")
    render_command = commands.add_parser("render", help="draw docs/images/<name>.svg from docs/captures/<name>.txt")
    render_command.add_argument("name")
    arguments = parser.parse_args(argv)
    if arguments.command == "extract":
        extract(arguments.transcript, arguments.first, arguments.last, arguments.name, arguments.force)
    else:
        render(arguments.name)


if __name__ == "__main__":
    main()
