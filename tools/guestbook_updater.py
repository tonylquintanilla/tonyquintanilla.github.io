#!/usr/bin/env python3
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
        p  pin or unpin an entry. A pinned entry stays at the top of
           the guest book; unpinned, it goes back to its place by date
        f  set the form's public address, which turns on the lobby's
           "Sign the guest book" link
        s  change the sheet's private address -- after you stop
           publishing the sheet and publish it again, Google may give
           it a new address; paste the new one here
        q  finish
    Your own entries and replies can link to pages of the gallery. You
    can type a room ("solar_system/earth"), a card's id, or a live
    exhibit's name ("earth", "sun"). Each is checked against the
    gallery's own list of cards and rooms, so a typo is refused rather
    than published as a dead link. A visitor's message never carries a
    link -- the lobby shows it as plain text whatever it says.

    Anything else the form asks -- today, the overall rating -- is shown
    to you beside each message while you decide, and never written to
    the guest book. It stays private in your sheet.

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
    which is why it stays there. Paste it ONLY into this tool -- never
    into the run record or any file that is committed. On 2026-09-27 it
    reached the public orrery repo through the run record, and the cure
    was to stop publishing the sheet so the old address leads nowhere.

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

WHICH COLUMNS IT READS
    The message is the column whose heading contains "message" or
    "note" -- the form's is "Leave a note about the gallery". The name
    is the column whose heading contains "name". The first column is
    Google's timestamp. If no heading names a message or a note, the
    tool reads nothing and says so, rather than guess a column: a guess
    once pointed at an email column (2026-09-27).

THE CHECK
    tools/test_guestbook_updater.py runs this tool against made-up
    submissions with scripted answers. The gallery maintenance run
    runs it.

Role: devtool
Domain: dev_tools

Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
Module updated: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281,
Daily Run patch): the message column is found by "message" or "note",
with no fallback to a column by position; the heading row is found by
its "Timestamp" cell; other answers are shown privately during review.
Module updated: September 28, 2026 with Anthropic's Claude Opus 5.5 (L-281,
patch 7): the menu's p choice pins or unpins an entry.
Module updated: September 28, 2026 with Anthropic's Claude Opus 5.5 (L-281,
patch 5): the menu's s choice changes the sheet's private address and
fetches from the new one at once; a failed fetch says to use it.
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
    """The sheet's rows as submissions. The heading row is the first row
    with a "Timestamp" cell. The message column is the one whose heading
    holds "message" or "note", and there is no fallback: with neither,
    nothing is read. The name column holds "name"; without one, every
    message is from "A visitor". Every other column is kept as an extra,
    shown to Tony privately and never written to the book."""
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return [], "the sheet is empty"
    start = next((i for i, r in enumerate(rows)
                  if any(c.strip().lower() == "timestamp" for c in r)), 0)
    raw_head = [h.strip() for h in rows[start]]
    head = [h.lower() for h in raw_head]
    msg_col = next((i for i, h in enumerate(head)
                    if "message" in h or "note" in h), None)
    if msg_col is None:
        return [], ("no column heading contains 'message' or 'note', so "
                    "nothing was read. Headings found: %s"
                    % ", ".join(raw_head))
    name_col = next((i for i, h in enumerate(head)
                     if "name" in h and i != msg_col), None)
    out = []
    for row in rows[start + 1:]:
        if len(row) <= msg_col:
            continue
        time_raw = row[0].strip()
        name = row[name_col].strip() if name_col is not None and len(row) > name_col else ""
        message = row[msg_col].strip()
        if not message:
            continue
        extras = []
        for i, cell in enumerate(row):
            if i in (0, msg_col, name_col) or i >= len(raw_head):
                continue
            if cell.strip():
                extras.append((raw_head[i] or "column %d" % (i + 1), cell.strip()))
        out.append({
            "key": fingerprint(time_raw, name, message),
            "time_raw": time_raw,
            "time": parse_time(time_raw),
            "name": name,
            "message": message,
            "extras": extras,
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
        print("   %2d. %s%s, %s: %s" % (i, "[pinned] " if e.get("pinned") is True else "",
                                      e.get("name", "?"), (e.get("time") or "")[:10],
                                      short(e.get("text"), 45)))
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
        for heading, value in row.get("extras", []):
            print("   (private, not published) %s: %s" % (heading, value))
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

    counts = {"approved": 0, "declined": 0, "later": 0}

    def ask_sheet_address(intro):
        """Ask for the sheet's CSV address; save it if it is one. Returns
        the saved address, or None."""
        print("")
        for line in intro:
            print(line)
        print("Paste it only here -- never into the run record or any file")
        print("that is committed. Press Enter to leave it as it is.")
        typed = input("address > ").strip()
        if typed.startswith(CSV_PREFIX) and "output=csv" in typed:
            local["csv_url"] = typed
            write_json(LOCAL, local)
            print("Saved in %s (kept off the public repo)." % LOCAL)
            return typed
        if typed:
            print("That is not a Google Sheets 'Publish to web' CSV address "
                  "(it should start with %s and contain output=csv). Not saved." % CSV_PREFIX)
        return None

    def fetch_and_review(url):
        print("")
        print("Fetching the form's responses...")
        try:
            rows, problem = read_rows(fetch_csv(url))
        except Exception as exc:
            rows, problem = [], "could not fetch them (%s)" % exc
        if problem:
            print("Visitor messages skipped this time: %s." % problem)
            print("If the sheet was published again and has a new address,")
            print("choose s in the menu below and paste the new one.")
            return
        got = review(rows, book, local, save, targets, by_word)
        for k in counts:
            counts[k] += got[k]

    # 1. The form's submissions.
    url = local.get("csv_url", "")
    if not url:
        url = ask_sheet_address([
            "No link to the form's responses yet. In the Google Sheet the form",
            "writes to: File > Share > Publish to web, choose the responses",
            "sheet and Comma-separated values (.csv), click Publish, and copy",
            "the address it gives. Paste it here, or press Enter to skip",
            "visitor messages this time."])
    if url:
        fetch_and_review(url)

    # 2. The menu.
    while True:
        print("")
        answer = ask("w write, r reply, x remove, p pin/unpin, f form address, "
                     "s sheet address, q finish > ",
                     {"w", "r", "x", "p", "f", "s", "q"})
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
        elif answer == "p":
            entry = pick_entry(book)
            if entry is not None:
                if entry.get("pinned") is True:
                    del entry["pinned"]
                    print("   Unpinned: it goes back to its place by date.")
                else:
                    entry["pinned"] = True
                    print("   Pinned: it stays at the top of the guest book.")
                save()
        elif answer == "s":
            new = ask_sheet_address([
                "The sheet's private address changes when you stop publishing",
                "the sheet and publish it again. In the Google Sheet: File >",
                "Share > Publish to web, and copy the address it shows now."])
            if new:
                fetch_and_review(new)
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
