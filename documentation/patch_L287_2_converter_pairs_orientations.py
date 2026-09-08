"""
patch_L287_2_converter_pairs_orientations.py -- one card, two files, again (gallery repo)

Built on gallery 12241c0 (nightly run 9-8-26 L286 L288 L291)
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).

Found by Tony, 2026-09-08: the Earth-and-Moon card shows its landscape
file on the phone. He had converted a landscape export and a portrait
export separately, as he always has -- Studio handles each by its own
preset, so they are separate scenes -- and that used to give one card
that served the right file to each device.

WHAT BROKE, AND WHEN
  Until L-287 (2026-09-04) a card carried a "mode" tag and the viewer
  FILTERED the grid by device, so a landscape card and a portrait card
  each showed only where they belonged. L-287 replaced that with one
  card carrying two "files" slots; its migration paired the existing
  cards BY TITLE (one landscape + one portrait, same title -> one card,
  38 of them). The converter that shipped with it knows no pairing rule
  at all: _v2_entry attaches a new file to an existing card only when
  the FILENAME already matches, and Studio's two exports never share a
  filename (<base>_gallery vs <base>_mobile). So every pair converted
  since September 4 landed as two one-file cards, and the viewer -- which
  now shows every card everywhere -- serves the landscape one to the
  phone. Three such pairs exist: solar_system_20260907_earth_shells_moon,
  maps_disintegration_20260403_07_structures,
  artemis_ii_20260402-0411_mission_moon_center2. The last two also have
  slightly different titles between L and P, which is why a title rule
  alone would still miss them.

THE FIX
  tools/json_converter.py, _v2_entry: a new file joins an existing card
  when, in this order,
    1. the filename or id already matches (unchanged);
    2. the two share a STEM -- the name with a trailing _gallery /
       _mobile / _portrait / _landscape removed -- and the existing card
       lacks the arriving orientation;
    3. exactly ONE existing card has the same title and lacks that slot.
  The card keeps its id, title, description, room, live, featured and
  sources; the arriving file fills the empty slot. A pair that arrives
  portrait-first works the same way.

  gallery/gallery_metadata.json: the three stranded pairs are merged by
  the same stem rule: the landscape card survives (id, title,
  description, room, as the L-287 migration did), gains the portrait
  file and size, featured becomes either card's, sources are the union,
  and the portrait card is removed. Titles that differed are printed so
  you can pick in the editor. total_count and last_updated are updated.

HOW TO RUN
  Save to the GALLERY repo root. Open in VS Code and press Run. Open the
  editor: three cards fewer, each Earth / MAPS / Artemis card with two
  files. Offline runner, commit, push. Mode 5: open Earth and Moon on
  the phone -- the portrait file serves; on the desktop -- the landscape.

GUARDS
  Both files md5-checked (LF-normalised) against 12241c0. Every text
  edit must match exactly once. The merge runs only if each pair is
  exactly one landscape-only card and one portrait-only card. ASCII, LF.

Written September 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib
import json
import re
import sys
from collections import OrderedDict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "tools/json_converter.py": "2e73ec99535e3d3e580b8ae8099030a1",
    "gallery/gallery_metadata.json": "603694e0868ad58883ffe19e29e9c4e6",
}

OLD = (
    "    filename = f\"{safe_name}.json\"\n"
    "    slot = \"portrait\" if mode == \"portrait\" else \"landscape\"\n"
    "    viz_list = metadata.get(\"visualizations\", [])\n"
    "    for i, v in enumerate(viz_list):\n"
    "        files = v.get(\"files\") or {}\n"
    "        if filename in files.values() or v.get(\"id\") == safe_name:\n"
    "            files[slot] = filename\n"
)
NEW = (
    "    filename = f\"{safe_name}.json\"\n"
    "    slot = \"portrait\" if mode == \"portrait\" else \"landscape\"\n"
    "    viz_list = metadata.get(\"visualizations\", [])\n"
    "\n"
    "    # L-287 follow-on (2026-09-08). Studio exports a landscape and a\n"
    "    # portrait file of the same figure as SEPARATE scenes (each preset\n"
    "    # handles its own), named <base>_gallery and <base>_mobile. They are\n"
    "    # one card with two files. The L-287 migration paired existing cards;\n"
    "    # this is the same pairing for cards that arrive one file at a time,\n"
    "    # in the order: same filename/id, then same STEM, then same TITLE.\n"
    "    def _stem(name):\n"
    "        return re.sub(r\"_(gallery|mobile|portrait|landscape)$\", \"\", name)\n"
    "\n"
    "    def _joins(v):\n"
    "        files = v.get(\"files\") or {}\n"
    "        if filename in files.values() or v.get(\"id\") == safe_name:\n"
    "            return True\n"
    "        if slot in files:\n"
    "            return False          # that orientation is already taken\n"
    "        stems = {_stem(os.path.splitext(f)[0]) for f in files.values()}\n"
    "        stems.add(_stem(str(v.get(\"id\", \"\"))))\n"
    "        return _stem(safe_name) in stems\n"
    "\n"
    "    match = [i for i, v in enumerate(viz_list) if _joins(v)]\n"
    "    if not match and title:\n"
    "        by_title = [i for i, v in enumerate(viz_list)\n"
    "                    if v.get(\"title\") == title and slot not in (v.get(\"files\") or {})]\n"
    "        if len(by_title) == 1:\n"
    "            match = by_title\n"
    "    for i in match[:1]:\n"
    "        v = viz_list[i]\n"
    "        files = v.get(\"files\") or {}\n"
    "        if True:\n"
    "            files[slot] = filename\n"
)

PAIRS = [
    "solar_system_20260907_earth_shells_moon",
    "maps_disintegration_20260403_07_structures",
    "artemis_ii_20260402-0411_mission_moon_center2",
]


def merge_pairs(meta):
    viz = meta["visualizations"]
    by_id = {v["id"]: v for v in viz}
    removed = []
    for base in PAIRS:
        L = by_id.get(base + "_gallery")
        P = by_id.get(base + "_mobile")
        if not L or not P:
            raise RuntimeError("pair %s: one side missing" % base)
        if set(L.get("files", {})) != {"landscape"} or set(P.get("files", {})) != {"portrait"}:
            raise RuntimeError("pair %s: not a landscape-only + portrait-only pair" % base)
        L["files"]["portrait"] = P["files"]["portrait"]
        sizes = L.get("size_kb") if isinstance(L.get("size_kb"), dict) else {}
        sizes["portrait"] = (P.get("size_kb") or {}).get("portrait")
        L["size_kb"] = sizes
        L["featured"] = bool(L.get("featured")) or bool(P.get("featured"))
        L["sources"] = list(OrderedDict.fromkeys((L.get("sources") or []) + (P.get("sources") or [])))
        L["converted"] = max(L.get("converted", ""), P.get("converted", ""))
        if L.get("room") != P.get("room"):
            print("  NOTE %s: rooms differed (L %r, P %r); kept the landscape room" % (base, L.get("room"), P.get("room")))
        if L.get("title") != P.get("title"):
            print("  NOTE %s: titles differed -- kept %r, dropped %r; pick in the editor" % (base, L.get("title"), P.get("title")))
        removed.append(P["id"])
    meta["visualizations"] = [v for v in viz if v["id"] not in removed]
    meta["total_count"] = len(meta["visualizations"])
    meta["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return removed


def main():
    texts = {}
    for name, md5 in FILES.items():
        lf = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != md5:
            print("STOP: %s md5 (LF) is %s, expected %s (at 12241c0)." % (name, got, md5))
            print("      Either this patch already ran or the file moved. Nothing written.")
            return 1
        texts[name] = lf.decode("utf-8")

    conv = texts["tools/json_converter.py"]
    if conv.count(OLD) != 1:
        print("STOP: converter anchor matched %d time(s), expected 1. Nothing written." % conv.count(OLD))
        return 1
    if "\nimport re\n" not in conv and "\nimport re," not in conv:
        print("STOP: json_converter.py does not import re; expected it to. Nothing written.")
        return 1
    conv = conv.replace(OLD, NEW, 1)

    meta = json.loads(texts["gallery/gallery_metadata.json"], object_pairs_hook=OrderedDict)
    try:
        removed = merge_pairs(meta)
    except RuntimeError as exc:
        print("STOP: %s. Nothing written." % exc)
        return 1
    meta_text = json.dumps(meta, indent=2, ensure_ascii=False) + "\n"

    NEW.encode("ascii")
    (ROOT / "tools/json_converter.py").write_bytes(conv.encode("utf-8"))
    (ROOT / "gallery/gallery_metadata.json").write_bytes(meta_text.encode("utf-8"))
    print("Patched tools/json_converter.py       new md5 (LF) %s" % hashlib.md5(conv.encode("utf-8")).hexdigest())
    print("Patched gallery/gallery_metadata.json  new md5 (LF) %s" % hashlib.md5(meta_text.encode("utf-8")).hexdigest())
    print("Merged 3 landscape+portrait pairs into one card each; removed:")
    for r in removed:
        print("  " + r)
    print("Cards now: %d" % meta["total_count"])
    print("Next: editor (three cards fewer, each with two files); offline runner; commit; push;")
    print("  then Earth and Moon on the phone (portrait file) and desktop (landscape).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
