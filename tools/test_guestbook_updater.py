#!/usr/bin/env python3
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

Role: devtool
Domain: dev_tools

Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
Module updated: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281,
Daily Run patch): the made-up sheet uses the real form's columns; the
rating is shown privately and never written; a sheet whose message
column cannot be named is refused rather than guessed.
Module updated: September 28, 2026 with Anthropic's Claude Opus 5.5 (L-281,
patch 5): a fourth run changes the sheet address with s, checks a wrong
one is refused, the new one is saved and fetched at once, and earlier
decisions survive the change.
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

# The columns of Tony's real form, 2026-09-27: name, rating, note.
SHEET = (
    "Timestamp,Your Name,Overall Gallery Experience Rating,"
    "Leave a note about the gallery\r\n"
    "9/20/2026 10:15:00,Ana,5,\"Loved the Sun room.\nThe shells are beautiful.\"\r\n"
    "9/21/2026 11:00:00,Spam Bot,1,Buy things at example dot com\r\n"
    "9/22/2026 12:30:00,Ben,4,Please add Saturn's moons\r\n"
    "9/23/2026 08:00:00,,,A message with no name\r\n"
)

FAILURES = []
CHECKS = [0]
FETCHED = []


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
    gu.fetch_csv = lambda url: (FETCHED.append(url), sheet)[1]
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
        check("(private, not published) Overall Gallery Experience Rating: 5" in out,
              "run 1: the rating shown to Tony while he decides")
        check(b"Rating" not in raw and b'"5"' not in raw,
              "run 1: the rating not written to the book")

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

        # ---- run 4: the sheet republished at a new address ----
        new_url = "https://docs.google.com/spreadsheets/d/e/NEW/pub?output=csv"
        del FETCHED[:]
        code, out = run(root, [
            "s", "https://example.com/pub?output=csv",   # refused
            "s", new_url,                                 # saved, fetched at once
            "q",
        ])
        check(code == 0, "run 4 finished (%s)" % code)
        check("Not saved." in out, "run 4: a non-Google sheet address refused")
        local = json.load(open(os.path.join(root, gu.LOCAL)))
        check(local.get("csv_url") == new_url, "run 4: the new sheet address saved")
        check(FETCHED == [url, new_url],
              "run 4: fetched from the old address, then at once from the new (%s)"
              % [u.split("/")[-2] for u in FETCHED])
        check(sorted(local.get("seen", {}).values()) == ["approved", "approved", "approved", "declined"],
              "run 4: decisions kept across the address change")

        # ---- columns in another order ----
        rows, problem = gu.read_rows("Timestamp,Message,Name\n9/24/2026 09:00:00,Hi,Cy\n")
        check(not problem and rows and rows[0]["name"] == "Cy" and rows[0]["message"] == "Hi",
              "columns found by their headings, whatever the order")
        rows, problem = gu.read_rows("Timestamp\n9/24/2026 09:00:00\n")
        check(bool(problem), "a sheet without name and message columns is reported")
        # The form as it first was: an email column third, and no heading
        # with "message". The old fallback read the third column as the
        # message -- the email addresses. Now nothing is read.
        rows, problem = gu.read_rows(
            "Timestamp,Your Name,Your Email Address,Your comments\n"
            "9/24/2026 09:00:00,Dee,dee@example.com,Hello\n")
        check(bool(problem) and not rows and "Headings found" in problem,
              "no message or note heading: nothing read, headings named")
        # Deleted questions can leave empty columns behind.
        rows, problem = gu.read_rows(
            "Timestamp,Your Name,Your Email Address,Overall Gallery Experience Rating,"
            "Which exhibit or installation was your favorite,Leave a note about the gallery\n"
            "9/24/2026 09:00:00,Eve,,3,,Nice\n")
        check(not problem and bool(rows) and rows[0]["message"] == "Nice" and rows[0]["name"] == "Eve"
              and rows[0]["extras"] == [("Overall Gallery Experience Rating", "3")],
              "empty left-behind columns ignored; note and rating read")
        rows, problem = gu.read_rows(
            "Form_Responses,,\nTimestamp,Your Name,Leave a note\n9/24/2026 09:00:00,Fay,Hi\n")
        check(not problem and rows and rows[0]["name"] == "Fay",
              "a title row above the headings is skipped")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("")
    if FAILURES:
        print("=== GUEST BOOK UPDATER: %d of %d checks FAILED" % (len(FAILURES), CHECKS[0]))
        return 1
    print("=== GUEST BOOK UPDATER: all %d checks passed (4 scripted runs, "
          "self-test first)" % CHECKS[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
