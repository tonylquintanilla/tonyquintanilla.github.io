"""patch_L429_3_goto_centre_L237_date_L216_no_pause.py

Built on gallery cb9038ccb7aa9747194b330e49c8a52d70598ce8 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
("L428"). Written October 10, 2026 with Anthropic's Claude Opus 5.5,
from Tony's run record documentation/WHERE_WE_ARE_10-9-26_2307_run_record.md
(in the orrery) and his answers of 2026-10-10.

HOW TO RUN
    Save this file in the gallery repo's ROOT folder (the folder that
    holds index.html). Open it in VS Code and press Run. Or, from a
    terminal in that folder:
        python patch_L429_3_goto_centre_L237_date_L216_no_pause.py

WHAT IT CHANGES
    interactive.html (L-429, Tony: "For uniformity rename the Go buttons
        in all rooms to Go To and center.")
      - In every room's list, GO is now "GO TO", in the middle of the
        row. In the Solar System room, "Enter the ... room" sits to its
        right, so a row reads: the name, Go To, then the room.
      - A long name continues on the next lines, so every name shows in
        full (Tony, 2026-10-10). A row for a
        layer the page cannot draw yet keeps its full width.
      - The Solar System room's info panel says "Go To".
    tools/headless/walk_solar_system_drawer.js (Claude-only check)
      - Checks that Go To is centred and the room button follows it.
    gallery/assembler/tests/test_artifact1_earth.py (L-237)
      - The test takes its date from the served cache (Earth's stored
        "today") instead of the fixed July 13, 2026, which the served
        window has moved past. The Artifact 1 row goes green again,
        with the same five results as its pin.
    daily_run.py (L-216, Tony: "you can remove the pause check from the
        daily run. the retry is sufficient")
      - No stop to pause OneDrive, and no "Resume OneDrive" at the end.
        The cache build follows the guest book straight away. To skip a
        build, run the guest book updater alone from the dashboard.
    tools/exhibit_store_editor.py and tools/test_exhibit_store_editor.py
      - The editor's save message no longer says to pause OneDrive, and
        its check now requires that it does not.
    Each file's header gains an "Updated" entry.

SAFETY
    Each file is checked against its content at cb9038c (line endings
    ignored). Every edit must match exactly once. If any check fails,
    NOTHING is written. Undo after a run is Discard Changes in GitHub
    Desktop. Success prints one "ok" line per edit and "patch applied".
    Once it has run, move this file into the gallery's documentation/
    folder. A second run says it was already applied.
"""
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FILES = {
    "interactive.html": "23b41c3d2b4a62e8b5a94a1ae65d4677",
    "tools/headless/walk_solar_system_drawer.js": "63de61d5f55679ad42e36c6f960a63f0",
    "gallery/assembler/tests/test_artifact1_earth.py": "fb733512f6b2457f4b98701978b3dfba",
    "daily_run.py": "cfb5036025ecc200dc699857376579b6",
    "tools/exhibit_store_editor.py": "26968f32cb10d4c7aa8f6b40182c804d",
    "tools/test_exhibit_store_editor.py": "6ba954cdc68bbace5dbf306923547f44",
}

# ========================================================== interactive.html

IA = []

IA.append(("interactive.html: header comment stamp", (
b"""        on the name's line when sideways. The info panel says so)
     Architecture: Option C viewer""",
b"""        on the name's line when sideways. The info panel says so)
     Updated: October 10, 2026 with Anthropic's Claude Opus 5.5
       (L-429, Tony's rulings of 2026-10-10: "For uniformity rename the
        Go buttons in all rooms to Go To and center." In every room's
        list GO reads GO TO and sits in the middle of the row; in the
        Solar System room the room button follows it on the right, so a
        row reads name, Go To, room. The row is a three-column grid;
        the left end still ticks and the name keeps the left half)
     Architecture: Option C viewer""")))

IA.append(("interactive.html: the row is a three-column grid", (
b"""        .sun-row {
            display: flex; align-items: center; gap: 0; width: 100%;
            min-height: 44px;
            background: none; border: none; padding: 0 16px 0 0; cursor: pointer;""",
b"""        /* L-429, Tony, 2026-10-10: Go To in the middle of every row.
           Three equal-sided columns: the left end and the name share
           the first, Go To is the second, the room button (Solar System
           room) the third. The name starts after the left end's 65 px,
           and the left end sits above it, so it still takes the tap. */
        .sun-row {
            display: grid; align-items: center; width: 100%;
            grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
            column-gap: 10px;
            min-height: 44px;
            /* Even sides, so Go To sits on the row's true centre; the left
               end reaches back over the left padding (margin below), so
               its tap area still starts at the edge. */
            background: none; border: none; padding: 0 16px; cursor: pointer;""")))

IA.append(("interactive.html: left end above the name", (
b"""        .sun-row .pick {
            display: flex; align-items: center; gap: 10px;
            align-self: stretch; flex-shrink: 0;
            padding: 0 12px 0 16px;
        }""",
b"""        .sun-row .pick {
            display: flex; align-items: center; gap: 10px;
            align-self: stretch; flex-shrink: 0;
            padding: 0 12px 0 16px;
            grid-column: 1; grid-row: 1; justify-self: start;
            position: relative; z-index: 1; margin-left: -16px;
        }""")))

IA.append(("interactive.html: name in the left half", (
b"""        .sun-row .rname {
            flex: 1; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
        }""",
b"""        .sun-row .rname {
            flex: 1; overflow: hidden; text-overflow: ellipsis;
            white-space: nowrap;
            grid-column: 1; grid-row: 1; min-width: 0; padding-left: 49px;
        }
        /* A layer not drawn yet has no Go To; its words keep the row. */
        .sun-row.absent .rname { grid-column: 1 / -1; }
        /* The left half is narrow, so a long name continues on the next
           lines instead of being cut (Tony, 2026-10-10: every name shown
           in full). On the desktop the names fit on one line anyway. */
        .sun-row .rname {
            white-space: normal; overflow-wrap: anywhere;
            line-height: 1.25; padding-top: 6px; padding-bottom: 6px;
        }""")))

IA.append(("interactive.html: Go To in the middle", (
b"""        .sun-row .go {
            margin-left: 10px;
            color: #f0594a;""",
b"""        .sun-row .go {
            grid-column: 2; grid-row: 1; justify-self: center;
            white-space: nowrap;
            color: #f0594a;""")))

IA.append(("interactive.html: the room button on the right", (
b"""        .sun-row .open-inline {
            flex-shrink: 0; margin-left: 10px;
            color: var(--text-dim); font-size: 12px; white-space: nowrap;
        }""",
b"""        .sun-row .open-inline {
            grid-column: 3; grid-row: 1; justify-self: end; min-width: 0;
            color: var(--text-dim); font-size: 12px; white-space: nowrap;
        }""")))

IA.append(("interactive.html: inline CSS comment", (
b"""           row puts its button, or "No room or cards yet", on the name's
           line, between the name and GO, and stays one line tall. Shown""",
b"""           row puts its button, or "No room or cards yet", on the name's
           line, after Go To since L-429, and stays one line tall. Shown""")))

IA.append(("interactive.html: info panel says Go To", (
b"""    "<li>GO takes the view to a body, and Home backs out to hold every",""",
b"""    "<li>Go To takes the view to a body, and Home backs out to hold every",""")))

IA.append(("interactive.html: inline holder after Go To", (
b"""    const go = row.querySelector(".go");
    if (go) { row.insertBefore(inline, go); } else { row.appendChild(inline); }""",
b"""    // After Go To since L-429 (2026-10-10): name, Go To, then the room.
    row.appendChild(inline);""")))

IA.append(("interactive.html: the button's word", (
b"""            '<span class="go">go</span>';""",
b"""            '<span class="go">go to</span>';""")))

# ==================================================== the walk (Claude-only)

WK = []

WK.append(("walk: header note", (
b"""// room shows its button on its row always; a body with none still opens.""",
b"""// room shows its button on its row always; a body with none still opens.
// Since 2026-10-10 Go To sits in the middle of the row and the room's
// button after it.""")))

WK.append(("walk: arrival order on the row", (
b"""  ok(inl("earth").nextElementSibling === row("earth").querySelector(".go"), "Earth's button not before GO");""",
b"""  ok(inl("earth").previousElementSibling === row("earth").querySelector(".go"), "Earth's button not after Go To");
  ok(row("earth").querySelector(".go").textContent === "go to", "the button's word is not go to");""")))

WK.append(("walk: sideways order", (
b"""  ok(inl("earth").nextElementSibling === row("earth").querySelector(".go"), "sideways: the button not before GO");""",
b"""  ok(inl("earth").previousElementSibling === row("earth").querySelector(".go"), "sideways: the button not after Go To");""")))

# ================================================= the Artifact 1 test (L-237)

AT = []

AT.append(("test_artifact1_earth.py: date from the cache", (
b"""             "epoch": "2026-07-13T00:00:00Z"}""",
b"""             "epoch": _iso_from_jd(aot["t"])}""")))

AT.append(("test_artifact1_earth.py: the date helper", (
b"""def _load():""",
b"""def _iso_from_jd(jd):
    # L-237, 2026-10-10: the scene's date is Earth's stored "today" in the
    # served cache, so it is inside the served window on every build. The
    # fixed 2026-07-13 fell out of the window with the build of
    # 2026-10-09, and T2 to T5 stopped printing.
    import datetime
    t = datetime.datetime(2000, 1, 1, 12) + datetime.timedelta(days=jd - 2451545.0)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _load():""")))

AT.append(("test_artifact1_earth.py: header stamp", (
b"""Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
""",
b"""Module created: July 2026 with Anthropic's Claude Opus 4.8 (Phase 2 artifact 1).
Module updated: October 10, 2026 with Anthropic's Claude Opus 5.5 (L-237:
T2's scene date is Earth's stored "today" from the served cache, not the
fixed 2026-07-13 the served window moved past on 2026-10-09).
""")))

# ======================================================== daily_run.py (L-216)

DR = []

DR.append(("daily_run.py: no pause before the build", (
b"""    # 2. The cache build, after the OneDrive pause.
    print("")
    print(LINE)
    print("  Before the cache build: PAUSE ONEDRIVE and note the time.")
    print("  (OneDrive icon in the taskbar > Pause syncing > 2 hours.)")
    print(LINE)
    answer = input("Press Enter when OneDrive is paused, or type s to skip the build today > ")
    paused_at = datetime.datetime.now()
    paused = answer.strip().lower() != "s"
    if not paused:
        results.append(("Cache builder", "skipped today"))
        print("Cache build skipped.")
    else:
        print("OneDrive paused at %s; the pause lasts until about %s."
              % (paused_at.strftime("%H:%M"),
                 (paused_at + datetime.timedelta(hours=2)).strftime("%H:%M")))
        results.append(("Cache builder", run_step(2, *STEPS[1])))
        print("")
        print("The builder's next steps start with the maintenance run.")
        print("The Daily Run runs it now.")""",
b"""    # 2. The cache build. No OneDrive pause since 2026-10-10 (L-216):
    # Tony, "the retry is sufficient" -- the builder retries a refused
    # rename and the swap log records any retry.
    results.append(("Cache builder", run_step(2, *STEPS[1])))
    print("")
    print("The builder's next steps start with the maintenance run.")
    print("The Daily Run runs it now.")""")))

DR.append(("daily_run.py: no resume at the end", (
b"""    print("    2. Then the dashboard's Gallery Maintenance Run -- live, AFTER a push.")
    if paused:
        print("    3. Resume OneDrive.")
""",
b"""    print("    2. Then the dashboard's Gallery Maintenance Run -- live, AFTER a push.")
""")))

DR.append(("daily_run.py: docstring step 2", (
b"""    2. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. Before
       it starts, the Daily Run asks you to pause OneDrive and note the
       time (L-216); press Enter when it is paused, or type s to skip
       the build today. The builder fetches from Horizons, swaps in the
       new cache, and prints its own [SWAP] line and next steps.""",
b"""    2. CACHE BUILDER (tools/gallery_cache_builder.py), no flags. It
       starts straight after the guest book: no OneDrive pause since
       2026-10-10 (L-216, Tony: "the retry is sufficient"). To skip a
       build, run the guest book updater alone from the dashboard. The
       builder fetches from Horizons, swaps in the new cache, and
       prints its own [SWAP] line and next steps.""")))

DR.append(("daily_run.py: docstring summary line", (
b"""    look at GitHub Desktop's change list, commit and push, run the
    maintenance run's live pass, and resume OneDrive.""",
b"""    look at GitHub Desktop's change list, commit and push, and run the
    maintenance run's live pass.""")))

DR.append(("daily_run.py: header stamp", (
b"""Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
""",
b"""Module created: September 27, 2026 with Anthropic's Claude Opus 5.5 (L-281).
Module updated: October 10, 2026 with Anthropic's Claude Opus 5.5 (L-216:
the OneDrive pause and its resume line are gone, by Tony's ruling of
2026-10-10, "the retry is sufficient").
""")))

# ===================================================== the editor and its check

ED = [("exhibit_store_editor.py: no pause in the save message", (
b"""    lines.append("A visitor does not see this yet. To deploy it:")
    lines.append("  1. Pause OneDrive syncing.")
    lines.append("  2. Run the cache builder by hand, watching the change "
                 "list in GitHub Desktop.")
    lines.append("  3. Run the checks.")
    lines.append("  4. Commit the config and the cache TOGETHER, and push.")""",
b"""    lines.append("A visitor does not see this yet. To deploy it:")
    lines.append("  1. Run the cache builder by hand, watching the change "
                 "list in GitHub Desktop.")
    lines.append("  2. Run the checks.")
    lines.append("  3. Commit the config and the cache TOGETHER, and push.")""")),
      ("exhibit_store_editor.py: header stamp", (
b"""Updated October 6, 2026 with Anthropic's Claude Opus 5.5 (L-421: a""",
b"""Updated October 10, 2026 with Anthropic's Claude Opus 5.5 (L-216: the
save message no longer says to pause OneDrive; Tony, 2026-10-10, "the
retry is sufficient").
Updated October 6, 2026 with Anthropic's Claude Opus 5.5 (L-421: a"""))]

TE = [("test_exhibit_store_editor.py: the message names no pause", (
b"""    check("a word save names the cache builder",
          "cache builder" in words_only and "OneDrive" in words_only)""",
b"""    check("a word save names the cache builder, and no OneDrive pause",
          "cache builder" in words_only and "OneDrive" not in words_only)""")),
      ("test_exhibit_store_editor.py: header stamp", (
b"""Updated October 1, 2026 with Anthropic's Claude Opus 5.5 (L-404: check""",
b"""Updated October 10, 2026 with Anthropic's Claude Opus 5.5 (L-216: the save
message must not say to pause OneDrive).
Updated October 1, 2026 with Anthropic's Claude Opus 5.5 (L-404: check"""))]

EDITS = {
    "interactive.html": IA,
    "tools/headless/walk_solar_system_drawer.js": WK,
    "gallery/assembler/tests/test_artifact1_earth.py": AT,
    "daily_run.py": DR,
    "tools/exhibit_store_editor.py": ED,
    "tools/test_exhibit_store_editor.py": TE,
}
DONE_MARK = {
    "interactive.html": b'<span class="go">go to</span>',
    "tools/headless/walk_solar_system_drawer.js": b"Earth's button not after Go To",
    "gallery/assembler/tests/test_artifact1_earth.py": b"def _iso_from_jd(jd):",
    "daily_run.py": b"No OneDrive pause since 2026-10-10",
    "tools/exhibit_store_editor.py": b"save message no longer says to pause OneDrive",
    "tools/test_exhibit_store_editor.py": b"message must not say to pause OneDrive",
}


def fail(msg):
    print("FAILURE: " + msg)
    print("NOTHING was written. Undo is not needed.")
    sys.exit(1)


def main():
    loaded = {}
    for rel in FILES:
        path = os.path.join(ROOT, rel)
        if not os.path.isfile(path):
            fail("%s not found. Save this script in the gallery repo root." % rel)
        raw = open(path, "rb").read()
        loaded[rel] = (raw.replace(b"\r\n", b"\n"), b"\r\n" in raw)

    if all(DONE_MARK[r] in loaded[r][0] for r in FILES):
        print("already applied: all six files carry this patch. Nothing written.")
        return

    out = {}
    for rel, md5 in FILES.items():
        text = loaded[rel][0]
        fp = hashlib.md5(text).hexdigest()
        if fp != md5:
            fail("%s is not the file this patch was built on (content md5 %s, "
                 "expected %s at gallery cb9038c). Has it changed since that "
                 "commit?" % (rel, fp, md5))
        for name, (old, new) in EDITS[rel]:
            n = text.count(old)
            if n != 1:
                fail("ANCHOR FAIL, %s: expected 1 match, found %d." % (name, n))
            text = text.replace(old, new)
            print("ok  " + name)
        bad = sum(1 for b in text if b > 127)
        if bad:
            fail("%s would hold %d non-ASCII byte(s)." % (rel, bad))
        out[rel] = text

    for rel, text in out.items():
        open(os.path.join(ROOT, rel), "wb").write(text)
        if loaded[rel][1]:
            print("note: %s was CRLF in the working copy; written LF" % rel)
    print("stamps updated: the header of each of the six files (October 10, 2026)")
    print("patch applied (%d files)" % len(out))
    print("")
    print("Next: run gallery_maintenance_run.py -- the Artifact 1 row should now")
    print("pass -- then commit and push the gallery in GitHub Desktop, and look")
    print("on the phone (close the Home Screen clip's tab first). Then move this")
    print("script into documentation/.")


if __name__ == "__main__":
    main()
