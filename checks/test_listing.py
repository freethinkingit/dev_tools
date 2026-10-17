"""The plugin folder meets the plugin directory's mechanical listing rules.

The directory portal rejects a plugin whose README holds fewer than 40 words
outside code blocks, that has no license, or whose icon is not a square PNG of
512 to 2048 pixels a side. These checks catch each before a submission does.
"""

import json
import re
import struct
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "freethinking"

README_MIN_WORDS = 40
ICON_MIN_PX = 512
ICON_MAX_PX = 2048
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
FENCE_OPENER = re.compile(r"`{3,}|~{3,}")


def read_manifest(folder):
    """Return the parsed ``.claude-plugin/plugin.json`` of a plugin folder."""
    return json.loads((folder / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))


def readme_word_count(folder):
    """Return the number of words in the folder's ``README.md`` outside fenced code blocks, or None if there is no README."""
    readme = folder / "README.md"
    if not readme.is_file():
        return None
    return sum(len(line.split()) for line in prose_lines(readme.read_text(encoding="utf-8")))


def prose_lines(text):
    """Yield the lines of Markdown text that lie outside fenced code blocks; an unclosed fence runs to the end."""
    fence = None
    for line in text.splitlines():
        stripped = line.strip()
        if fence is None:
            opener = FENCE_OPENER.match(stripped)
            if opener:
                fence = opener.group()
            else:
                yield line
        elif stripped.startswith(fence) and stripped == fence[0] * len(stripped):
            fence = None


def has_license(folder, manifest):
    """Return True when the folder has a ``LICENSE`` file or the manifest has a ``license`` field."""
    return (folder / "LICENSE").is_file() or bool(manifest.get("license"))


def icon_size(folder, manifest):
    """Return the ``(width, height)`` of the PNG the manifest's ``icon`` field names.

    Raises ValueError naming the problem when the field is missing or not a
    string, the path is absolute or leaves the plugin folder, the file is
    absent, or the file is not a PNG.
    """
    icon = manifest.get("icon")
    if not icon:
        raise ValueError("the manifest has no icon field")
    if not isinstance(icon, str):
        raise ValueError("icon {!r} is not a string".format(icon))
    if Path(icon).is_absolute():
        raise ValueError("icon {} is an absolute path; it must be relative to the plugin folder".format(icon))
    path = folder / icon
    if not path.resolve().is_relative_to(folder.resolve()):
        raise ValueError("icon {} resolves outside the plugin folder".format(icon))
    if not path.is_file():
        raise ValueError("icon {} names no file".format(icon))
    header = path.read_bytes()[:24]
    if len(header) < 24 or header[:8] != PNG_SIGNATURE or header[12:16] != b"IHDR":
        raise ValueError("icon {} is not a PNG".format(icon))
    return struct.unpack(">II", header[16:24])


class ListingTest(unittest.TestCase):
    def setUp(self):
        self.manifest = read_manifest(PLUGIN)

    def test_readme_has_enough_words(self):
        words = readme_word_count(PLUGIN)
        self.assertIsNotNone(words, "{} has no README.md".format(PLUGIN.relative_to(ROOT)))
        self.assertGreaterEqual(
            words,
            README_MIN_WORDS,
            "README.md has {} words outside fenced blocks; the minimum is {}".format(words, README_MIN_WORDS),
        )

    def test_license_is_declared(self):
        self.assertTrue(
            has_license(PLUGIN, self.manifest),
            "{} has no LICENSE file and plugin.json has no license field".format(PLUGIN.relative_to(ROOT)),
        )

    def test_icon_is_a_square_png_of_the_right_size(self):
        try:
            width, height = icon_size(PLUGIN, self.manifest)
        except ValueError as error:
            self.fail(str(error))
        self.assertEqual(width, height, "icon is {} by {} px; it must be square".format(width, height))
        for side in (width, height):
            with self.subTest(side=side):
                self.assertTrue(
                    ICON_MIN_PX <= side <= ICON_MAX_PX,
                    "icon side is {} px; it must be {} to {} px".format(side, ICON_MIN_PX, ICON_MAX_PX),
                )


if __name__ == "__main__":
    unittest.main()
