"""
patch_L510_3_mirror_follows_e_rule.py -- the website's objects mirror
follows a body across e = 1 by itself, both ways (L-510 (the typed fields
stop deciding)): road stage 13's first quick win.

Built on gallery e605f5683a1e72c6ac4e8350bd67911c05d70ed1 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
ca4dceea55243e20e75689263ef31b996c8b1a3c at
https://github.com/tonylquintanilla/palomas_orrery (branch main), both
read live on Nov 5, 2026, 13:10 Chicago. Written by the coordinating
session of Nov 5 (Claude Opus 5.5), tested on a copy of the website at
that commit.

Tony's local folders: gallery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
and orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\

WHY

    On Nov 4 and 5 the website's night stopped three times at the objects
    mirror (tools/mirror_objects.py): the orrery had moved piece C of
    comet C/2025 K1 from a path to an orbit, by the e of its orbit
    solution in JPL's small-body database, and the mirror refused to
    delete its path plan and open_path mark ("a person decides").
    patch_L510_1 fixed piece C by hand. Tony's ruling of Nov 4, 23:47
    Chicago, "the website should follow the same rule as the orrery,
    based on eccentricity", is now done by the mirror for any body, so
    the next comet that changes side does not stop a night.

WHAT IT CHANGES (three files in tools\\, nothing under data\\)

    tools/mirror_objects.py, the objects mirror:
      - TO AN ORBIT: when the config holds open_path true and the
        orrery's export serves none, it removes "path" and "open_path",
        sets availability "path" -> "analytic", canonical_frame
        "arc-natural" -> "heliocentric", trace_policy "full-arc" ->
        "none", and inserts the period the export now serves.
      - TO A PATH: when the export serves open_path true and the config
        holds an orbit's entry, it removes "period", sets the three
        fields the other way, and inserts the path plan and open_path.
      - Either way it rewrites the entry's notes to say what happened and
        on which day (a person's own note is kept after it), and prints
        every change. It does NOT move the body's drawer row: the drawer
        groups by JPL's class, which the export does not carry, so the
        change line names the row's group for a person to check.
      - It still refuses, by name, a side change over an entry whose
        availability, frame and trace were set by hand, and any other
        field the export serves as null.
    tools/test_mirror_objects.py, its tests: both side changes on a
      fixture and on the real config, a person's note kept, the drawer
      row left alone, a second run quiet, the hand-set refusal, and three
      planted faults caught (among them the mirror as it was before this
      patch, which refuses exactly as it did on Nov 4).
    tools/test_gallery_cache_builder_offline.py, the builder's offline
      test, which the night runs:
      - a stand-in orbit for any body newly drawn as an orbit that its
        table of fake JPL answers does not hold (named when used), so
        the night does not stop on a missing entry, as it would have for
        piece C without patch_L510_1's hand-made one;
      - the fixed count of comets on open paths (13) replaced by a
        comparison, by name, with the orrery's export, since the count
        would turn the night red on the next side change;
      - an end-to-end case: West moved to an orbit and Hale-Bopp to a
        path in a copy of the export, the mirror writes a config from it,
        the builder builds it and passes, West served as an orbit and
        Hale-Bopp as a path.
    Each file's "Module updated" line says so.

    Permanent: the mirror's side-change rule and the three new test
    cases. Disposable: this script.

    Checked only at the lines it edits, each of which must be found
    exactly once. A file that already holds the result is accepted and
    reported, not refused.

RUN COMMAND

    Save this file in the website's root folder
    (tonyquintanilla.github.io), open it in VS Code and click Run.
    (python patch_L510_3_mirror_follows_e_rule.py)

    It writes the three files, then runs the mirror's tests and the
    builder's offline test (about half a minute) and prints their last
    lines. Success: one "ok" line per file, "patch applied", then
    "MIRROR OBJECTS SUITE: pass" and "PASS (511 checks, 0 failures)".
    Failure before writing: one ERROR or ANCHOR FAIL line, and nothing
    is written. Undo is Discard Changes in GitHub Desktop.

Written November 5, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import subprocess
import sys

TARGETS = [
    ('tools/mirror_objects.py', '2a5207e632be0b083fd6c93acfee865d', '5f7423917a7d2b5374182a0af92110ae', [
        ("    value, so a fix is reported and not only made (Tony's ruling,\n    2026-10-01: simple errors are fixed and reported).\n\nWHAT IT REFUSES (named, and the run exits 1)\n\n    - the export or the config is missing or unreadable\n",
         '    value, so a fix is reported and not only made (Tony\'s ruling,\n    2026-10-01: simple errors are fixed and reported).\n\nWHEN A BODY CHANGES SIDE (L-510)\n\n    The orrery draws a small body as a path when the e of its orbit\n    solution in JPL\'s small-body database is at or above 1, and as an\n    orbit below it (path_or_orbit.py), and the website follows the same\n    rule (Tony, 2026-11-04, 23:47 Chicago: "the website should follow the\n    same rule as the orrery, based on eccentricity"). When JPL\'s new\n    solution moves a body across 1, the export\'s open_path tells this\n    tool, which follows by itself:\n\n    to an orbit   the config holds open_path true and the export serves\n                  none. path and open_path are removed; availability\n                  "path" -> "analytic", canonical_frame "arc-natural" ->\n                  "heliocentric", trace_policy "full-arc" -> "none"; the\n                  period the export now serves is inserted.\n    to a path     the export serves open_path true and the config holds\n                  an orbit\'s entry (availability "analytic"). The period\n                  is removed; the three fields the other way; the path\n                  plan and open_path inserted.\n\n    Either way the entry\'s notes say what happened and when (a note that\n    only described the old side is replaced; any other is kept after the\n    new one), and every change is printed. Its drawer row is NOT moved:\n    the drawer groups by JPL\'s class, which the export does not carry, so\n    the change line names the row\'s group for a person to check. The\n    builder then serves the body on its new side; the comet that first\n    did this, piece C of C/2025 K1, stopped three nights at this tool\n    while it refused, before this rule (L-510\'s note of 2026-11-05).\n\nWHAT IT REFUSES (named, and the run exits 1)\n\n    - the export or the config is missing or unreadable\n'),
        ("      export: the room would show a body with no description or link\n    - a key in the export with no object of that slug in the config\n    - a field the export serves as null while the config holds one: the\n      tool does not delete a person's words, so a person decides\n    - an export older than schema 2, which carries no periods: the\n      website's rooms print a period from this copy, so the orrery's\n      export must be pulled again after the orrery has pushed (L-431)\n",
         "      export: the room would show a body with no description or link\n    - a key in the export with no object of that slug in the config\n    - a field the export serves as null while the config holds one: the\n      tool does not delete a person's words, so a person decides. The one\n      exception is a side change, below\n    - a side change whose entry does not hold the old side's\n      availability, frame and trace: it was set by hand, so a person\n      decides\n    - an export older than schema 2, which carries no periods: the\n      website's rooms print a period from this copy, so the orrery's\n      export must be pulled again after the orrery has pushed (L-431)\n"),
        ('5.5 (L-493: JPL\'s name for each body, the export\'s horizons_name, which\nthe Horizons check confirms, is copied, for the Solar System room\'s\nsearch box to look in.)\n"""\n\nimport json\nimport os\nimport sys\n\nfrom mirror_constants import member_separator, parse_with_spans, render\n\nCONFIG = os.path.join("data", "objects_config.json")\nEXPORT = os.path.join("data", "objects_export.json")\n',
         '5.5 (L-493: JPL\'s name for each body, the export\'s horizons_name, which\nthe Horizons check confirms, is copied, for the Solar System room\'s\nsearch box to look in.)\nModule updated: November 5, 2026 with Anthropic\'s Claude Opus 5.5 (L-510:\na body the orrery moves across e = 1 follows by itself, both ways; see\nWHEN A BODY CHANGES SIDE. patch_L510_3_mirror_follows_e_rule.py.)\n"""\n\nimport json\nimport os\nimport sys\nfrom datetime import datetime, timezone\n\nfrom mirror_constants import (anchor_separator, member_separator,\n                              parse_with_spans, render)\n\nCONFIG = os.path.join("data", "objects_config.json")\nEXPORT = os.path.join("data", "objects_export.json")\n'),
        ('        self.text = text\n\n\ndef plan(config_text, export):\n    """(edits, changes, failures, linked) for this config and export.\n\n    changes are printed lines naming each field that would move; failures\n    are refusals, each named.\n    """\n    root = parse_with_spans(config_text)\n    edits, changes, failures, linked = [], [], [], []\n    served = export.get("objects") or {}\n',
         '        self.text = text\n\n\n# L-510: the two sides a small body is drawn on, by the e of its orbit\n# solution in JPL\'s small-body database (the orrery\'s path_or_orbit.py;\n# the website follows the same rule, Tony\'s ruling of 2026-11-04, 23:47\n# Chicago). What an entry of each side holds here, as Hale-Bopp\'s and the\n# comets on open paths\' entries hold it.\nORBIT_SIDE = (("availability", "analytic"),\n              ("canonical_frame", "heliocentric"),\n              ("trace_policy", "none"))\nPATH_SIDE = (("availability", "path"),\n             ("canonical_frame", "arc-natural"),\n             ("trace_policy", "full-arc"))\n# What a side change removes when the export stops serving it: a path\'s\n# plan and mark (to an orbit), an orbit\'s period (to a path). Any other\n# field the export serves as null is still refused for a person.\nSIDE_FIELDS = ("path", "open_path", "period")\n# A note that only describes the old side is replaced; any other note is\n# a person\'s words and is kept after the new one.\nSIDE_NOTE_STARTS = ("A comet on an open path (L-443",\n                    "A comet drawn as an orbit, by the e",\n                    "A small body drawn as an orbit, by the e",\n                    "A small body on an open path, by the e")\nORBIT_NOTE = (\n    "A small body drawn as an orbit, by the e of its orbit solution in "\n    "JPL\'s small-body database, which is below 1 (L-510; the website "\n    "follows the orrery\'s rule, Tony\'s ruling of 2026-11-04). Its name, "\n    "horizons_id, id_type, description, link and period come from the "\n    "orrery\'s list (celestial_objects.py) through the objects mirror. "\n    "Until %s it was drawn as a path; that day the objects mirror removed "\n    "its path plan and open_path mark, which the orrery\'s export no longer "\n    "served, and set its availability, frame and trace as an orbit\'s. No "\n    "date is typed here.")\nPATH_NOTE = (\n    "A small body on an open path, by the e of its orbit solution in JPL\'s "\n    "small-body database, which is at or above 1 (L-510; the website "\n    "follows the orrery\'s rule, Tony\'s ruling of 2026-11-04). Its name, "\n    "horizons_id, id_type, description, link, open_path mark and path plan "\n    "come from the orrery\'s list (celestial_objects.py) through the objects "\n    "mirror: the plan the orrery\'s path_plan.py makes from JPL\'s own "\n    "positions. The cache builder fetches the path by that plan, as it "\n    "fetches a spacecraft\'s, and the room draws it solid to the minute "\n    "shown and dashed after. Until %s it was drawn as an orbit; that day "\n    "the objects mirror removed its period, which the orrery\'s export no "\n    "longer served, and set its availability, frame and trace as a path\'s. "\n    "No date is typed here.")\n\n\ndef side_change(members, want):\n    """L-510: "orbit" or "path" when the orrery\'s export moves this entry\n    to the other side, else None.\n\n    To an orbit: the config holds open_path true and the export serves\n    none. To a path: the export serves open_path true and the config\n    holds an orbit\'s entry (availability "analytic"); an entry with no\n    availability yet is a body being keyed, and its mark is inserted as\n    before (L-443).\n    """\n    held = members.get("open_path")\n    held_path = held is not None and held[0].value is True\n    served_path = want.get("open_path") is True\n    if held_path and not served_path:\n        return "orbit"\n    if served_path and not held_path:\n        avail = members.get("availability")\n        if avail is not None and avail[0].value == "analytic":\n            return "path"\n    return None\n\n\ndef removal(text, members, field):\n    """An Edit removing one member and the comma before it, or None when\n    the member is its object\'s first (none is, in this config)."""\n    child, key_start = members[field]\n    i = key_start - 1\n    while i >= 0 and text[i] in " \\t\\r\\n":\n        i -= 1\n    if i < 0 or text[i] != ",":\n        return None\n    return Edit(i, child.end, "")\n\n\ndef short(value):\n    """A value as a change line prints it: a path plan by its span, a\n    period by its kind, anything else in full."""\n    if isinstance(value, dict) and "span" in value:\n        return "a path plan, span %s" % render(value.get("span"))\n    if isinstance(value, dict) and "kind" in value:\n        return "a %s period" % value.get("kind")\n    return render(value)\n\n\ndef drawer_group(root, slug):\n    rooms = root.value.get("rooms") or {}\n    rows = ((rooms.get(ROOM) or {}).get("drawer") or {}).get("rows") or []\n    for row in rows:\n        if isinstance(row, dict) and row.get("slug") == slug:\n            return row.get("in")\n    return None\n\n\ndef plan(config_text, export, today=None):\n    """(edits, changes, failures, linked) for this config and export.\n\n    changes are printed lines naming each field that would move; failures\n    are refusals, each named. today (YYYY-MM-DD, UTC) dates the note a side\n    change writes; the run passes none and today\'s UTC date is used.\n    """\n    if today is None:\n        today = datetime.now(timezone.utc).date().isoformat()\n    root = parse_with_spans(config_text)\n    edits, changes, failures, linked = [], [], [], []\n    served = export.get("objects") or {}\n'),
        ('            failures.append("%s.period: fetched from JPL with no centre; "\n                            "refused rather than copied" % slug)\n            continue\n        for field in INSERTED:\n            new = wanted(want, field)\n            if field in members:\n                child, _ = members[field]\n                if new is None:\n                    failures.append("%s.%s: the export serves none and the "\n                                    "config holds %s; a person decides"\n                                    % (slug, field, render(child.value)))\n',
         '            failures.append("%s.period: fetched from JPL with no centre; "\n                            "refused rather than copied" % slug)\n            continue\n        # L-510: a body the orrery now draws on the other side of e = 1.\n        side = side_change(members, want)\n        if side is not None:\n            old_side, new_side = ((PATH_SIDE, ORBIT_SIDE) if side == "orbit"\n                                  else (ORBIT_SIDE, PATH_SIDE))\n            held = dict((f, members[f][0].value if f in members else None)\n                        for f, _v in old_side)\n            if held != dict(old_side):\n                failures.append(\n                    "%s: the orrery\'s export draws it as %s, but the config\'s "\n                    "%s are not a %s\'s (%s); a person decides"\n                    % (slug, "an orbit" if side == "orbit" else "a path",\n                       "availability, frame and trace",\n                       "path" if side == "orbit" else "orbit",\n                       ", ".join("%s %s" % (f, render(v))\n                                 for f, v in sorted(held.items()))))\n                continue\n            group = drawer_group(root, slug)\n            changes.append(\n                "%s: drawn as %s now, as the orrery draws it (the e of its "\n                "orbit solution in JPL\'s small-body database is %s 1, "\n                "L-510)%s" % (\n                    slug, "an orbit" if side == "orbit" else "a path",\n                    "below" if side == "orbit" else "at or above",\n                    "" if group is None else\n                    "; its drawer row stays in %s, since JPL\'s class is not "\n                    "in the export: a person checks it" % group))\n            for (field, old), (_f, new) in zip(old_side, new_side):\n                child, _ = members[field]\n                changes.append("%s.%s: %s -> %s" % (slug, field, render(old),\n                                                    render(new)))\n                edits.append(Edit(child.start, child.end, render(new)))\n            note = (ORBIT_NOTE if side == "orbit" else PATH_NOTE) % today\n            if "notes" in members:\n                child, _ = members["notes"]\n                old_note = child.value or ""\n                if old_note and not old_note.startswith(SIDE_NOTE_STARTS):\n                    note += " Earlier note: " + old_note\n                changes.append("%s.notes: rewritten for its new side" % slug)\n                edits.append(Edit(child.start, child.end, render(note)))\n            else:\n                last, _ = max(members.values(), key=lambda m: m[0].end)\n                changes.append("%s.notes: added for its new side" % slug)\n                edits.append(Edit(last.end, last.end, \'%s"notes": %s\' % (\n                    anchor_separator(config_text, last.end), render(note))))\n        for field in INSERTED:\n            new = wanted(want, field)\n            if field in members:\n                child, _ = members[field]\n                if new is None and side is not None and field in SIDE_FIELDS:\n                    gone = removal(config_text, members, field)\n                    if gone is None:\n                        failures.append("%s.%s: the first member of its "\n                                        "entry, so it cannot be removed; a "\n                                        "person decides" % (slug, field))\n                        continue\n                    changes.append("%s.%s: removed (%s)" % (\n                        slug, field, short(child.value)))\n                    edits.append(gone)\n                elif new is None:\n                    failures.append("%s.%s: the export serves none and the "\n                                    "config holds %s; a person decides"\n                                    % (slug, field, render(child.value)))\n'),
        ('\n\ndef apply(text, edits):\n    for edit in sorted(edits, key=lambda e: e.start, reverse=True):\n        text = text[:edit.start] + edit.text + text[edit.end:]\n    return text\n\n',
         '\n\ndef apply(text, edits):\n    # L-510: a removed member and a member inserted at the same anchor can\n    # share a start (the period removed from just after id_type, the path\n    # inserted there). Sorted by (start, end), last first, the removal is\n    # applied before the insertion, so it never removes what was inserted.\n    for edit in sorted(edits, key=lambda e: (e.start, e.end), reverse=True):\n        text = text[:edit.start] + edit.text + text[edit.end:]\n    return text\n\n'),
    ]),
    ('tools/test_mirror_objects.py', '22c7049056d5363beaf62e9f9549b5d7', '18cf2932ad83aa060e899aa5b1500c70', [
        ('build B: a spacecraft\'s path is copied without the orrery\'s bookkeeping,\nnone for another body, and a planted mirror that drops the events is\ncaught.)\n"""\n\nimport json\n',
         'build B: a spacecraft\'s path is copied without the orrery\'s bookkeeping,\nnone for another body, and a planted mirror that drops the events is\ncaught.)\nModule updated: November 5, 2026 with Anthropic\'s Claude Opus 5.5 (L-510:\na body moved across e = 1 is followed both ways, on fixtures and on the\nreal config, with three planted faults; a side change over a hand-set\nentry is refused. patch_L510_3_mirror_follows_e_rule.py.)\n"""\n\nimport json\n'),
        ('          "an export older than schema 2 was not refused")\n\n\ndef real():\n    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n    path = os.path.join(root, mo.EXPORT)\n',
         '          "an export older than schema 2 was not refused")\n\n\n# L-510: a comet on an open path and a comet drawn as an orbit, as the\n# real config holds them (one member per line, the side\'s three fields on\n# shared lines), for the side-change cases.\nSIDE_CONFIG = """{\n  "objects": [\n    {\n      "slug": "west", "name": "West", "horizons_id": "C/1975 V1-A", "id_type": "smallbody",\n      "horizons_name": "West (C/1975 V1-A)",\n      "path": {"made": "2026-10-26", "span": {"end": "2027-10-26", "start": "1975-02-25"}, "events": []},\n      "description": "A comet.",\n      "open_path": true,\n      "category": "comet", "availability": "path", "parent": "sun",\n      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "arc-natural",\n      "trajectory_of": null, "trace_policy": "full-arc", "features": {},\n      "notes": "A comet on an open path (L-443 slice 2, build B part 2). Old words."\n    },\n    {\n      "slug": "hale_bopp", "name": "Hale-Bopp", "horizons_id": "C/1995 O1", "id_type": "smallbody",\n      "period": {"kind": "fetched", "center": "@0", "days": 900000.0},\n      "description": "Another comet.",\n      "category": "comet", "availability": "analytic", "parent": "sun",\n      "canonical_center": "@sun", "center_slug": "sun", "canonical_frame": "heliocentric",\n      "trajectory_of": null, "trace_policy": "none", "features": {},\n      "notes": "A person\'s words about Hale-Bopp."\n    }\n  ],\n  "rooms": {"solar-system": {"drawer": {"rows": [\n    {"slug": "west", "in": "comets_hyp"}, {"slug": "hale_bopp", "in": "comets"}]}}}\n}\n"""\n\nSIDE_PLAN = {"made": "2026-11-05", "span": {"start": "2025-01-01",\n                                            "end": "2027-11-05"},\n             "backbone": {"step": "7d", "thin_tol_au": 0.02}, "events": []}\n\n\ndef side_export():\n    """The export after JPL moved both across e = 1: West to an orbit, with\n    a fetched period; Hale-Bopp to a path, with a plan and no period."""\n    west = obj("West", "C/1975 V1-A", "smallbody", "A comet.")\n    west["horizons_name"] = "West (C/1975 V1-A)"\n    west["period"] = {"kind": "fetched", "center": "@sun", "days": 5.0e8}\n    west["path"] = None\n    hale = obj("Hale-Bopp", "C/1995 O1", "smallbody", "Another comet.")\n    hale["period"] = None\n    hale["path"] = SIDE_PLAN\n    hale["open_path"] = True\n    return export_of(west=west, hale_bopp=hale)\n\n\ndef side_problems(mirror_plan):\n    """What is wrong with mirror_plan\'s handling of both side changes; an\n    empty list when it is right. Run on the real mirror, and on planted\n    faults that must give a non-empty list."""\n    problems = []\n    ex = side_export()\n    edits, changes, failures, _l = mirror_plan(SIDE_CONFIG, ex,\n                                               today="2026-11-05")\n    if failures:\n        problems.append("a side change was refused: %s" % failures)\n    out = mo.apply(SIDE_CONFIG, edits)\n    by = {o["slug"]: o for o in json.loads(out)["objects"]}\n    w, h = by["west"], by["hale_bopp"]\n    if not ("path" not in w and "open_path" not in w\n            and w.get("period", {}).get("center") == "@sun"\n            and (w.get("availability"), w.get("canonical_frame"),\n                 w.get("trace_policy")) == ("analytic", "heliocentric",\n                                            "none")):\n        problems.append("West was not turned into an orbit: %s" % {\n            k: w.get(k) for k in ("availability", "canonical_frame",\n                                  "trace_policy", "open_path", "period")})\n    if not (h.get("open_path") is True and h.get("path") == SIDE_PLAN\n            and "period" not in h\n            and (h.get("availability"), h.get("canonical_frame"),\n                 h.get("trace_policy")) == ("path", "arc-natural",\n                                            "full-arc")):\n        problems.append("Hale-Bopp was not turned into a path: %s" % {\n            k: h.get(k) for k in ("availability", "canonical_frame",\n                                  "trace_policy", "open_path", "period")})\n    if not (w.get("notes", "").startswith("A small body drawn as an orbit")\n            and "Until 2026-11-05 it was drawn as a path" in w["notes"]\n            and "Old words" not in w["notes"]):\n        problems.append("West\'s note does not say it is an orbit now, or "\n                        "kept the old side\'s words: %r" % w.get("notes"))\n    if not (h.get("notes", "").startswith("A small body on an open path")\n            and h["notes"].endswith(\n                "Earlier note: A person\'s words about Hale-Bopp.")):\n        problems.append("Hale-Bopp\'s note does not say it is a path now, or "\n                        "lost a person\'s words: %r" % h.get("notes"))\n    if not (any(c.startswith("west: drawn as an orbit now") and\n                "stays in comets_hyp" in c for c in changes)\n            and any(c.startswith("hale_bopp: drawn as a path now") and\n                    "stays in comets" in c for c in changes)\n            and any(c.startswith("west.path: removed") for c in changes)\n            and any(c.startswith("hale_bopp.period: removed")\n                    for c in changes)):\n        problems.append("the side changes were not each printed, with the "\n                        "drawer row\'s group: %s" % changes)\n    rows = json.loads(out)["rooms"]["solar-system"]["drawer"]["rows"]\n    if rows != [{"slug": "west", "in": "comets_hyp"},\n                {"slug": "hale_bopp", "in": "comets"}]:\n        problems.append("a drawer row was moved: %s" % rows)\n    again = mirror_plan(out, ex, today="2026-11-06")\n    if again[0] or again[2]:\n        problems.append("a second run still moves or refuses: %s %s"\n                        % (again[1], again[2]))\n    return problems\n\n\ndef side_cases():\n    # L-510: both ways, on the real mirror.\n    for p in side_problems(mo.plan):\n        check(False, "L-510: " + p)\n\n    # Planted faults: each must be caught by the same cases.\n    def no_removal(text, ex, today=None):\n        keep = mo.SIDE_FIELDS\n        mo.SIDE_FIELDS = ("open_path",)\n        try:\n            return mo.plan(text, ex, today=today)\n        finally:\n            mo.SIDE_FIELDS = keep\n\n    def no_side_fields(text, ex, today=None):\n        keep = mo.PATH_SIDE, mo.ORBIT_SIDE\n        mo.PATH_SIDE = mo.ORBIT_SIDE = (("availability", "path"),)\n        try:\n            return mo.plan(text, ex, today=today)\n        finally:\n            mo.PATH_SIDE, mo.ORBIT_SIDE = keep\n\n    def refuses_like_before(text, ex, today=None):\n        keep = mo.side_change\n        mo.side_change = lambda members, want: None\n        try:\n            return mo.plan(text, ex, today=today)\n        finally:\n            mo.side_change = keep\n\n    for name, fault in (("a mirror that removes only the mark",\n                         no_removal),\n                        ("a mirror that leaves the frame and trace",\n                         no_side_fields),\n                        ("the mirror before L-510, which refused",\n                         refuses_like_before)):\n        check(side_problems(fault),\n              "L-510: planted fault not caught: %s" % name)\n\n    # A side change over an entry set by hand is refused, and nothing in\n    # that entry is written.\n    hand = SIDE_CONFIG.replace(\'"trace_policy": "full-arc"\',\n                               \'"trace_policy": "recent"\', 1)\n    edits, _c, failures, _l = mo.plan(hand, side_export(), today="2026-11-05")\n    by = {o["slug"]: o for o in json.loads(mo.apply(hand, edits))["objects"]}\n    check(any(f.startswith("west: the orrery\'s export draws it as an orbit")\n              for f in failures) and by["west"].get("open_path") is True\n          and by["west"].get("availability") == "path",\n          "L-510: a side change over a hand-set entry was not refused, or "\n          "wrote to it: %s" % failures)\n\n\ndef real():\n    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))\n    path = os.path.join(root, mo.EXPORT)\n'),
        ('          "%d refusal(s)." % (len(linked), ", ".join(linked), len(changes),\n                              len(failures)))\n\n\ndef main():\n    cases()\n    real()\n    if FAILS:\n        print("MIRROR OBJECTS SUITE: FAIL")\n',
         '          "%d refusal(s)." % (len(linked), ", ".join(linked), len(changes),\n                              len(failures)))\n\n    # L-510: on the real config too, West moved to an orbit and Hale-Bopp\n    # to a path in a copy of the export, and the result read back.\n    if "west" in export.get("objects", {}) and \\\n            "hale_bopp" in export.get("objects", {}):\n        x = json.loads(json.dumps(export))\n        west, hale = x["objects"]["west"], x["objects"]["hale_bopp"]\n        plan_copy = west.get("path")\n        west.pop("open_path", None)\n        west["path"] = None\n        west["period"] = {"kind": "fetched", "center": "@sun", "days": 5.0e8}\n        hale["open_path"] = True\n        hale["path"] = plan_copy\n        hale["period"] = None\n        e2, c2, f2, _l2 = mo.plan(out, x, today="2026-11-05")\n        out2 = mo.apply(out, e2)\n        by2 = {o["slug"]: o for o in json.loads(out2)["objects"]}\n        check(not f2 and by2["west"].get("availability") == "analytic"\n              and "open_path" not in by2["west"]\n              and by2["hale_bopp"].get("availability") == "path"\n              and "period" not in by2["hale_bopp"]\n              and not mo.plan(out2, x, today="2026-11-06")[0],\n              "L-510: the real config did not follow West to an orbit and "\n              "Hale-Bopp to a path, or a second run still moved it: %s" % f2)\n        print("Real config, both side changes planted (West to an orbit, "\n              "Hale-Bopp to a path): %d field(s) moved, %d refusal(s)."\n              % (len(c2), len(f2)))\n    else:\n        check(False, "L-510: the real export has no West or Hale-Bopp to "\n              "plant the side changes on")\n\n\ndef main():\n    cases()\n    side_cases()\n    real()\n    if FAILS:\n        print("MIRROR OBJECTS SUITE: FAIL")\n'),
        ('          "for a body that is not one, and a mirror that drops the events "\n          "caught (L-443); a comet\'s open_path mark copied, and written for "\n          "no other body (slice 2\'s comets); JPL\'s name copied, and written "\n          "for no body without one (L-493).")\n    print("MIRROR OBJECTS SUITE: pass")\n    return 0\n\n',
         '          "for a body that is not one, and a mirror that drops the events "\n          "caught (L-443); a comet\'s open_path mark copied, and written for "\n          "no other body (slice 2\'s comets); JPL\'s name copied, and written "\n          "for no body without one (L-493); a body the orrery moves across "\n          "e = 1 followed both ways, its note rewritten and a person\'s words "\n          "kept, its drawer row left and named, a second run quiet, a "\n          "side change over a hand-set entry refused, and three planted "\n          "faults caught (L-510).")\n    print("MIRROR OBJECTS SUITE: pass")\n    return 0\n\n'),
    ]),
    ('tools/test_gallery_cache_builder_offline.py', '3efb65c06dfeb860399afc0343c862a7', '72f738c57c7ff3221783bc3b06e063e2', [
        ('    not depend on a pull: in the config as committed, a spacecraft\'s plan\n    arrives only when the objects mirror copies it from the pulled export."""\n    stand_in_drawings(config, Path(out_dir).parent)\n    return REAL_RUN_BUILD(stand_in_plans(config), out_dir, *args, **kwargs)\n\n\nSTAND_IN_PLAN = {\'made\': \'2026-07-01\',\n',
         '    not depend on a pull: in the config as committed, a spacecraft\'s plan\n    arrives only when the objects mirror copies it from the pulled export."""\n    stand_in_drawings(config, Path(out_dir).parent)\n    stand_in_orbits(config)\n    return REAL_RUN_BUILD(stand_in_plans(config), out_dir, *args, **kwargs)\n\n\n# L-510, 2026-11-05: a small body the objects mirror has just moved to an\n# orbit (the e of its orbit solution in JPL\'s small-body database below 1)\n# is asked its elements before anyone adds it to ELEMS above. It gets this\n# stand-in, never served, and is named in STAND_IN_ORBITS_USED, so the\n# night\'s run of this suite does not stop on a KeyError, as it would have\n# for piece C of C/2025 K1 without a hand-made entry.\nSTAND_IN_ORBIT = (100.0, 0.9)\nSTAND_IN_ORBITS_USED = set()\n\n\ndef stand_in_orbits(cfg):\n    for o in cfg.get(\'objects\', []):\n        hid = o.get(\'horizons_id\')\n        if (o.get(\'availability\') == \'analytic\' and not o.get(\'open_path\')\n                and o.get(\'category\') in (\'comet\', \'asteroid\', \'dwarf_planet\')\n                and hid and hid not in ELEMS):\n            ELEMS[hid] = STAND_IN_ORBIT\n            STAND_IN_ORBITS_USED.add(hid)\n\n\nSTAND_IN_PLAN = {\'made\': \'2026-07-01\',\n'),
        ('\n        # --- L-443 build B part 2: a comet on an open path is a path ---\n        paths = [s for s, o in cfg_by_slug(cfg).items() if o.get(\'open_path\')]\n        # L-510, 2026-11-04: 13 since piece C of C/2025 K1 is drawn as\n        # an orbit by JPL\'s database e. The count moves whenever a\n        # comet changes side, so the check names them.\n        check(len(paths) == 13, "L-443 part 2: the config serves 13 comets on "\n              "open paths (%d: %s)" % (len(paths), ", ".join(sorted(paths))))\n        bad = [s for s in paths if not (objs.get(s, {}).get(\'osculating\') is None\n                                        and objs.get(s, {}).get(\'positions\')\n                                        and objs.get(s, {}).get(\'open_path\') is True\n',
         '\n        # --- L-443 build B part 2: a comet on an open path is a path ---\n        paths = [s for s, o in cfg_by_slug(cfg).items() if o.get(\'open_path\')]\n        # L-510, 2026-11-05: was a fixed count (14, then 13 when piece C\n        # of C/2025 K1 became an orbit by JPL\'s database e). Since the\n        # objects mirror follows a body across e = 1 by itself, a fixed\n        # count would turn the night red on the next one, so the config\'s\n        # comets on open paths are compared with the orrery\'s export, by\n        # name.\n        export_path = cfg_path.parent / \'objects_export.json\'\n        exported = sorted(\n            s for s, o in (json.load(open(export_path, encoding=\'utf-8\'))\n                           .get(\'objects\') or {}).items()\n            if o.get(\'open_path\')) if export_path.exists() else None\n        check(paths and sorted(paths) == exported,\n              "L-443 part 2, L-510: the config serves as open paths exactly "\n              "the comets the orrery\'s export does (%d: %s; export: %s)"\n              % (len(paths), ", ".join(sorted(paths)),\n                 "not found" if exported is None else ", ".join(exported)))\n        bad = [s for s in paths if not (objs.get(s, {}).get(\'osculating\') is None\n                                        and objs.get(s, {}).get(\'positions\')\n                                        and objs.get(s, {}).get(\'open_path\') is True\n'),
        ('    path_by_plan_checks(cfg, check)\n    uncertainty_checks(cfg, check)\n    fresh_answer_checks(check)\n\n    print("\\n%s (%d checks, %d failures)"\n          % ("PASS" if not failures else "FAIL", total[0], len(failures)))\n',
         '    path_by_plan_checks(cfg, check)\n    uncertainty_checks(cfg, check)\n    fresh_answer_checks(check)\n    side_change_checks(cfg_path, check)\n\n    print("\\n%s (%d checks, %d failures)"\n          % ("PASS" if not failures else "FAIL", total[0], len(failures)))\n'),
        ('        self._ask(\'ephemerides\', kw)\n\n\ndef fresh_answer_checks(check):\n    """L-399, 2026-10-29: every question the builder asks through\n    astroquery goes to JPL, never to astroquery\'s week-long saved answers,\n',
         '        self._ask(\'ephemerides\', kw)\n\n\ndef served_side(o):\n    """L-510: how a built index serves one body: \'path\' (positions, no\n    elements, open_path), \'orbit\' (elements, no open_path), else None."""\n    if not o:\n        return None\n    if o.get(\'osculating\') is None and o.get(\'positions\') and \\\n            o.get(\'open_path\') is True:\n        return \'path\'\n    if o.get(\'osculating\') and not o.get(\'open_path\'):\n        return \'orbit\'\n    return None\n\n\ndef side_change_checks(cfg_path, check):\n    """L-510: the night survives a body moving across e = 1 both ways. The\n    orrery\'s export is changed as JPL\'s new solutions would change it (West\n    to an orbit, Hale-Bopp to a path), the objects mirror writes the\n    config from it, and that config is built and read back."""\n    import mirror_objects as mo\n    export_path = cfg_path.parent / \'objects_export.json\'\n    if not export_path.exists():\n        check(False, "L-510: no data/objects_export.json to plant the side "\n              "changes on")\n        return\n    text = cfg_path.read_text(encoding=\'utf-8\')\n    export = json.load(open(export_path, encoding=\'utf-8\'))\n    west, hale = export[\'objects\'][\'west\'], export[\'objects\'][\'hale_bopp\']\n    plan_copy = west.get(\'path\')\n    west.pop(\'open_path\', None)\n    west[\'path\'] = None\n    west[\'period\'] = {\'kind\': \'fetched\', \'center\': \'@sun\', \'days\': 5.0e8}\n    hale[\'open_path\'] = True\n    hale[\'path\'] = plan_copy\n    hale[\'period\'] = None\n    edits, changes, failures, _l = mo.plan(text, export, today=\'2026-11-05\')\n    check(not failures and any(c.startswith(\'west: drawn as an orbit now\')\n                               for c in changes)\n          and any(c.startswith(\'hale_bopp: drawn as a path now\')\n                  for c in changes),\n          "L-510: the objects mirror follows West to an orbit and Hale-Bopp "\n          "to a path, refusing nothing (%s)" % (failures or \'none refused\'))\n    with tempfile.TemporaryDirectory() as td:\n        data = Path(td) / \'data\'\n        out = data / \'solar-system\'\n        out.mkdir(parents=True)\n        flipped = data / \'objects_config.json\'\n        flipped.write_text(mo.apply(text, edits), encoding=\'utf-8\')\n        cfg2 = b.load_config(str(flipped))\n        buf = io.StringIO()\n        try:\n            with contextlib.redirect_stdout(buf):\n                rm = b.run_build(cfg2, out, mode=\'first-build\',\n                                 do_commit=False)\n            idx = json.load(open(out / \'coverage_index.json\'))\n            objs = idx[\'objects\']\n            why = rm[\'structural_validation\']\n        except Exception as exc:  # the build\'s own words, for the reader\n            print(buf.getvalue()[-2000:])\n            objs, why = {}, \'raised %s\' % exc\n        sides = (served_side(objs.get(\'west\')),\n                 served_side(objs.get(\'hale_bopp\')))\n        check(why == \'pass\' and sides == (\'orbit\', \'path\'),\n              "L-510: a config the mirror has flipped builds and passes, West "\n              "served as an orbit and Hale-Bopp as a path (%s; %s, %s)"\n              % (why, sides[0], sides[1]))\n    # The contrast, so the reading above can fail: the same test on bodies\n    # served on the other side gives the other answer.\n    check(served_side({\'osculating\': None, \'positions\': {\'2026-07-09\': {}},\n                       \'open_path\': True}) == \'path\'\n          and served_side({\'osculating\': {\'a\': 1.0}}) == \'orbit\'\n          and served_side({\'osculating\': {\'a\': 1.0}, \'open_path\': True})\n          is None,\n          "L-510: the served-side reading tells a path from an orbit, and "\n          "names a half-moved body neither")\n    print("  L-510: stand-in orbits used for bodies with none in ELEMS: %s"\n          % (", ".join(sorted(STAND_IN_ORBITS_USED)) or "none"))\n\n\ndef fresh_answer_checks(check):\n    """L-399, 2026-10-29: every question the builder asks through\n    astroquery goes to JPL, never to astroquery\'s week-long saved answers,\n'),
    ]),
]


def md5(text):
    return hashlib.md5(text.encode("ascii")).hexdigest()


def main():
    here = os.getcwd()
    if os.path.basename(here).lower() == "documentation":
        print("ERROR: run this from the website's root folder "
              "(tonyquintanilla.github.io), not from documentation\\. "
              "Nothing written.")
        return 1
    if not (os.path.exists(os.path.join("data", "objects_config.json"))
            and os.path.exists(os.path.join("tools", "mirror_objects.py"))):
        print("ERROR: this folder is not the website's root (no "
              "data\\objects_config.json or tools\\mirror_objects.py). Save "
              "the patch in tonyquintanilla.github.io and run it there. "
              "Nothing written.")
        return 1

    results = []
    for path, base_md5, after_md5, edits in TARGETS:
        full = os.path.join(*path.split("/"))
        with open(full, "rb") as handle:
            raw = handle.read()
        was_crlf = b"\r\n" in raw
        try:
            text = raw.replace(b"\r\n", b"\n").decode("ascii")
        except UnicodeDecodeError:
            text = raw.replace(b"\r\n", b"\n").decode("utf-8")
        if md5(text) == after_md5:
            results.append((full, None, "already there, identical", was_crlf))
            continue
        same_base = md5(text) == base_md5
        for number, (old, new) in enumerate(edits, 1):
            found = text.count(old)
            if found != 1:
                print("ANCHOR FAIL: %s, edit %d of %d: its text was found %d "
                      "times, not once (it begins %r). The file is not the "
                      "one this patch was built on (gallery e605f568). "
                      "Nothing written." % (path, number, len(edits), found,
                                            old.strip()[:60]))
                return 1
        for old, new in edits:
            text = text.replace(old, new, 1)
        if same_base and md5(text) != after_md5:
            print("ERROR: %s did not come out as tested. Nothing written."
                  % path)
            return 1
        note = "" if same_base else ("; it differs from gallery e605f568 "
                                     "elsewhere, so it was checked at the "
                                     "edited lines only")
        results.append((full, text, "%d edits%s" % (len(edits), note),
                        was_crlf))

    for full, text, _what, _crlf in results:
        if text is not None:
            text.encode("ascii")
    for full, text, what, was_crlf in results:
        if text is not None:
            with open(full, "wb") as handle:
                handle.write(text.encode("ascii"))
        print("ok %s (%s)" % (full, what))
        if was_crlf and text is not None:
            print("note: %s was CRLF in the working copy; written LF" % full)
    print("patch applied")

    print("")
    print("Running the mirror's tests and the builder's offline test ...")
    ok = True
    for script, last in ((os.path.join("tools", "test_mirror_objects.py"),
                          "MIRROR OBJECTS SUITE:"),
                         (os.path.join("tools",
                                       "test_gallery_cache_builder_offline.py"),
                          "checks,")):
        run = subprocess.run([sys.executable, script], capture_output=True,
                             text=True)
        lines = [l for l in run.stdout.splitlines() if last in l]
        shown = lines[-1].strip() if lines else "(no result line)"
        print("  %s: %s" % (script, shown))
        if run.returncode != 0:
            ok = False
            fails = [l for l in run.stdout.splitlines()
                     if l.startswith(" FAIL ") or l.startswith("  - ")]
            for l in fails[:10]:
                print("    " + l.strip())
            if run.stderr.strip():
                print("    " + run.stderr.strip().splitlines()[-1])
    if not ok:
        print("")
        print("A TEST FAILED. The three files are written; Discard Changes "
              "in GitHub Desktop undoes them. Paste these lines to the "
              "session.")
        return 1

    print("")
    print("Do next:")
    print("  1. (do) Move this file into documentation\\.")
    print("  2. (do) In GitHub Desktop (website): the change list shows "
          "tools\\mirror_objects.py, tools\\test_mirror_objects.py and "
          "tools\\test_gallery_cache_builder_offline.py, plus this file in "
          "documentation\\. Commit and push. Nothing under data\\ changes.")
    print("  3. Nothing else: tonight's night runs the new mirror. It "
          "prints a side change only when a body crosses e = 1.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
