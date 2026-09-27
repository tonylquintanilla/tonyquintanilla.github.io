#!/usr/bin/env python3
"""
patch_L281_2_guestbook_updater.py -- the guest book updater (L-281, step 2).

RUN: save this file in the GALLERY repo root (the folder that holds
index.html), open it in VS Code and click Run. Or, from that folder:

    python patch_L281_2_guestbook_updater.py

WHAT IT DOES, all or nothing:
  Creates two new files:
    tools/guestbook_updater.py       fetches the form's submissions, asks
                                     you to approve or decline each, and
                                     lets you write entries, replies with
                                     gallery links, remove an entry, and
                                     set the form's address
    tools/test_guestbook_updater.py  its offline check, three scripted
                                     runs against made-up submissions
  Edits two files:
    .gitignore                  keeps tools/guestbook_local.json (the
                                private sheet address and the list of
                                decided messages) out of the public repo
    gallery_maintenance_run.py  adds the "Guest book updater" check;
                                header stamp

It checks both edited files are the ones it was built against (gallery
70a77347) before writing anything. If either differs, or a new file
already exists with different contents, it writes NOTHING and says why.
Undo is Discard Changes in GitHub Desktop.

PERMANENT PARTS: the two new files and the edits. This script is
one-shot; once it has run, move it to documentation/.

Written September 27, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

BASE = "70a77347"

EXPECTED = {
    "gallery_maintenance_run.py": "cb4c8ced2bca2f9e5be5cad222f2625e",
    ".gitignore": "e92c829bc606a01d29222c97cfee6cd9",
}

EDITS = {
    "gallery_maintenance_run.py": [
        ("header stamp",
         b"""Module updated: September 26, 2026 with Anthropic's Claude Opus 5.5
(L-281: the "Guest book" checker runs documentation/smoke_guestbook.js,
and the --live pass fetches gallery/guestbook.js and data/guestbook.json).
""",
         b"""Module updated: September 27, 2026 with Anthropic's Claude Opus 5.5
(L-281: the "Guest book updater" checker runs
tools/test_guestbook_updater.py; since September 26 the "Guest book"
checker runs documentation/smoke_guestbook.js, and the --live pass
fetches gallery/guestbook.js and data/guestbook.json).
"""),
        ("updater checker",
         b"""    ("Guest book", "node",
     ["documentation/smoke_guestbook.js"], ".", None, False),
""",
         b"""    ("Guest book", "node",
     ["documentation/smoke_guestbook.js"], ".", None, False),

    # L-281 (2026-09-27): the tool that writes data/guestbook.json. Three
    # scripted runs in a throwaway folder against made-up submissions:
    # approve, decline, later, a reply, an entry of Tony's with a
    # misspelt link refused, a removal. Nothing real is written and
    # nothing is fetched. Its self-test first shows the link check
    # refusing made-up pages and accepting real ones. Gates.
    ("Guest book updater", "python",
     ["tools/test_guestbook_updater.py"], ".", None, False),
"""),
    ],
    ".gitignore": [
        ("guest book local file",
         b"""data/solar-system (*)/
data/[0-9]*-solar-system/
""",
         b"""data/solar-system (*)/
data/[0-9]*-solar-system/

# The guest book updater's own file (L-281): the private address of the
# form's responses, and fingerprints of the messages already decided.
# Anyone with that address can read every submission, approved or not,
# so it never goes to the public repo. The .tmp is the updater's
# half-written copy, which exists only for the moment of a save.
tools/guestbook_local.json
tools/guestbook_local.json.tmp
data/guestbook.json.tmp
"""),
    ],
}

NEW_FILES = {
    'tools/guestbook_updater.py': ('b1c22d0af2d0eb3b73006656147d610d', r'''#!/usr/bin/env python3
"""
guestbook_updater.py -- look after the lobby's guest book (L-281).

WHAT IT DOES
    Visitors write in the guest book through a Google Form. The form
    saves each message as a row in a Google Sheet. This tool fetches
    those rows, shows you each one you have not seen, and asks what to
    do with it:
        a  approve   it goes into data/guestbook.json and appears in
                     the lobby after your next push
        d  decline   it never appears, and this tool never shows it again
        l  later     it waits, and this tool shows it again next time
        q  stop      stop going through messages for now
    After that it offers a small menu, so you can:
        w  write an entry of your own
        r  reply publicly under an entry
        x  remove an entry from the guest book
        f  set the form's public address, which turns on the lobby's
           "Sign the guest book" link
        q  finish
    Your own entries and replies can link to pages of the gallery. You
    can type a room ("solar_system/earth"), a card's id, or a live
    exhibit's name ("earth", "sun"). Each is checked against the
    gallery's own list of cards and rooms, so a typo is refused rather
    than published as a dead link. A visitor's message never carries a
    link -- the lobby shows it as plain text whatever it says.

    It does not commit or push. When it finishes it says whether the
    guest book changed; if it did, commit data/guestbook.json in
    GitHub Desktop and push.

HOW IT READS THE FORM'S SUBMISSIONS -- no Google credentials
    In the Google Sheet the form writes to, File > Share > Publish to
    web, with the responses sheet and "Comma-separated values (.csv)"
    chosen, gives a long private web address. The first time you run
    this tool it asks you to paste that address, and keeps it in
    tools/guestbook_local.json. That file stays on your machine: git is
    told to ignore it, so it never reaches the public repo. Anyone who
    had the address could read every submission, approved or not,
    which is why it stays there.

    guestbook_local.json also remembers which submissions you have
    approved or declined. It keeps a short fingerprint of each, not the
    message itself, so a declined message is not stored anywhere by
    this tool.

HOW TO RUN IT
    From the dashboard: the Guest Book Updater button, alone or as the
    first step of the Daily Run. From VS Code: open this file and press
    Run. It asks its questions in the panel that opens; answer there.
    It works from the gallery repo root (the folder above tools/),
    wherever it is started.

THE CHECK
    tools/test_guestbook_updater.py runs this tool against made-up
    submissions with scripted answers. The gallery maintenance run
    runs it.

Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
"""

import csv
import datetime
import hashlib
import io
import json
import os
import re
import sys
import time
import urllib.request

HOST_NAME = "Tony"

BOOK = os.path.join("data", "guestbook.json")
LOCAL = os.path.join("tools", "guestbook_local.json")
METADATA = os.path.join("gallery", "gallery_metadata.json")
CONFIG = os.path.join("gallery", "gallery_config.json")

CSV_PREFIX = "https://docs.google.com/spreadsheets/"
FORM_PREFIXES = ("https://docs.google.com/forms/", "https://forms.gle/")
SITE_PREFIXES = ("https://palomasorrery.com/", "http://palomasorrery.com/",
                 "https://www.palomasorrery.com/", "palomasorrery.com/")

# The same three shapes gallery/guestbook.js will draw. A link that does
# not match one of these is never written, because the page would drop it.
SAFE_HREF = (
    re.compile(r"^#[A-Za-z0-9_\-.]+$"),
    re.compile(r"^#room=[A-Za-z0-9_\-/]+$"),
    re.compile(r"^interactive\.html\?exhibit=[A-Za-z0-9_\-]+$"),
)

TIME_FORMATS = ("%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M", "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M")

HTTP_TIMEOUT_SECONDS = 30
SHOW_RECENT = 10


# ============================================================
# FILES
# ============================================================

def find_root():
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in (os.path.dirname(here), here, os.getcwd()):
        if os.path.exists(os.path.join(candidate, "index.html")) and \
                os.path.isdir(os.path.join(candidate, "data")):
            return candidate
    return None


def read_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    """Write through a temporary file, then swap it in. ensure_ascii keeps
    the file ASCII: an accent or an emoji a visitor typed is stored as a
    \\u escape, which the browser reads back as the same character."""
    text = json.dumps(data, indent=2, ensure_ascii=True) + "\n"
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="ascii", newline="\n") as f:
        f.write(text)
    for attempt in range(5):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            # OneDrive can hold a file for a moment (L-216).
            if attempt == 4:
                raise
            time.sleep(1.0)


# ============================================================
# WHERE A LINK MAY POINT
# ============================================================

def load_targets(root):
    """Everything a link may point at, from the gallery's own files:
    {href: default label}, plus lookups from what Tony types."""
    targets = {}
    by_word = {}
    meta = read_json(os.path.join(root, METADATA), {})
    for viz in meta.get("visualizations", []) or []:
        vid = viz.get("id")
        if vid:
            href = "#" + vid
            targets[href] = viz.get("title") or vid
            by_word[vid] = href
        live = viz.get("live") or ""
        m = re.match(r"^interactive\.html\?exhibit=([A-Za-z0-9_\-]+)$", str(live))
        if m:
            href = "interactive.html?exhibit=" + m.group(1)
            targets[href] = (viz.get("title") or m.group(1))
            by_word.setdefault(m.group(1), href)
    cfg = read_json(os.path.join(root, CONFIG), {})

    def walk(nodes, prefix):
        for node in nodes or []:
            key = node.get("key")
            if not key:
                continue
            path = prefix + "/" + key if prefix else key
            href = "#room=" + path
            targets[href] = node.get("label") or path
            by_word[path] = href
            walk(node.get("rooms"), path)
    walk(cfg.get("doors"), "")
    return targets, by_word


def resolve_link(typed, targets, by_word):
    """What Tony typed -> an href the page will draw, or None."""
    t = (typed or "").strip()
    for prefix in SITE_PREFIXES:
        if t.startswith(prefix):
            t = t[len(prefix):]
    if t.startswith("index.html"):
        t = t[len("index.html"):]
    t = t.strip()
    if t in targets:
        href = t
    elif t.startswith("room=") and "#" + t in targets:
        href = "#" + t
    elif t in by_word:
        href = by_word[t]
    else:
        return None
    return href if any(p.match(href) for p in SAFE_HREF) else None


# ============================================================
# THE FORM'S SUBMISSIONS
# ============================================================

def parse_time(raw):
    raw = (raw or "").strip()
    for fmt in TIME_FORMATS:
        try:
            return datetime.datetime.strptime(raw, fmt).strftime("%Y-%m-%dT%H:%M")
        except ValueError:
            pass
    return None


def fingerprint(time_raw, name, message):
    joined = "\x1f".join([time_raw, name, message]).encode("utf-8")
    return hashlib.sha1(joined).hexdigest()[:16]


def fetch_csv(url):
    req = urllib.request.Request(url, headers={"User-Agent": "guestbook_updater"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
        return resp.read().decode("utf-8-sig")


def read_rows(text):
    """The sheet's rows as submissions. The first column is Google's
    timestamp; the name and message columns are found by their headings,
    and fall back to the second and third columns."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return [], "the sheet is empty"
    head = [h.strip().lower() for h in rows[0]]
    name_col = next((i for i, h in enumerate(head) if "name" in h), 1)
    msg_col = next((i for i, h in enumerate(head) if "message" in h), 2)
    if len(head) <= max(name_col, msg_col):
        return [], ("the sheet has %d column(s); it needs a timestamp, a "
                    "name and a message" % len(head))
    out = []
    for row in rows[1:]:
        if len(row) <= max(name_col, msg_col):
            continue
        time_raw = row[0].strip()
        name = row[name_col].strip()
        message = row[msg_col].strip()
        if not message:
            continue
        out.append({
            "key": fingerprint(time_raw, name, message),
            "time_raw": time_raw,
            "time": parse_time(time_raw),
            "name": name,
            "message": message,
        })
    out.sort(key=lambda r: r["time"] or "")
    return out, None


# ============================================================
# ASKING
# ============================================================

def ask(prompt, choices=None):
    while True:
        answer = input(prompt).strip()
        if choices is None or answer.lower() in choices:
            return answer.lower() if choices else answer
        print("   Please type one of: " + ", ".join(sorted(choices)))


def ask_text(what):
    print("   Type %s. Press Enter on an empty line to finish." % what)
    lines = []
    while True:
        line = input("   > ")
        if not line.strip():
            break
        lines.append(line.rstrip())
    return "\n".join(lines)


def ask_links(targets, by_word):
    links = []
    print("   Links (optional). Type a room such as solar_system/earth, a")
    print("   card's id, or a live exhibit such as earth or sun. Press Enter")
    print("   on an empty line when done.")
    while True:
        typed = input("   link > ").strip()
        if not typed:
            return links
        href = resolve_link(typed, targets, by_word)
        if not href:
            print("   Not a page of this gallery -- nothing added. Check the spelling.")
            continue
        default = targets.get(href, href)
        label = input("   label [%s] > " % default).strip() or default
        links.append({"label": label, "href": href})
        print("   added: %s -> %s" % (label, href))


def now_iso():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")


def short(text, width=70):
    one = " ".join((text or "").split())
    return one if len(one) <= width else one[:width - 3] + "..."


def pick_entry(book):
    entries = sorted(book.get("entries", []), key=lambda e: e.get("time", ""), reverse=True)
    if not entries:
        print("   The guest book has no entries.")
        return None
    shown = entries[:SHOW_RECENT]
    for i, e in enumerate(shown, 1):
        print("   %2d. %s, %s: %s" % (i, e.get("name", "?"), (e.get("time") or "")[:10],
                                    short(e.get("text"), 50)))
    answer = ask("   Which number (Enter to cancel)? ")
    if not answer:
        return None
    if not answer.isdigit() or not 1 <= int(answer) <= len(shown):
        print("   No such number.")
        return None
    return shown[int(answer) - 1]


# ============================================================
# THE RUN
# ============================================================

def review(rows, book, local, save, targets, by_word):
    counts = {"approved": 0, "declined": 0, "later": 0}
    seen = local.setdefault("seen", {})
    pending = [r for r in rows if r["key"] not in seen]
    if not pending:
        print("No new messages.")
        return counts
    oldest = pending[0]["time"]
    age = ""
    if oldest:
        days = (datetime.datetime.now() -
                datetime.datetime.strptime(oldest, "%Y-%m-%dT%H:%M")).days
        age = " The oldest has waited %d day%s." % (days, "" if days == 1 else "s")
    print("%d new message%s.%s" % (len(pending), "" if len(pending) == 1 else "s", age))
    for n, row in enumerate(pending, 1):
        print("")
        print("-- %d of %d -- %s, %s" % (n, len(pending), row["name"] or "(no name)",
                                         row["time_raw"]))
        for line in row["message"].splitlines() or [""]:
            print("   " + line)
        answer = ask("a approve, d decline, l later, q stop > ", {"a", "d", "l", "q"})
        if answer == "q":
            counts["later"] += len(pending) - n + 1
            break
        if answer == "l":
            counts["later"] += 1
            continue
        if answer == "d":
            seen[row["key"]] = "declined"
            counts["declined"] += 1
            save()
            continue
        entry = {
            "id": (row["time"] or now_iso()) + "-v-" + row["key"][:6],
            "time": row["time"] or now_iso(),
            "name": row["name"] or "A visitor",
            "by": "visitor",
            "text": row["message"],
            "links": [],
            "replies": [],
        }
        book.setdefault("entries", []).append(entry)
        seen[row["key"]] = "approved"
        counts["approved"] += 1
        save()
        print("   Approved.")
        if ask("   Reply to it now? y/n > ", {"y", "n"}) == "y":
            add_reply(entry, targets, by_word, save)
    return counts


def add_reply(entry, targets, by_word, save):
    text = ask_text("your reply")
    if not text:
        print("   No text -- no reply added.")
        return False
    links = ask_links(targets, by_word)
    entry.setdefault("replies", []).append(
        {"time": now_iso(), "name": HOST_NAME, "text": text, "links": links})
    save()
    print("   Reply added.")
    return True


def main():
    root = find_root()
    if not root:
        print("Could not find the gallery repo (a folder with index.html and data/).")
        print("Keep this file in tonyquintanilla.github.io/tools/ and run it again.")
        return 1
    os.chdir(root)
    print("=" * 70)
    print("  guest book updater -- %s" % root)
    print("=" * 70)

    book = read_json(BOOK, None)
    if book is None:
        print("%s is missing. Nothing was changed." % BOOK)
        return 1
    local = read_json(LOCAL, {})
    before = json.dumps(book, sort_keys=True)
    targets, by_word = load_targets(root)
    print("%d entr%s in the guest book; %d gallery pages a link may point at."
          % (len(book.get("entries", [])), "y" if len(book.get("entries", [])) == 1 else "ies",
             len(targets)))

    def save():
        write_json(BOOK, book)
        write_json(LOCAL, local)

    # 1. The form's submissions.
    url = local.get("csv_url", "")
    if not url:
        print("")
        print("No link to the form's responses yet. In the Google Sheet the form")
        print("writes to: File > Share > Publish to web, choose the responses")
        print("sheet and Comma-separated values (.csv), click Publish, and copy")
        print("the address it gives. Paste it here, or press Enter to skip")
        print("visitor messages this time.")
        typed = input("address > ").strip()
        if typed.startswith(CSV_PREFIX) and "output=csv" in typed:
            local["csv_url"] = url = typed
            write_json(LOCAL, local)
            print("Saved in %s (kept off the public repo)." % LOCAL)
        elif typed:
            print("That is not a Google Sheets 'Publish to web' CSV address "
                  "(it should start with %s and contain output=csv). Not saved." % CSV_PREFIX)
    counts = {"approved": 0, "declined": 0, "later": 0}
    if url:
        print("")
        print("Fetching the form's responses...")
        try:
            rows, problem = read_rows(fetch_csv(url))
        except Exception as exc:
            rows, problem = [], "could not fetch them (%s)" % exc
        if problem:
            print("Visitor messages skipped this time: %s." % problem)
        else:
            counts = review(rows, book, local, save, targets, by_word)

    # 2. The menu.
    while True:
        print("")
        answer = ask("w write an entry, r reply, x remove an entry, f form address, q finish > ",
                     {"w", "r", "x", "f", "q"})
        if answer == "q":
            break
        if answer == "w":
            text = ask_text("your entry")
            if not text:
                print("   No text -- nothing added.")
                continue
            links = ask_links(targets, by_word)
            stamp = now_iso()
            book.setdefault("entries", []).append({
                "id": stamp + "-host-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:6],
                "time": stamp, "name": HOST_NAME, "by": "host",
                "text": text, "links": links, "replies": []})
            save()
            print("   Entry added.")
        elif answer == "r":
            entry = pick_entry(book)
            if entry is not None:
                add_reply(entry, targets, by_word, save)
        elif answer == "x":
            entry = pick_entry(book)
            if entry is not None:
                print("   Remove: %s, %s" % (entry.get("name"), short(entry.get("text"))))
                if ask("   Sure? y/n > ", {"y", "n"}) == "y":
                    book["entries"].remove(entry)
                    save()
                    print("   Removed.")
        elif answer == "f":
            typed = input("   The form's public address (from the form's Send button) > ").strip()
            if typed.startswith(FORM_PREFIXES) and not re.search(r"[\"'<>\s]", typed):
                book["form_url"] = typed
                save()
                print("   Saved. The lobby will show 'Sign the guest book' after your push.")
            elif typed:
                print("   Not a Google Forms address -- not saved.")

    # 3. What happened.
    changed = json.dumps(book, sort_keys=True) != before
    print("")
    print("=" * 70)
    print("  approved %d, declined %d, waiting %d; the guest book now has %d entr%s"
          % (counts["approved"], counts["declined"], counts["later"],
             len(book.get("entries", [])), "y" if len(book.get("entries", [])) == 1 else "ies"))
    if changed:
        print("  CHANGED: commit data/guestbook.json in GitHub Desktop and push.")
    else:
        print("  No change to data/guestbook.json.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''),
    'tools/test_guestbook_updater.py': ('a34afb77388aa1b32aa1818c5475c65d', r'''#!/usr/bin/env python3
"""
test_guestbook_updater.py -- the guest book updater, checked offline (L-281).

RUN: from the gallery repo root, `python tools/test_guestbook_updater.py`,
or open it in VS Code and press Run. The gallery maintenance run runs it.

WHAT IT DOES
    Builds a throwaway copy of the gallery's files in a temporary folder
    -- index.html left empty, the REAL gallery_metadata.json and
    gallery_config.json, a guest book holding one entry -- and runs
    tools/guestbook_updater.py against it with scripted answers and a
    made-up sheet of submissions in place of Google. Nothing in the real
    repo is written, and nothing is fetched from the network.

WHAT MAKES IT FAIL
    - an approved message missing from the book, or a declined or
      "later" one in it
    - a declined message shown again on the next run, or a "later" one
      not shown again
    - the declined message's words stored anywhere by the tool
    - a link to something that is not a page of this gallery written to
      the book, or a real room, card or exhibit refused
    - a reply landing under the wrong entry, a removal removing the wrong
      one, a non-Google address saved as the form or the sheet
    - the book written in anything but ASCII, or unreadable as JSON
    - the sheet read wrongly when its columns are in another order

    A SELF-TEST runs first: the link check is handed made-up names that
    must be refused and real ones that must be accepted, so a check that
    accepts everything or nothing fails here before it can pass below.

Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
"""

import builtins
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import guestbook_updater as gu  # noqa: E402

SHEET = (
    "Timestamp,Your name,Your message\r\n"
    "9/20/2026 10:15:00,Ana,\"Loved the Sun room.\nThe shells are beautiful.\"\r\n"
    "9/21/2026 11:00:00,Spam Bot,Buy things at example dot com\r\n"
    "9/22/2026 12:30:00,Ben,Please add Saturn's moons\r\n"
    "9/23/2026 08:00:00,,A message with no name\r\n"
)

FAILURES = []
CHECKS = [0]


def check(ok, what):
    CHECKS[0] += 1
    if ok:
        print("ok   " + what)
    else:
        FAILURES.append(what)
        print("FAIL " + what)


def make_root():
    root = tempfile.mkdtemp(prefix="gb_test_")
    os.makedirs(os.path.join(root, "data"))
    os.makedirs(os.path.join(root, "gallery"))
    os.makedirs(os.path.join(root, "tools"))
    open(os.path.join(root, "index.html"), "w").close()
    for rel in (gu.METADATA, gu.CONFIG):
        shutil.copy(os.path.join(REPO, rel), os.path.join(root, rel))
    book = {"about": "test", "form_url": "", "entries": [
        {"id": "seed", "time": "2026-09-01T09:00", "name": "Tony", "by": "host",
         "text": "Welcome", "links": [], "replies": []}]}
    with open(os.path.join(root, gu.BOOK), "w") as f:
        json.dump(book, f)
    return root


def run(root, answers, sheet=SHEET):
    """Run the tool's main() in root with scripted answers. Returns what
    it printed. Fails the check if it asks more questions than scripted."""
    queue = list(answers)
    printed = io.StringIO()
    real_input, real_find, real_fetch, real_stdout = (
        builtins.input, gu.find_root, gu.fetch_csv, sys.stdout)

    def fake_input(prompt=""):
        printed.write(prompt)
        if not queue:
            raise RuntimeError("the tool asked more than the script answers: " + prompt)
        answer = queue.pop(0)
        printed.write(answer + "\n")
        return answer

    builtins.input = fake_input
    gu.find_root = lambda: root
    gu.fetch_csv = lambda url: sheet
    sys.stdout = printed
    cwd = os.getcwd()
    try:
        code = gu.main()
    except RuntimeError as exc:
        code = "error: %s" % exc
    finally:
        builtins.input, gu.find_root, gu.fetch_csv, sys.stdout = (
            real_input, real_find, real_fetch, real_stdout)
        os.chdir(cwd)
    if queue:
        code = "error: %d scripted answer(s) left unused" % len(queue)
    return code, printed.getvalue()


def book_of(root):
    with open(os.path.join(root, gu.BOOK), "rb") as f:
        raw = f.read()
    return raw, json.loads(raw.decode("ascii"))


def main():
    # ---- self-test: the link check can say no and can say yes ----
    targets, by_word = gu.load_targets(REPO)
    bogus = ["solar_system/earthh", "nosuchcard", "https://example.com/",
             "javascript:alert(1)", "#room=x\" onclick=\"y", ""]
    real = ["solar_system/earth", "earth", "sun", "#room=solar_system/sun",
            "https://palomasorrery.com/#room=solar_system"]
    refused = [b for b in bogus if gu.resolve_link(b, targets, by_word) is None]
    accepted = [r for r in real if gu.resolve_link(r, targets, by_word)]
    check(len(refused) == len(bogus), "self-test: %d of %d made-up links refused"
          % (len(refused), len(bogus)))
    check(len(accepted) == len(real), "self-test: %d of %d real pages accepted"
          % (len(accepted), len(real)))
    check(len(targets) > 20, "self-test: %d gallery pages found to link to" % len(targets))

    root = make_root()
    try:
        # ---- run 1: first run, link pasted, three decisions, then stop ----
        url = "https://docs.google.com/spreadsheets/d/e/XYZ/pub?output=csv"
        code, out = run(root, [
            url,
            "a", "y", "Thank you!", "", "earth", "", "",  # Ana: approve, reply, link
            "d",                                      # Spam: decline
            "l",                                      # Ben: later
            "q",                                      # stop reviewing
            "q",                                      # finish
        ])
        check(code == 0, "run 1 finished (%s)" % code)
        raw, book = book_of(root)
        names = [e["name"] for e in book["entries"]]
        check(names == ["Tony", "Ana"], "run 1: book holds Tony and Ana only (%s)" % names)
        ana = book["entries"][1]
        check(ana["by"] == "visitor" and ana["links"] == [],
              "run 1: Ana's entry is a visitor's, with no links")
        check(ana["text"] == "Loved the Sun room.\nThe shells are beautiful.",
              "run 1: a two-line message kept both lines")
        check(ana["time"] == "2026-09-20T10:15", "run 1: Google's timestamp read as %s" % ana["time"])
        reply = (ana.get("replies") or [{}])[0]
        check(reply.get("text") == "Thank you!" and reply.get("name") == gu.HOST_NAME,
              "run 1: reply under Ana's entry")
        check(reply.get("links") == [{"label": targets["interactive.html?exhibit=earth"],
                                      "href": "interactive.html?exhibit=earth"}],
              "run 1: reply's link is the Earth exhibit, labelled with its card title")
        check(all(b < 128 for b in raw), "run 1: the book is ASCII")
        local = json.load(open(os.path.join(root, gu.LOCAL)))
        check(local.get("csv_url") == url, "run 1: sheet address saved locally")
        check(sorted(local.get("seen", {}).values()) == ["approved", "declined"],
              "run 1: two decisions remembered, 'later' not")
        local_text = open(os.path.join(root, gu.LOCAL)).read()
        check("Buy things" not in local_text and "Spam" not in local_text,
              "run 1: the declined message is not stored")
        check("CHANGED: commit data/guestbook.json" in out, "run 1: says to commit")

        # ---- run 2: only Ben and the nameless one come back ----
        code, out = run(root, [
            "a", "n",           # Ben (shown first, oldest waiting): approve, no reply
            "a", "n",           # the nameless one: approve
            "w", "Two new rooms are open.", "", "solar_system/earthh",
            "solar_system/earth", "The Earth room", "", # own entry: typo refused, then good
            "f", "https://example.com/form",           # bad form address refused
            "f", "https://forms.gle/AbC123",           # good form address
            "q",
        ])
        check(code == 0, "run 2 finished (%s)" % code)
        check("2 new messages" in out, "run 2: two waiting messages shown, not four")
        check("Spam Bot" not in out and "Ana" not in out.split("new message")[1].split("w write")[0],
              "run 2: decided messages not shown again")
        check("Not a page of this gallery" in out, "run 2: the misspelt room refused")
        check("Not a Google Forms address" in out, "run 2: non-Google form address refused")
        raw, book = book_of(root)
        names = [e["name"] for e in book["entries"]]
        check(names == ["Tony", "Ana", "Ben", "A visitor", "Tony"],
              "run 2: order in the file is as added (%s)" % names)
        own = book["entries"][-1]
        check(own["by"] == "host" and own["links"] == [
            {"label": "The Earth room", "href": "#room=solar_system/earth"}],
            "run 2: own entry with only the good link")
        check(book["form_url"] == "https://forms.gle/AbC123", "run 2: form address saved")
        every = []
        for e in book["entries"]:
            every += e.get("links", [])
            for r in e.get("replies", []):
                every += r.get("links", [])
        check(all(any(p.match(l["href"]) for p in gu.SAFE_HREF) for l in every),
              "run 2: all %d links in the book are ones the page draws" % len(every))

        # ---- run 3: nothing new; remove Ben's entry ----
        # newest first: Tony (now), A visitor (9/23), Ben (9/22) -> number 3
        code, out = run(root, ["x", "3", "y", "q"])
        check(code == 0, "run 3 finished (%s)" % code)
        check("No new messages." in out, "run 3: nothing new to review")
        raw, book = book_of(root)
        check([e["name"] for e in book["entries"]] == ["Tony", "Ana", "A visitor", "Tony"],
              "run 3: Ben's entry removed, the rest kept")

        # ---- columns in another order ----
        rows, problem = gu.read_rows("Timestamp,Message,Name\n9/24/2026 09:00:00,Hi,Cy\n")
        check(not problem and rows and rows[0]["name"] == "Cy" and rows[0]["message"] == "Hi",
              "columns found by their headings, whatever the order")
        rows, problem = gu.read_rows("Timestamp\n9/24/2026 09:00:00\n")
        check(bool(problem), "a sheet without name and message columns is reported")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("")
    if FAILURES:
        print("=== GUEST BOOK UPDATER: %d of %d checks FAILED" % (len(FAILURES), CHECKS[0]))
        return 1
    print("=== GUEST BOOK UPDATER: all %d checks passed (3 scripted runs, "
          "self-test first)" % CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''),
}


def fingerprint(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def fail(message):
    print("FAILURE: " + message)
    print("NOTHING was written. Undo is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root, "index.html")):
        fail("index.html is not beside this script. Save it in the gallery "
             "repo root (tonyquintanilla.github.io) and run it again.")

    results = {}
    for name, want in EXPECTED.items():
        with open(os.path.join(root, name), "rb") as f:
            data = f.read()
        got = fingerprint(data)
        if got != want:
            fail("%s is not the file this patch was built against (gallery "
                 "%s). Expected %s, found %s." % (name, BASE, want, got))
        crlf = b"\r\n" in data
        text = data.replace(b"\r\n", b"\n")
        for label, old, new in EDITS[name]:
            n = text.count(old)
            if n != 1:
                fail("ANCHOR FAIL in %s, edit '%s': expected 1 match, found %d."
                     % (name, label, n))
            if any(b > 127 for b in new):
                fail("edit '%s' carries non-ASCII bytes." % label)
            text = text.replace(old, new)
        if crlf:
            text = text.replace(b"\n", b"\r\n")
        results[name] = (text, [e[0] for e in EDITS[name]], crlf)

    creates = []
    for rel, (md5, content) in NEW_FILES.items():
        if hashlib.md5(content.encode("ascii")).hexdigest() != md5:
            fail("%s: the copy inside this script is damaged." % rel)
        path = os.path.join(root, *rel.split("/"))
        if os.path.exists(path):
            with open(path, "rb") as f:
                if fingerprint(f.read()) == md5:
                    print("same %s already exists and matches; left as is" % rel)
                    continue
            fail("%s already exists with different contents." % rel)
        creates.append((rel, path, content))

    for rel, path, content in creates:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="ascii", newline="") as f:
            f.write(content)
        print("ok   created %s (%d bytes)" % (rel, len(content)))
    for name, (text, labels, crlf) in results.items():
        with open(os.path.join(root, name), "wb") as f:
            f.write(text)
        for label in labels:
            print("ok   %s: %s" % (name, label))
        print("     %s written (%d bytes%s)" % (name, len(text), ", CRLF kept" if crlf else ""))
    print("stamps updated: gallery_maintenance_run.py docstring")
    print("patch applied")
    print("")
    print("NEXT: run gallery_maintenance_run.py. It should show a new row,")
    print("'Guest book updater', passing. Then commit and push.")


if __name__ == "__main__":
    main()
