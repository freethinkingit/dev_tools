"""Every name, path, link, command and image the documentation mentions exists, and every capture matches its source.

The pages are the root README, the plugin's README, llms.txt and every
Markdown file under docs/. A failure names the page, the line and the name
that does not resolve, so the page can be fixed without searching for it.
"""

import importlib.util
import os
import re
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = Path("plugins") / "ponderly"
SKILLS_DIR = PLUGIN / "skills"
AGENTS_DIR = PLUGIN / "agents"
RULES_DIR = PLUGIN / "rules"
HOOKS_DIR = PLUGIN / "hooks"
LISTING_PAGE = PLUGIN / "README.md"
REFERENCE = Path("docs") / "reference.md"
LLMS = Path("llms.txt")
CAPTURES = Path("docs") / "captures"
IMAGES = Path("docs") / "images"
RENDERER = ROOT / CAPTURES / "render.py"

CHECKED_FOLDERS = ("plugins/", "evals/", "checks/", "docs/", ".github/", ".claude-plugin/", "bin/")
ROOT_FILES = ("README.md", "LICENSE", "Makefile", "llms.txt")
PATTERN_CHARACTERS = ("<", "*", "{")
ENUMERATED_TARGETS = {"eval-skill-": "skills", "eval-rule-": "rules", "eval-agent-": "agents"}
MAKE_OPTIONS_WITH_VALUE = ("-C", "-f", "-I", "-o", "-W", "--directory", "--file", "--makefile", "--include-dir")
COMPONENT_PATHS = {"skill": "skills/{}/?", "agent": "agents/{}\\.md", "rule": "rules/{}\\.md"}

FENCE_OPENER = re.compile(r"`{3,}|~{3,}")
CODE_SPAN = re.compile(r"`((?:[^`\n]|\n(?![ \t]*\n))+)`")
IMAGE = re.compile(r"!\[([^\[\]]*)\]\(\s*<?([^)\s>]*)>?(?:\s+\"[^\"]*\")?\s*\)")
LINK = re.compile(r"\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?([^)\s>]*)>?(?:\s+\"[^\"]*\")?\s*\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
HTML_ALT = re.compile(r"""\balt\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
HTML_SRC = re.compile(r"""\bsrc\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.IGNORECASE)
OWN_REPOSITORY = re.compile(r"^https://github\.com/sabind/ponderly/(?:blob|tree)/main/([^#?]*)(#.*)?$")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
SKILL_COMMAND = re.compile(r"/ponderly:([\w-]+)")
AGENT_NAME = re.compile(r"(?:(?<![\w/.@-])|(?<=@agent-))ponderly:([\w-]+)")
MAKE_COMMAND = re.compile(r"^\s*(?:\$\s+)?make\s+(.*)$")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
MAKE_RULE = re.compile(r"^([^\s:=#][^:=#]*?)\s*::?(?!=)")

SECRET_PATTERNS = (
    ("a GitHub token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})")),
    ("an Anthropic or OpenAI key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}")),
    ("an AWS access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("a Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}")),
    ("a private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("a bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}")),
    ("a credential", re.compile(r"(?i)\b(?:password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\s*[:=]\s*['\"]?[^\s'\"]{8,}")),
    ("an email address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")),
    ("a home-directory path", re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+")),
)


def load_renderer():
    spec = importlib.util.spec_from_file_location("docs_capture_render", RENDERER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


render_svg = load_renderer().render_svg


def doc_pages(root=ROOT):
    """Return every Doc_Page in the tree at root: the two READMEs, llms.txt and every Markdown file under docs/."""
    pages = [root / "README.md", root / LISTING_PAGE, root / LLMS]
    pages.extend(sorted((root / "docs").rglob("*.md")))
    return pages


def normalised(path):
    return Path(os.path.normpath(str(path)))


def inside_repository(path, root=ROOT):
    normal = normalised(path)
    return normal == root or root in normal.parents


def relative(path, root=ROOT):
    return normalised(path).relative_to(root).as_posix()


def split_fences(text):
    """Return the text with fenced blocks blanked and, separately, with everything but fenced blocks blanked.

    Both keep every line in its place, so an offset in either gives the page's line number.
    """
    prose, fenced = [], []
    fence = None
    for line in text.split("\n"):
        stripped = line.strip()
        if fence is None:
            opener = FENCE_OPENER.match(stripped)
            if opener:
                fence = opener.group()
                prose.append("")
                fenced.append("")
            else:
                prose.append(line)
                fenced.append("")
        else:
            if stripped.startswith(fence) and stripped == fence[0] * len(stripped):
                fence = None
                fenced.append("")
            else:
                fenced.append(line)
            prose.append("")
    return "\n".join(prose), "\n".join(fenced)


def line_at(text, offset):
    return text.count("\n", 0, offset) + 1


def blanked(match):
    return re.sub(r"[^\n]", " ", match.group())


def blank_code_spans(prose):
    return CODE_SPAN.sub(blanked, prose)


def images_and_links(prose):
    """Return (line, target) for every image, then every link, outside code; a linked image gives both."""
    searchable = blank_code_spans(prose)
    found = [(line_at(prose, match.start()), match.group(2)) for match in IMAGE.finditer(searchable)]
    without_images = IMAGE.sub(blanked, searchable)
    found.extend((line_at(prose, match.start()), match.group(2)) for match in LINK.finditer(without_images))
    return found


def heading_slugs(path):
    """Return the GitHub anchors of a Markdown file's headings, numbered the way GitHub numbers repeats."""
    prose, _ = split_fences(path.read_text(encoding="utf-8-sig"))
    slugs = set()
    seen = {}
    for line in prose.split("\n"):
        match = HEADING.match(line)
        if not match:
            continue
        slug = github_slug(match.group(2))
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        slugs.add(slug if count == 0 else "{}-{}".format(slug, count))
    return slugs


def github_slug(heading):
    """Return the anchor GitHub gives a heading: lower case, punctuation but hyphens dropped, spaces to hyphens."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading)
    text = re.sub(r"<[^>]+>", "", text).lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def resolve_target(page, target, root=ROOT):
    """Return the local path and anchor a link target names, or None when it points outside the repository."""
    own = OWN_REPOSITORY.match(target)
    if own:
        return root / own.group(1), (own.group(2) or "")[1:]
    if SCHEME.match(target):
        return None
    path_part, _, anchor = target.partition("#")
    if not path_part:
        return page, anchor
    if path_part.startswith("/"):
        return root / path_part.lstrip("/"), anchor
    return page.parent / path_part, anchor


def link_failures(page, text, root=ROOT):
    """Yield a failure for each link or image on the page whose file or heading does not exist."""
    prose, _ = split_fences(text)
    for line, target in images_and_links(prose):
        yield from target_failures(page, line, target, root)
    for match in HTML_IMAGE.finditer(blank_code_spans(prose)):
        source = HTML_SRC.search(match.group())
        if source:
            yield from target_failures(page, line_at(prose, match.start()), source.group(1) or source.group(2), root)


def target_failures(page, line, target, root=ROOT):
    where = "{}:{}".format(relative(page, root), line)
    if not target:
        yield "{}: a link has no target".format(where)
        return
    resolved = resolve_target(page, target, root)
    if resolved is None:
        return
    path, anchor = resolved
    if not inside_repository(path, root):
        yield "{}: {} names a file outside the repository".format(where, target)
    elif not path.exists():
        yield "{}: {} names no file".format(where, target)
    elif anchor and path.suffix in (".md", ".txt") and path.is_file() and anchor not in heading_slugs(path):
        yield "{}: {} names no heading in {}".format(where, target, relative(path, root))


def makefile_targets(root=ROOT):
    """Return the rule names the tree's Makefile defines and the eval targets it enumerates from evals/."""
    targets = set()
    for line in (root / "Makefile").read_text(encoding="utf-8").split("\n"):
        match = MAKE_RULE.match(line)
        if match:
            targets.update(name for name in match.group(1).split() if "$" not in name and "%" not in name)
    for prefix, folder in ENUMERATED_TARGETS.items():
        cases = root / "evals" / folder
        if cases.is_dir():
            targets.update(prefix + child.name for child in cases.iterdir() if child.is_dir())
    return targets


def make_target(arguments):
    """Return the first target a ``make`` command line names, skipping options and variable assignments."""
    skip_value = False
    for word in arguments.split():
        if word.startswith("#"):
            return None
        if skip_value:
            skip_value = False
            continue
        if word in MAKE_OPTIONS_WITH_VALUE:
            skip_value = True
            continue
        if word.startswith("-") or "=" in word:
            continue
        return word.rstrip(".,;:")
    return None


def is_pattern(text):
    return any(character in text for character in PATTERN_CHARACTERS)


def name_failures(page, text, targets, root=ROOT):
    """Yield a failure for each command, agent name, make target or repository path on the page that does not exist."""
    where = relative(page, root)
    for match in SKILL_COMMAND.finditer(text):
        if not (root / SKILLS_DIR / match.group(1)).is_dir():
            yield "{}:{}: /ponderly:{} names no skill".format(where, line_at(text, match.start()), match.group(1))
    for match in AGENT_NAME.finditer(text):
        name = match.group(1)
        if not (root / AGENTS_DIR / "{}.md".format(name)).is_file() and not (root / SKILLS_DIR / name).is_dir():
            yield "{}:{}: ponderly:{} names no agent or skill".format(where, line_at(text, match.start()), name)
    prose, fenced = split_fences(text)
    commands = [(line_at(prose, match.start()), match.group(1).strip()) for match in CODE_SPAN.finditer(prose)]
    commands.extend(enumerate(fenced.split("\n"), 1))
    for line, command in sorted(commands):
        make = MAKE_COMMAND.match(command)
        if not make:
            continue
        target = make_target(make.group(1))
        if target and not is_pattern(target) and target not in targets:
            yield "{}:{}: make {} names no Makefile target".format(where, line, target)
    for match in CODE_SPAN.finditer(prose):
        path = match.group(1).strip()
        if not is_repository_path(path):
            continue
        if not (root / path.partition("#")[0]).exists():
            yield "{}:{}: {} names no file or folder".format(where, line_at(prose, match.start()), path)


def is_repository_path(text):
    if not text or any(character.isspace() for character in text) or is_pattern(text):
        return False
    return text.startswith(CHECKED_FOLDERS) or text.partition("#")[0] in ROOT_FILES


def alt_text_failures(page, text, root=ROOT):
    """Yield a failure for each image on the page with empty alt text."""
    prose, _ = split_fences(text)
    searchable = blank_code_spans(prose)
    for match in IMAGE.finditer(searchable):
        if not match.group(1).strip():
            yield "{}:{}: image {} has empty alt text".format(relative(page, root), line_at(prose, match.start()), match.group(2))
    for match in HTML_IMAGE.finditer(searchable):
        alt = HTML_ALT.search(match.group())
        if not alt or not (alt.group(1) or alt.group(2) or "").strip():
            yield "{}:{}: image {} has empty alt text".format(relative(page, root), line_at(prose, match.start()), match.group())


def components(root=ROOT):
    """Return (kind, name) for every skill folder, agent file and rule file in the plugin."""
    found = [("skill", path.name) for path in sorted((root / SKILLS_DIR).iterdir()) if path.is_dir()]
    found.extend(("agent", path.stem) for path in sorted((root / AGENTS_DIR).glob("*.md")))
    found.extend(("rule", path.stem) for path in sorted((root / RULES_DIR).glob("*.md")))
    return found


def hook_scripts(root=ROOT):
    """Return the name of every hook script in the plugin, its hooks.json left out."""
    return [path.name for path in sorted((root / HOOKS_DIR).iterdir()) if path.is_file() and path.suffix != ".json"]


def lists(text, kind, name):
    """Return True when a list item opens with the component, in backticks, as link text or as a ``/ponderly:`` command, or links to its path."""
    escaped = re.escape(name)
    opening = re.compile(
        r"^\s*(?:[-*+]|\d+\.)\s+(?:`(?:/?ponderly:)?{0}`|\[`?{0}`?\]\(|/ponderly:{0}(?![\w-]))".format(escaped),
        re.MULTILINE,
    )
    target = re.compile(
        r"^\s*(?:[-*+]|\d+\.)\s+.*\]\([^)\s]*/{}[)#]".format(COMPONENT_PATHS[kind].format(escaped)),
        re.MULTILINE,
    )
    return opening.search(text) is not None or target.search(text) is not None


def reference_headings(root=ROOT):
    """Return the text of every ``###`` heading in the Reference, with backticks removed."""
    prose, _ = split_fences((root / REFERENCE).read_text(encoding="utf-8"))
    return {line[4:].replace("`", "").strip() for line in prose.split("\n") if line.startswith("### ")}


def broken_links(root=ROOT):
    """Return a failure for each link or image on a Doc_Page of the tree at root that does not resolve."""
    failures = []
    for page in doc_pages(root):
        failures.extend(link_failures(page, page.read_text(encoding="utf-8"), root))
    return failures


def missing_alt_text(root=ROOT):
    """Return a failure for each image on a Doc_Page of the tree at root with empty alt text."""
    failures = []
    for page in doc_pages(root):
        failures.extend(alt_text_failures(page, page.read_text(encoding="utf-8"), root))
    return failures


def missing_names(root=ROOT):
    """Return a failure for each command, agent name, make target or path on a Doc_Page of the tree at root that does not exist."""
    targets = makefile_targets(root)
    failures = []
    for page in doc_pages(root):
        failures.extend(name_failures(page, page.read_text(encoding="utf-8"), targets, root))
    return failures


def missing_components(root=ROOT):
    """Return a failure for each component the Listing_Page, the Reference or llms.txt leaves out, and each hook script the Reference leaves out."""
    listing = (root / LISTING_PAGE).read_text(encoding="utf-8")
    llms = (root / LLMS).read_text(encoding="utf-8")
    headings = reference_headings(root)
    failures = []
    for kind, name in components(root):
        if not lists(listing, kind, name):
            failures.append("{}: no list item names the {} {}".format(LISTING_PAGE.as_posix(), kind, name))
        if name not in headings:
            failures.append("{}: no ### heading names the {} {}".format(REFERENCE.as_posix(), kind, name))
        if not lists(llms, kind, name):
            failures.append("{}: no list item names the {} {}".format(LLMS.as_posix(), kind, name))
    for name in hook_scripts(root):
        if name not in headings:
            failures.append("{}: no ### heading names the hook script {}".format(REFERENCE.as_posix(), name))
    return failures


def stale_captures(root=ROOT):
    """Return a failure for each capture source in the tree at root whose SVG is missing or differs from its render."""
    failures = []
    for source in sorted((root / CAPTURES).glob("*.txt")):
        image = root / IMAGES / "{}.svg".format(source.stem)
        if not image.is_file():
            failures.append("{}:1: {} has no SVG at {}".format(relative(source, root), source.stem, relative(image, root)))
            continue
        with open(image, encoding="utf-8", newline="") as handle:
            drawn = handle.read()
        if drawn != render_svg(source.read_text(encoding="utf-8")):
            failures.append(
                "{}:1: {} differs from its source's render; run python3 docs/captures/render.py render {}".format(
                    relative(image, root), source.stem, source.stem
                )
            )
    return failures


def orphan_images(root=ROOT):
    """Return a failure for each SVG in the tree at root with no capture source."""
    return [
        "{}:1: {} has no source in {}".format(relative(image, root), image.stem, CAPTURES.as_posix())
        for image in sorted((root / IMAGES).glob("*.svg"))
        if not (root / CAPTURES / "{}.txt".format(image.stem)).is_file()
    ]


def leaked_secrets(root=ROOT):
    """Return a failure for each line of a capture source in the tree at root that holds a credential, token, email or home path."""
    failures = []
    for source in sorted((root / CAPTURES).glob("*.txt")):
        for number, line in enumerate(source.read_text(encoding="utf-8").split("\n"), 1):
            for kind, pattern in SECRET_PATTERNS:
                if pattern.search(line):
                    failures.append("{}:{}: the line holds {}".format(relative(source, root), number, kind))
    return failures


class LinksTest(unittest.TestCase):
    def test_every_link_and_image_resolves(self):
        failures = broken_links()
        self.assertEqual([], failures, "\n".join(failures))

    def test_every_image_has_alt_text(self):
        failures = missing_alt_text()
        self.assertEqual([], failures, "\n".join(failures))


class NamesTest(unittest.TestCase):
    def test_every_command_agent_target_and_path_exists(self):
        failures = missing_names()
        self.assertEqual([], failures, "\n".join(failures))


class CoverageTest(unittest.TestCase):
    def test_every_component_is_in_the_listing_page_the_reference_and_llms_txt_and_every_hook_in_the_reference(self):
        failures = missing_components()
        self.assertEqual([], failures, "\n".join(failures))


class CapturesTest(unittest.TestCase):
    def test_every_svg_equals_its_sources_render(self):
        failures = stale_captures()
        self.assertEqual([], failures, "\n".join(failures))

    def test_every_svg_has_a_source(self):
        failures = orphan_images()
        self.assertEqual([], failures, "\n".join(failures))

    def test_no_source_holds_a_credential_token_email_or_home_path(self):
        failures = leaked_secrets()
        self.assertEqual([], failures, "\n".join(failures))


FIXTURE_SOURCE = "title: A session\ndate: 2026-10-22\nplugin: ponderly v1.1.0\nsource: a demo session\nalt: Claude answers.\n\n> a request\n● an answer\n"

FIXTURE_FILES = {
    "plugins/ponderly/skills/demo/SKILL.md": "---\nname: demo\n---\n",
    "plugins/ponderly/agents/helper.md": "---\nname: helper\n---\n",
    "plugins/ponderly/rules/style.md": "# Style\n",
    "plugins/ponderly/hooks/hooks.json": "{}\n",
    "plugins/ponderly/hooks/inject.sh": "#!/bin/sh\n",
    "plugins/ponderly/README.md": "# Ponderly\n\n- `demo`: does a thing.\n- `helper`: helps.\n- `style`: a rule.\n",
    "llms.txt": "# Ponderly\n\n- `demo`: when you want a thing.\n- `helper`: when you want help.\n- `style`: always.\n",
    "docs/reference.md": "# Reference\n\n### demo\n\n### helper\n\n### style\n\n### inject.sh\n",
    "Makefile": "check:\n\tpython3 -m unittest\n",
    "docs/captures/session.txt": FIXTURE_SOURCE,
    "docs/images/session.svg": render_svg(FIXTURE_SOURCE),
    "README.md": (
        "# Front door\n"
        "\n"
        "Read [the reference](docs/reference.md#reference).\n"
        "\n"
        "![Claude answers a request](docs/images/session.svg)\n"
        "\n"
        "Run `/ponderly:demo`, hand off to `ponderly:helper`, then `make check`.\n"
    ),
}


def build_tree(root):
    """Write a small clean repository at root: a plugin with one skill, agent, rule and hook, its pages, a Makefile and one capture."""
    for name, text in FIXTURE_FILES.items():
        write(root, name, text)


def write(root, name, text):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


class FixtureTreeTest(unittest.TestCase):
    """Runs a check against a clean fixture tree with one file replaced."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        build_tree(self.root)

    def replace(self, name, text):
        write(self.root, name, text)


class CleanTreeTest(FixtureTreeTest):
    """Property 1: Every name a page mentions exists. Property 2: Every component is named where it must be."""

    def test_a_clean_tree_passes_every_check(self):
        failures = (
            broken_links(self.root)
            + missing_alt_text(self.root)
            + missing_names(self.root)
            + missing_components(self.root)
            + stale_captures(self.root)
            + orphan_images(self.root)
            + leaked_secrets(self.root)
        )
        self.assertEqual([], failures)


class BrokenMentionTest(FixtureTreeTest):
    """Property 1: Every name a page mentions exists. Property 5: A failure names its place."""

    def test_a_link_to_a_missing_file_fails_with_the_page_line_and_target(self):
        self.replace("README.md", "# Front door\n\nRead [the guide](docs/missing.md).\n")
        self.assertEqual(["README.md:3: docs/missing.md names no file"], broken_links(self.root))

    def test_a_link_to_a_missing_heading_fails_with_the_page_line_and_target(self):
        self.replace("README.md", "# Front door\n\nRead [the reference](docs/reference.md#nowhere).\n")
        self.assertEqual(
            ["README.md:3: docs/reference.md#nowhere names no heading in docs/reference.md"], broken_links(self.root)
        )

    def test_a_command_naming_a_missing_skill_fails_with_the_page_line_and_command(self):
        self.replace("README.md", "# Front door\n\nRun `/ponderly:absent`.\n")
        self.assertEqual(["README.md:3: /ponderly:absent names no skill"], missing_names(self.root))

    def test_a_make_command_naming_a_missing_target_fails_with_the_page_line_and_target(self):
        self.replace("README.md", "# Front door\n\nRun `make absent`.\n")
        self.assertEqual(["README.md:3: make absent names no Makefile target"], missing_names(self.root))


    def test_an_agent_name_naming_no_agent_or_skill_fails_with_the_page_line_and_name(self):
        self.replace("README.md", "# Front door\n\nHand off to `ponderly:absent`.\n")
        self.assertEqual(["README.md:3: ponderly:absent names no agent or skill"], missing_names(self.root))

    def test_a_repository_path_naming_no_file_fails_with_the_page_line_and_path(self):
        self.replace("README.md", "# Front door\n\nSee `docs/absent.md`.\n")
        self.assertEqual(["README.md:3: docs/absent.md names no file or folder"], missing_names(self.root))

    def test_an_image_whose_file_is_missing_fails_with_the_page_line_and_image(self):
        self.replace("README.md", "# Front door\n\n![A session](docs/images/absent.svg)\n")
        self.assertEqual(["README.md:3: docs/images/absent.svg names no file"], broken_links(self.root))

    def test_a_link_leaving_the_repository_fails_with_the_page_line_and_target(self):
        self.replace("README.md", "# Front door\n\nRead [the parent](../outside.md).\n")
        self.assertEqual(["README.md:3: ../outside.md names a file outside the repository"], broken_links(self.root))

    def test_a_link_with_an_empty_target_fails_with_the_page_and_line(self):
        self.replace("README.md", "# Front door\n\nRead [nothing]().\n")
        self.assertEqual(["README.md:3: a link has no target"], broken_links(self.root))


class AwkwardPageTest(FixtureTreeTest):
    """Property 1: Every name a page mentions exists, read the way GitHub reads awkward pages."""

    def test_a_page_that_begins_with_a_byte_order_mark_resolves_a_link_to_its_first_heading(self):
        self.replace("README.md", "\ufeff# Front door\n\nBack to [the top](#front-door).\n")
        self.assertEqual([], broken_links(self.root))

    def test_a_link_to_a_heading_in_a_non_latin_script_resolves_to_its_github_slug(self):
        self.replace("docs/reference.md", FIXTURE_FILES["docs/reference.md"] + "\n## Résumé 日本語\n")
        self.replace("README.md", "# Front door\n\nRead [the summary](docs/reference.md#résumé-日本語).\n")
        self.assertEqual([], broken_links(self.root))


class AltTextTest(FixtureTreeTest):
    """Property 5: A failure names its place."""

    def test_an_image_with_no_alt_text_fails_with_the_page_line_and_image(self):
        self.replace("README.md", "# Front door\n\n![](docs/images/session.svg)\n")
        self.assertEqual(["README.md:3: image docs/images/session.svg has empty alt text"], missing_alt_text(self.root))

    def test_an_html_image_with_empty_alt_text_fails_with_the_page_line_and_tag(self):
        self.replace("README.md", '# Front door\n\n<img src="docs/images/session.svg" alt="">\n')
        self.assertEqual(
            ['README.md:3: image <img src="docs/images/session.svg" alt=""> has empty alt text'],
            missing_alt_text(self.root),
        )


class CaptureFixtureTest(FixtureTreeTest):
    """Requirements 6.6 and 9.4: every capture's SVG is its source's render and has a source. Requirement 6.9: no source holds a secret."""

    def test_an_svg_with_no_source_fails_with_the_image_and_name(self):
        self.replace("docs/images/orphan.svg", render_svg(FIXTURE_SOURCE))
        self.assertEqual(["docs/images/orphan.svg:1: orphan has no source in docs/captures"], orphan_images(self.root))

    def test_a_source_with_no_svg_fails_with_the_source_and_missing_image(self):
        self.replace("docs/captures/extra.txt", FIXTURE_SOURCE)
        self.assertEqual(
            ["docs/captures/extra.txt:1: extra has no SVG at docs/images/extra.svg"], stale_captures(self.root)
        )

    def test_a_stale_svg_fails_with_the_image_and_capture_name(self):
        self.replace("docs/images/session.svg", render_svg(FIXTURE_SOURCE.replace("an answer", "an older answer")))
        self.assertEqual(
            [
                "docs/images/session.svg:1: session differs from its source's render; "
                "run python3 docs/captures/render.py render session"
            ],
            stale_captures(self.root),
        )

    def test_a_source_holding_a_github_token_fails_with_the_source_line_and_kind(self):
        token = "ghp_" + "a" * 36
        self.replace("docs/captures/session.txt", FIXTURE_SOURCE + "● the token is {}\n".format(token))
        self.assertEqual(["docs/captures/session.txt:9: the line holds a GitHub token"], leaked_secrets(self.root))


class MissingComponentTest(FixtureTreeTest):
    """Property 2: Every component is named where it must be. Property 5: A failure names its place, here the page and the name."""

    def test_a_skill_the_listing_page_leaves_out_fails_with_the_page_and_skill(self):
        self.replace("plugins/ponderly/README.md", "# Ponderly\n\n- `helper`: helps.\n- `style`: a rule.\n")
        self.assertEqual(
            ["plugins/ponderly/README.md: no list item names the skill demo"], missing_components(self.root)
        )

    def test_an_agent_the_reference_has_no_heading_for_fails_with_the_page_and_agent(self):
        self.replace("docs/reference.md", "# Reference\n\n### demo\n\n### style\n\n### inject.sh\n")
        self.assertEqual(["docs/reference.md: no ### heading names the agent helper"], missing_components(self.root))

    def test_a_rule_llms_txt_leaves_out_fails_with_the_page_and_rule(self):
        self.replace("llms.txt", "# Ponderly\n\n- `demo`: when you want a thing.\n- `helper`: when you want help.\n")
        self.assertEqual(["llms.txt: no list item names the rule style"], missing_components(self.root))

    def test_a_hook_script_the_reference_has_no_heading_for_fails_with_the_page_and_script(self):
        self.replace("docs/reference.md", "# Reference\n\n### demo\n\n### helper\n\n### style\n")
        self.assertEqual(
            ["docs/reference.md: no ### heading names the hook script inject.sh"], missing_components(self.root)
        )


if __name__ == "__main__":
    unittest.main()
