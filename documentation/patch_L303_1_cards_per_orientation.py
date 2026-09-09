"""
patch_L303_1_cards_per_orientation.py -- one card per orientation (gallery repo)

Built on gallery 700b426d4cecc1f80fd6f9ca5758e5058ea497a6
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-303 (RULED 2026-09-08), in the orrery repo at d39cf27c.

WHAT THIS DOES (four files, one run)

1. tools/json_converter.py -- the converter's pairing rule (L-301) is
   KEPT and INVERTED. Same detection (a file already on a card replaces
   that card's file in place; otherwise a card of the other orientation
   with a shared stem, else exactly one title match), different action:
   instead of filling the empty slot on the existing card, a NEW card
   is created for the new file, inserted right after the one it
   matched, and both cards are stamped "sibling": <the other id>. The
   new card inherits the matched card's room, description and sources,
   so a re-exported portrait lands beside its landscape, not in Storage.

2. index.html -- ONE viewer rule, Tony's wording: on a phone (width
   under 768 px, the same test the sweep uses), hide a landscape card
   that has a portrait sibling -- and only when that sibling is itself
   served (in a room). A landscape card with no sibling still shows and
   still sweeps. Desktop and tablet show everything. Three small
   consequences, each one line: a deep link (#id) to a hidden card on a
   phone opens its portrait sibling instead; a card that has a sibling
   shows its shape (16:9 or 9:16) after its size, so two cards with the
   same title read apart on the desktop; the lobby's Featured strip
   shows one of a featured pair, not both.

3. tools/sweep_report.py -- the report gains the class "no sweep:
   hidden on the phone (portrait sibling)" and stops predicting a class
   that no longer occurs.

4. gallery/gallery_metadata.json -- the split migration. Every card
   with two file slots becomes two cards: the LANDSCAPE card keeps the
   id, title, room, live, featured, sources and converted date; the new
   PORTRAIT card takes its id from its filename, the same title,
   description, room, featured and sources, shape 9:16, and is inserted
   right after. Both get the sibling stamp. Prints every card it makes,
   by id. Known loss, ruled: two of L-301's three merges lost their
   portrait titles to the landscape title; those two portrait cards are
   named at the end and get retyped in the editor.
   One card at 700b426d lists the SAME file in both slots
   (keeling_curve_co2_concentration); that is not a pair and becomes
   a one-file landscape card, no sibling. Named in the output.

WHAT IS PERMANENT
   The converter rule, the viewer rule, the report class, and the
   "sibling" key on cards. The script itself is one-shot.

HOW TO RUN
   Save to the GALLERY repo root. Open in VS Code and press Run.
   Then run gallery_maintenance_run.py (offline), commit, push, report
   the SHA. Mode 5 on the phone: the Earth and Moon card, the Keeling
   Curve card and any card that had two files. Expect: on the phone,
   one card per figure, the portrait file; on the desktop, two cards
   per figure side by side, tagged 16:9 and 9:16.

GUARDS
   All four files read in binary mode, LF-normalised, md5 checked
   against 700b426d. Every code edit must match exactly the number of
   times stated. The migration refuses if no card has two slots (it
   already ran). Nothing is written unless everything passes. Inserted
   text is ASCII-only, LF. No backups are written; undo is Discard
   Changes in GitHub Desktop.

Written September 2026 with Anthropic's Claude Opus 5.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "tools/json_converter.py": "34e8c64de52e02cda6776a0dc46fc6e1",
    "index.html": "16cd5d9d01d15dd901860253fcf12db4",
    "tools/sweep_report.py": "9b82880a5bf7e4e4b8bd20f29047ab8b",
    "gallery/gallery_metadata.json": "95ed6933323ff135655c6e61b9aa6989",
}

# (old, new, expected match count)
EDITS = {
    "tools/json_converter.py": [
        (
            'def _v2_entry(metadata, safe_name, title, description, size_kb, mode):\n'
            '    """Build or update a schema-v2 card (L-287).\n'
            '\n'
            '    New card: room "other" (storage), one files slot keyed by mode\n'
            '    ("both" -> landscape), shape from the mode. If some card already lists\n'
            '    this filename, that slot is updated in place and the card keeps its\n'
            '    room, live, featured and sources. Returns (entry, replaced_index).\n'
            '    """\n'
            '    filename = f"{safe_name}.json"\n'
            '    slot = "portrait" if mode == "portrait" else "landscape"\n'
            '    viz_list = metadata.get("visualizations", [])\n'
            '\n'
            '    # L-287 follow-on (2026-09-08). Studio exports a landscape and a\n'
            '    # portrait file of the same figure as SEPARATE scenes (each preset\n'
            '    # handles its own), named <base>_gallery and <base>_mobile. They are\n'
            '    # one card with two files. The L-287 migration paired existing cards;\n'
            '    # this is the same pairing for cards that arrive one file at a time,\n'
            '    # in the order: same filename/id, then same STEM, then same TITLE.\n'
            '    def _stem(name):\n'
            '        return re.sub(r"_(gallery|mobile|portrait|landscape)$", "", name)\n'
            '\n'
            '    def _joins(v):\n'
            '        files = v.get("files") or {}\n'
            '        if filename in files.values() or v.get("id") == safe_name:\n'
            '            return True\n'
            '        if slot in files:\n'
            '            return False          # that orientation is already taken\n'
            '        stems = {_stem(os.path.splitext(f)[0]) for f in files.values()}\n'
            '        stems.add(_stem(str(v.get("id", ""))))\n'
            '        return _stem(safe_name) in stems\n'
            '\n'
            '    match = [i for i, v in enumerate(viz_list) if _joins(v)]\n'
            '    if not match and title:\n'
            '        by_title = [i for i, v in enumerate(viz_list)\n'
            '                    if v.get("title") == title and slot not in (v.get("files") or {})]\n'
            '        if len(by_title) == 1:\n'
            '            match = by_title\n'
            '    for i in match[:1]:\n'
            '        v = viz_list[i]\n'
            '        files = v.get("files") or {}\n'
            '        if True:\n'
            '            files[slot] = filename\n'
            '            sizes = v.get("size_kb") if isinstance(v.get("size_kb"), dict) else {}\n'
            '            sizes[slot] = round(size_kb, 1)\n'
            '            v["files"] = files\n'
            '            v["size_kb"] = sizes\n'
            '            v["converted"] = datetime.now().strftime("%Y-%m-%d %H:%M")\n'
            '            if description:\n'
            '                v["description"] = description\n'
            '            return v, i\n'
            '    entry = {\n'
            '        "id": safe_name,\n'
            '        "title": title,\n'
            '        "description": description,\n'
            '        "room": "other",\n'
            '        "shape": "9:16" if slot == "portrait" else "16:9",\n'
            '        "files": {slot: filename},\n'
            '        "live": None,\n'
            '        "featured": False,\n'
            '        "sources": [],\n'
            '        "converted": datetime.now().strftime("%Y-%m-%d %H:%M"),\n'
            '        "size_kb": {slot: round(size_kb, 1)},\n'
            '    }\n'
            '    return entry, None\n',
            'def _v2_entry(metadata, safe_name, title, description, size_kb, mode):\n'
            '    """Build or update a schema-v2 card (L-287; card model ruled L-303).\n'
            '\n'
            '    ONE CARD, ONE FILE. A landscape export and a portrait export of the\n'
            '    same figure are separate cards, stamped as siblings -- never two\n'
            '    slots on one card (Tony\'s ruling, L-303, 2026-09-08; the two-slot\n'
            '    card was L-287\'s merge, not his workflow).\n'
            '\n'
            '    - A file already on some card (by filename or id) REPLACES that\n'
            '      card\'s file in place; the card keeps its room, live, featured and\n'
            '      sources. That is a re-export.\n'
            '    - Otherwise L-301\'s pairing detection finds a SIBLING: a card of\n'
            '      the other orientation, not yet stamped, with a shared STEM\n'
            '      (trailing _gallery|_mobile|_portrait|_landscape removed), else\n'
            '      exactly one title match. Same rule as L-301, inverted action: a\n'
            '      NEW card is built for the new file, inheriting the sibling\'s\n'
            '      room, description and sources, and both carry\n'
            '      "sibling": <the other card\'s id>. The caller inserts the new card\n'
            '      right after its sibling. The viewer (index.html) hides a\n'
            '      landscape card on a phone when its portrait sibling is served.\n'
            '    - Otherwise a new card in Storage, one slot, shape from the mode.\n'
            '\n'
            '    Returns (entry, replaced_index, insert_after_index). Exactly one of\n'
            '    the two indices is not None for a new card; both are None for a\n'
            '    plain new card.\n'
            '    """\n'
            '    filename = f"{safe_name}.json"\n'
            '    slot = "portrait" if mode == "portrait" else "landscape"\n'
            '    other = "landscape" if slot == "portrait" else "portrait"\n'
            '    viz_list = metadata.get("visualizations", [])\n'
            '    now = datetime.now().strftime("%Y-%m-%d %H:%M")\n'
            '\n'
            '    def _stem(name):\n'
            '        return re.sub(r"_(gallery|mobile|portrait|landscape)$", "", name)\n'
            '\n'
            '    # 1. Re-export: the file (or id) is already a card.\n'
            '    for i, v in enumerate(viz_list):\n'
            '        files = v.get("files") or {}\n'
            '        if filename in files.values() or v.get("id") == safe_name:\n'
            '            v["files"] = {slot: filename}\n'
            '            v["size_kb"] = {slot: round(size_kb, 1)}\n'
            '            v["shape"] = "9:16" if slot == "portrait" else "16:9"\n'
            '            v["converted"] = now\n'
            '            if description:\n'
            '                v["description"] = description\n'
            '            return v, i, None\n'
            '\n'
            '    # 2. Sibling: a card of the other orientation, not yet paired.\n'
            '    def _is_sibling(v):\n'
            '        files = v.get("files") or {}\n'
            '        if other not in files or v.get("sibling"):\n'
            '            return False\n'
            '        stems = {_stem(os.path.splitext(f)[0]) for f in files.values()}\n'
            '        stems.add(_stem(str(v.get("id", ""))))\n'
            '        return _stem(safe_name) in stems\n'
            '\n'
            '    match = [i for i, v in enumerate(viz_list) if _is_sibling(v)]\n'
            '    if not match and title:\n'
            '        by_title = [i for i, v in enumerate(viz_list)\n'
            '                    if v.get("title") == title and other in (v.get("files") or {})\n'
            '                    and not v.get("sibling")]\n'
            '        if len(by_title) == 1:\n'
            '            match = by_title\n'
            '\n'
            '    entry = {\n'
            '        "id": safe_name,\n'
            '        "title": title,\n'
            '        "description": description,\n'
            '        "room": "other",\n'
            '        "shape": "9:16" if slot == "portrait" else "16:9",\n'
            '        "files": {slot: filename},\n'
            '        "live": None,\n'
            '        "featured": False,\n'
            '        "sources": [],\n'
            '        "converted": now,\n'
            '        "size_kb": {slot: round(size_kb, 1)},\n'
            '    }\n'
            '    if match:\n'
            '        i = match[0]\n'
            '        sib = viz_list[i]\n'
            '        entry["room"] = sib.get("room", "other")\n'
            '        entry["sources"] = list(sib.get("sources") or [])\n'
            '        entry["featured"] = bool(sib.get("featured"))\n'
            '        if not description and sib.get("description"):\n'
            '            entry["description"] = sib["description"]\n'
            '        entry["sibling"] = sib.get("id")\n'
            '        sib["sibling"] = safe_name\n'
            '        return entry, None, i\n'
            '    return entry, None, None\n',
            1,
        ),
        (
            '        entry, idx = _v2_entry(metadata, safe_name, title, description, size_kb, mode)\n'
            '        viz_list = metadata.get("visualizations", [])\n'
            '        if idx is None:\n'
            '            viz_list.append(entry)\n'
            '            print(f"  metadata: new card {safe_name} in Storage; place it in the editor")\n'
            '        else:\n'
            '            print(f"  metadata: updated {entry[\'id\']} ({\', \'.join(entry[\'files\'])})")\n',
            '        entry, idx, after = _v2_entry(metadata, safe_name, title, description, size_kb, mode)\n'
            '        viz_list = metadata.get("visualizations", [])\n'
            '        if idx is not None:\n'
            '            print(f"  metadata: replaced the file on {entry[\'id\']} ({\', \'.join(entry[\'files\'])})")\n'
            '        elif after is not None:\n'
            '            viz_list.insert(after + 1, entry)\n'
            '            sib = viz_list[after]\n'
            '            print(f"  metadata: new card {safe_name} ({entry[\'shape\']}) beside its sibling "\n'
            '                  f"{sib.get(\'id\')} in room {entry[\'room\']} (L-303)")\n'
            '        else:\n'
            '            viz_list.append(entry)\n'
            '            print(f"  metadata: new card {safe_name} in Storage; place it in the editor")\n',
            1,
        ),
    ],
    "index.html": [
        # 5 (bottom-up): handleHash -- a deep link to a hidden landscape
        # card on a phone opens its portrait sibling.
        (
            "        function handleHash() {\n"
            "            var hash = window.location.hash.replace('#', '');\n"
            "            if (hash && vizLookup[hash]) {\n"
            "                loadVisualization(hash);\n"
            "            }\n"
            "        }\n",
            "        function handleHash() {\n"
            "            var hash = window.location.hash.replace('#', '');\n"
            "            // A link to a landscape card hidden on this phone (L-303)\n"
            "            // opens its portrait sibling instead of nothing.\n"
            "            if (hash && !vizLookup[hash] && hiddenSibling[hash]) hash = hiddenSibling[hash];\n"
            "            if (hash && vizLookup[hash]) {\n"
            "                loadVisualization(hash);\n"
            "            }\n"
            "        }\n",
            1,
        ),
        # 4: the card's size line names its shape when it has a sibling
        # (three copies of the card body -- all three are edited).
        (
            "Math.round(loose.size_kb) + ' KB</div>'",
            "sizeLabel(loose) + '</div>'",
            1,
        ),
        (
            "Math.round(item.size_kb) + ' KB</div>'",
            "sizeLabel(item) + '</div>'",
            2,
        ),
        # 3: the lobby's Featured strip shows one of a featured pair.
        (
            "            var featured = [];\n"
            "            for (var f = 0; f < shown.length; f++) {\n"
            "                if (shown[f].featured) featured.push(shown[f]);\n"
            "            }\n",
            "            var featured = [];\n"
            "            for (var f = 0; f < shown.length; f++) {\n"
            "                if (!shown[f].featured) continue;\n"
            "                // One of a featured pair, not both (L-303): the portrait\n"
            "                // card yields when its landscape sibling is also shown.\n"
            "                var sibF = shown[f].sibling && vizLookup[shown[f].sibling];\n"
            "                if (sibF && sibF.featured && shown[f].shape === '9:16') continue;\n"
            "                featured.push(shown[f]);\n"
            "            }\n",
            1,
        ),
        # 2: the one viewer rule, applied where Storage is filtered.
        (
            "                    metadata.visualizations = (metadata.visualizations || []).filter(\n"
            "                        function (v) { return v.room && v.room !== STORAGE_KEY; });\n"
            "                }\n",
            "                    metadata.visualizations = (metadata.visualizations || []).filter(\n"
            "                        function (v) { return v.room && v.room !== STORAGE_KEY; });\n"
            "                    // ONE rule (Tony's ruling, L-303, 2026-09-08): on a phone,\n"
            "                    // hide a landscape card that has a portrait sibling -- and\n"
            "                    // only when that sibling is itself served. A landscape card\n"
            "                    // with no sibling still shows and still sweeps. Desktop and\n"
            "                    // tablet show everything. Phone is the sweep's own test.\n"
            "                    if (window.innerWidth < 768) {\n"
            "                        var servedIds = {};\n"
            "                        metadata.visualizations.forEach(function (v) { servedIds[v.id] = v; });\n"
            "                        metadata.visualizations = metadata.visualizations.filter(function (v) {\n"
            "                            var files = v.files || {};\n"
            "                            var sib = v.sibling && servedIds[v.sibling];\n"
            "                            var hide = !!(files.landscape && !files.portrait && sib &&\n"
            "                                          (sib.files || {}).portrait);\n"
            "                            if (hide) hiddenSibling[v.id] = v.sibling;\n"
            "                            return !hide;\n"
            "                        });\n"
            "                    }\n"
            "                }\n",
            1,
        ),
        # 1: sizeLabel helper and the hidden-sibling map, beside fileForMode.
        (
            "        // Which file to open for this card in this mode. A one-file card\n"
            "        // serves its one file either way; a two-file card picks by mode.\n"
            "        function fileForMode(viz, mode) {\n",
            "        // Landscape cards hidden on this phone (L-303), id -> portrait\n"
            "        // sibling id, so a deep link to a hidden card can be redirected.\n"
            "        var hiddenSibling = {};\n"
            "\n"
            "        // The card's size line; a card with a sibling also names its\n"
            "        // shape, so two cards with one title read apart on the desktop.\n"
            "        function sizeLabel(viz) {\n"
            "            var s = Math.round(viz.size_kb) + ' KB';\n"
            "            if (viz.sibling && viz.shape) s += ' \\u00b7 ' + viz.shape;\n"
            "            return s;\n"
            "        }\n"
            "\n"
            "        // Which file to open for this card in this mode. A one-file card\n"
            "        // serves its one file either way; a two-file card (none since\n"
            "        // L-303, but the editor can still make one) picks by mode.\n"
            "        function fileForMode(viz, mode) {\n",
            1,
        ),
    ],
    "tools/sweep_report.py": [
        (
            '    if files.get("portrait"):\n'
            '        return "no sweep: portrait file serves", title, room, ""\n',
            '    if files.get("portrait"):\n'
            '        return "no sweep: portrait file serves", title, room, ""\n'
            '    if card.get("sibling"):\n'
            '        # L-303: the phone hides this card; its portrait sibling shows.\n'
            '        return ("no sweep: hidden on the phone (portrait sibling)",\n'
            '                title, room, "sibling %s" % card["sibling"])\n',
            1,
        ),
        (
            '        "no sweep: portrait file serves",\n'
            '        "no sweep: shape 9:16",\n',
            '        "no sweep: hidden on the phone (portrait sibling)",\n'
            '        "no sweep: portrait file serves",\n'
            '        "no sweep: shape 9:16",\n',
            1,
        ),
    ],
}

# The two L-301 merges whose portrait titles were lost (ledger L-303).
RETYPE = {
    "maps_disintegration_20260403_07_structures_mobile",
    "artemis_ii_20260402-0411_mission_moon_center2_mobile",
}


def split_cards(meta):
    """Split every two-slot card into a landscape card and a portrait card."""
    src = meta.get("visualizations", [])
    ids = {v.get("id") for v in src}
    out, made, collapsed = [], [], []
    for v in src:
        files = v.get("files") or {}
        if not (files.get("landscape") and files.get("portrait")):
            out.append(v)
            continue
        sizes = v.get("size_kb") if isinstance(v.get("size_kb"), dict) else {}
        if files["landscape"] == files["portrait"]:
            v["files"] = {"landscape": files["landscape"]}
            v["size_kb"] = {"landscape": sizes.get("landscape", sizes.get("portrait"))}
            v["shape"] = "16:9"
            out.append(v)
            collapsed.append(v["id"])
            continue
        pid = files["portrait"][:-5] if files["portrait"].endswith(".json") else files["portrait"]
        while pid in ids:
            pid += "_portrait"
        ids.add(pid)
        portrait = {
            "id": pid,
            "title": v.get("title"),
            "description": v.get("description"),
            "room": v.get("room", "other"),
            "shape": "9:16",
            "files": {"portrait": files["portrait"]},
            "live": v.get("live"),
            "featured": bool(v.get("featured")),
            "sources": list(v.get("sources") or []),
            "converted": v.get("converted"),
            "size_kb": {"portrait": sizes["portrait"]} if "portrait" in sizes else {},
            "sibling": v["id"],
        }
        v["files"] = {"landscape": files["landscape"]}
        v["size_kb"] = {"landscape": sizes["landscape"]} if "landscape" in sizes else {}
        v["shape"] = "16:9"
        v["sibling"] = pid
        out.append(v)
        out.append(portrait)
        made.append((v["id"], pid, v.get("room")))
    meta["visualizations"] = out
    meta["total_count"] = len(out)
    return made, collapsed


def main():
    texts = {}
    for name, md5 in FILES.items():
        raw = (ROOT / name).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != md5:
            print("STOP: %s md5 (LF) is %s, expected %s (at 700b426d)." % (name, got, md5))
            print("      Either this patch already ran or the file moved. Nothing written.")
            return 1
        texts[name] = lf.decode("utf-8")

    for name, edits in EDITS.items():
        t = texts[name]
        for i, (old, new, want) in enumerate(edits, 1):
            c = t.count(old)
            if c != want:
                print("STOP: %s edit %d matched %d time(s), expected %d. Nothing written."
                      % (name, i, c, want))
                return 1
            new.encode("ascii")
            t = t.replace(old, new)
        texts[name] = t

    meta = json.loads(texts["gallery/gallery_metadata.json"])
    two = [v["id"] for v in meta.get("visualizations", [])
           if (v.get("files") or {}).get("landscape") and (v.get("files") or {}).get("portrait")]
    if not two:
        print("STOP: no card has two file slots; the migration already ran. Nothing written.")
        return 1
    before = len(meta["visualizations"])
    made, collapsed = split_cards(meta)

    # Write everything only now.
    for name in ("tools/json_converter.py", "index.html", "tools/sweep_report.py"):
        (ROOT / name).write_bytes(texts[name].encode("utf-8"))
        print("ok  %s" % name)
    (ROOT / "gallery/gallery_metadata.json").write_bytes(
        (json.dumps(meta, indent=2) + "\n").encode("utf-8"))
    print("ok  gallery/gallery_metadata.json: %d cards -> %d" % (before, len(meta["visualizations"])))

    print("\nPortrait cards made (%d), each beside its landscape sibling:" % len(made))
    for land, port, room in made:
        print("  %-52s <- %s  [%s]" % (port, land, room))
    if collapsed:
        print("\nCollapsed to one file, no sibling (same file in both slots) (%d):" % len(collapsed))
        for c in collapsed:
            print("  " + c)
    print("\nTony-action (do), in the editor: retype the portrait title on these two")
    print("(L-301 kept the landscape title; the portrait title was lost):")
    for r in sorted(RETYPE):
        print("  " + r)
    print("\npatch applied. Next: gallery_maintenance_run.py (offline), commit, push.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
