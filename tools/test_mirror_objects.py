"""
test_mirror_objects.py -- tools/mirror_objects.py does what it says, on
fixtures where each refusal and each kind of write must happen, and then
on the real config.

WHY THIS EXISTS
    The real config and export, on a good day, produce no change and no
    refusal, so a check that ran only on them could pass without its
    refusals ever having run. Each case below forces one path and fails
    the suite if the path does not produce what it must.

RUN COMMAND
    python test_mirror_objects.py     (from tools/; the maintenance run
                                       does this among its checkers)

Role: devtool
Domain: gallery

Module created: October 1, 2026 with Anthropic's Claude Opus 5.5
(L-395, the first build).
Module updated: October 14, 2026 with Anthropic's Claude Opus 5.5 (L-431,
build 3: the period's copy, its refusals, and a planted mirror that drops
the centre, each forced on a fixture.)
Module updated: October 26, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B part 2: a comet's open_path mark is copied, and written for no
other body.) Evening (L-493): JPL's name is copied, and written for no
body without one.
Module updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,
build B: a spacecraft's path is copied without the orrery's bookkeeping,
none for another body, and a planted mirror that drops the events is
caught.)
Module updated: November 5, 2026 with Anthropic's Claude Opus 5.5 (L-510:
a body moved across e = 1 is followed both ways, on fixtures and on the
real config, with three planted faults; a side change over a hand-set
entry is refused. patch_L510_3_mirror_follows_e_rule.py.)
Module updated: November 5, 2026 with Anthropic's Claude Opus 5.5 (L-507,
more voyages: an ended mission's mission_end and end_note are copied, and
written for no body without them.)
"""

import json
import os
import sys

import mirror_objects as mo

CONFIG = """{
  "objects": [
    {
      "slug": "mars", "name": "Mars", "horizons_id": "499", "id_type": "majorbody",
      "category": "planet", "features": {}
    },
    { "slug": "apophis", "name": "Apophis", "horizons_id": "99942", "id_type": "smallbody", "category": "asteroid" }
  ],
  "rooms": {"solar-system": {"drawer": {"rows": [{"slug": "sun"}, {"slug": "mars"}]}}}
}
"""

FAILS = []


def check(condition, message):
    if not condition:
        FAILS.append(message)


def export_of(**objects):
    return {"schema": 2, "objects": objects}


def obj(name, hid, id_type=None, description=None, info_url=None):
    return {"name": name, "horizons_id": hid, "id_type": id_type,
            "description": description, "info_url": info_url}


def cases():
    sun = obj("Sun", "10")
    ex = export_of(sun=sun, mars=obj("Mars", "499", None, 'NASA: "Red."',
                                     "https://science.nasa.gov/mars/"),
                   apophis=obj("Apophis", "2004 MN4", "smallbody", "Near.",
                               "https://example.nasa.gov/a/"))
    cfg = CONFIG.replace('"objects": [', '"objects": [\n    { "slug": "sun", '
                         '"name": "Sun", "horizons_id": "10", "id_type": '
                         '"majorbody" },', 1)
    edits, changes, failures, linked = mo.plan(cfg, ex)
    out = mo.apply(cfg, edits)
    data = json.loads(out)
    by = {o["slug"]: o for o in data["objects"]}
    check(not failures, "a clean export was refused: %s" % failures)
    check(by["mars"]["description"] == 'NASA: "Red."' and
          by["mars"]["info_url"] == "https://science.nasa.gov/mars/",
          "description and link were not inserted on a multi-line entry")
    check(by["apophis"]["horizons_id"] == "2004 MN4",
          "a changed Horizons id was not written")
    check(any(c.startswith("apophis.horizons_id: \"99942\" -> \"2004 MN4\"")
              for c in changes), "the id change was not reported by name")
    check(by["mars"]["id_type"] == "majorbody" and
          by["sun"]["id_type"] == "majorbody",
          "a blank id_type in the export overwrote the config's")
    check(by["mars"]["category"] == "planet" and "features" in by["mars"],
          "a field the mirror does not own was disturbed")
    check('"id_type": "majorbody",\n      "description"' in out,
          "the inserted fields did not follow the entry's own layout")
    again = mo.plan(out, ex)
    check(not again[0] and not again[1],
          "a second plan after writing still found changes: %s" % again[1])

    # A room row with no key in the export is refused, by name.
    ex2 = export_of(mars=ex["objects"]["mars"])
    failures = mo.plan(CONFIG, ex2)[2]
    check(any(f.startswith("sun:") for f in failures),
          "a room row with no key was not refused")
    # A key with no object in the config is refused.
    ex3 = export_of(sun=sun, mars=ex["objects"]["mars"],
                    venus=obj("Venus", "299"))
    failures = mo.plan(CONFIG, ex3)[2]
    check(any(f.startswith("venus:") for f in failures),
          "a key with no object was not refused")
    # The export serving none where the config holds words is refused.
    cfg4 = mo.apply(cfg, mo.plan(cfg, ex)[0])
    ex4 = json.loads(json.dumps(ex))
    ex4["objects"]["mars"]["info_url"] = None
    failures = mo.plan(cfg4, ex4)[2]
    check(any(f.startswith("mars.info_url:") for f in failures),
          "a null over a held link was not refused")

    # L-431, build 3: the period.
    fetched = {"kind": "fetched", "typed": False, "center": "@sun",
               "center_label": "the Sun", "open_orbit": False,
               "fetched": "2026-10-13", "words": None,
               "years": {"value": 1.881, "figures": 4, "text": "1.881"},
               "days": {"value": 687.0, "figures": 4, "text": "687.0"},
               "record": {"days": 686.98, "error_days": 0.05,
                          "elements": {"a": 1.52}}}
    ex5 = json.loads(json.dumps(ex))
    ex5["objects"]["mars"]["period"] = fetched
    ex5["objects"]["sun"]["period"] = None
    edits, changes, failures, linked = mo.plan(cfg4, ex5)
    out5 = mo.apply(cfg4, edits)
    by5 = {o["slug"]: o for o in json.loads(out5)["objects"]}
    check(not failures and by5["mars"].get("period", {}).get("center")
          == "@sun", "a fetched period was not copied with its centre")
    check("record" not in by5["mars"].get("period", {}),
          "the orrery's record was copied into the config")
    check("period" not in by5["sun"], "a null period was written for the Sun")
    check(any(c.startswith("mars.period: added") for c in changes),
          "the period was not reported by name")
    # A planted mirror that drops the centre: the next plan sees it.
    real_copy = mo.period_copy
    mo.period_copy = lambda p: ({k: v for k, v in real_copy(p).items()
                                 if k != "center"} if isinstance(p, dict)
                                else p)
    try:
        dropped = mo.apply(cfg4, mo.plan(cfg4, ex5)[0])
    finally:
        mo.period_copy = real_copy
    again = mo.plan(dropped, ex5)[1]
    check(any(c.startswith("mars.period:") for c in again),
          "a mirror that drops the centre was not caught on the next check")
    # A fetched period with no centre is refused, not copied.
    ex6 = json.loads(json.dumps(ex5))
    ex6["objects"]["mars"]["period"]["center"] = None
    failures = mo.plan(cfg4, ex6)[2]
    check(any(f.startswith("mars.period:") for f in failures),
          "a fetched period with no centre was not refused")
    # L-443 build B: a spacecraft's path, copied without the orrery's
    # bookkeeping; none for a body that is not one.
    plan = {"made": "2026-10-25",
            "span": {"start": "1977-09-06", "end": "2099-12-31"},
            "backbone": {"step": "7d", "thin_tol_au": 0.02},
            "events": [{"body": "Jupiter", "kind": "flyby", "stays": False,
                        "closest": "1979-03-05 12:05", "jd": 2443938.0,
                        "dist_km": 348436.0, "v_kms": 29.0,
                        "hill_km": 53000000, "ideal_step_s": 1200.0,
                        "window": ["1979-03-04 16:00", "1979-03-06 08:00"],
                        "step": "30m"}],
            "searched": ["Sun", "Jupiter"]}
    ex8 = json.loads(json.dumps(ex5))
    ex8["objects"]["apophis"]["path"] = plan
    ex8["objects"]["mars"]["path"] = None
    edits, changes, failures, linked = mo.plan(cfg4, ex8)
    by8 = {o["slug"]: o for o in json.loads(mo.apply(cfg4, edits))["objects"]}
    got = by8["apophis"].get("path") or {}
    ev = (got.get("events") or [{}])[0]
    check(not failures and got.get("span") == plan["span"]
          and ev.get("window") == plan["events"][0]["window"]
          and ev.get("step") == "30m" and ev.get("kind") == "flyby",
          "a path was not copied with its span and each event's window, "
          "step and kind")
    check("searched" not in got and "v_kms" not in ev and "jd" not in ev
          and ev.get("dist_km") == 348436.0,
          "the orrery's bookkeeping was copied with the path")
    check("path" not in by8["mars"], "a null path was written")
    # A planted mirror that drops the events: the next plan sees it.
    real_path = mo.path_copy
    mo.path_copy = lambda p_: (dict(real_path(p_), events=[])
                               if isinstance(p_, dict) else p_)
    try:
        dropped8 = mo.apply(cfg4, mo.plan(cfg4, ex8)[0])
    finally:
        mo.path_copy = real_path
    check(any(c.startswith("apophis.path:")
              for c in mo.plan(dropped8, ex8)[1]),
          "a mirror that drops a path's events was not caught on the next "
          "check")

    # L-443, slice 2's comets: a comet's open_path mark is copied with its
    # path, and written for no other body.
    ex9 = json.loads(json.dumps(ex8))
    ex9["objects"]["apophis"]["open_path"] = True
    edits9, _c9, failures9, _l9 = mo.plan(cfg4, ex9)
    by9 = {o["slug"]: o for o in json.loads(mo.apply(cfg4, edits9))["objects"]}
    check(not failures9 and by9["apophis"].get("open_path") is True
          and "open_path" not in by9["mars"],
          "a comet's open_path mark was not copied, or was written for a "
          "body without one")

    # L-493: JPL's name is copied, for the drawer's search box, and
    # written for no body the export gives none.
    ex10 = json.loads(json.dumps(ex8))
    ex10["objects"]["apophis"]["horizons_name"] = "99942 Apophis"
    edits10, _c10, failures10, _l10 = mo.plan(cfg4, ex10)
    by10 = {o["slug"]: o for o in json.loads(mo.apply(cfg4, edits10))["objects"]}
    check(not failures10 and by10["apophis"].get("horizons_name") == "99942 Apophis"
          and "horizons_name" not in by10["mars"],
          "JPL's name was not copied, or was written for a body without one")

    # L-507, more voyages: an ended mission's end day and its end_note are
    # copied, for the text box, and written for no body the export gives
    # none.
    ex11 = json.loads(json.dumps(ex8))
    ex11["objects"]["apophis"]["mission_end"] = "2025-09-18"
    ex11["objects"]["apophis"]["end_note"] = "Lost in April 2024."
    ex11["objects"]["apophis"]["cutoff_note"] = "Cut on 23 July."
    edits11, _c11, failures11, _l11 = mo.plan(cfg4, ex11)
    by11 = {o["slug"]: o for o in json.loads(mo.apply(cfg4, edits11))["objects"]}
    check(not failures11 and by11["apophis"].get("mission_end") == "2025-09-18"
          and by11["apophis"].get("end_note") == "Lost in April 2024."
          and by11["apophis"].get("cutoff_note") == "Cut on 23 July."
          and not any(f in by11["mars"] for f in
                      ("mission_end", "end_note", "cutoff_note")),
          "an ended mission's mission_end, end_note or cutoff_note was not "
          "copied, or was written for a body without one")

    # An export older than schema 2 is refused.
    ex7 = json.loads(json.dumps(ex5))
    ex7["schema"] = 1
    failures = mo.plan(cfg4, ex7)[2]
    check(any("schema 1" in f for f in failures),
          "an export older than schema 2 was not refused")


# L-510: a comet on an open path and a comet drawn as an orbit, as the
# real config holds them (one member per line, the side's three fields on
# shared lines), for the side-change cases.
SIDE_CONFIG = """{
  "objects": [
    {
      "slug": "west", "name": "West", "horizons_id": "C/1975 V1-A", "id_type": "smallbody",
      "horizons_name": "West (C/1975 V1-A)",
      "path": {"made": "2026-10-26", "span": {"end": "2027-10-26", "start": "1975-02-25"}, "events": []},
      "description": "A comet.",
      "open_path": true,
      "category": "comet", "availability": "path", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "arc-natural",
      "trajectory_of": null, "trace_policy": "full-arc", "features": {},
      "notes": "A comet on an open path (L-443 slice 2, build B part 2). Old words."
    },
    {
      "slug": "hale_bopp", "name": "Hale-Bopp", "horizons_id": "C/1995 O1", "id_type": "smallbody",
      "period": {"kind": "fetched", "center": "@0", "days": 900000.0},
      "description": "Another comet.",
      "category": "comet", "availability": "analytic", "parent": "sun",
      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",
      "trajectory_of": null, "trace_policy": "none", "features": {},
      "notes": "A person's words about Hale-Bopp."
    }
  ],
  "rooms": {"solar-system": {"drawer": {"rows": [
    {"slug": "west", "in": "comets_hyp"}, {"slug": "hale_bopp", "in": "comets"}]}}}
}
"""

SIDE_PLAN = {"made": "2026-11-05", "span": {"start": "2025-01-01",
                                            "end": "2027-11-05"},
             "backbone": {"step": "7d", "thin_tol_au": 0.02}, "events": []}


def side_export():
    """The export after JPL moved both across e = 1: West to an orbit, with
    a fetched period; Hale-Bopp to a path, with a plan and no period."""
    west = obj("West", "C/1975 V1-A", "smallbody", "A comet.")
    west["horizons_name"] = "West (C/1975 V1-A)"
    west["period"] = {"kind": "fetched", "center": "@sun", "days": 5.0e8}
    west["path"] = None
    hale = obj("Hale-Bopp", "C/1995 O1", "smallbody", "Another comet.")
    hale["period"] = None
    hale["path"] = SIDE_PLAN
    hale["open_path"] = True
    return export_of(west=west, hale_bopp=hale)


def side_problems(mirror_plan):
    """What is wrong with mirror_plan's handling of both side changes; an
    empty list when it is right. Run on the real mirror, and on planted
    faults that must give a non-empty list."""
    problems = []
    ex = side_export()
    edits, changes, failures, _l = mirror_plan(SIDE_CONFIG, ex,
                                               today="2026-11-05")
    if failures:
        problems.append("a side change was refused: %s" % failures)
    out = mo.apply(SIDE_CONFIG, edits)
    by = {o["slug"]: o for o in json.loads(out)["objects"]}
    w, h = by["west"], by["hale_bopp"]
    if not ("path" not in w and "open_path" not in w
            and w.get("period", {}).get("center") == "@sun"
            and (w.get("availability"), w.get("canonical_frame"),
                 w.get("trace_policy")) == ("analytic", "heliocentric",
                                            "none")):
        problems.append("West was not turned into an orbit: %s" % {
            k: w.get(k) for k in ("availability", "canonical_frame",
                                  "trace_policy", "open_path", "period")})
    if not (h.get("open_path") is True and h.get("path") == SIDE_PLAN
            and "period" not in h
            and (h.get("availability"), h.get("canonical_frame"),
                 h.get("trace_policy")) == ("path", "arc-natural",
                                            "full-arc")):
        problems.append("Hale-Bopp was not turned into a path: %s" % {
            k: h.get(k) for k in ("availability", "canonical_frame",
                                  "trace_policy", "open_path", "period")})
    if not (w.get("notes", "").startswith("A small body drawn as an orbit")
            and "Until 2026-11-05 it was drawn as a path" in w["notes"]
            and "Old words" not in w["notes"]):
        problems.append("West's note does not say it is an orbit now, or "
                        "kept the old side's words: %r" % w.get("notes"))
    if not (h.get("notes", "").startswith("A small body on an open path")
            and h["notes"].endswith(
                "Earlier note: A person's words about Hale-Bopp.")):
        problems.append("Hale-Bopp's note does not say it is a path now, or "
                        "lost a person's words: %r" % h.get("notes"))
    if not (any(c.startswith("west: drawn as an orbit now") and
                "stays in comets_hyp" in c for c in changes)
            and any(c.startswith("hale_bopp: drawn as a path now") and
                    "stays in comets" in c for c in changes)
            and any(c.startswith("west.path: removed") for c in changes)
            and any(c.startswith("hale_bopp.period: removed")
                    for c in changes)):
        problems.append("the side changes were not each printed, with the "
                        "drawer row's group: %s" % changes)
    rows = json.loads(out)["rooms"]["solar-system"]["drawer"]["rows"]
    if rows != [{"slug": "west", "in": "comets_hyp"},
                {"slug": "hale_bopp", "in": "comets"}]:
        problems.append("a drawer row was moved: %s" % rows)
    again = mirror_plan(out, ex, today="2026-11-06")
    if again[0] or again[2]:
        problems.append("a second run still moves or refuses: %s %s"
                        % (again[1], again[2]))
    return problems


def side_cases():
    # L-510: both ways, on the real mirror.
    for p in side_problems(mo.plan):
        check(False, "L-510: " + p)

    # Planted faults: each must be caught by the same cases.
    def no_removal(text, ex, today=None):
        keep = mo.SIDE_FIELDS
        mo.SIDE_FIELDS = ("open_path",)
        try:
            return mo.plan(text, ex, today=today)
        finally:
            mo.SIDE_FIELDS = keep

    def no_side_fields(text, ex, today=None):
        keep = mo.PATH_SIDE, mo.ORBIT_SIDE
        mo.PATH_SIDE = mo.ORBIT_SIDE = (("availability", "path"),)
        try:
            return mo.plan(text, ex, today=today)
        finally:
            mo.PATH_SIDE, mo.ORBIT_SIDE = keep

    def refuses_like_before(text, ex, today=None):
        keep = mo.side_change
        mo.side_change = lambda members, want: None
        try:
            return mo.plan(text, ex, today=today)
        finally:
            mo.side_change = keep

    for name, fault in (("a mirror that removes only the mark",
                         no_removal),
                        ("a mirror that leaves the frame and trace",
                         no_side_fields),
                        ("the mirror before L-510, which refused",
                         refuses_like_before)):
        check(side_problems(fault),
              "L-510: planted fault not caught: %s" % name)

    # A side change over an entry set by hand is refused, and nothing in
    # that entry is written.
    hand = SIDE_CONFIG.replace('"trace_policy": "full-arc"',
                               '"trace_policy": "recent"', 1)
    edits, _c, failures, _l = mo.plan(hand, side_export(), today="2026-11-05")
    by = {o["slug"]: o for o in json.loads(mo.apply(hand, edits))["objects"]}
    check(any(f.startswith("west: the orrery's export draws it as an orbit")
              for f in failures) and by["west"].get("open_path") is True
          and by["west"].get("availability") == "path",
          "L-510: a side change over a hand-set entry was not refused, or "
          "wrote to it: %s" % failures)


def real():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, mo.EXPORT)
    if not os.path.exists(path):
        print("Real config: %s is not pulled yet, so only the fixtures ran."
              % mo.EXPORT.replace(os.sep, "/"))
        return
    with open(os.path.join(root, mo.CONFIG), encoding="utf-8",
              newline="") as handle:
        text = handle.read()
    with open(path, encoding="utf-8") as handle:
        export = json.load(handle)
    edits, changes, failures, linked = mo.plan(text, export)
    out = mo.apply(text, edits)
    json.loads(out)
    again = mo.plan(out, export)
    check(not again[0], "the real config still moves after one write")
    print("Real config: %d linked (%s); %d field(s) would change; "
          "%d refusal(s)." % (len(linked), ", ".join(linked), len(changes),
                              len(failures)))

    # L-510: on the real config too, West moved to an orbit and Hale-Bopp
    # to a path in a copy of the export, and the result read back.
    if "west" in export.get("objects", {}) and \
            "hale_bopp" in export.get("objects", {}):
        x = json.loads(json.dumps(export))
        west, hale = x["objects"]["west"], x["objects"]["hale_bopp"]
        plan_copy = west.get("path")
        west.pop("open_path", None)
        west["path"] = None
        west["period"] = {"kind": "fetched", "center": "@sun", "days": 5.0e8}
        hale["open_path"] = True
        hale["path"] = plan_copy
        hale["period"] = None
        e2, c2, f2, _l2 = mo.plan(out, x, today="2026-11-05")
        out2 = mo.apply(out, e2)
        by2 = {o["slug"]: o for o in json.loads(out2)["objects"]}
        check(not f2 and by2["west"].get("availability") == "analytic"
              and "open_path" not in by2["west"]
              and by2["hale_bopp"].get("availability") == "path"
              and "period" not in by2["hale_bopp"]
              and not mo.plan(out2, x, today="2026-11-06")[0],
              "L-510: the real config did not follow West to an orbit and "
              "Hale-Bopp to a path, or a second run still moved it: %s" % f2)
        print("Real config, both side changes planted (West to an orbit, "
              "Hale-Bopp to a path): %d field(s) moved, %d refusal(s)."
              % (len(c2), len(f2)))
    else:
        check(False, "L-510: the real export has no West or Hale-Bopp to "
              "plant the side changes on")


def main():
    cases()
    side_cases()
    real()
    if FAILS:
        print("MIRROR OBJECTS SUITE: FAIL")
        for f in FAILS:
            print("  - " + f)
        return 1
    print("Fixtures: insert on a multi-line entry, an id change reported, a "
          "blank id_type kept, a room row without a key refused, a key "
          "without an object refused, a null over held words refused; a "
          "period copied with its centre and without the orrery's record, "
          "a mirror that drops the centre caught, a fetched period with no "
          "centre refused, an export older than schema 2 refused (L-431); "
          "a spacecraft's path copied with its span and each event's "
          "window, step and kind, without the orrery's bookkeeping, none "
          "for a body that is not one, and a mirror that drops the events "
          "caught (L-443); a comet's open_path mark copied, and written for "
          "no other body (slice 2's comets); JPL's name copied, and written "
          "for no body without one (L-493); a body the orrery moves across "
          "e = 1 followed both ways, its note rewritten and a person's words "
          "kept, its drawer row left and named, a second run quiet, a "
          "side change over a hand-set entry refused, and three planted "
          "faults caught (L-510); an ended mission's mission_end, end_note "
          "and cutoff_note copied, and written for no body without them "
          "(L-507).")
    print("MIRROR OBJECTS SUITE: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
