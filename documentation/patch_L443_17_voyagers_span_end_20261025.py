r"""patch_L443_17_voyagers_span_end_20261025.py -- the Voyagers' paths fetched
to JPL's last minute, and Voyager 1 gold (L-443).

Built on gallery 191d68fa05f70097377fad4545d4e2cb753ebabe at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main).

WHAT IT FIXES

    Your Daily Run of Oct 25: JPL refused both Voyagers' paths ("No
    ephemeris ... after A.D. 2100-JAN-01 00:00"). Their data ends at that
    minute exactly, and the builder adds 69 seconds to every time it asks
    JPL (UTC to JPL's time), so it asked for one minute too many. The
    builder now stops at JPL's last minute exactly. Its suite gains a
    check and a planted fault (436 checks).

    Voyager 1's path and marker are goldenrod, as Parker's are, by your
    choice: the white path did not show against the white grid.

WHAT IT EDITS

    tools/gallery_cache_builder.py, tools/test_gallery_cache_builder_offline.py,
    gallery/assembler/presentation.py.

HOW TO RUN

    Open it in VS Code and press Run. It prints an "ok" line per file,
    then "patch applied". All or nothing; a second run refuses. Then the
    dashboard's Daily Run.

Written October 25, 2026 with Anthropic's Claude Opus 5.5.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DONE = "patch applied: the Voyagers to JPL's last minute, Oct 25 (%d files edited, %d new)"
EDITS = [('tools/gallery_cache_builder.py', [("\ndef _plan_span(plan):\n    span = plan.get('span') or {}\n    return _parse_calendar(span['start']), _parse_calendar(span['end'])\n\n\n", '\ndef _plan_span(plan):\n    """(start, end) of a plan\'s span, as instants this builder asks for.\n\n    The span\'s dates are JPL\'s own, read from its answer, in JPL\'s time\n    (TDB), and fetch_vectors_range adds utc_to_tdb\'s 69 s to every time it\n    asks. So the end is taken back by the same 69 s, and the stop JPL is\n    asked for is exactly the span\'s end, never past it. FIXED, L-443,\n    2026-10-25: the Voyagers\' data ends at 2100-01-01 00:00 TDB to the\n    minute, the stop asked was 00:01, and JPL refused both paths ("No\n    ephemeris for target ... after A.D. 2100-JAN-01 00:00:00.0000 TD").\n    The other ten end later in their last day, so the minute did not\n    show."""\n    span = plan.get(\'span\') or {}\n    end = _parse_calendar(span[\'end\'])\n    return _parse_calendar(span[\'start\']), end - (utc_to_tdb(end) - end)\n\n\n')]), ('tools/test_gallery_cache_builder_offline.py', [('                  "L-443 build B: the raw archive records the plan it was "\n                  "fetched by")\n            # the same plan, a night later: only the tail\n            del calls[:]\n', '                  "L-443 build B: the raw archive records the plan it was "\n                  "fetched by")\n            # FIXED 2026-10-25: JPL refuses a stop past the end of its data,\n            # and its span\'s end is in its own time, so no stop asked, once\n            # utc_to_tdb has added its 69 s, may pass the span\'s end\n            span_end = b._parse_calendar(\'2099-12-31\')\n            past = [c_ for c_ in calls if c_[0] == \'-31\'\n                    and b.utc_to_tdb(c_[2]) > span_end]\n            check(not past and any(b.utc_to_tdb(c_[2]) == span_end\n                                   for c_ in calls if c_[0] == \'-31\'),\n                  "L-443 build B: the stop JPL is asked for is the span\'s "\n                  "end exactly, never past it (%d stop(s) past it)" % len(past))\n            real_span = b._plan_span\n            b._plan_span = lambda p: (b._parse_calendar(p[\'span\'][\'start\']),\n                                      b._parse_calendar(p[\'span\'][\'end\']))\n            del calls[:]\n            try:\n                b.fetch_path_by_plan(\n                    dict(c1[\'objects\'][[o.get(\'slug\') for o in c1[\'objects\']]\n                                       .index(\'voyager_1\')],\n                         horizons_id=\'-31\', id_type=\'id\',\n                         canonical_center=\'@10\', slug=\'voyager_1\'),\n                    [o for o in c1[\'objects\']\n                     if o.get(\'slug\') == \'voyager_1\'][0][\'path\'],\n                    FIXED_NOW, 7, lambda m: None)\n            finally:\n                b._plan_span = real_span\n            check(any(b.utc_to_tdb(c_[2]) > span_end for c_ in calls),\n                  "L-443 build B: planted fault caught -- the span\'s end "\n                  "taken as it stands asks JPL past the end of its data, as "\n                  "the Voyagers\' first build did")\n            # the same plan, a night later: only the tail\n            del calls[:]\n')]), ('gallery/assembler/presentation.py', [("\nModule updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,\nbuild B: the twelve spacecraft's colours, the orrery's.)\n\nRole: rendering\n", "\nModule updated: October 25, 2026 with Anthropic's Claude Opus 5.5 (L-443,\nbuild B: the twelve spacecraft's colours, the orrery's; later the same\nday Voyager 1 goldenrod, by Tony's phone look.)\n\nRole: rendering\n"), ('    # orrery 0c27f47). Voyager 1\'s was #ff6f61 here, a choice of this file;\n    # it takes the orrery\'s now. A first choice for Tony\'s phone look.\n    "voyager_1": "white",\n    "voyager_2": "magenta",\n    "new_horizons": "cyan",\n', '    # orrery 0c27f47). Voyager 1\'s was #ff6f61 here, a choice of this file;\n    # it takes the orrery\'s now. A first choice for Tony\'s phone look.\n    # Voyager 1 is goldenrod, not the orrery\'s white, by Tony\'s phone look\n    # of 2026-10-25: a white path "does not contrast with the white grid";\n    # asked whether to share Parker\'s gold, he chose "Gold, like Parker".\n    "voyager_1": "goldenrod",\n    "voyager_2": "magenta",\n    "new_horizons": "cyan",\n')])]
NEW_FILES = []
SENTINELS = {'tools/gallery_cache_builder.py': "    (TDB), and fetch_vectors_range adds utc_to_tdb's 69 s to every time it", 'tools/test_gallery_cache_builder_offline.py': '                  "end exactly, never past it (%d stop(s) past it)" % len(past))', 'gallery/assembler/presentation.py': "    # Voyager 1 is goldenrod, not the orrery's white, by Tony's phone look"}
POST_CALLS = []


def fail(msg):
    print(msg)
    print("NOTHING was written. Undo is not needed.")
    sys.exit(1)


def main():
    same_new = set()
    for rel, content in NEW_FILES:
        full = os.path.join(HERE, *rel.split("/"))
        if os.path.exists(full):
            have = open(full, "rb").read().replace(b"\r\n", b"\n")
            if have == content.encode("utf-8"):
                same_new.add(rel)
                continue
            fail("ERROR: %s already exists and differs from what this patch "
                 "writes. Most likely a copy of the same document saved from "
                 "a download or an attachment: delete it and run this patch "
                 "again." % rel)
    staged = []
    for rel, edits in EDITS:
        path = os.path.join(HERE, *rel.split("/"))
        if not os.path.isfile(path):
            fail("ERROR: not found: %s -- is this file in the right folder?"
                 % path)
        raw = open(path, "rb").read()
        crlf = b"\r\n" in raw
        text = raw.replace(b"\r\n", b"\n").decode("utf-8")
        if SENTINELS.get(rel) and SENTINELS[rel] in text:
            fail("ERROR: %s already carries this patch's change; this "
                 "patch has run." % rel)
        for k, (old, new) in enumerate(edits):
            n = text.count(old)
            if n != 1:
                if new and text.count(new) == 1 and old not in text:
                    fail("ERROR: %s already carries edit %d of %d; this "
                         "patch has run." % (rel, k + 1, len(edits)))
                fail("ANCHOR FAIL in %s, edit %d of %d: expected 1 match, "
                     "found %d" % (rel, k + 1, len(edits), n))
            text = text.replace(old, new)
        staged.append((rel, path, text, crlf, len(edits)))
    for rel, path, text, crlf, n in staged:
        open(path, "wb").write(text.encode("utf-8"))
        print("ok  %s (%d edits)" % (rel, n))
        if crlf:
            print("note: %s was CRLF in the working copy; written LF" % rel)
        bad = sum(1 for c in text if ord(c) > 127)
        if bad:
            print("note: %s holds %d non-ASCII character(s) this patch did "
                  "not add" % (rel, bad))
    for rel, content in NEW_FILES:
        full = os.path.join(HERE, *rel.split("/"))
        if rel in same_new:
            print("ok  %s: already there, identical" % rel)
            continue
        d = os.path.dirname(full)
        if d and not os.path.isdir(d):
            os.makedirs(d)
        open(full, "wb").write(content.encode("utf-8"))
        print("ok  %s: new" % rel)
    for name in POST_CALLS:
        for line in globals()[name](HERE):
            print(line)
    print(DONE % (len(staged), len(NEW_FILES)))


if __name__ == "__main__":
    main()
