"""
patch_L510_2_orbit_body_drops_future_points.py -- the website's nightly
builder no longer stops on a body that used to be drawn as a path and
is now drawn as an orbit (L-510 (the typed fields stop deciding)).

Built on gallery e5352a86814b45d50319b5de06b975d133a73b9a at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
45433fd at https://github.com/tonylquintanilla/palomas_orrery (branch
main), both read live on Nov 5, 2026, 09:10 Chicago. Written by the
coordinating session (Claude Opus 5.5). Follows
patch_L510_1_piece_c_orbit_website.py, which ran and was pushed at
e5352a86.

WHY

    The manual night of Nov 5 (14:54 UTC) passed its pulls -- patch 1
    did its job -- and then the builder stopped: "[ABORT] #T c2025_k1_c:
    as_of_today.t not within 48h of generated -- no swap, no commit".
    For a body drawn as an orbit, the builder takes the newest saved
    position as today's. Piece C's saved positions
    (data/solar-system/raw/vectors/c2025_k1_c.json) were left from its
    days as a path, fetched by its plan out to 2027-10-19, so its
    "today" was eleven months ahead. A comet drawn as an orbit keeps a
    few days (Hale-Bopp's file holds days, not years).

    The served data is never edited by hand (the website's CLAUDE.md),
    so the builder does it, by rule, and says so: a body that is not
    drawn as a path keeps no saved position dated after today. This
    also covers the next comet that changes side, which Tony's ruling of
    Nov 4, 23:47 Chicago asks for: "the website should follow the same
    rule as the orrery, based on eccentricity."

WHAT IT CHANGES (two files)

    tools/gallery_cache_builder.py
      - for a body that is not a path, after tonight's positions are
        added: every saved position dated after today is dropped, with
        the plan's old stamps (plan_made, plan_span), and one warning
        names the body and the count. A path (a spacecraft, a comet on
        an open path) keeps its predicted future, as before.
      - its Module updated stamp.

    tools/test_gallery_cache_builder_offline.py, which the night runs
      - before its nightly re-run, plants a saved position a year ahead
        and an old plan stamp in Hale-Bopp's saved file; after it,
        checks that both are gone, the warning named Hale-Bopp, and the
        night passed. Without the builder's edit the planted position
        stops the re-run, so the check can fail.
      - its Module updated stamp.

    Checked only at the lines it edits. A file that already holds the
    result is accepted and reported, not refused.

RUN COMMAND

    Save this file in the website's root folder
    (tonyquintanilla.github.io), open it in VS Code and click Run.
    (python patch_L510_2_orbit_body_drops_future_points.py)

    Success: one "ok" line per edit, then "patch applied". Failure: one
    ERROR or ANCHOR FAIL line, and nothing is written. Undo is Discard
    Changes in GitHub Desktop.

    Then move this file into documentation\\, commit and push the
    website, and run the night again from the Actions tab.

Written November 5, 2026 with Anthropic's Claude Opus 5.5.
"""

import os
import sys

BUILDER = os.path.join("tools", "gallery_cache_builder.py")
TEST = os.path.join("tools", "test_gallery_cache_builder_offline.py")

BUILDER_EDITS = [
    ("future positions dropped for a body that is not a path",
     b"        points.update(new)  # overwrite-by-date on the refresh window; past frozen\n"
     b"        run_manifest['objects'][slug] = ('backfilled(%d)' % len(new)\n"
     b"                                         if mode == 'first-build' else 'nightly(%d)' % len(new))\n",
     b"        points.update(new)  # overwrite-by-date on the refresh window; past frozen\n"
     b"        run_manifest['objects'][slug] = ('backfilled(%d)' % len(new)\n"
     b"                                         if mode == 'first-build' else 'nightly(%d)' % len(new))\n"
     b"        # L-510 (2026-11-05): a body that is not drawn as a path keeps no\n"
     b"        # saved position after today. One that was a path (piece C of\n"
     b"        # C/2025 K1, drawn as an orbit by JPL's database e since Nov 4)\n"
     b"        # still held its plan's predicted future, its newest point was\n"
     b"        # taken as today's, and #T stopped the night. Dropped by rule\n"
     b"        # and named, never by hand.\n"
     b"        upto_jd = _dt_to_jd(today) + 0.5\n"
     b"        future = [day for day, pt in points.items() if pt['jd'] > upto_jd]\n"
     b"        for day in future:\n"
     b"            del points[day]\n"
     b"        stamps = [s for s in ('plan_made', 'plan_span') if s in raw]\n"
     b"        for stamp in stamps:   # not k: guard_monitor below needs it\n"
     b"            del raw[stamp]\n"
     b"        if future or stamps:\n"
     b"            warn(\"%s: drawn as an orbit, not a path; %d saved position(s) \"\n"
     b"                 \"after today dropped%s\" % (slug, len(future),\n"
     b"                 \", and its old plan's stamps\" if stamps else \"\"))\n"),
    ("Module updated stamp",
     b"day the mission ended, not up to six days short at the 7-day backbone.)\n\"\"\"",
     b"day the mission ended, not up to six days short at the 7-day backbone.)\n"
     b"Module updated: November 5, 2026 with Anthropic's Claude Opus 5.5 (L-510:\n"
     b"a body that is not drawn as a path keeps no saved position after today;\n"
     b"one left from its days as a path is dropped and named, with its old\n"
     b"plan's stamps. Piece C of C/2025 K1, drawn as an orbit by JPL's\n"
     b"database e since Nov 4, had stopped the night on #T.\n"
     b"patch_L510_2_orbit_body_drops_future_points.py.)\n\"\"\""),
]

TEST_EDITS = [
    ("planted future position in Hale-Bopp's saved file",
     b"        old_pt = earth_before[old_date]\n"
     b"        _said_449 = io.StringIO()\n",
     b"        old_pt = earth_before[old_date]\n"
     b"        # L-510 (2026-11-05): an orbit body left with a saved position\n"
     b"        # a year ahead, and an old plan's stamp, as piece C of C/2025 K1\n"
     b"        # was. The nightly drops both and names it; without that the\n"
     b"        # planted point is taken as today's and #T stops the re-run.\n"
     b"        _hb_path = out / 'raw' / 'vectors' / 'hale_bopp.json'\n"
     b"        _hb = json.load(open(_hb_path))\n"
     b"        _hb_last = _hb['points'][sorted(_hb['points'])[-1]]\n"
     b"        _hb['points']['2099-01-01'] = dict(_hb_last, jd=_hb_last['jd'] + 365.0)\n"
     b"        _hb['plan_made'] = '2026-10-26'\n"
     b"        json.dump(_hb, open(_hb_path, 'w'))\n"
     b"        _said_449 = io.StringIO()\n"),
    ("checks after the nightly re-run",
     b"        check(earth_after.get(old_date) == old_pt, \"frozen past point unchanged byte-for-byte\")\n",
     b"        check(earth_after.get(old_date) == old_pt, \"frozen past point unchanged byte-for-byte\")\n"
     b"        _hb_after = json.load(open(_hb_path))\n"
     b"        check('2099-01-01' not in _hb_after['points']\n"
     b"              and 'plan_made' not in _hb_after,\n"
     b"              \"L-510: an orbit body's saved position after today, and its \"\n"
     b"              \"old plan's stamp, are dropped (hale_bopp, planted)\")\n"
     b"        check(\"hale_bopp: drawn as an orbit, not a path; 1 saved position(s) \"\n"
     b"              \"after today dropped\" in _said_449.getvalue(),\n"
     b"              \"L-510: the drop is named (hale_bopp)\")\n"),
    ("Module updated stamp",
     b"open paths 13, named. patch_L510_1_piece_c_orbit_website.py.)\n\"\"\"",
     b"open paths 13, named. patch_L510_1_piece_c_orbit_website.py.)\n"
     b"Module updated: November 5, 2026 with Anthropic's Claude Opus 5.5\n"
     b"(L-510: a saved position a year ahead and an old plan's stamp planted\n"
     b"in Hale-Bopp's file before the nightly re-run; both dropped and named.\n"
     b"patch_L510_2_orbit_body_drops_future_points.py.)\n\"\"\""),
]


def plan(path, edits):
    """(ok, new bytes or None, was_crlf). None when already applied."""
    if not os.path.isfile(path):
        print("ERROR: %s not found. Run this from the website's root folder "
              "(tonyquintanilla.github.io). Nothing was written." % path)
        return False, None, False
    raw = open(path, "rb").read()
    was_crlf = b"\r\n" in raw
    text = raw.replace(b"\r\n", b"\n")
    if all(text.count(new) == 1 for _, _, new in edits):
        print("already there, identical: %s" % path)
        return True, None, was_crlf
    for label, old, new in edits:
        n = text.count(old)
        if n != 1:
            print("ANCHOR FAIL: %s in %s -- expected 1 match, found %d. "
                  "Nothing was written." % (label, path, n))
            return False, None, was_crlf
        text = text.replace(old, new)
        print("ok %s" % label)
    if any(c > 127 for c in text):
        print("ERROR: %s would hold non-ASCII bytes. Nothing was written."
              % path)
        return False, None, was_crlf
    return True, text, was_crlf


def main():
    results = []
    for path, edits in ((BUILDER, BUILDER_EDITS), (TEST, TEST_EDITS)):
        ok, out, was_crlf = plan(path, edits)
        if not ok:
            return 1
        results.append((path, len(edits), out, was_crlf))
    wrote = False
    for path, n, out, was_crlf in results:
        if out is None:
            continue
        with open(path, "wb") as f:
            f.write(out)
        wrote = True
        if was_crlf:
            print("note: %s was CRLF in the working copy; written LF" % path)
        print("ok %s (%d edits)" % (path, n))
    print("patch applied" if wrote else "Nothing to do.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
