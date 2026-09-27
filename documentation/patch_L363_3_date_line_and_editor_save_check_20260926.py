"""patch_L363_3_date_line_and_editor_save_check_20260926.py -- GALLERY repo.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. CLOSE the gallery
    editor and Gallery Studio first. Open this file in VS Code and
    click Run.

    This REPLACES the earlier copy of this script with the same name,
    which drew midnight UTC. If you already ran that one, do not run
    this; tell Claude instead.

WHAT IT CHANGES -- two files, all-or-nothing

    interactive.html -- the Solar System room
        The room draws NOW: the minute it is opened (Tony, 2026-09-26,
        since a visitor cannot choose a time yet). Right under its title
        it states that moment, in UTC only:
            Positions for 27 September 2026, 03:53 UTC
        Tony: that date is the reason for the exhibit at all.
        - The line is worked out from the moment the assembler actually
          drew, not from the page's clock, so it states what is shown.
        - The info panel's words say "where it is now" instead of
          "where it is today".
        - On an upright phone the arrow buttons sit in the top-right
          corner and covered the date, so in this room the title and
          its date move down to just below them. Turned sideways, they
          go back to the top.
        - If the date is ever missing, the info panel says so.
        The Sun and Earth rooms still draw today at 00:00 UTC, show no
        line, and are unchanged, checked before and after.

    tools/gallery_editor.py -- Save All checks the disk first
        On 2026-09-26 a card Gallery Studio had just written was lost:
        gallery_metadata.json was rewritten from an older copy three
        minutes later, and nothing said so. Now, before it saves, the
        editor checks that both files on disk are still what it
        loaded. If either changed -- Studio, another editor window,
        anything -- it saves NOTHING and says to Reload from disk
        first. The status bar and the console also name the file the
        editor opened, so it is plain which copy it is working on.

    Nothing under data/ changes, so there is no cache rebuild.

TESTED BEFORE DELIVERY on throwaway copies of the gallery at 3f7f50ab:
    - The room, headless, desktop and upright phone, with the browser
      set to Chicago, Madrid and UTC: no page errors; the line reads
      the current minute in UTC in all three; Earth's box moves with
      the minute. On the phone the title and line sit clear of the
      arrow buttons, and move to the top and back when it is turned
      sideways and upright again.
    - The Sun and Earth rooms, phone and desktop: traces, drawer, count,
      focus, range, panel text and title identical before and after.
    - The editor, headless: a card written to the file behind its back
      made Save All refuse, and the card survived. After Reload from
      disk, an edit saved and the card was kept. A second save in the
      same session, with nothing changed outside, saved normally.
    - The page's scripts pass a syntax check. The gallery maintenance
      run on the patched copy: 16 of 16. None of those checkers opens
      the Solar System room or the editor (L-367), so the tests above
      and your phone are their checks.

Built on gallery 3f7f50ab0dcc53bc989983913644be28621e9acd
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded from orrery 907436a80ebf1c6d4b0dbcc0fc7da2ceed721ed6.
Written September 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', '1f17abcba81a8963beb7526f58774388', '31fd74b318d55faa20316acf7bcd37dd', [("the page's Updated stamp", b'        behind today. The other planets and Pluto follow once they are\n        served. The info panel now shows a body\'s source even when it\n        has no link, and says "body" rather than "shell" in this room)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n', b'        behind today. The other planets and Pluto follow once they are\n        served. The info panel now shows a body\'s source even when it\n        has no link, and says "body" rather than "shell" in this room)\n     Updated: September 26, 2026 with Anthropic\'s Claude Opus 5.5\n       (L-363: the Solar System room draws the moment it is opened --\n        "now", Tony\'s ruling, since a visitor cannot yet choose a time --\n        and states that moment right under its title, in UTC (Tony: UTC\n        only, no local time). Tony: that date is the reason for the\n        exhibit at all. The line is read from the epoch the assembler\n        actually used. The Sun and Earth rooms still draw today at 00:00\n        UTC and show no line)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n       - interactive.html serves all interactive exhibits via ?exhibit= parameter\n'), ('the date line, worked out from the epoch the driver returns', b'json.dumps({\n    "figure": result.figure,\n    "bodies": _served,\n    "warnings": result.report["warnings"],\n})\n`;\n\n// The source line for a body, from its served Horizons query. Every\n// value is printed as served.\n', b'json.dumps({\n    "figure": result.figure,\n    "bodies": _served,\n    "epoch_jd": result.context.resolved_epoch_jd,\n    "warnings": result.report["warnings"],\n})\n`;\n\n// The line under the room\'s title: the moment the positions are for.\n// Tony, 2026-09-26: this date is the reason for the exhibit at all, and\n// the room draws NOW -- the minute it is opened (epochNow in its EXHIBITS\n// row) -- since a visitor cannot choose a time yet. The line is converted\n// from the epoch the assembler RESOLVED (a Julian date, returned by the\n// driver), so it states what was drawn, not what the page meant to ask\n// for. UTC only, Tony\'s ruling: no local time.\nconst SOLAR_SYSTEM_MONTHS = ["January", "February", "March", "April",\n    "May", "June", "July", "August", "September", "October", "November",\n    "December"];\nfunction solarSystemEpochStamp(jd) {\n    if (typeof jd !== "number" || !isFinite(jd)) { return null; }\n    // Julian date 2440587.5 is 1970-01-01 00:00 UTC, the Unix epoch.\n    // Rounded to the minute, which is what the page asked for.\n    const d = new Date(Math.round((jd - 2440587.5) * 1440) * 60000);\n    if (isNaN(d.getTime())) { return null; }\n    const pad = function (n) { return String(n).padStart(2, "0"); };\n    return "Positions for " + d.getUTCDate() + " " +\n        SOLAR_SYSTEM_MONTHS[d.getUTCMonth()] + " " + d.getUTCFullYear() +\n        ", " + pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + " UTC";\n}\n\n// The source line for a body, from its served Horizons query. Every\n// value is printed as served.\n'), ("the room's panel words: 'where it is now'", b'    "<div class=\\"info-focus\\" id=\\"sun-info-focus\\"></div>",\n    "<h3>The Solar System</h3>",\n    "<p>The Sun, Earth, Jupiter, Saturn and the asteroid Apophis, each",\n    " drawn as its symbol on its orbit, where it is today. Name a body",\n    " and the view moves to hold its orbit; its source appears above.</p>",\n    "<p>This room is being built up. The other planets and Pluto join",\n    " it as the gallery\'s data service begins to carry them, and each",\n', b'    "<div class=\\"info-focus\\" id=\\"sun-info-focus\\"></div>",\n    "<h3>The Solar System</h3>",\n    "<p>The Sun, Earth, Jupiter, Saturn and the asteroid Apophis, each",\n    " drawn as its symbol on its orbit, where it is now: at the minute",\n    " you opened this room, as the line under the title says. Name a body",\n    " and the view moves to hold its orbit; its source appears above.</p>",\n    "<p>This room is being built up. The other planets and Pluto join",\n    " it as the gallery\'s data service begins to carry them, and each",\n'), ("the panel's note: 'where it sits now'", b'    " inventor\'s daughter. Every orbit here comes from JPL Horizons, the",\n    " observatory\'s own service, fetched fresh each night: the page",\n    " carries a small set of orbit values for each body and works out",\n    " where it sits today.</div>"\n].join("");\n\n// ONE table, three rooms. What differs between the rooms is data:\n', b'    " inventor\'s daughter. Every orbit here comes from JPL Horizons, the",\n    " observatory\'s own service, fetched fresh each night: the page",\n    " carries a small set of orbit values for each body and works out",\n    " where it sits now.</div>"\n].join("");\n\n// ONE table, three rooms. What differs between the rooms is data:\n'), ('the room asks for the current minute', b'        driver: SOLAR_SYSTEM_DRIVER,\n        infoHtml: SOLAR_SYSTEM_INFO_HTML,\n        focusNoun: "body",\n        pyGlobals: { BODIES_JSON: JSON.stringify(SOLAR_SYSTEM_BODIES) },\n        // The assembler\'s figure only: no features are built, so no\n        // shells. Each body\'s position marker names its drawer row\n', b'        driver: SOLAR_SYSTEM_DRIVER,\n        infoHtml: SOLAR_SYSTEM_INFO_HTML,\n        focusNoun: "body",\n        // Draw the minute the room is opened (Tony, 2026-09-26). The Sun\n        // and Earth rooms leave this out and draw today at 00:00 UTC.\n        epochNow: true,\n        pyGlobals: { BODIES_JSON: JSON.stringify(SOLAR_SYSTEM_BODIES) },\n        // The assembler\'s figure only: no features are built, so no\n        // shells. Each body\'s position marker names its drawer row\n'), ("the room's compose returns the date line", b'                    t.meta = Object.assign({}, t.meta || {}, { label_target: true });\n                }\n            }\n            return { traces: traces, warnings: warnings, absent: [] };\n        }\n    }\n};\n', b'                    t.meta = Object.assign({}, t.meta || {}, { label_target: true });\n                }\n            }\n            // The date under the title. Missing is reported, not hidden.\n            const stamp = solarSystemEpochStamp(payload.epoch_jd);\n            if (!stamp) {\n                warnings.push("the scene\'s date was not reported by the assembler");\n            }\n            return { traces: traces, warnings: warnings, absent: [],\n                     subtitle: stamp };\n        }\n    }\n};\n'), ('where the title sits: clear of the arrow cross on an upright phone', b'    navPlaceCross();\n}\n\nfunction buildSunLayout(halfRangeAu) {\n    const r = halfRangeAu || EX.halfRangeAu;\n    const axisTemplate = {\n', b'    navPlaceCross();\n}\n\n// The line under the scene title, set from the room\'s compose, or null.\nlet sunSceneSubtitle = null;\n\n// Where the scene title sits. As it always has, except in a room with a\n// line under its title on an upright phone: there the arrow cross sits in\n// the top-right corner (L-316) and would cover the date, so the title and\n// its date move down to just below the cross. The Sun and Earth rooms have\n// no such line, so theirs does not move.\nfunction sunTitlePlacement() {\n    const base = { y: 0.97, yref: "container", yanchor: "auto" };\n    if (!sunSceneSubtitle || !sunPhonePortrait()) { return base; }\n    const plot = document.getElementById("plotly-container");\n    const cross = document.querySelector(".nav-cross-apart");\n    if (!plot || !cross) { return base; }\n    const pr = plot.getBoundingClientRect();\n    const cr = cross.getBoundingClientRect();\n    if (!pr.height || !cr.height || cr.bottom <= pr.top) { return base; }\n    const below = cr.bottom - pr.top + 10;\n    return { y: Math.max(0.05, 1 - below / pr.height), yref: "container",\n             yanchor: "top" };\n}\n\nfunction buildSunLayout(halfRangeAu) {\n    const r = halfRangeAu || EX.halfRangeAu;\n    const axisTemplate = {\n'), ('the title carries the date line', b'        paper_bgcolor: "#060a12",\n        plot_bgcolor: "#060a12",\n        font: { family: "DM Sans, system-ui", color: "#e8e6e3" },\n        title: {\n            text: EX.sceneTitle,\n            font: { family: "Cormorant Garamond, serif", size: 16,\n                    color: "#e8e6e3" },\n            x: 0.5, xanchor: "center", y: 0.97,\n        },\n        // NO LEGEND. L-267 Stage A: the eighteen entries moved into\n        // the drawer, because as an overlay they covered 58 percent of\n        // a portrait phone with the Sun behind them. The legend block\n', b'        paper_bgcolor: "#060a12",\n        plot_bgcolor: "#060a12",\n        font: { family: "DM Sans, system-ui", color: "#e8e6e3" },\n        title: Object.assign({\n            text: EX.sceneTitle,\n            font: { family: "Cormorant Garamond, serif", size: 16,\n                    color: "#e8e6e3" },\n            x: 0.5, xanchor: "center",\n        }, sunTitlePlacement(), sunSceneSubtitle ? { subtitle: {\n            text: sunSceneSubtitle,\n            font: { family: "DM Sans, system-ui", size: 12, color: "#b8b4ae" },\n        } } : {}),\n        // NO LEGEND. L-267 Stage A: the eighteen entries moved into\n        // the drawer, because as an overlay they covered 58 percent of\n        // a portrait phone with the Sun behind them. The legend block\n'), ('the boot path asks for the current minute when a room says so', b'            JSON.parse(cov).frame_constants);\n        pyodide.globals.set("COV_JSON", cov);\n        pyodide.globals.set("CFG_JSON", cfg);\n        pyodide.globals.set(\n            "EPOCH_ISO",\n            new Date().toISOString().slice(0, 10) + "T00:00:00Z");\n        // A room\'s own inputs to its driver, if it has any.\n        const pyGlobals = EX.pyGlobals || {};\n        for (const name of Object.keys(pyGlobals)) {\n', b'            JSON.parse(cov).frame_constants);\n        pyodide.globals.set("COV_JSON", cov);\n        pyodide.globals.set("CFG_JSON", cfg);\n        // Today at 00:00 UTC, or, for a room that asks, the current\n        // minute (the Solar System room, epochNow).\n        pyodide.globals.set(\n            "EPOCH_ISO",\n            EX.epochNow\n                ? new Date().toISOString().slice(0, 16) + ":00Z"\n                : new Date().toISOString().slice(0, 10) + "T00:00:00Z");\n        // A room\'s own inputs to its driver, if it has any.\n        const pyGlobals = EX.pyGlobals || {};\n        for (const name of Object.keys(pyGlobals)) {\n'), ("the boot path keeps the room's date line", b'\n        // Per room: how the payload becomes traces (the EXHIBITS table).\n        const built = EX.compose(payload);\n        sunAbsent = built.absent || [];\n\n        const notes = frameNotes.concat(payload.warnings || [],\n', b"\n        // Per room: how the payload becomes traces (the EXHIBITS table).\n        const built = EX.compose(payload);\n        // A room may put a line under its title (the Solar System room's\n        // date). The Sun and Earth rooms return none, so theirs is as it was.\n        sunSceneSubtitle = built.subtitle || null;\n        sunAbsent = built.absent || [];\n\n        const notes = frameNotes.concat(payload.warnings || [],\n"), ('the title stays clear of the cross when the phone turns', b'            });\n        }\n        navPlaceCross();\n        sunTapPicking(sunPlotDiv);\n    }, 180);\n}\n', b'            });\n        }\n        navPlaceCross();\n        // A room with a date under its title keeps it clear of the cross\n        // when the phone turns (the Sun and Earth rooms have none).\n        if (sunSceneSubtitle && sunPlotDiv && window.Plotly) {\n            const tp = sunTitlePlacement();\n            Plotly.relayout(sunPlotDiv, { "title.y": tp.y, "title.yref": tp.yref,\n                                          "title.yanchor": tp.yanchor });\n        }\n        sunTapPicking(sunPlotDiv);\n    }, 180);\n}\n')]), ('tools/gallery_editor.py', '5ccd8770f51e8bc476de3cfc1d3a97d5', '6a6da188bb3c8362aeba5df31536399a', [("the module's update stamp", b'the note says which card the phone shows, or that it shows neither when\nthe twin is set to none. The same test the page makes, so a twin kept in\nStorage does not count.\n\nRole: devtool\nDomain: gallery_pipeline\n"""\n\nimport tkinter as tk\nfrom tkinter import ttk, messagebox, simpledialog, colorchooser, filedialog\nimport json\nimport os\nimport re\nimport copy\nimport webbrowser\nimport urllib.request\nfrom datetime import datetime\n', b'the note says which card the phone shows, or that it shows neither when\nthe twin is set to none. The same test the page makes, so a twin kept in\nStorage does not count.\nModule updated: September 26, 2026 with Anthropic\'s Claude Opus 5.5\n(L-363): Save All refuses to write over a file that changed on disk since\nthe editor loaded it. On 2026-09-26 a card Gallery Studio had just written\nwas lost when gallery_metadata.json was rewritten from an older copy, and\nnothing said so. Now any window holding an older copy stops and says to\nReload from disk first. The status bar and the console name the file the\neditor opened, so it is plain which copy it is working on.\n\nRole: devtool\nDomain: gallery_pipeline\n"""\n\nimport tkinter as tk\nfrom tkinter import ttk, messagebox, simpledialog, colorchooser, filedialog\nimport json\nimport os\nimport re\nimport copy\nimport hashlib\nimport webbrowser\nimport urllib.request\nfrom datetime import datetime\n'), ('hashlib is imported; disk_fingerprint() reads what a file is now', b'# ============================================================\n# File I/O (line-ending preserving, ASCII output)\n# ============================================================\n\ndef read_json(path):\n    """Return (data, was_crlf). Raises on missing or invalid file."""\n', b'# ============================================================\n# File I/O (line-ending preserving, ASCII output)\n# ============================================================\n\ndef disk_fingerprint(path):\n    """MD5 of the file\'s bytes as they are on disk now, or None if absent."""\n    try:\n        with open(path, \'rb\') as f:\n            return hashlib.md5(f.read()).hexdigest()\n    except OSError:\n        return None\n\n\ndef read_json(path):\n    """Return (data, was_crlf). Raises on missing or invalid file."""\n'), ('the load records what both files were, and names the file', b'        self.config.setdefault(\'doors\', [])\n        self.config.setdefault(\'storage\', {\'key\': STORAGE_KEY, \'label\': \'Storage\', \'hidden\': True})\n        self.snapshot = (copy.deepcopy(self.config), copy.deepcopy(self.data))\n        self.dirty = False\n        self._update_title()\n        self._refresh_tree()\n        n = len(self.data.get(\'visualizations\', []))\n        stored = sum(1 for c in self.data[\'visualizations\'] if c.get(\'room\', STORAGE_KEY) == STORAGE_KEY)\n        self.status_var.set(f"Loaded {n} cards ({stored} in Storage), "\n                            f"{sum(1 for _ in walk_rooms(self.config[\'doors\']))} rooms")\n\n    def _reload(self):\n        if self.dirty and not messagebox.askyesno(\n', b'        self.config.setdefault(\'doors\', [])\n        self.config.setdefault(\'storage\', {\'key\': STORAGE_KEY, \'label\': \'Storage\', \'hidden\': True})\n        self.snapshot = (copy.deepcopy(self.config), copy.deepcopy(self.data))\n        # What the two files were when loaded. Save All compares these with\n        # the disk before writing, so an older copy cannot overwrite newer\n        # work (L-363).\n        self.loaded_sigs = {self.cfg_path: disk_fingerprint(self.cfg_path),\n                            self.meta_path: disk_fingerprint(self.meta_path)}\n        print(f"Gallery editor loaded {self.meta_path}")\n        self.dirty = False\n        self._update_title()\n        self._refresh_tree()\n        n = len(self.data.get(\'visualizations\', []))\n        stored = sum(1 for c in self.data[\'visualizations\'] if c.get(\'room\', STORAGE_KEY) == STORAGE_KEY)\n        self.status_var.set(f"Loaded {n} cards ({stored} in Storage), "\n                            f"{sum(1 for _ in walk_rooms(self.config[\'doors\']))} rooms, "\n                            f"from {self.meta_path}")\n\n    def _reload(self):\n        if self.dirty and not messagebox.askyesno(\n'), ('Save All refuses a file that changed on disk since it was loaded', b'        if not self.dirty:\n            self.status_var.set("No changes to save")\n            return\n        try:\n            report = self._save_report()\n            self.data[\'last_updated\'] = datetime.now().strftime(\'%Y-%m-%d %H:%M\')\n', b'        if not self.dirty:\n            self.status_var.set("No changes to save")\n            return\n        # L-363: refuse to write over a file that changed since it was\n        # loaded -- another program (Gallery Studio) or another editor\n        # window wrote it, and saving now would silently undo that work.\n        moved = [os.path.basename(p) for p, sig in self.loaded_sigs.items()\n                 if disk_fingerprint(p) != sig]\n        if moved:\n            messagebox.showerror(\n                "Not saved -- the file changed on disk",\n                f"{\' and \'.join(moved)} changed on disk after this editor "\n                "loaded it: another program or window wrote it.\\n\\n"\n                "Nothing was saved. Saving now would undo that change.\\n\\n"\n                "Note the edits you made here, use File > Reload from disk, "\n                "and make them again.")\n            print(f"NOT SAVED: {\', \'.join(moved)} changed on disk since the "\n                  "editor loaded it. Reload from disk first.")\n            self.status_var.set("Not saved: the file changed on disk. Reload from disk first.")\n            return\n        try:\n            report = self._save_report()\n            self.data[\'last_updated\'] = datetime.now().strftime(\'%Y-%m-%d %H:%M\')\n'), ('after a save, the record moves to what was written', b'        print(f"  {len(report)} change{\'s\' if len(report) != 1 else \'\'}. "\n              "Git is the backup; undo is Discard Changes in GitHub Desktop.")\n        self.snapshot = (copy.deepcopy(self.config), copy.deepcopy(self.data))\n        self.dirty = False\n        self._update_title()\n        keep = None\n', b'        print(f"  {len(report)} change{\'s\' if len(report) != 1 else \'\'}. "\n              "Git is the backup; undo is Discard Changes in GitHub Desktop.")\n        self.snapshot = (copy.deepcopy(self.config), copy.deepcopy(self.data))\n        self.loaded_sigs = {self.cfg_path: disk_fingerprint(self.cfg_path),\n                            self.meta_path: disk_fingerprint(self.meta_path)}\n        self.dirty = False\n        self._update_title()\n        keep = None\n')])]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile("index.html") or here in ("documentation", "gallery", "tools"):
        return fail(
            "index.html is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % os.getcwd())

    results = []
    for name, expected, result, edits in FILES:
        if not os.path.isfile(name):
            return fail("%s is not here." % name)
        raw = open(name, "rb").read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        actual = hashlib.md5(content).hexdigest()
        if actual == result:
            return fail("this patch has already been applied to %s." % name)
        if actual != expected:
            return fail(
                "BASE MOVED. %s is not the file this patch was built\n"
                "         against (gallery 3f7f50ab).\n"
                "         expected %s\n"
                "         found    %s\n"
                "         Tell Claude; do not edit the file by hand."
                % (name, expected, actual))
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL in %s: expected 1 match, found %d for: %s"
                            % (name, count, label))
            out = out.replace(old, new)
            print("  ok  %s: %s" % (name, label))
        if any(byt > 127 for byt in out):
            return fail("non-ASCII text would be written to %s; refusing" % name)
        if hashlib.md5(out).hexdigest() != result:
            return fail("%s would not be the file this patch was built and\n"
                        "         tested to produce." % name)
        print("  ok  %s is the file that was tested, and ASCII" % name)
        results.append((name, out.replace(b"\n", b"\r\n") if was_crlf else out, was_crlf))

    for name, data, was_crlf in results:
        with open(name, "wb") as handle:
            handle.write(data)
        print("  wrote %s (%d bytes)%s" % (name, len(data),
                                            " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 2 files")
    print("")
    print("Stamps updated: the 'Updated' line at the top of interactive.html,")
    print("and the 'Module updated' line in tools/gallery_editor.py.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into the GALLERY's documentation/ folder.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 16 of 16, as before.")
    print("  3. In GitHub Desktop the change list should show interactive.html,")
    print("     tools/gallery_editor.py and this script, plus what the run")
    print("     rewrites as usual. Commit and push.")
    print("  4. After the push: python gallery_maintenance_run.py --live")
    print("  5. After about ten minutes, open the Solar System room on your")
    print("     phone, upright and then sideways, and on the desktop. The date")
    print("     line should sit right under the title, clear of every button,")
    print("     and give the current minute in UTC.")
    print("  6. Open the gallery editor: its status bar should end with the")
    print("     path of the gallery_metadata.json it opened.")
    print("  7. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 7 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
