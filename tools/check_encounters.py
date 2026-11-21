"""
check_encounters.py -- the gallery run's Encounters row: every encounter
card, its package under data/encounters/, and the plan it must agree with.

WHAT IT CHECKS (L-529, guided encounters; the brief's step 13)

    For every card in gallery/gallery_metadata.json that carries an
    "encounter" block:
    - THE CARD: its block names an id, a package under data/encounters/,
      a centre and its craft; its live address is exactly
      interactive.html?encounter=<id>; it is not also a scene; its package
      is on disk, ASCII, with LF line endings.
    - EVERY BODY SHARES THE MOMENTS: the package's moments rise; every
      body holds one position, one velocity and one speed for each of
      them, all numbers; each body's JPL name, less its id, is its
      entry's horizons_name today.
    - NO GAP IN THE HOURS: the frames are every whole UTC hour from the
      window's start to its end, none missing, none twice.
    - THE MINUTE WINDOWS ARE WHOLE: for each craft, every minute of its
      flyby window on its entry (path.events) is a moment of the package.
    - EACH PASS IS THE PLAN'S: the package's copy of each craft's flyby
      is its entry's event, field for field; the package holds a moment
      at the plan's closest (JPL's clock, TDB), the distance there is the
      plan's to 0.1 km, and no minute of the window is nearer. This is
      also the alarm if the orrery's plan ever moves a completed pass.
    - THE PAGE FETCHES IT AND THE NIGHT LEAVES IT: gallery/encounter.js
      and each package are in the maintenance run's SERVED_FILES (the
      live check compares them with the site); daily_run.py's
      night_allow_list lets the night touch nothing under
      data/encounters/; and documentation/check_cache_siblings.py knows
      the folder by name.

    It prints what it examined and how many of each. Its self-test runs
    first: each fault below is planted in a copy and must be caught, or
    the row fails -- a gap in the hours, a body short of a moment, a
    minute window cut, a pass moved on the entry, a card whose address is
    not its encounter's, the package missing from SERVED_FILES, and the
    night's allow-list holding data/encounters/. Nothing is fetched.

HOW TO RUN IT
    From VS Code: open this file and press Run. The gallery run runs it as
    its Encounters row. It needs no internet.

Role: check
Domain: gallery

Written November 20, 2026 with Anthropic's Claude Opus 5.5 (L-529,
slice 1: ESCAPADE's Earth flybys).
"""

import copy
import json
import math
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
METADATA = os.path.join(ROOT, "gallery", "gallery_metadata.json")
CONFIG = os.path.join(ROOT, "data", "objects_config.json")
ENC_DIR = "data/encounters/"
LIVE_PREFIX = "interactive.html?encounter="
MINUTE = 1.0 / 1440.0
EPS = 1e-6           # days: about 0.09 s, finer than JPL's printed Julian date


def calendar_jd(text):
    """A plan's moment, 'YYYY-MM-DD HH:MM' on JPL's clock (TDB), as a TDB
    Julian date. The calendar is read on its own clock, so no leap second
    enters."""
    d = datetime.strptime(text, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    return 2440587.5 + d.timestamp() / 86400.0


def utc_of(text):
    s = text.replace(" ", "T")
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    d = datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)
    return d


def entry_of(config, slug):
    for o in config.get("objects", []):
        if o.get("slug") == slug:
            return o
    return None


def flyby(entry, centre_name):
    for ev in ((entry or {}).get("path") or {}).get("events") or []:
        if ev.get("kind") == "flyby" and ev.get("body") == centre_name:
            return ev
    return None


def encounter_cards(metadata):
    return [v for v in metadata.get("visualizations", [])
            if isinstance(v, dict) and isinstance(v.get("encounter"), dict)]


def check_card(card, read_text):
    """(failures, package) for one card. read_text(path) -> text or None."""
    bad = []
    enc = card["encounter"]
    cid = enc.get("id")
    if not isinstance(cid, str) or not cid:
        return ["card %s: its encounter block names no id" % card.get("id")], None
    if card.get("live") != LIVE_PREFIX + cid:
        bad.append("card %s: its address is %r, not %r" % (card.get("id"), card.get("live"),
                                                        LIVE_PREFIX + cid))
    if card.get("scene") is True:
        bad.append("card %s is both an encounter and a scene" % card.get("id"))
    if not isinstance(enc.get("centre"), str) or not isinstance(enc.get("craft"), list) \
            or not enc.get("craft"):
        bad.append("card %s: its encounter block names no centre or no craft" % card.get("id"))
    pkg_path = enc.get("package")
    if not isinstance(pkg_path, str) or not pkg_path.startswith(ENC_DIR) \
            or not pkg_path.endswith(".json"):
        bad.append("card %s: its package %r is not under %s" % (card.get("id"), pkg_path, ENC_DIR))
        return bad, None
    text = read_text(pkg_path)
    if text is None:
        bad.append("card %s: its package %s is not on disk" % (card.get("id"), pkg_path))
        return bad, None
    if any(ord(ch) > 127 for ch in text):
        bad.append("%s is not ASCII" % pkg_path)
    if "\r" in text:
        bad.append("%s has CR line endings" % pkg_path)
    try:
        pkg = json.loads(text)
    except ValueError as exc:
        bad.append("%s is not JSON: %s" % (pkg_path, exc))
        return bad, None
    if pkg.get("id") != cid:
        bad.append("%s is encounter %r, the card's is %r" % (pkg_path, pkg.get("id"), cid))
    return bad, pkg


def check_package(pkg, card, config, counts):
    """Failures for one package against its card and the config."""
    bad = []
    enc = card["encounter"]
    m = pkg.get("moments") or {}
    jds = m.get("jd_tdb") or []
    n = len(jds)
    if n < 2 or any(not isinstance(j, (int, float)) for j in jds):
        return ["its moments are fewer than two, or not numbers"]
    if any(not (jds[i] > jds[i - 1]) for i in range(1, n)):
        bad.append("its moments do not rise")
    if len(m.get("utc") or []) != n or len(m.get("frame") or []) != n:
        bad.append("its UTC or frame list is not one to a moment")
        return bad
    centre = entry_of(config, enc["centre"])
    if centre is None:
        return bad + ["its centre %r has no entry in the config" % enc["centre"]]
    bodies = pkg.get("bodies") or {}
    counts["bodies"] += len(bodies)
    counts["moments"] += n
    for slug, b in sorted(bodies.items()):
        for f in ("pos_km", "vel_kms", "speed_kms"):
            arr = b.get(f)
            if not isinstance(arr, list) or len(arr) != n:
                bad.append("%s: its %s holds %s values for %d moments"
                           % (slug, f, len(arr) if isinstance(arr, list) else "no", n))
                continue
            flat = [v for row in arr for v in (row if isinstance(row, list) else [row])]
            if any(not isinstance(v, (int, float)) or math.isnan(v) for v in flat):
                bad.append("%s: its %s holds something that is not a number" % (slug, f))
        e = entry_of(config, slug)
        hid = str(b.get("horizons_id"))
        tail = " (%s)" % hid
        jn = str(b.get("jpl_name") or "")
        name = jn[:-len(tail)] if jn.endswith(tail) else None
        if e is None:
            bad.append("%s has no entry in the config" % slug)
        elif name != e.get("horizons_name") or hid != str(e.get("horizons_id")):
            bad.append("%s: JPL's name %r and id %s are not its entry's (%r, %s)"
                       % (slug, jn, hid, e.get("horizons_name"), e.get("horizons_id")))
    # No gap in the hours.
    w = pkg.get("window") or {}
    try:
        w0, w1 = utc_of(w["start_utc"]), utc_of(w["end_utc"])
    except (KeyError, ValueError):
        return bad + ["its window's start or end cannot be read"]
    hours = int(round((w1 - w0).total_seconds() / 3600.0))
    frames = [utc_of(m["utc"][i]) for i in range(n) if m["frame"][i]]
    counts["hours"] += len(frames)
    want = [w0.timestamp() + 3600.0 * k for k in range(hours + 1)]
    got = [f.timestamp() for f in frames]
    if got != want:
        missing = sorted(set(want) - set(got))
        extra = sorted(set(got) - set(want))
        bad.append("its hours are not every hour of the window: %d frames for %d hours; "
                   "missing %s; extra %s"
                   % (len(got), hours + 1,
                      [datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d %H:%M")
                       for t in missing[:3]],
                      [datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d %H:%M")
                       for t in extra[:3]]))
    # The minute windows, and each pass.
    passes = {p.get("slug"): p for p in (pkg.get("passes") or []) if isinstance(p, dict)}
    for slug in enc.get("craft") or []:
        ev = flyby(entry_of(config, slug), centre["name"])
        if ev is None:
            bad.append("%s: its entry has no flyby of %s" % (slug, centre["name"]))
            continue
        a, z = calendar_jd(ev["window"][0]), calendar_jd(ev["window"][1])
        mins = int(round((z - a) / MINUTE))
        idx = {}
        for i, j in enumerate(jds):
            k = (j - a) / MINUTE
            if -EPS * 1440 <= k <= mins + EPS * 1440 and abs(k - round(k)) * MINUTE < EPS:
                idx[int(round(k))] = i
        counts["minutes"] += len(idx)
        if sorted(idx) != list(range(mins + 1)):
            bad.append("%s: its minute window %s to %s TDB holds %d of its %d minutes"
                       % (slug, ev["window"][0], ev["window"][1], len(idx), mins + 1))
            continue
        p = passes.get(slug)
        if p is None:
            bad.append("%s: the package holds no pass for it" % slug)
            continue
        counts["passes"] += 1
        if p.get("event") != ev:
            diff = sorted(k for k in set(ev) | set(p.get("event") or {})
                          if ev.get(k) != (p.get("event") or {}).get(k))
            bad.append("%s: the package's pass is not its entry's event (%s differ)"
                       % (slug, ", ".join(diff)))
        cj = calendar_jd(ev["closest"])
        i = p.get("index")
        if not isinstance(i, int) or not (0 <= i < n) or abs(jds[i] - cj) > EPS:
            bad.append("%s: the package's pass is not at the plan's closest, %s TDB"
                       % (slug, ev["closest"]))
            continue
        pos = bodies[slug]["pos_km"]
        d = math.sqrt(sum(c * c for c in pos[i]))
        if round(d, 1) != round(float(ev["dist_km"]), 1):
            bad.append("%s: %.1f km at the plan's closest, the plan's %.1f km"
                       % (slug, d, ev["dist_km"]))
        nearest = min(idx.values(), key=lambda q: sum(c * c for c in pos[q]))
        if nearest != i:
            bad.append("%s: a minute of its window, %s, is nearer than the plan's closest"
                       % (slug, m["utc"][nearest]))
    return bad


def check_wiring(cards, served_files, allow, known_folders):
    bad = []
    if "gallery/encounter.js" not in served_files:
        bad.append("gallery/encounter.js is not in the maintenance run's SERVED_FILES")
    for c in cards:
        p = c["encounter"].get("package")
        if p not in served_files:
            bad.append("%s is not in the maintenance run's SERVED_FILES" % p)
    files, folders = allow
    held = [f for f in files if f.startswith(ENC_DIR)] + \
        [f for f in folders if ENC_DIR.startswith(f) or f.startswith(ENC_DIR)]
    if held:
        bad.append("the night's allow-list holds %s" % ", ".join(held))
    if "encounters" not in known_folders:
        bad.append("documentation/check_cache_siblings.py does not know data/encounters/")
    return bad


def run_all(metadata, config, read_text, served_files, allow, known_folders):
    counts = {"cards": 0, "bodies": 0, "moments": 0, "hours": 0, "minutes": 0, "passes": 0}
    bad = []
    cards = encounter_cards(metadata)
    counts["cards"] = len(cards)
    for c in cards:
        cb, pkg = check_card(c, read_text)
        bad.extend(cb)
        if pkg is not None:
            bad.extend("%s: %s" % (c["encounter"]["id"], s)
                       for s in check_package(pkg, c, config, counts))
    bad.extend(check_wiring(cards, served_files, allow, known_folders))
    return bad, counts


def load_real():
    with open(METADATA, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    with open(CONFIG, "r", encoding="utf-8") as f:
        config = json.load(f)
    sys.path.insert(0, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "documentation"))
    import gallery_maintenance_run as gmr
    import daily_run
    import check_cache_siblings
    allow = daily_run.night_allow_list(ROOT)

    def read_text(rel):
        p = os.path.join(ROOT, rel.replace("/", os.sep))
        if not os.path.exists(p):
            return None
        with open(p, "rb") as f:
            return f.read().decode("latin-1")
    return (metadata, config, read_text, list(gmr.SERVED_FILES), allow,
            dict(check_cache_siblings.KNOWN_FOLDERS))


def self_test(real):
    """Each fault planted in a copy must be caught. Returns the faults that
    were not."""
    metadata, config, read_text, served, allow, known = real
    cards = encounter_cards(metadata)
    if not cards:
        return ["there is no encounter card to plant faults in"]
    card = cards[0]
    pkg = json.loads(read_text(card["encounter"]["package"]))
    pkg_path = card["encounter"]["package"]
    missed = []

    def caught(label, md=None, cfg=None, pk=None, sv=None, al=None, kn=None, words=None):
        def rt(rel):
            if pk is not None and rel == pkg_path:
                return json.dumps(pk)
            return read_text(rel)
        bad, _c = run_all(md or metadata, cfg or config, rt, sv or served,
                          al or allow, kn or known)
        hit = [b for b in bad if words in b]
        print("  %s planted: %s -> %s" % ("ok  " if hit else "MISS", label,
                                          hit[0] if hit else "not caught"))
        if not hit:
            missed.append(label)

    # A gap in the hours: one hourly frame taken out (every list in step).
    p1 = copy.deepcopy(pkg)
    k = [i for i, f in enumerate(p1["moments"]["frame"]) if f][100]
    for f in ("jd_tdb", "utc", "frame"):
        del p1["moments"][f][k]
    for b in p1["bodies"].values():
        for f in ("pos_km", "vel_kms", "speed_kms"):
            del b[f][k]
    for p in p1["passes"]:
        p["index"] -= 1 if p["index"] > k else 0
    caught("an hour taken out of the frames", pk=p1, words="not every hour")
    # A body short of a moment.
    p2 = copy.deepcopy(pkg)
    slug = sorted(p2["bodies"])[0]
    p2["bodies"][slug]["speed_kms"] = p2["bodies"][slug]["speed_kms"][:-1]
    caught("a body short of a moment", pk=p2, words="speed_kms holds")
    # A minute window cut: a minute of the first craft's window taken out.
    p3 = copy.deepcopy(pkg)
    craft = card["encounter"]["craft"][0]
    pi = [p for p in p3["passes"] if p["slug"] == craft][0]["index"]
    cut = pi + 5
    for f in ("jd_tdb", "utc", "frame"):
        del p3["moments"][f][cut]
    for b in p3["bodies"].values():
        for f in ("pos_km", "vel_kms", "speed_kms"):
            del b[f][cut]
    caught("a minute cut from a flyby window", pk=p3, words="minute window")
    # The plan moves a completed pass: the entry's distance changed.
    c4 = copy.deepcopy(config)
    ev = flyby(entry_of(c4, craft), entry_of(c4, card["encounter"]["centre"])["name"])
    ev["dist_km"] = float(ev["dist_km"]) + 2.0
    caught("the plan's pass moved 2 km on the entry", cfg=c4, words="is not its entry's event")
    # A card whose address is not its encounter's.
    m5 = copy.deepcopy(metadata)
    for v in encounter_cards(m5):
        v["live"] = "interactive.html?encounter=another"
    caught("a card opening another encounter's address", md=m5, words="its address is")
    # The package missing from SERVED_FILES.
    caught("the package missing from SERVED_FILES",
           sv=[s for s in served if s != pkg_path], words="SERVED_FILES")
    # The night's allow-list holding data/encounters/.
    caught("the night's allow-list holding data/encounters/",
           al=(allow[0], list(allow[1]) + ["data/encounters/"]), words="allow-list holds")
    return missed


def main():
    print("=== Encounters (L-529): the cards, their packages, the plan, the night ===")
    real = load_real()
    missed = self_test(real)
    bad, counts = run_all(*real)
    cards = encounter_cards(real[0])
    for c in cards:
        print("  examined: card %s -> %s (%s)" % (c["id"], c["encounter"].get("package"),
                                              ", ".join(c["encounter"].get("craft") or [])))
    print("  examined: %d card(s); %d bodies at %d moments in all; %d hourly frames; "
          "%d flyby minutes; %d passes held to the plan"
          % (counts["cards"], counts["bodies"], counts["moments"], counts["hours"],
             counts["minutes"], counts["passes"]))
    print("  examined: SERVED_FILES, the night's allow-list (%d files, folders %s), "
          "the sibling check's known folders (%s)"
          % (len(real[4][0]), ", ".join(real[4][1]), ", ".join(sorted(real[5]))))
    for b in bad:
        print("  FAIL " + b)
    if missed:
        print("  FAIL the self-test missed: " + "; ".join(missed))
    if not cards:
        print("  FAIL no encounter card was found, so nothing was examined")
    ok = not bad and not missed and bool(cards)
    print("=== %s ===" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
