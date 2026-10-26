"""Proves the capture renderer in docs/captures/render.py draws a source faithfully and reproducibly.

Rendering a source twice gives the same bytes, and every character of the
source's body reaches the SVG's text in order once XML escaping and line
wrapping are undone. ``extract`` given an id the transcript lacks exits
non-zero and writes nothing.
"""

import importlib.util
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ElementTree

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RENDERER = os.path.join(ROOT, "docs", "captures", "render.py")

SVG_TEXT = "{http://www.w3.org/2000/svg}text"


def load_renderer():
    spec = importlib.util.spec_from_file_location("capture_render", RENDERER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render = load_renderer()

HEADER = "title: A session\ndate: 2026-10-22\nplugin: 0.16.0\nsource: session abc\nalt: A session & its <output>\n\n"

BODIES = [
    "> plain request\n● plain answer\n",
    "> " + "word " * 60 + "\n● " + "x" * 250 + "\n",
    "⏺ Bash(command: echo \"a < b && c > d\" | grep '&amp;')\n  continued <tag attr=\"v\"> & more\n",
    "> café naïve 日本語 テキスト — “quotes” ✓\n● emoji-free but wide: 中文中文中文 " + "é" * 120 + "\n",
    "● first\n\n  indented continuation\n" + "    " + "lead " * 40 + "\n",
    "",
]

ALPHABET = list("abcdefghijklmnopqrstuvwxyz      <>&\"'é日✓—") + ["  "]
PREFIXES = [render.AUTHOR, render.TEXT, render.TOOL, render.CONTINUATION, ""]


def random_body(generator):
    lines = []
    for _ in range(generator.randint(1, 12)):
        length = generator.choice([0, 5, 40, 99, 100, 101, 180, 320])
        text = "".join(generator.choice(ALPHABET) for _ in range(length))
        lines.append(generator.choice(PREFIXES) + text if text else "")
    return "\n".join(lines) + "\n"


def sources():
    generator = random.Random(20261022)
    bodies = BODIES + [random_body(generator) for _ in range(50)]
    return [HEADER + body for body in bodies]


def body_text(svg):
    """Return the unescaped text of the SVG's body lines, the title bar's and footer's text left out."""
    texts = [element.text or "" for element in ElementTree.fromstring(svg).iter(SVG_TEXT)]
    return texts[1:-1]


class RenderingIsDeterministicTest(unittest.TestCase):
    """Property 3: Rendering is deterministic."""

    def test_rendering_a_source_twice_gives_the_same_bytes(self):
        for source in sources():
            with self.subTest(source=source[len(HEADER):][:60]):
                first = render.render_svg(source).encode("utf-8")
                second = render.render_svg(source).encode("utf-8")
                self.assertEqual(first, second)


class RenderingKeepsTheTextTest(unittest.TestCase):
    """Property 4: Rendering keeps the text as recorded."""

    def test_every_body_character_reaches_the_svg_in_order(self):
        for source in sources():
            body = source[len(HEADER):]
            with self.subTest(body=body[:60]):
                svg = render.render_svg(source)
                self.assertEqual("".join(body_text(svg)), body.replace("\n", ""))

    def test_body_lines_survive_one_after_another(self):
        for source in sources():
            body = source[len(HEADER):]
            with self.subTest(body=body[:60]):
                rows = iter(body_text(render.render_svg(source)))
                for line in body.split("\n")[:-1] if body else []:
                    shown = next(rows)
                    while len(shown) < len(line):
                        shown += next(rows)
                    self.assertEqual(shown, line)
                self.assertEqual(list(rows), [])

    def test_long_lines_are_wrapped_at_one_hundred_columns(self):
        source = HEADER + "● " + "y" * 250 + "\n"
        rows = body_text(render.render_svg(source))
        self.assertGreater(len(rows), 1)
        self.assertLessEqual(len(rows[0]), render.COLUMNS)
        self.assertTrue(all(2 + len(row) <= render.COLUMNS for row in rows[1:]))


class ExtractUnknownIdTest(unittest.TestCase):
    """Extract refuses an id the transcript lacks and writes nothing."""

    def test_unknown_id_exits_non_zero_and_writes_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            captures = os.path.join(folder, "captures")
            os.mkdir(captures)
            script = os.path.join(captures, "render.py")
            shutil.copyfile(RENDERER, script)
            transcript = os.path.join(folder, "session.jsonl")
            record = {"uuid": "known", "type": "user", "message": {"content": "hello"}}
            with open(transcript, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
            before = sorted(os.listdir(folder)), sorted(os.listdir(captures))

            result = subprocess.run(
                [sys.executable, script, "extract", transcript, "--from", "known", "--to", "missing-id", "--name", "excerpt"],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing-id", result.stderr)
            self.assertEqual((sorted(os.listdir(folder)), sorted(os.listdir(captures))), before)


if __name__ == "__main__":
    unittest.main()
