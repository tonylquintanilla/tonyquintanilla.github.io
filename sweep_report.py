"""
sweep_report.py - Which cards sweep on a phone in portrait, and why.

The sweep (L-286 room-shape rule, built 2026-09-05 in index.html) draws
a 2D plot served from a landscape-only card at its own width in a
portrait phone room and scrolls it sideways. Tony's phone pass found it
working with exceptions. This report applies the page's own rule to
every card and prints the result BY CLASS, names first, so the
exceptions can be checked one per class rather than one per card.

The rule, exactly as index.html's sweepWanted() has it:
  - a card whose shape is 9:16                 -> no sweep (portrait shape)
  - a card with a portrait file                -> no sweep (portrait slot serves)
  - a card whose figure has a 3D scene         -> no sweep (scales to fit)
  - otherwise (2D, landscape-only, not 9:16)   -> SWEEPS, at the figure's
    own width/height if the file carries them, else 16:9; and if that
    width fits the phone anyway, nothing scrolls.

Two classes the rule cannot see and this report adds:
  - Mapbox figures (sweep applies, but the map has its own drag)
  - figures stored taller than wide (they sweep only a little:
    Warming Stripes is 1200 x 1400 and sweeps to 689 px on a 390 px
    phone at 804 px room height)

Run from the gallery repo root or from tools/ (VS Code Run button):
    python tools/sweep_report.py
Reads gallery/gallery_metadata.json and each landscape figure JSON.
Writes nothing. Network not needed.

Module created: September 6, 2026 with Anthropic's Claude Fable 5.1 (L-286)

Role: devtool
Domain: gallery_pipeline
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..")) if os.path.basename(HERE) == "tools" else HERE
GALLERY = os.path.join(ROOT, "gallery")

# The phone the rule was measured on (iPhone, portrait, Safari): the room
# below the toolbar. Only used to say whether a swept plot actually
# scrolls; the rule itself does not depend on it.
PHONE_W = 390
ROOM_H = 804


def read_figure(path):
    """Return (has_scene, has_mapbox, width, height, error)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            fig = json.load(f)
    except Exception as e:  # noqa: BLE001 - report, do not hide
        return None, None, None, None, "%s: %s" % (type(e).__name__, e)
    layout = fig.get("layout", {}) if isinstance(fig, dict) else {}
    has_scene = "scene" in layout or any(k.startswith("scene") for k in layout)
    has_mapbox = "mapbox" in layout or any(
        isinstance(t, dict) and str(t.get("type", "")).endswith("mapbox")
        for t in (fig.get("data", []) if isinstance(fig, dict) else [])
    )
    return has_scene, has_mapbox, layout.get("width"), layout.get("height"), None


def classify(card):
    files = card.get("files") or {}
    shape = card.get("shape")
    room = card.get("room", "")
    title = card.get("title") or card.get("id")
    live = card.get("live")

    if not files:
        return "no file (interactive scene only)", title, room, ""
    if shape == "9:16":
        return "no sweep: shape 9:16", title, room, ""
    if files.get("portrait"):
        return "no sweep: portrait file serves", title, room, ""
    land = files.get("landscape")
    if not land:
        return "no sweep: no landscape file", title, room, ""

    path = os.path.join(GALLERY, land)
    if not os.path.exists(path):
        return "FILE MISSING", title, room, land
    has_scene, has_mapbox, w, h, err = read_figure(path)
    if err:
        return "FILE UNREADABLE", title, room, "%s -- %s" % (land, err)
    if has_scene:
        return "no sweep: 3D scene (scales to fit)", title, room, land

    aspect = (w / h) if (w and h) else 16.0 / 9.0
    swept_w = int(round(ROOM_H * aspect))
    detail = "%s  stored %sx%s -> %d px wide in a %d px room" % (
        land, w if w else "?", h if h else "?", swept_w, PHONE_W)
    if swept_w <= PHONE_W:
        return "sweeps by rule, but fits: nothing scrolls", title, room, detail
    if has_mapbox:
        return "SWEEPS -- Mapbox figure (map has its own drag)", title, room, detail
    if w and h and h > w:
        return "SWEEPS a little -- stored taller than wide", title, room, detail
    if not (w and h):
        return "SWEEPS at 16:9 (file carries no width/height)", title, room, detail
    return "SWEEPS at the file's own aspect", title, room, detail


def main():
    meta_path = os.path.join(GALLERY, "gallery_metadata.json")
    if not os.path.exists(meta_path):
        print("ERROR: %s not found. Run from the gallery repo root or tools/." % meta_path)
        sys.exit(1)
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)
    cards = meta.get("visualizations", [])
    print("sweep report -- %d cards in %s" % (len(cards), meta_path))
    print("rule: index.html sweepWanted(); phone %d px wide, room %d px high" % (PHONE_W, ROOM_H))
    print()

    classes = {}
    for c in cards:
        cls, title, room, detail = classify(c)
        classes.setdefault(cls, []).append((room, title, detail))

    order = [
        "SWEEPS at the file's own aspect",
        "SWEEPS at 16:9 (file carries no width/height)",
        "SWEEPS a little -- stored taller than wide",
        "SWEEPS -- Mapbox figure (map has its own drag)",
        "sweeps by rule, but fits: nothing scrolls",
        "no sweep: 3D scene (scales to fit)",
        "no sweep: portrait file serves",
        "no sweep: shape 9:16",
        "no sweep: no landscape file",
        "no file (interactive scene only)",
        "FILE MISSING",
        "FILE UNREADABLE",
    ]
    for cls in order + sorted(k for k in classes if k not in order):
        items = classes.get(cls)
        if not items:
            continue
        print("%s (%d)" % (cls, len(items)))
        for room, title, detail in sorted(items):
            line = "  %-42s %s" % (title[:42], room)
            if detail:
                line += "\n      " + detail
            print(line)
        print()

    total = sum(len(v) for v in classes.values())
    sweeping = sum(len(v) for k, v in classes.items() if k.startswith("SWEEPS"))
    missing = len(classes.get("FILE MISSING", [])) + len(classes.get("FILE UNREADABLE", []))
    print("%d cards: %d sweep on the phone, %d do not, %d could not be examined."
          % (total, sweeping, total - sweeping - missing, missing))
    if missing:
        print("A card that could not be examined is a finding, not a pass.")
        sys.exit(2)


if __name__ == "__main__":
    main()
