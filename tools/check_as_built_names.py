"""
check_as_built_names.py -- every code name INTERACTIVE_AS_BUILT.md gives
in backticks is found in the code it belongs to.

WHY THIS EXISTS

    L-522 (document caps), step 2, 2026-11-11. What interactive.html does
    moved out of the interactive-exhibit skill into INTERACTIVE_AS_BUILT.md
    at this repository's root, and a build that changes the page changes
    that page in the same commit. A sentence that names a function, a file
    or an object's member which the code no longer has is a claim the
    code has quietly stopped making. Nothing read the old skill's names
    against the code; this does, every run.

RUN COMMAND

    python tools/check_as_built_names.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    among the offline checkers, as "As-built names".

WHAT IT READS

    Each backticked thing on the page, sorted into one of two piles. A
    backticked thing may wrap one line; its line break and indent are
    read as one space.
    NAMES, each looked for in the code:
      - a file or folder (a path with "/", or a name ending .js .py .json
        .html .md .css .bat .yml): a path is found from this repository's
        root or the orrery's; a bare file name is found anywhere in either
      - an identifier, dotted or not (`GalleryArrival.applyArrival`): each
        part found as a word in the code
      - a call (`sunGridDtick(span)`): the name before the bracket
      - a key and its value (`hovermode: false`): the key
      - a quoted key (`"rooms"`): the key without its quotes
      - a CSS class or id (`.bfold`, `#ss-outside`, `body.sun-exhibit`),
        or a hyphenated name (`sun-chrome`): found as a word
      - a family (`sunHud*`): some word in the code begins with it
      - a name's ending (`_Y`, beside `SUN_LABEL_PHONE_X`): some word ends
        with it
      - a command (`gallery_maintenance_run.py --live`): its file
    NOT NAMES, set aside and counted by kind: words or a snippet with
    spaces, an object's shape (`{group, label}`), a page address or
    parameter (`?exhibit=`), a pattern with a placeholder
    (`positions/<slug>.json`), an HTML entity, a date.
    THE CODE: this repository's .py .js .html .css .yml files (not
    documentation/patch_* or the fixtures, which are not code), its
    data/*.json and gallery/gallery_metadata.json, but not this file,
    which names the page's examples and its own planted faults (its
    first self-test run went red on exactly that); and the orrery's .py
    files outside its documentation/, in the sibling folder
    ..\\palomas_orrery_for_github.

    Two named lists, printed every run:
      - PLOTLY_NAMES: names the page gives from plotly.js 2.35.2, which
        is fetched from its CDN and is in neither repository. Set aside.
      - ORRERY_NAMES: the names found only in the orrery. On GitHub's
        nightly run the orrery is not checked out, so these are printed
        as not examined that night and every other name is checked; on
        Tony's computer each is looked for in the orrery, and the list
        must equal the names found only there.

    A MARK: a sentence whose name the code does not have, and whose right
    name is not plain from the code, keeps its sentence and is marked by
    the words  [not in the code, L-522]  right after the closing
    backtick. A marked name is printed every run and not red; a marked
    name the code does have is red, so the mark is dropped.

WHAT MAKES IT FAIL

    - a name found in neither code, each one named (unless marked)
    - a backticked thing that begins or ends with a space: the backticks
      are paired wrongly there, and the names beside it are not read
    - a marked name the code has
    - on Tony's computer, ORRERY_NAMES not equal to the names found only
      in the orrery, each difference named
    - the page not found, or the self-test below not going red

    Before reading the real page it plants, on a throwaway copy, a name
    no code has, a file no repository has, a mark on a name the code
    does have, a call wrapped across a line, a name after it on the same
    closing line, and a backticked thing beginning with a space, and each
    must be reported.

HOW TO FIX A FAILURE

    A name gone from the code: correct the sentence to the name the code
    now uses, in the commit that changed the code. Where the right name
    is not plain, leave the sentence, add the mark, and list it on the
    ledger for Tony. A new name only the orrery has: add it to
    ORRERY_NAMES below.

Written November 11, 2026 with Anthropic's Claude Opus 5.5 (L-522,
document caps, step 2).
"""

import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ORRERY = os.path.join(os.path.dirname(ROOT), "palomas_orrery_for_github")
PAGE = os.path.join(ROOT, "INTERACTIVE_AS_BUILT.md")

MARK = " [not in the code, L-522]"
FILE_EXT = (".js", ".py", ".json", ".html", ".md", ".css", ".bat", ".yml")
CODE_EXT = (".py", ".js", ".html", ".css", ".yml", ".bat")

# Names the page gives from plotly.js 2.35.2 (served from its CDN; in
# neither repository). Set aside by name, never looked for.
PLOTLY_NAMES = {"Fx.loneHover", "annotation-text-g", "clipToBounds"}

# The names found only in the orrery's code. Checked against the orrery
# on Tony's computer; not examined on GitHub's night, which has no orrery.
ORRERY_NAMES = {
    "celestial_objects.py", "constants_new.py", "export_drawings.py",
    "galactic_tide_sampler.py", "main_belt_sampler.py",
    "outer_oort_sampler.py", "skills/interactive-exhibit/SKILL.md",
    "van_allen_belt_sampler.py",
}

IDENT = re.compile(r"[A-Za-z_$][A-Za-z0-9_$]*")
HYPH = re.compile(r"[A-Za-z_][A-Za-z0-9_-]*")
# A span may wrap ONE line; its line break and indent read as one space.
# (Until 2026-11-11, evening, a span stopped at a line end, so the four
# that wrap threw the pairing off for the rest of their closing line and
# the names there went unexamined; found by the coordinating session.)
SPAN = re.compile(r"`([^`\n]+(?:\n[^`\n]+)?)`")
WRAP = re.compile(r"[ \t]*\n[ \t]*")


def classify(s):
    """(kind, what) -- kind is a NAME kind, with the thing to look for,
    or a set-aside kind, with what None."""
    if s in PLOTLY_NAMES:
        return ("plotly", None)
    m = re.fullmatch(r"([\w./-]+\.(?:py|js)) .+", s)
    if m:
        return ("file", m.group(1))
    if s in ("http://", "https://") or re.search(r"\.html\?", s):
        return ("a page address or parameter", None)
    if "<" in s or ">" in s:
        return ("a pattern with a placeholder", None)
    if s.startswith("&#"):
        return ("an HTML entity", None)
    if s[0] in "?&" or s.endswith("="):
        return ("a page address or parameter", None)
    if re.fullmatch(r"\d{4}-\d\d-\d\d(T[\d:]+Z)?", s):
        return ("a date", None)
    if s[0] in "{[":
        return ("an object's shape", None)
    m = re.fullmatch(r"([\w$.]+)\((.*)\)", s)
    if m:
        return ("call", m.group(1))
    m = re.fullmatch(r'"?([\w$.]+)"?: .+', s)
    if m:
        return ("key", m.group(1))
    if re.search(r"\s", s):
        return ("words or a snippet", None)
    m = re.fullmatch(r"""["']([\w$.]+)["']""", s)
    if m:
        return ("ident", m.group(1))
    if "/" in s or s.endswith(FILE_EXT):
        return ("file", s.split("::")[0].rstrip("/") or s)
    if s.endswith("*"):
        return ("family", s[:-1])
    if re.fullmatch(r"_[A-Z][A-Z0-9_]*", s):
        return ("ending", s)
    m = re.fullmatch(r"(?:[a-z]+)?[.#]([A-Za-z][\w-]*)", s)
    if m:
        return ("css", m.group(1))
    if re.fullmatch(r"[A-Za-z_$][\w$]*(\.[A-Za-z_$][\w$]*)*(\(\))?", s):
        return ("ident", s.rstrip("()"))
    if re.fullmatch(r"[A-Za-z_][\w-]*", s):
        return ("css", s)
    if re.fullmatch(r"[\w$]+::[\w$]+", s):
        return ("ident", s.replace("::", "."))
    return ("words or a snippet", None)


def walk(top, skip):
    for dirpath, dirnames, filenames in os.walk(top):
        rel = os.path.relpath(dirpath, top).replace("\\", "/")
        dirnames[:] = [d for d in dirnames
                       if not skip(("" if rel == "." else rel + "/") + d)]
        for name in filenames:
            yield ((rel + "/" if rel != "." else "") + name,
                   os.path.join(dirpath, name))


def gallery_skip(rel):
    return (rel.split("/")[-1] in (".git", "__pycache__", "node_modules")
            or rel.startswith("data/solar-system"))


def orrery_skip(rel):
    return rel.split("/")[0] in (".git", "__pycache__", "documentation",
                                 "data", "star_data", "images", "papers",
                                 "reports", "test_output", "docs")


class Code:
    """The words and files of one repository's code."""

    def __init__(self, top, skip, is_code):
        self.top = top
        self.idents, self.hyph, self.basenames = set(), set(), set()
        self.paths, self.dirs = set(), set()
        self.files = 0
        for rel, full in walk(top, skip):
            self.paths.add(rel)
            parts = rel.split("/")
            self.basenames.add(parts[-1])
            for i in range(1, len(parts)):
                self.dirs.add("/".join(parts[:i]))
            if not is_code(rel):
                continue
            try:
                with open(full, "rb") as handle:
                    text = handle.read().decode("utf-8", "replace")
            except OSError:
                continue
            self.files += 1
            self.idents.update(IDENT.findall(text))
            self.hyph.update(HYPH.findall(text))
        self.prefixes = sorted(self.idents | self.hyph)

    def has(self, kind, what):
        if kind == "file":
            if "/" in what:
                return any(os.path.exists(os.path.join(self.top, base, what))
                           for base in ("", "gallery"))
            return what in self.basenames or what in self.dirs
        if kind == "family":
            return any(p.startswith(what) and p != what for p in
                       self.prefixes[self._lo(what):self._lo(what) + 50])
        if kind == "ending":
            return any(p.endswith(what) and p != what for p in self.idents)
        if kind == "css":
            return what in self.hyph
        return all(part in self.idents for part in what.split(".") if part)

    def _lo(self, what):
        import bisect
        return bisect.bisect_left(self.prefixes, what)


def gallery_is_code(rel):
    name = rel.split("/")[-1]
    if rel == "tools/check_as_built_names.py":
        # This file names the page's examples and its planted faults; read
        # as code, it would find them all (its own first self-test run).
        return False
    if rel.startswith("documentation/"):
        return name.endswith(".js") and not name.startswith(
            ("patch_", "fixture_"))
    if rel.startswith("data/"):
        return rel.count("/") == 1 and name.endswith(".json")
    if rel == "gallery/gallery_metadata.json":
        return True
    return name.endswith(CODE_EXT)


def orrery_is_code(rel):
    return rel.endswith(".py")


def read_page(path):
    with open(path, "rb") as handle:
        text = handle.read().decode("ascii")
    found = []
    for m in SPAN.finditer(text):
        marked = text.startswith(MARK, m.end())
        found.append((WRAP.sub(" ", m.group(1)), marked))
    return found


def check(path, gallery, orrery, quiet=False):
    """Return (failures, report lines)."""
    lines, failures = [], []
    spans = read_page(path)
    kinds, set_aside, plotly = {}, {}, set()
    seen = {}
    edges = sorted({t for t, _ in spans if t != t.strip()})
    for text in edges:
        failures.append("%r: a backticked thing that begins or ends with a "
                        "space -- the backticks are paired wrongly here, so "
                        "names nearby go unexamined" % text)
    for text, marked in spans:
        if text != text.strip():
            continue
        kind, what = classify(text)
        if what is None:
            if kind == "plotly":
                plotly.add(text)
            else:
                set_aside.setdefault(kind, set()).add(text)
            continue
        prev = seen.get(text)
        seen[text] = (kind, what, marked or (prev[2] if prev else False))
    in_gallery = in_orrery = 0
    missing, marked_ok, only_orrery, not_tonight = [], [], set(), []
    for text in sorted(seen):
        kind, what, marked = seen[text]
        g = gallery.has(kind, what)
        o = orrery.has(kind, what) if orrery else None
        if orrery is None and not g and text in ORRERY_NAMES:
            not_tonight.append(text)
            continue
        found = g or bool(o)
        if g:
            in_gallery += 1
        elif o:
            in_orrery += 1
            only_orrery.add(text)
        if marked and found:
            failures.append("%s: marked as not in the code, but the code "
                            "has it -- drop the mark" % text)
        elif marked:
            marked_ok.append(text)
        elif not found:
            missing.append(text)
            failures.append("%s: not found in the code (%s)" % (text, kind))
    if orrery is not None:
        for name in sorted(only_orrery - ORRERY_NAMES):
            failures.append("%s: found only in the orrery; add it to "
                            "ORRERY_NAMES" % name)
        for name in sorted(ORRERY_NAMES - only_orrery):
            failures.append("%s: on ORRERY_NAMES but not found only in the "
                            "orrery; take it off" % name)
    n_aside = sum(len(v) for v in set_aside.values())
    lines.append("  read %s: %d backticked, %d different"
                 % (os.path.basename(path), len(spans),
                    len({t for t, _ in spans})))
    lines.append("  code: the gallery's %d files%s" % (
        gallery.files, "; the orrery's %d files" % orrery.files
        if orrery else "; the orrery folder is not here (GitHub's night)"))
    lines.append("  examined %d names: %d found in the gallery's code, %d "
                 "only in the orrery's, %d marked, %d not found%s"
                 % (len(seen), in_gallery, in_orrery, len(marked_ok),
                    len(missing), ", %d not examined tonight" %
                    len(not_tonight) if not_tonight else ""))
    lines.append("  set aside %d as not names:" % n_aside)
    for kind in sorted(set_aside):
        items = sorted(set_aside[kind])
        lines.append("    %s (%d): %s" % (kind, len(items),
                                         ", ".join(items)))
    lines.append("  set aside %d as plotly.js's own (PLOTLY_NAMES): %s"
                 % (len(plotly), ", ".join(sorted(plotly))))
    if not_tonight:
        lines.append("  not examined tonight, the orrery's (ORRERY_NAMES): "
                     + ", ".join(not_tonight))
    elif orrery is not None:
        lines.append("  found only in the orrery (ORRERY_NAMES, %d): %s"
                     % (len(only_orrery), ", ".join(sorted(only_orrery))))
    for text in marked_ok:
        lines.append("  marked, not in the code: %s" % text)
    return failures, lines


def self_test(gallery, orrery):
    """Plant three faults on a throwaway copy; each must be reported."""
    with open(PAGE, "rb") as handle:
        text = handle.read().decode("ascii")
    planted = text + (
        "\nPlanted: `zzPlantedNameL522`, `gallery/zz_planted_l522.js`,"
        " and `EXHIBITS`%s.\n"
        "A wrapped one, `zzWrappedL522(a,\n  b)` and `zzAfterWrapL522`;"
        " and ` zzEdgeL522`.\n" % MARK)
    folder = tempfile.mkdtemp(prefix="as_built_selftest_")
    copy = os.path.join(folder, "INTERACTIVE_AS_BUILT.md")
    with open(copy, "wb") as handle:
        handle.write(planted.encode("ascii"))
    try:
        failures, _ = check(copy, gallery, orrery, quiet=True)
    finally:
        os.remove(copy)
        os.rmdir(folder)
    wanted = ["zzPlantedNameL522:", "gallery/zz_planted_l522.js:",
              "EXHIBITS: marked", "zzWrappedL522(a, b):",
              "zzAfterWrapL522:", "' zzEdgeL522':"]
    return [w for w in wanted if not any(f.startswith(w) for f in failures)]


def main():
    print("AS-BUILT NAMES -- every code name INTERACTIVE_AS_BUILT.md gives "
          "in backticks is in the code")
    if not os.path.isfile(PAGE):
        print("AS-BUILT NAMES: FAIL -- %s not found" % PAGE)
        return 1
    gallery = Code(ROOT, gallery_skip, gallery_is_code)
    orrery = (Code(ORRERY, orrery_skip, orrery_is_code)
              if os.path.isdir(ORRERY) else None)
    unreported = self_test(gallery, orrery)
    if unreported:
        for name in unreported:
            print("  self-test: the planted fault was NOT reported: %s" % name)
        print("AS-BUILT NAMES: FAIL -- the check could not show it can fail")
        return 1
    print("  self-test: 6 planted faults on a throwaway copy, each reported")
    failures, lines = check(PAGE, gallery, orrery)
    for line in lines:
        print(line)
    if failures:
        for failure in failures:
            print("  NOT FOUND: " + failure if "not found in the code" in
                  failure else "  " + failure)
        print("AS-BUILT NAMES: FAIL -- %d finding(s)" % len(failures))
        return 1
    print("AS-BUILT NAMES: ok -- every name examined is in the code")
    return 0


if __name__ == "__main__":
    sys.exit(main())
