"""patch_L428_3_L429_1_lobby_contrast_drawer_button.py

Built on gallery 2aab10fdead213ade0cc9c8bdbfe1a6bc03c30b5 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
("L428_1 lobby option E"). Written October 10, 2026 with Anthropic's
Claude Opus 5.5, from Tony's run record of 2026-10-09
(documentation/WHERE_WE_ARE_10-9-26_2307_run_record.md in the orrery)
and his message of 2026-10-10 00:08 about the Solar System room's list.

HOW TO RUN
    Save this file in the gallery repo's ROOT folder (the folder that
    holds index.html). Open it in VS Code and press Run. Or, from a
    terminal in that folder:
        python patch_L428_3_L429_1_lobby_contrast_drawer_button.py

WHAT IT CHANGES
    index.html (L-428, the lobby's way in, round 2)
      - The start card's background is the same see-through dark blue
        as the other lobby cards, so the doves show through it. The
        room's picture stays solid.
      - The lobby's grey type is brighter: the headings are blue, and
        the grey lines (the welcome line, the doors' sentences and
        counts, the card labels, the count line, the guest book's
        dates and note, the doors' arrows, the footer) are near white,
        with the guest
        book's soft dark shadow so they read over the doves. A door's
        own page keeps its colours.
    interactive.html (L-429, the room button on the row)
      - In the Solar System room's list, a body with a room of its own
        (the Sun, Earth) shows its "Enter the ... room" button on its
        own row, beside GO, all the time. No tap is needed to see it.
        A body with no room still opens to "No room or cards yet".
        The Sun's row keeps an empty space where GO would be, so its
        button lines up with Earth's.
      - The info panel's line about it now reads: "Tap a body's name to
        select it. A body with a room of its own has a button on its
        row to enter it."
    tools/headless/walk_solar_system_drawer.js (Claude-only check)
      - Checks the new behaviour instead of the old.
    Each page's header comment gains an "Updated" entry.

SAFETY
    Each file is checked against its content at 2aab10f (line endings
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
    "index.html": "72fdda89c9aeee53161b2c17a915f188",
    "interactive.html": "60903f49f3273858c060288e5583813e",
    "tools/headless/walk_solar_system_drawer.js": "f57d4775657f17ffa41109cced6f96bb",
}

# ================================================================ index.html

IX = []

IX.append(("index.html: header comment stamp", (
b"""       - "Doors" is renamed "Or explore by subject": a first-time
         visitor has no way to know what a door is. -->""",
b"""       - "Doors" is renamed "Or explore by subject": a first-time
         visitor has no way to know what a door is.
     Updated: October 10, 2026 with Anthropic's Claude Opus 5.5 (L-428)
       - Tony's look on the phone, 2026-10-09: the start card is as
         see-through as the other lobby cards, so the doves show; and
         the lobby's grey type is brighter ("grey is too dim"):
         headings blue, the grey lines near white, with the guest
         book's soft shadow. A door's own page keeps its colours. -->""")))

IX.append(("index.html: start card see-through", (
b"""        .lobby-start {
            margin: 0 -18px 26px;
            background: rgba(5, 7, 13, 0.92);""",
b"""        .lobby-start {
            margin: 0 -18px 26px;
            /* The other lobby cards' see-through blue, so the doves
               show (Tony, 2026-10-09). The picture itself stays solid. */
            background: rgba(9, 20, 38, 0.78);""")))

IX.append(("index.html: brighter lobby type", (
b"""        .lobby .welcome-version { margin: 18px 0 0; text-align: center; }
""",
b"""        .lobby .welcome-version { margin: 18px 0 0; text-align: center; }
        /* Brighter type over the dove wall (L-428, Tony's look of
           2026-10-09: "grey is too dim"). The lobby only; a door's page
           keeps its colours. Headings blue, so they stay apart from the
           white names; the grey lines near white; each with the guest
           book's soft dark shadow, for where it crosses a dove. */
        .lobby .lobby-heading { color: #9db0ff; }
        .lobby .welcome-text,
        .lobby .lobby-door-sentence,
        .lobby .lobby-door-meta,
        .lobby .lobby-card-room,
        .lobby .welcome-version,
        .lobby .gb-note,
        .lobby .gb-date,
        .lobby .lobby-door-chevron,
        .lobby .lobby-footer { color: #d6d4d0; }
        .lobby .lobby-heading,
        .lobby .welcome-text,
        .lobby .lobby-door-sentence,
        .lobby .lobby-door-meta,
        .lobby .welcome-version,
        .lobby .gb-note,
        .lobby .gb-date {
            text-shadow: 0 0 4px rgba(0, 0, 0, 0.9), 0 1px 2px rgba(0, 0, 0, 0.8);
        }
""")))

# ========================================================== interactive.html

IA = []

IA.append(("interactive.html: header comment stamp", (
b"""        ticked; the handle names the last body ticked. Home's code is
        unchanged)
     Architecture: Option C viewer""",
b"""        ticked; the handle names the last body ticked. Home's code is
        unchanged)
     Updated: October 10, 2026 with Anthropic's Claude Opus 5.5
       (L-429, Tony, 2026-10-10: "so the visitor does not need to tap
        the row to see the button then tap again to enter the room".
        In the Solar System room's list a body with a room of its own
        shows its "Enter the ... room" button on its own row, beside
        GO, on every screen, all the time. A body with no room still
        opens to "No room or cards yet": under the row when upright,
        on the name's line when sideways. The info panel says so)
     Architecture: Option C viewer""")))

IA.append(("interactive.html: inline button CSS comment", (
b"""        /* L-363, Tony's ruling of 2026-10-03 (option 3): with the phone
           sideways the drawer shows about a row and a half, so an opened
           row puts its button, or "No room or cards yet", on the name's
           line, between the name and GO, and stays one line tall. Shown
           and hidden by ssRender, by ssPhoneSideways(). */""",
b"""        /* L-363, Tony's ruling of 2026-10-03 (option 3): with the phone
           sideways the drawer shows about a row and a half, so an opened
           row puts its button, or "No room or cards yet", on the name's
           line, between the name and GO, and stays one line tall. Shown
           and hidden by ssRender, by ssPhoneSideways(). Since L-429
           (2026-10-10) a body WITH a room shows its button here always,
           on every screen, so one tap enters the room. */""")))

IA.append(("interactive.html: the Sun's GO keeps its space", (
b"""        /* The Sun is the scene's fixed centre: no box to tick, no GO. Its
           box keeps its space so the names stay in one column. */
        .sun-row.fixed .box { visibility: hidden; }
        .sun-row.fixed .go { display: none; }""",
b"""        /* The Sun is the scene's fixed centre: no box to tick, no GO. Its
           box keeps its space so the names stay in one column, and its GO
           keeps its space too, so its room button lines up with Earth's
           (L-429, 2026-10-10). Hidden things take no taps. */
        .sun-row.fixed .box { visibility: hidden; }
        .sun-row.fixed .go { visibility: hidden; pointer-events: none; }""")))

IA.append(("interactive.html: info panel line", (
b"""    "<li>Tap a body's name to open its row; a body with a room of its own",
    " has a button to enter it.</li>",""",
b"""    "<li>Tap a body's name to select it. A body with a room of its own",
    " has a button on its row to enter it.</li>",""")))

IA.append(("interactive.html: drawer notes", (
b"""//   - A row opens: "Enter the ... room" where the body has a room in
//     EXHIBITS, "No room or cards yet" where it has none.""",
b"""//   - "Enter the ... room" sits on the row of every body with a room in
//     EXHIBITS, always (L-429, 2026-10-10); a row with none opens to
//     "No room or cards yet".""")))

IA.append(("interactive.html: rows know whether they have a room", (
b"""    const room = SSD.roomFor(served, Object.keys(EXHIBITS));
    [panel, inline].forEach(function (holder) {""",
b"""    const room = SSD.roomFor(served, Object.keys(EXHIBITS));
    // L-429: ssRender reads this to keep a room's button on its row.
    panel.setAttribute("data-room", room ? "yes" : "no");
    inline.setAttribute("data-room", room ? "yes" : "no");
    [panel, inline].forEach(function (holder) {""")))

IA.append(("interactive.html: ssRender shows a room's button always", (
b"""    const sideways = ssPhoneSideways();
    const panels = list.querySelectorAll(".sun-row-open");
    for (let p = 0; p < panels.length; p++) {
        const key = panels[p].getAttribute("data-open-for");
        panels[p].hidden = sideways || !(seen[key] && ssDrawer.open === key);
    }
    const inlines = list.querySelectorAll(".sun-row .open-inline");
    for (let q = 0; q < inlines.length; q++) {
        const key = inlines[q].getAttribute("data-open-for");
        inlines[q].hidden = !sideways || !(seen[key] && ssDrawer.open === key);
    }""",
b"""    const sideways = ssPhoneSideways();
    // A body with a room shows its button on its row, always (L-429);
    // the line under the row is then never needed. A body with none
    // opens as before: under the row upright, on its line sideways.
    const panels = list.querySelectorAll(".sun-row-open");
    for (let p = 0; p < panels.length; p++) {
        const key = panels[p].getAttribute("data-open-for");
        const hasRoom = panels[p].getAttribute("data-room") === "yes";
        panels[p].hidden = hasRoom || sideways ||
            !(seen[key] && ssDrawer.open === key);
    }
    const inlines = list.querySelectorAll(".sun-row .open-inline");
    for (let q = 0; q < inlines.length; q++) {
        const key = inlines[q].getAttribute("data-open-for");
        const hasRoom = inlines[q].getAttribute("data-room") === "yes";
        inlines[q].hidden = hasRoom ? false :
            (!sideways || !(seen[key] && ssDrawer.open === key));
    }""")))

IA.append(("interactive.html: ssWireRow comment", (
b"""    // The opened row: hidden until this row is opened. Upright and on the
    // desktop it is a line under the row; with the phone sideways the
    // same words sit on the row's own line, before GO (Tony, 2026-10-03).""",
b"""    // The opened row: hidden until this row is opened. Upright and on the
    // desktop it is a line under the row; with the phone sideways the
    // same words sit on the row's own line, before GO (Tony, 2026-10-03).
    // A body with a room keeps its button on the row's line always, on
    // every screen (L-429, 2026-10-10).""")))

# ==================================================== the walk (Claude-only)

WK = []

WK.append(("walk: header note", (
b"""// ticked), All / none, GO, the info panel's lists, and an opened row with
// the phone sideways (2026-10-04).""",
b"""// ticked), All / none, GO, the info panel's lists, and an opened row with
// the phone sideways (2026-10-04). Since L-429 (2026-10-10) a body with a
// room shows its button on its row always; a body with none still opens.""")))

WK.append(("walk: arrival room buttons", (
b"""  ok(panel("center").textContent === "Enter the Sun room" && panel("earth").textContent === "Enter the Earth room", "enter words");
  ok(panel("center").querySelector("a").getAttribute("href") === "interactive.html?exhibit=sun", "Sun room link");
  ok(panel("earth").querySelector("a").getAttribute("href") === "interactive.html?exhibit=earth", "Earth room link");""",
b"""  const inl = (key) => row(key).querySelector(".open-inline") ||
    { hidden: true, textContent: "", nextElementSibling: null };
  const expanded = (key) => row(key).getAttribute("aria-expanded") === "true";
  // L-429: a room's button is on its row from the start, no tap needed.
  ok(!inl("center").hidden && !inl("earth").hidden, "a room's button is not on its row on arrival");
  ok(inl("center").textContent === "Enter the Sun room" && inl("earth").textContent === "Enter the Earth room", "enter words");
  ok(inl("earth").nextElementSibling === row("earth").querySelector(".go"), "Earth's button not before GO");
  ok(inl("center").querySelector("a").getAttribute("href") === "interactive.html?exhibit=sun", "Sun room link");
  ok(inl("earth").querySelector("a").getAttribute("href") === "interactive.html?exhibit=earth", "Earth room link");
  ok(inl("mars").hidden, "Mars shows a button on its row");""")))

WK.append(("walk: the Sun opens and closes", (
b"""  ok(focus() === "center" && !panel("center").hidden, "Sun's left end did not name and open its row");
  await name("center");
  ok(panel("center").hidden, "second tap on the Sun did not close its row");""",
b"""  ok(focus() === "center" && expanded("center") && panel("center").hidden && !inl("center").hidden, "Sun's left end did not name and open its row");
  await name("center");
  ok(!expanded("center") && !inl("center").hidden, "second tap on the Sun did not close its row");""")))

WK.append(("walk: name tap on Earth", (
b"""  ok(focus() === "earth" && !panel("earth").hidden && panel("neptune").hidden, "name tap did not name+open Earth");""",
b"""  ok(focus() === "earth" && expanded("earth") && panel("earth").hidden && panel("neptune").hidden, "name tap did not name+open Earth");""")))

WK.append(("walk: info words", (
b"""info.indexOf("Tap a body's name to open its row") >= 0""",
b"""info.indexOf("A body with a room of its own has a button on its row") >= 0""")))

WK.append(("walk: sideways section", (
b"""  const inl = (key) => row(key).querySelector(".open-inline") ||
    { hidden: true, textContent: "", nextElementSibling: null };
  ok(!panel("earth").hidden && inl("earth").hidden, "upright: the button not under the row");
  Object.defineProperty(w, "innerWidth", { value: 844, configurable: true });
  Object.defineProperty(w, "innerHeight", { value: 390, configurable: true });
  E("renderSunDrawer()");
  ok(panel("earth").hidden && !inl("earth").hidden, "sideways: the button not on the name's line");
  ok(inl("earth").nextElementSibling === row("earth").querySelector(".go"), "sideways: the button not before GO");
  ok(inl("earth").textContent === "Enter the Earth room", "sideways words " + inl("earth").textContent);
  ok(inl("mercury").hidden, "sideways: a closed row shows its button");
  await E("ssSelect(ssIndex('mercury'), true)"); await h.done();
  ok(inl("earth").hidden && !inl("mercury").hidden && inl("mercury").textContent === "No room or cards yet", "sideways: Mercury's opened row");""",
b"""  ok(panel("earth").hidden && !inl("earth").hidden, "upright: Earth's button not on its row");
  Object.defineProperty(w, "innerWidth", { value: 844, configurable: true });
  Object.defineProperty(w, "innerHeight", { value: 390, configurable: true });
  E("renderSunDrawer()");
  ok(panel("earth").hidden && !inl("earth").hidden, "sideways: the button not on the name's line");
  ok(inl("earth").nextElementSibling === row("earth").querySelector(".go"), "sideways: the button not before GO");
  ok(inl("earth").textContent === "Enter the Earth room", "sideways words " + inl("earth").textContent);
  ok(inl("mercury").hidden, "sideways: a closed row shows its button");
  await E("ssSelect(ssIndex('mercury'), true)"); await h.done();
  ok(!inl("earth").hidden && !inl("mercury").hidden && inl("mercury").textContent === "No room or cards yet", "sideways: Mercury's opened row");""")))

EDITS = {
    "index.html": IX,
    "interactive.html": IA,
    "tools/headless/walk_solar_system_drawer.js": WK,
}
DONE_MARK = {
    "index.html": b"Updated: October 10, 2026 with Anthropic's Claude Opus 5.5 (L-428)",
    "interactive.html": b"(L-429, Tony, 2026-10-10:",
    "tools/headless/walk_solar_system_drawer.js": b"Since L-429 (2026-10-10)",
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
        print("already applied: all three files carry this patch. Nothing written.")
        return

    out = {}
    for rel, md5 in FILES.items():
        text = loaded[rel][0]
        fp = hashlib.md5(text).hexdigest()
        if fp != md5:
            fail("%s is not the file this patch was built on (content md5 %s, "
                 "expected %s at gallery 2aab10f). Has it changed since that "
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
    print("stamps updated: index.html and interactive.html header comments "
          "(October 10, 2026)")
    print("patch applied (%s)" % ", ".join("%s %d bytes" % (r, len(t)) for r, t in out.items()))
    print("")
    print("Next: run gallery_maintenance_run.py, commit and push the gallery")
    print("in GitHub Desktop, then look on the phone (close the Home Screen")
    print("clip's tab first). Then move this script into documentation/.")


if __name__ == "__main__":
    main()
