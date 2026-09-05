"""
patch_L287_1_migrate_schema_v2.py -- migrate the gallery's two index files
to schema version 2 (the room tree and one-card-per-exhibit shape).

RUN: save this file into the gallery repo's  gallery/  folder, next to
gallery_config.json and gallery_metadata.json. Open it in VS Code and
click Run. It also works from the repo root: it finds gallery/ relative
to its own location either way.

    python patch_L287_1_migrate_schema_v2.py

WHAT IT DOES (the mechanical half of L-287; you do the rest in the editor)

gallery_config.json
  - Rewrites the flat category list as a nested room tree, version 2:
    three doors (Solar System, Earth System, Stars), each with its body
    or subject rooms, all EMPTY, plus the hidden storage room.
  - Every door and room carries key, label, short, sentence, rooms.
    Sentences are placeholders ("") for you to fill in the editor.
  - Colors are L-283's placeholders. L-283 sets the real ones.

gallery_metadata.json
  - Pairs every title that appears as ONE landscape card and ONE
    portrait card into a single card with two entries under "files".
    A missing "mode" counts as landscape (index.html line 1912 rule).
  - Rewrites every other card to one "files" entry. "mode": "both" and
    missing "mode" become the landscape file.
  - Replaces category / category_label / subcategory / subcategory_label
    with  "room": "other"  (storage). Replaces filename / mode with
    "files" and "shape". Adds "live": null and "sources": [].
    Keeps id, title, description, featured, converted, size_kb.
  - "shape" is a first guess: portrait-only card -> "9:16", else "16:9".
  - Titles duplicated in the SAME orientation are NOT merged. They are
    kept as separate cards and named in the output.
  - Adds "version": 2 at the top level of both files so a consumer can
    tell old from new before touching a card. Updates last_updated and
    total_count (now a count of cards, not files).

GUARDS
  - Refuses unless both files' content fingerprints match the gallery
    repo at e414af13 (LF-normalized md5, so a CRLF working copy passes).
  - Refuses if either file is already version 2.
  - All-or-nothing: writes nothing unless both rewrites succeed.
  - No .bak. Undo is Discard Changes in GitHub Desktop.

Success prints one line per pair merged, one per card rewritten class,
the odd groups by name, then "migration applied". Failure prints one
ERROR line and writes nothing.

Written September 4, 2026 with Anthropic's Claude Fable 5.1. Built on
gallery e414af13d4c4c736a6c6d792d3fe7ad651f2fbdc at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Archive to documentation/ once run.
"""

import hashlib
import json
import os
import sys
from collections import OrderedDict, defaultdict
from datetime import date

EXPECT_CONFIG_MD5 = "e500c1ed9846d14d7013f51c29edc5e5"
EXPECT_META_MD5 = "c0813ada1e9fd93ec6e34273d574b397"
BUILT_ON = "e414af13"

# --------------------------------------------------------------------------
# The room tree. Doors carry color; rooms inherit. Sentences are
# placeholders except the one Earth System sentence the museum already
# has (L-282).
# --------------------------------------------------------------------------

def room(key, label, short, sentence="", special=False, rooms=None):
    r = OrderedDict()
    r["key"] = key
    r["label"] = label
    r["short"] = short
    r["sentence"] = sentence
    if special:
        r["special"] = True
    r["rooms"] = rooms or []
    return r


def door(key, label, short, color, sentence, rooms):
    d = OrderedDict()
    d["key"] = key
    d["label"] = label
    d["short"] = short
    d["color"] = color
    d["sentence"] = sentence
    d["rooms"] = rooms
    return d


def build_tree():
    solar = door("solar_system", "Solar System", "Solar", "#c9a44a", "", [
        room("orbital_mechanics", "Orbital Mechanics", "Orbits", special=True),
        room("sun", "The Sun", "Sun"),
        room("mercury", "Mercury", "Mercury"),
        room("venus", "Venus", "Venus"),
        room("earth", "Earth", "Earth", rooms=[
            room("moon", "The Moon", "Moon"),
        ]),
        room("mars", "Mars", "Mars"),
        room("jupiter", "Jupiter", "Jupiter"),
        room("saturn", "Saturn", "Saturn"),
        room("uranus", "Uranus", "Uranus"),
        room("neptune", "Neptune", "Neptune"),
        room("pluto", "Pluto", "Pluto"),
    ])
    earth_system = door("earth_system", "Earth System", "Earth", "#3f9a8a",
                        "Data preservation is climate action.", [])
    stars = door("stars", "Stars", "Stars", "#7a6bb5", "", [
        room("distance", "By Distance", "Distance"),
        room("magnitude", "By Magnitude", "Magnitude"),
        room("exoplanets", "Exoplanets", "Exoplanets"),
        room("galactic_center", "The Galactic Center", "Galactic Center"),
    ])
    tree = OrderedDict()
    tree["version"] = 2
    tree["doors"] = [solar, earth_system, stars]
    storage = OrderedDict()
    storage["key"] = "other"
    storage["label"] = "Storage"
    storage["hidden"] = True
    tree["storage"] = storage
    return tree


# --------------------------------------------------------------------------
# Card migration
# --------------------------------------------------------------------------

def eff_mode(card):
    """index.html treats a missing mode as landscape (line 1912 at e414af13)."""
    return card.get("mode") or "landscape"


def new_card(primary, landscape=None, portrait=None, featured=None,
             converted=None, description=None):
    c = OrderedDict()
    c["id"] = primary["id"]
    c["title"] = primary["title"]
    c["description"] = description if description is not None else primary.get("description", "")
    c["room"] = "other"
    files = OrderedDict()
    sizes = OrderedDict()
    if landscape is not None:
        files["landscape"] = landscape["filename"]
        sizes["landscape"] = landscape.get("size_kb")
    if portrait is not None:
        files["portrait"] = portrait["filename"]
        sizes["portrait"] = portrait.get("size_kb")
    c["shape"] = "9:16" if (landscape is None and portrait is not None) else "16:9"
    c["files"] = files
    c["live"] = None
    c["featured"] = bool(featured if featured is not None else primary.get("featured", False))
    c["sources"] = []
    c["converted"] = converted if converted is not None else primary.get("converted")
    c["size_kb"] = sizes
    return c


def migrate_cards(vizs):
    by_title = defaultdict(list)
    for v in vizs:
        by_title[v["title"]].append(v)

    merged_titles = []          # (title, landscape id, portrait id)
    desc_differed = []          # (title, landscape desc, portrait desc)
    odd_groups = []             # (title, [(id, mode)])
    single_counts = defaultdict(int)
    out = []
    done = set()

    for v in vizs:
        if v["id"] in done:
            continue
        group = by_title[v["title"]]
        if len(group) == 1:
            m = eff_mode(v)
            if m == "portrait":
                out.append(new_card(v, portrait=v))
                single_counts["portrait -> one portrait file, 9:16"] += 1
            elif m == "both":
                out.append(new_card(v, landscape=v))
                single_counts["mode both -> one landscape file"] += 1
            elif v.get("mode") is None:
                out.append(new_card(v, landscape=v))
                single_counts["mode absent -> one landscape file"] += 1
            else:
                out.append(new_card(v, landscape=v))
                single_counts["landscape -> one landscape file"] += 1
            done.add(v["id"])
            continue

        modes = sorted(eff_mode(g) for g in group)
        if modes == ["landscape", "portrait"]:
            L = [g for g in group if eff_mode(g) == "landscape"][0]
            P = [g for g in group if eff_mode(g) == "portrait"][0]
            featured = bool(L.get("featured")) or bool(P.get("featured"))
            conv = max(str(L.get("converted") or ""), str(P.get("converted") or "")) or None
            dl, dp = L.get("description", ""), P.get("description", "")
            if dl != dp:
                desc_differed.append((v["title"], dl, dp))
            out.append(new_card(L, landscape=L, portrait=P, featured=featured,
                                converted=conv, description=dl))
            merged_titles.append((v["title"], L["id"], P["id"]))
            done.update([L["id"], P["id"]])
        else:
            # Same-orientation duplicates (or 3+). Keep every card separate.
            odd_groups.append((v["title"], [(g["id"], eff_mode(g)) for g in group]))
            for g in group:
                if eff_mode(g) == "portrait":
                    out.append(new_card(g, portrait=g))
                else:
                    out.append(new_card(g, landscape=g))
                done.add(g["id"])

    return out, merged_titles, desc_differed, odd_groups, single_counts


# --------------------------------------------------------------------------
# File handling: fingerprint on LF-normalized content, write back in the
# line-ending style found.
# --------------------------------------------------------------------------

def read_guarded(path, expect_md5, label):
    if not os.path.exists(path):
        die("%s not found at %s" % (label, path))
    raw = open(path, "rb").read()
    was_crlf = b"\r\n" in raw
    content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
    actual = hashlib.md5(content).hexdigest()
    if actual != expect_md5:
        die("%s does not match the gallery repo at %s (md5 %s, expected %s). "
            "Built against a different file; nothing written." %
            (label, BUILT_ON, actual, expect_md5))
    print("ok  %s matches %s%s" % (label, BUILT_ON, " (working copy is CRLF)" if was_crlf else ""))
    return json.loads(content.decode("utf-8")), was_crlf


def die(msg):
    print("ERROR: " + msg)
    print("NOTHING was written. Undo, if ever needed, is Discard Changes in GitHub Desktop.")
    sys.exit(1)


def dump(obj, was_crlf):
    text = json.dumps(obj, indent=2, ensure_ascii=True) + "\n"
    data = text.encode("ascii")
    return data.replace(b"\n", b"\r\n") if was_crlf else data


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    gallery_dir = here if os.path.exists(os.path.join(here, "gallery_metadata.json")) \
        else os.path.join(here, "gallery")
    cfg_path = os.path.join(gallery_dir, "gallery_config.json")
    meta_path = os.path.join(gallery_dir, "gallery_metadata.json")
    print("gallery folder: %s" % gallery_dir)

    cfg, cfg_crlf = read_guarded(cfg_path, EXPECT_CONFIG_MD5, "gallery_config.json")
    meta, meta_crlf = read_guarded(meta_path, EXPECT_META_MD5, "gallery_metadata.json")
    if cfg.get("version") == 2 or meta.get("version") == 2:
        die("a file is already version 2; this migration has run.")

    vizs = meta["visualizations"]
    n_in = len(vizs)
    cards, merged, desc_diff, odd, singles = migrate_cards(vizs)

    # Every input card must land exactly once.
    landed = sum(len(c["files"]) for c in cards)
    if landed != n_in:
        die("card accounting failed: %d input cards, %d file slots written" % (n_in, landed))
    ids = [c["id"] for c in cards]
    if len(ids) != len(set(ids)):
        die("duplicate card ids after merge")

    new_meta = OrderedDict()
    new_meta["version"] = 2
    new_meta["visualizations"] = cards
    new_meta["last_updated"] = date.today().isoformat()
    new_meta["total_count"] = len(cards)
    new_cfg = build_tree()

    cfg_bytes = dump(new_cfg, cfg_crlf)
    meta_bytes = dump(new_meta, meta_crlf)

    # Both rewrites succeeded in memory; now write both.
    with open(cfg_path, "wb") as f:
        f.write(cfg_bytes)
    with open(meta_path, "wb") as f:
        f.write(meta_bytes)

    # ---- report: counts AND names ----
    print("")
    print("gallery_config.json: %d doors, %d rooms, 1 storage room (%d bytes)" %
          (len(new_cfg["doors"]), count_rooms(new_cfg["doors"]), len(cfg_bytes)))
    for d in new_cfg["doors"]:
        print("  %-13s %s" % (d["key"], ", ".join(r["label"] for r in d["rooms"]) or "(no rooms yet)"))
    print("")
    print("gallery_metadata.json: %d cards in -> %d cards out (%d bytes)" % (n_in, len(cards), len(meta_bytes)))
    print("  merged landscape+portrait pairs: %d" % len(merged))
    for t, li, pi in merged:
        print("    %s" % t)
    for label, n in sorted(singles.items()):
        print("  %s: %d" % (label, n))
    print("  all cards placed in room 'other' (storage); shape guessed from orientation")
    print("")
    if desc_diff:
        print("descriptions differed within %d merged pairs; the LANDSCAPE text was kept:" % len(desc_diff))
        for t, dl, dp in desc_diff:
            print("    %s" % t)
            print("      kept:    %s" % dl)
            print("      dropped: %s" % dp)
        print("")
    if odd:
        print("NOT merged, %d titles duplicated in the same orientation (%d cards kept separate; sort in the editor):" %
              (len(odd), sum(len(g) for _, g in odd)))
        for t, g in odd:
            print("    %s" % t)
            for cid, m in g:
                print("      %s (%s)" % (cid, m))
        print("")
    print("stamped: last_updated -> %s, total_count -> %d, version -> 2 in both files" %
          (new_meta["last_updated"], len(cards)))
    print("migration applied. Undo is Discard Changes in GitHub Desktop.")
    print("Do NOT push yet: index.html, json_converter.py and gallery_cleanup.py still read the old fields.")


def count_rooms(rooms):
    n = 0
    for r in rooms:
        n += len(r["rooms"]) + count_rooms(r["rooms"])
    return n


if __name__ == "__main__":
    main()
