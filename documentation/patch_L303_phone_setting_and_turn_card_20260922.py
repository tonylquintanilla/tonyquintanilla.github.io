#!/usr/bin/env python3
"""patch_L303_phone_setting_and_turn_card_20260922.py -- GALLERY repo.

Tony's ruling of 2026-09-22, card 5 of the card pass (Orbital
Transformation of Mercury). The editor's "Shape (phone only)" setting had
two choices, and the 16:9 one squeezed a 3D figure to fit an upright
phone, which looks like a broken card. It now has four, and the page
follows them:

  16:9 2D  sweeps sideways       -- as before
  16:9 3D  asks the visitor to turn the phone to landscape
  9:16     shows as today        -- as before
  none     not on the phone      -- the desktop keeps both tabs

  1. index.html. On a phone, a card whose shape is "none" is left out of
     every list. On a phone held upright, a 3D figure served from a
     landscape file shows a card with the exhibit's title and "Turn your
     phone to landscape to view this card." instead of the squeezed
     scene. Turning the phone draws the figure; turning it back brings
     the card back. A turn made in the lobby opens nothing. The desktop,
     both tabs, is unchanged.

  2. tools/gallery_editor.py. The four choices. Both 16:9 choices save
     shape "16:9"; the form offers the one that matches the card's
     landscape file, read from the file the way the page reads it, so an
     existing card needs no setting by hand. "none" saves shape "none".

  3. tools/json_converter.py. A re-export used to reset a card's shape
     from the file it wrote. It now keeps "none", which is Tony's
     setting, not the file's.

  4. tools/sweep_report.py. A "none" card is its own class, and the 3D
     class says what the phone now does.

The metadata is NOT edited. After the push, set the Mercury card to
"none" in the editor and save; that is step 6 below.

Built on tonyquintanilla.github.io 1a12cadedf49fcc959a67ceb52fcb7916741d5c8
at https://github.com/tonylquintanilla/tonyquintanilla.github.io .

RUN IT LIKE THIS, from the GALLERY repo root (the folder that holds
index.html), by opening this file in VS Code and clicking Run:

    python patch_L303_phone_setting_and_turn_card_20260922.py

It edits four files and is all-or-nothing. Nothing under data/ changes,
so no cache rebuild is needed.

What is permanent, once this script is filed away: the edits above.

Module created: September 22, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

PROBE = "index.html"

EDITS_PAGE = [
    ('index.html: header Updated stamp',
     b'         exhibit count all read it. It replaces L-287\'s "every card\n         shows in every mode". -->\n',
     b'         exhibit count all read it. It replaces L-287\'s "every card\n         shows in every mode".\n     Updated: September 22, 2026 with Anthropic\'s Claude Opus 5.5\n       - The phone setting (Tony\'s ruling from the card pass, card 5):\n         a card whose shape is "none" is not listed on a phone. A 3D\n         figure served from a landscape file, on a phone held upright,\n         shows a card asking the visitor to turn the phone instead of\n         a scene squeezed to fit; turning the phone draws the figure,\n         and turning it back brings the card back. The desktop, both\n         tabs, is unchanged. -->\n'),
    ('index.html: style for the turn-the-phone card',
     b'        .error-text {\n            color: var(--cat-inner);\n            font-size: 0.9rem;\n        }\n',
     b'        .error-text {\n            color: var(--cat-inner);\n            font-size: 0.9rem;\n        }\n\n        /* Turn-the-phone card (2026-09-22): a 3D figure from a landscape\n           file, on a phone held upright, shows this instead of the scene */\n        .turn-card {\n            display: flex;\n            flex-direction: column;\n            align-items: center;\n            justify-content: center;\n            height: 100%;\n            text-align: center;\n            padding: 40px 28px;\n            gap: 14px;\n        }\n\n        .turn-card-title {\n            color: var(--text-primary);\n            font-size: 1rem;\n        }\n\n        .turn-card-text {\n            color: var(--text-secondary);\n            font-size: 0.9rem;\n            line-height: 1.5;\n        }\n'),
    ('index.html: the phone leaves out a card set to none',
     b'                    if (window.innerWidth < 768) {\n                        var servedIds = {};\n                        metadata.visualizations.forEach(function (v) { servedIds[v.id] = v; });\n                        metadata.visualizations = metadata.visualizations.filter(function (v) {\n                            var files = v.files || {};\n',
     b"                    if (window.innerWidth < 768) {\n                        var servedIds = {};\n                        metadata.visualizations.forEach(function (v) { servedIds[v.id] = v; });\n                        metadata.visualizations = metadata.visualizations.filter(function (v) {\n                            // A card whose phone setting is none is not on\n                            // the phone at all (Tony's ruling, 2026-09-22).\n                            // Its twin, if it has one, keeps its own setting.\n                            if (v.shape === 'none') return false;\n                            var files = v.files || {};\n"),
    ('index.html: turnWanted() beside sweepWanted()',
     b'            if (layout && layout.scene) return false;      // 3D scales to fit\n            return true;\n        }\n',
     b'            if (layout && layout.scene) return false;      // 3D: see turnWanted\n            return true;\n        }\n\n        // ---- The turn-the-phone card (Tony\'s ruling, 2026-09-22) ----\n        // A 3D figure served from a landscape file, on a phone held\n        // upright, used to be squeezed to fit, and it looked broken. The\n        // phone now shows a card asking the visitor to turn it; when they\n        // do, the figure is drawn, and turning back brings the card back.\n        // Same tests as sweepWanted, with the 3D test the other way round:\n        // a 2D figure sweeps, a 3D figure asks. 9:16 and a portrait file\n        // are untouched. is3d is the figure\'s own layout.scene, read from\n        // the file, never from the card, so the card cannot disagree.\n        var turnIs3d = false;         // the current figure has a 3D scene\n\n        function turnWanted(viz, is3d) {\n            if (!viz || !is3d || viz.shape === \'9:16\') return false;\n            var phone = window.innerWidth < 768;\n            var portrait = window.innerHeight > window.innerWidth;\n            if (!phone || !portrait) return false;\n            var files = viz.files || {};\n            if (files.portrait) return false;\n            return true;\n        }\n\n        function showTurnCard(viz) {\n            loadingOverlay.classList.remove(\'visible\');\n            if (typeof Plotly !== \'undefined\') Plotly.purge(\'plotly-graph\');\n            plotlyGraph.style.display = \'none\';\n            zoomControls.classList.remove(\'visible\');\n            panControls.classList.remove(\'visible\');\n            resetStandalone.classList.remove(\'visible\');\n            flytoControls.classList.remove(\'visible\');\n            var kmz = document.getElementById(\'kmz-handoff-btn\');\n            if (kmz) { kmz.style.display = \'none\'; kmz.href = \'#\'; }\n            linkReset();\n            welcomeState.innerHTML =\n                \'<div class="turn-card" id="turnCard">\' +\n                \'<div class="turn-card-title">\' + escapeHtml(viz.title || \'Untitled\') + \'</div>\' +\n                \'<div class="turn-card-text">Turn your phone to landscape to view this card.</div>\' +\n                \'</div>\';\n            welcomeState.style.display = \'flex\';\n        }\n\n        // On rotation: redraw only when the answer changes, and only while\n        // a card is on screen (the turn card or a drawn figure), so a turn\n        // made in the lobby never opens a card. Debounced, because a phone\n        // fires several resize events per turn and more as its address bar\n        // slides.\n        var turnTimer = null;\n        function turnCheck() {\n            var viz = vizLookup[currentVizId];\n            if (!viz) return false;\n            // welcomeState keeps the turn card\'s markup after the figure is\n            // drawn, so "held" means the card is on screen, not merely there.\n            var held = welcomeState.style.display !== \'none\' &&\n                       !!document.getElementById(\'turnCard\');\n            var drawn = plotlyGraph.style.display !== \'none\';\n            if (!held && !drawn) return false;\n            var want = turnWanted(viz, turnIs3d);\n            if (held === want) return false;\n            if (turnTimer) clearTimeout(turnTimer);\n            turnTimer = setTimeout(function () {\n                turnTimer = null;\n                if (currentVizId === viz.id) loadVisualization(viz.id);\n            }, 250);\n            return true;\n        }\n'),
    ('index.html: the loader holds a 3D landscape figure on an upright phone',
     b'                var figDict = await resp.json();\n\n                figDict.layout = figDict.layout || {};\n',
     b'                var figDict = await resp.json();\n\n                figDict.layout = figDict.layout || {};\n\n                // The turn-the-phone card (2026-09-22): see turnWanted.\n                turnIs3d = !!figDict.layout.scene;\n                if (turnWanted(viz, turnIs3d)) {\n                    showTurnCard(viz);\n                    return;\n                }\n'),
    ('index.html: rotation redraws when the answer changes',
     b"            window.addEventListener('resize', function() {\n                if (plotlyGraph.style.display !== 'none') {\n",
     b"            window.addEventListener('resize', function() {\n                if (turnCheck()) return;      // the turn card or the figure, redrawn\n                if (plotlyGraph.style.display !== 'none') {\n"),
]

EDITS_EDITOR = [
    ('editor: docstring stamp',
     b'Module updated: September 6, 2026 (L-288): live_scene_urls() now lives in\njson_converter.py and is imported; Studio reads the same list.\n',
     b'Module updated: September 6, 2026 (L-288): live_scene_urls() now lives in\njson_converter.py and is imported; Studio reads the same list.\nModule updated: September 22, 2026 with Anthropic\'s Claude Opus 5.5 (card\npass, Tony\'s ruling): the phone setting. "Shape (phone only)" offers\n"16:9 2D -- sweeps sideways", "16:9 3D -- asks the visitor to turn the\nphone", "9:16 -- shows as today" and "none -- not on the phone". The two\n16:9 choices both save shape "16:9"; which one is offered is read from the\ncard\'s landscape file (a 3D scene or not), because the page decides from\nthe file too, so the editor cannot record a choice the page will not\nfollow. "none" saves shape "none" and the phone leaves the card out; the\ndesktop, both tabs, is unchanged.\n'),
    ('editor: the shape values',
     b"SHAPES = ('16:9', '9:16')\n",
     b"SHAPES = ('16:9', '9:16', 'none')    # 'none': not on the phone (2026-09-22)\n"),
    ("editor: a helper that reads whether a card's landscape figure is 3D",
     b'    @staticmethod\n    def _find_file(path):\n',
     b'    def _figure_is_3d(self, c):\n        """True if the card\'s landscape figure has a 3D scene, False if it\n        is 2D, None if there is no landscape file or it cannot be read.\n        The same test the page makes (layout.scene), on the same file."""\n        fn = (c.get(\'files\') or {}).get(\'landscape\')\n        if not fn:\n            return None\n        path = os.path.join(os.path.dirname(self.meta_path), fn)\n        try:\n            key = (path, os.path.getmtime(path))\n        except OSError:\n            return None\n        cache = getattr(self, \'_fig3d_cache\', None)\n        if cache is None:\n            cache = self._fig3d_cache = {}\n        if key not in cache:\n            try:\n                with open(path, \'rb\') as fh:\n                    fig = json.loads(fh.read().decode(\'utf-8\'))\n                cache[key] = bool((fig.get(\'layout\') or {}).get(\'scene\'))\n            except Exception:\n                cache[key] = None\n        return cache[key]\n\n    @staticmethod\n    def _find_file(path):\n'),
    ('editor: the phone setting in the card form',
     b'        sh = tk.StringVar(value=c.get(\'shape\', \'16:9\'))\n        self.form_vars[\'shape\'] = sh\n        ttk.Label(f, text="Shape (phone only)").grid(row=7, column=0, sticky=\'w\', padx=(0, 10), pady=4)\n        shf = ttk.Frame(f)\n        shf.grid(row=7, column=1, columnspan=2, sticky=\'w\')\n        ttk.Radiobutton(shf, text="16:9  sweeps sideways (2D) / scales to fit (3D)",\n                        variable=sh, value=\'16:9\', command=self._on_field_leave).pack(anchor=\'w\')\n        ttk.Radiobutton(shf, text="9:16  shows as today", variable=sh, value=\'9:16\',\n                        command=self._on_field_leave).pack(anchor=\'w\')\n',
     b'        # The phone setting (Tony\'s ruling, 2026-09-22). Four choices, one\n        # stored field. Both 16:9 choices store \'16:9\'; the form offers the\n        # one that matches the landscape file, because the page reads the\n        # file, not the card, to decide between sweeping and turning.\n        fig3d = self._figure_is_3d(c)\n        cur = c.get(\'shape\', \'16:9\')\n        if cur in (\'9:16\', \'none\'):\n            ui = cur\n        else:\n            ui = \'16:9/3d\' if fig3d else \'16:9/2d\'\n        sh = tk.StringVar(value=ui)\n        self.form_vars[\'shape\'] = sh\n        ttk.Label(f, text="Shape (phone only)").grid(row=7, column=0, sticky=\'nw\', padx=(0, 10), pady=4)\n        shf = ttk.Frame(f)\n        shf.grid(row=7, column=1, columnspan=2, sticky=\'w\')\n        r2d = ttk.Radiobutton(shf, text="16:9 2D  sweeps sideways",\n                              variable=sh, value=\'16:9/2d\', command=self._on_field_leave)\n        r2d.pack(anchor=\'w\')\n        r3d = ttk.Radiobutton(shf, text="16:9 3D  asks the visitor to turn the phone to landscape",\n                              variable=sh, value=\'16:9/3d\', command=self._on_field_leave)\n        r3d.pack(anchor=\'w\')\n        ttk.Radiobutton(shf, text="9:16  shows as today", variable=sh, value=\'9:16\',\n                        command=self._on_field_leave).pack(anchor=\'w\')\n        ttk.Radiobutton(shf, text="none  not on the phone (the desktop keeps both tabs)",\n                        variable=sh, value=\'none\', command=self._on_field_leave).pack(anchor=\'w\')\n        if fig3d is True:\n            r2d.state([\'disabled\'])\n            note = "the landscape file is a 3D figure, so 16:9 means 3D here"\n        elif fig3d is False:\n            r3d.state([\'disabled\'])\n            note = "the landscape file is a 2D figure, so 16:9 means 2D here"\n        else:\n            r2d.state([\'disabled\'])\n            r3d.state([\'disabled\'])\n            note = "no landscape file to read, so the 16:9 choices are off"\n        ttk.Label(shf, text=note, foreground=\'#777777\').pack(anchor=\'w\')\n'),
    ('editor: saving maps the two 16:9 choices to one value',
     b"                'shape': self.form_vars['shape'].get(),\n",
     b"                'shape': ('16:9' if self.form_vars['shape'].get().startswith('16:9')\n                          else self.form_vars['shape'].get()),\n"),
]

EDITS_CONVERTER = [
    ('converter: docstring stamp',
     b'live_scene_urls() moved here from the editor; add_live_card() writes an\nINTERACTIVE card (live scene, no file) into storage for Gallery Studio.\n',
     b'live_scene_urls() moved here from the editor; add_live_card() writes an\nINTERACTIVE card (live scene, no file) into storage for Gallery Studio.\nModule updated: September 22, 2026 with Anthropic\'s Claude Opus 5.5 (card\npass): a re-export keeps a card\'s shape "none" (not on the phone) instead\nof resetting it from the file\'s slot; that setting is Tony\'s, made in the\ngallery editor.\n'),
    ('converter: a re-export keeps shape none',
     b'            v["size_kb"] = {slot: round(size_kb, 1)}\n            v["shape"] = "9:16" if slot == "portrait" else "16:9"\n            v["converted"] = now\n',
     b'            v["size_kb"] = {slot: round(size_kb, 1)}\n            if v.get("shape") != "none":      # not on the phone: Tony\'s call, kept\n                v["shape"] = "9:16" if slot == "portrait" else "16:9"\n            v["converted"] = now\n'),
]

EDITS_SWEEP = [
    ('sweep report: the rule list',
     b'  - a card whose figure has a 3D scene         -> no sweep (scales to fit)\n',
     b'  - a card whose figure has a 3D scene         -> no sweep (on a phone held\n    upright it asks the visitor to turn the phone; 2026-09-22)\n'),
    ('sweep report: docstring stamp',
     b"Module created: September 6, 2026 with Anthropic's Claude Fable 5.1 (L-286)\n",
     b'Module created: September 6, 2026 with Anthropic\'s Claude Fable 5.1 (L-286)\nModule updated: September 22, 2026 with Anthropic\'s Claude Opus 5.5 (card\npass): a card with shape "none" is its own class, not on the phone; the 3D\nclass says the phone asks the visitor to turn it, as the page now does.\n'),
    ('sweep report: shape none is its own class',
     b'    if not files:\n        return "no file (interactive scene only)", title, room, ""\n    if shape == "9:16":\n',
     b'    if shape == "none":\n        return "not on the phone (shape none)", title, room, ""\n    if not files:\n        return "no file (interactive scene only)", title, room, ""\n    if shape == "9:16":\n'),
    ('sweep report: the 3D class names what the phone does',
     b'        return "no sweep: 3D scene (scales to fit)", title, room, land\n',
     b'        return "no sweep: 3D scene (asks to turn the phone)", title, room, land\n'),
    ('sweep report: the class order',
     b'        "no sweep: 3D scene (scales to fit)",\n',
     b'        "no sweep: 3D scene (asks to turn the phone)",\n        "not on the phone (shape none)",\n'),
]


FILES = [
    ("index.html", "0d5eae9a8f863ae40ef24d4533c47c72", EDITS_PAGE),
    ("tools/gallery_editor.py", "48c0a28f6725b73d78cff68f7aa2296f", EDITS_EDITOR),
    ("tools/json_converter.py", "c47cb3506b543cab41af898a43e18ff5", EDITS_CONVERTER),
    ("tools/sweep_report.py", "335fab5a98842f024c9393acfd7d26c5", EDITS_SWEEP),
]

# One line from each file's new text: if all four are already there, the
# patch has run.
APPLIED = [
    (path, edits[-1][2]) for path, _h, edits in FILES
]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written -- none of the four files.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile(PROBE) or here in ("documentation", "gallery",
                                              "tools"):
        return fail(
            "%s is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % (PROBE, os.getcwd()))

    done = 0
    for path, marker in APPLIED:
        if os.path.isfile(path):
            body = open(path, "rb").read().replace(b"\r\n", b"\n")
            if marker in body:
                done += 1
    if done == len(APPLIED):
        return fail("this patch has already been applied: all four files\n"
                    "         already hold its changes.")

    staged = []
    for path, expected, edits in FILES:
        if not os.path.isfile(path):
            return fail("%s is missing from this checkout." % path)
        raw = open(path, "rb").read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        actual = hashlib.md5(content).hexdigest()
        if actual != expected:
            return fail(
                "BASE MOVED. %s is not the file this patch was built\n"
                "         against (gallery 1a12cade).\n"
                "         expected %s\n"
                "         found    %s\n"
                "         (Line endings were normalised before comparing, so\n"
                "         CRLF does not explain this -- the content differs.\n"
                "         Tell Claude; do not edit the file by hand.)"
                % (path, expected, actual))
        if was_crlf:
            print("note: %s is CRLF here; compared normalised, written back"
                  % path)
            print("      CRLF exactly as found.")
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL: expected 1 match, found %d for: %s"
                            % (count, label))
            out = out.replace(old, new)
            print("  ok  %s" % label)
        staged.append((path, out, was_crlf))

    inserted = b"".join(new for _p, _h, edits in FILES for _l, _o, new in edits)
    bad = sum(1 for byt in inserted if byt > 127)
    if bad:
        return fail("this patch would insert %d non-ASCII byte(s); refusing"
                    % bad)
    dirty = [(p, sum(1 for byt in o if byt > 127)) for p, o, _c in staged]
    dirty = [(p, n) for p, n in dirty if n]
    for path, n in dirty:
        print("note: %s holds %d non-ASCII byte(s) this patch did not" % (path, n))
        print("      reach; they are unchanged.")
    if not dirty:
        print("  ok  encoding gate: inserted text is ASCII, and no file holds")
        print("      a non-ASCII byte.")

    for path, out, _c in staged:
        if path.endswith(".py"):
            try:
                compile(out.decode("ascii"), path, "exec")
            except SyntaxError as err:
                return fail("%s would not compile after the edit: %s"
                            % (path, err))
    print("  ok  the three Python files compile after the edit")

    for path, out, was_crlf in staged:
        final = out.replace(b"\n", b"\r\n") if was_crlf else out
        with open(path, "wb") as handle:
            handle.write(final)
        print("  wrote %s (%d bytes)%s"
              % (path, len(final), " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 4 file(s)")
    print("")
    print("Stamps updated: the 'Updated' line at the top of index.html and the")
    print("'Module updated' line in each of the three tools.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect every gating checker to pass, as before. None of them")
    print("     opens a card on a phone, so a pass does not speak for this")
    print("     change; your eyes in step 7 do.")
    print("  3. In GitHub Desktop the change list should show exactly five")
    print("     files: index.html, the three tools, and this script under")
    print("     documentation/. Commit and push.")
    print("  4. After the push, check what the live site serves:")
    print("         python gallery_maintenance_run.py --live")
    print("  5. Open the gallery editor (tools/gallery_editor.py, Run) and click")
    print("     the Mercury card. 'Shape (phone only)' should show four")
    print("     choices, with '16:9 3D' picked and '16:9 2D' greyed out.")
    print("  6. Pick 'none', Save All, then commit and push")
    print("     gallery/gallery_metadata.json.")
    print("  7. On the phone, held upright:")
    print("       - Orbital Mechanics should no longer list the Mercury card.")
    print("       - Open Trappist1 Exoplanet System. It should show its title")
    print("         and 'Turn your phone to landscape to view this card.'")
    print("         Turn the phone: the figure is drawn. Turn it back: the")
    print("         card returns.")
    print("       - A 2D card should sweep sideways as before, and a 9:16 card")
    print("         should look as before.")
    print("     On the desktop, both tabs should look as before, Mercury")
    print("     included.")
    print("  8. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 8 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
