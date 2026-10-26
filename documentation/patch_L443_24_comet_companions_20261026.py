r"""patch_L443_24_comet_companions_20261026.py -- a comet on an open path ticks its companions as a
spacecraft does: the farthest planet whose orbit its path has reached so
far, up to the minute shown (Tony, Oct 26, at his phone look: "i thought
we were adding the farthest planetary orbit for perspective?", then "so
far"). And the builder suite's span check reads the comet's own plan
(L-443).

Built on gallery dd9d0faecd4fa9a8f5a433165681fdccf35a1748 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch
main), with orrery 140db0ae0ff05badc17b85fc7c214d36505ace32 at
https://github.com/tonylquintanilla/palomas_orrery.

WHAT IT EDITS, all or nothing

    interactive.html: the Solar System room's driver works out a comet's
        reach from its served points up to the minute shown (a
        spacecraft's stays its whole path, JPL's predicted part
        included), and the room ticks each comet's companions: West,
        McNaught, 'Oumuamua and 2I/Borisov tick Pluto; 3I/ATLAS Saturn;
        the rest Jupiter. The change note.
    tools/headless/walk_solar_system_drawer.js: ticking West ticks Pluto
        before it; Go To on 3I/ATLAS ticks Saturn and not Uranus.
    tools/test_gallery_cache_builder_offline.py: the span check reads
        the comet's own plan's span. It had typed the stand-in's dates,
        which is why the Cache builder suite was red in today's Daily
        Run with the builder right.

    No data changes, so no build is needed: the page reaches a visitor
    on the push.

HOW TO RUN

    Save it in the website folder (tonyquintanilla.github.io), open it
    in VS Code and press Run. It prints an "ok" line per file and "patch
    applied"; a second run refuses. Then gallery_maintenance_run.py,
    which should be green; move this file into documentation\, commit
    and push. Undo before a commit is Discard Changes in GitHub Desktop.

Written October 26, 2026 with Anthropic's Claude Opus 5.5.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DONE = "patch applied: a comet's planets so far, Oct 26 (%d files edited, %d new)"
EDITS = [('interactive.html', [("        class name explained in plain words, from its row's about, first\n        in the text box and the panel of every body in it; a comet's\n        perihelion explained in its span sentence.)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n", '        class name explained in plain words, from its row\'s about, first\n        in the text box and the panel of every body in it; a comet\'s\n        perihelion explained in its span sentence. Evening, at Tony\'s phone\n        look: a comet on an open path ticks its companions as a spacecraft\n        does, the farthest planet its path has reached so far, Tony\'s\n        "so far"; the dashed year ahead does not count.)\n     Architecture: Option C viewer (master plan v8 Section 2a)\n       - index.html serves curated gallery cards (unchanged)\n'), ('    return _out\n\ndef _path_reach_au(_p):\n    _d = (_p or {}).get("data") or {}\n    _x, _y, _z = _d.get("x") or [], _d.get("y") or [], _d.get("z") or []\n    _n = min(len(_x), len(_y), len(_z))\n    if not _n:\n        return None\n    from assembler.render_spacecraft import AU_KM as _AU_KM\n    return max((_x[_i] ** 2 + _y[_i] ** 2 + _z[_i] ** 2) ** 0.5\n               for _i in range(_n)) / _AU_KM\n\n_served = {}\n', '    return _out\n\n# L-443, 2026-10-26 (Tony, for a comet on an open path: "so far"): a\n# comet\'s reach counts only the served points up to the moment shown,\n# since its dashed year ahead is a drawing choice, not JPL\'s plan; a\n# spacecraft\'s counts its whole path, JPL\'s predicted part included.\ndef _path_reach_au(_p, _until_jd=None):\n    _d = (_p or {}).get("data") or {}\n    _x, _y, _z = _d.get("x") or [], _d.get("y") or [], _d.get("z") or []\n    _t = _d.get("t") or []\n    _n = min(len(_x), len(_y), len(_z))\n    _keep = [_i for _i in range(_n)\n             if _until_jd is None or (_i < len(_t) and _t[_i] <= _until_jd)]\n    if not _keep:\n        return None\n    from assembler.render_spacecraft import AU_KM as _AU_KM\n    return max((_x[_i] ** 2 + _y[_i] ** 2 + _z[_i] ** 2) ** 0.5\n               for _i in _keep) / _AU_KM\n\n_served = {}\n'), ('        # plan (the config\'s copy of the orrery\'s).\n        # L-443 build B part 2: a comet on an open path is drawn from its\n        # served positions too, kind "comet_path"; it names no companions.\n        "kind": ("spacecraft" if _rec.get("category") == "spacecraft"\n                 else "comet_path" if _rec.get("open_path") else None),\n', '        # plan (the config\'s copy of the orrery\'s).\n        # L-443 build B part 2: a comet on an open path is drawn from its\n        # served positions too, kind "comet_path". It ticks companions as a\n        # spacecraft does (Tony, 2026-10-26, at his phone look: "i thought\n        # we were adding the farthest planetary orbit for perspective?"),\n        # the farthest planet its path has reached so far.\n        "kind": ("spacecraft" if _rec.get("category") == "spacecraft"\n                 else "comet_path" if _rec.get("open_path") else None),\n'), ('                      .get("backbone") or {}).get("step"),\n        "path_events": (_path_events(_objs.get(_slug) or {})\n                        if _rec.get("category") == "spacecraft" else None),\n        "path_reach_au": (_path_reach_au(_pos.get(_slug))\n                          if _rec.get("category") == "spacecraft" else None),\n    }\n\n', '                      .get("backbone") or {}).get("step"),\n        "path_events": (_path_events(_objs.get(_slug) or {})\n                        if (_rec.get("category") == "spacecraft"\n                            or _rec.get("open_path")) else None),\n        "path_reach_au": (_path_reach_au(_pos.get(_slug))\n                          if _rec.get("category") == "spacecraft"\n                          else _path_reach_au(_pos.get(_slug),\n                                              result.context.resolved_epoch_jd)\n                          if _rec.get("open_path") else None),\n    }\n\n'), ('            for (const row of rows) {\n                const b = bodies[row.slug];\n                if (!b || b.kind !== "spacecraft") { continue; }\n                const c = SSD.companions(\n                    { events: b.path_events || [], reach_au: b.path_reach_au },\n', '            for (const row of rows) {\n                const b = bodies[row.slug];\n                if (!b || (b.kind !== "spacecraft" && b.kind !== "comet_path")) { continue; }\n                const c = SSD.companions(\n                    { events: b.path_events || [], reach_au: b.path_reach_au },\n')]), ('tools/headless/walk_solar_system_drawer.js', [('// 3I/ATLAS\'s whole path, and Reset. Later that day: each group\'s class\n// explained, first in West\'s text box and panel, and the perihelion in\n// its span sentence.\nconst h = require("./page_harness.js");\nfunction solarDay(jd) {\n', '// 3I/ATLAS\'s whole path, and Reset. Later that day: each group\'s class\n// explained, first in West\'s text box and panel, and the perihelion in\n// its span sentence. Evening: a comet ticks the farthest planet its path\n// has reached so far, West Pluto and 3I/ATLAS Saturn (Tony: "so far").\nconst h = require("./page_harness.js");\nfunction solarDay(jd) {\n'), ('       "West\'s two parts do not meet at its marker");\n    ok(mk && mk.marker && mk.marker.symbol === "diamond", "West\'s marker is not a comet\'s diamond");\n    ok(order() === "earth,west" && !E("ssDrawer.companions.west"),\n       "ticking West ticked something else: " + order());\n    const wl = mk.text[0].split(/<br[^>]*>/);\n    const joined = wl.join(" ").replace(/<br soft>/g, " ");\n', '       "West\'s two parts do not meet at its marker");\n    ok(mk && mk.marker && mk.marker.symbol === "diamond", "West\'s marker is not a comet\'s diamond");\n    // L-443, 2026-10-26 (Tony: "so far"): a comet ticks the farthest\n    // planet its path has reached up to the minute shown. West\'s has\n    // gone past Pluto\'s orbit.\n    ok(order() === "earth,pluto_barycenter,west" &&\n       E("JSON.stringify(ssDrawer.companions.west)") === \'["pluto_barycenter"]\',\n       "ticking West did not tick Pluto before it: order " + order() + ", companions " +\n       E("JSON.stringify(ssDrawer.companions.west)"));\n    const wl = mk.text[0].split(/<br[^>]*>/);\n    const joined = wl.join(" ").replace(/<br soft>/g, " ");\n'), ('    await click(row("atlas_3i").querySelector(".go"));\n    ok(near(range(), wholeR("atlas_3i")), "GO 3I/ATLAS frame " + range() + " vs its whole path " + wholeR("atlas_3i"));\n    await click(d.getElementById("sun-drawer-all"));\n    ok(order() === "earth" && !E("ssDrawer.folds.comets_hyp") && !E("ssDrawer.folds.interstellar"),\n', '    await click(row("atlas_3i").querySelector(".go"));\n    ok(near(range(), wholeR("atlas_3i")), "GO 3I/ATLAS frame " + range() + " vs its whole path " + wholeR("atlas_3i"));\n    // So far, not the whole drawn path: 3I/ATLAS has passed Saturn\'s\n    // orbit, and its dashed year ahead, which reaches past Uranus\'s\n    // perihelion, does not count.\n    ok(shown("saturn") && !shown("uranus") &&\n       E("JSON.stringify(ssDrawer.companions.atlas_3i)") === \'["saturn"]\',\n       "Go To on 3I/ATLAS did not tick Saturn alone: companions " +\n       E("JSON.stringify(ssDrawer.companions.atlas_3i)"));\n    await click(d.getElementById("sun-drawer-all"));\n    ok(order() === "earth" && !E("ssDrawer.folds.comets_hyp") && !E("ssDrawer.folds.interstellar"),\n')]), ('tools/test_gallery_cache_builder_offline.py', [('span and no further, and one with no plan is named and not fetched. The\ntrust checks hold every comet on an open path as they hold a spacecraft.)\n"""\nimport contextlib\n', 'span and no further, and one with no plan is named and not fetched. The\ntrust checks hold every comet on an open path as they hold a spacecraft.)\nModule updated: October 26, 2026, evening, with Anthropic\'s Claude Opus 5.5\n(L-443: the span check reads the comet\'s own plan\'s span, the config\'s\nonce the mirror has copied the orrery\'s plan; it had typed the stand-in\'s\ndates and failed on the first real plans.)\n"""\nimport contextlib\n'), ('              "carried (%s)" % (", ".join(bad) or "all 14"))\n        if paths:\n            raw_w = sorted(b.load_raw_vectors(out, paths[0])[\'points\'])\n            span_ok = (raw_w and raw_w[0] >= \'2025-01-15\'\n                       and raw_w[-1] <= \'2027-07-09 23:59\')\n            check(span_ok, "L-443 part 2: %s\'s path is fetched inside its "\n                  "plan\'s span, nothing extended (%s to %s)"\n                  % (paths[0], raw_w[0] if raw_w else None,\n                     raw_w[-1] if raw_w else None))\n        probe = dict(cfg_by_slug(cfg)[paths[0]]) if paths else {}\n', '              "carried (%s)" % (", ".join(bad) or "all 14"))\n        if paths:\n            # The comet\'s own plan\'s span: the config\'s, once the mirror has\n            # copied the orrery\'s plan, else the suite\'s stand-in. FIXED: the\n            # stand-in\'s dates were typed here, so the check failed on Tony\'s\n            # machine the day the real plans arrived (2026-10-26), with the\n            # builder right (West\'s plan runs from 1975).\n            span = ((cfg_by_slug(cfg)[paths[0]].get(\'path\') or\n                     STAND_IN_COMET_PLAN)[\'span\'])\n            raw_w = sorted(b.load_raw_vectors(out, paths[0])[\'points\'])\n            span_ok = (raw_w and raw_w[0] >= span[\'start\']\n                       and raw_w[-1] <= span[\'end\'] + \' 23:59\')\n            check(span_ok, "L-443 part 2: %s\'s path is fetched inside its "\n                  "plan\'s span, %s to %s, nothing extended (%s to %s)"\n                  % (paths[0], span[\'start\'], span[\'end\'],\n                     raw_w[0] if raw_w else None,\n                     raw_w[-1] if raw_w else None))\n        probe = dict(cfg_by_slug(cfg)[paths[0]]) if paths else {}\n')])]
NEW_FILES = []
SENTINELS = {'interactive.html': "        perihelion explained in its span sentence. Evening, at Tony's phone", 'tools/headless/walk_solar_system_drawer.js': '// its span sentence. Evening: a comet ticks the farthest planet its path', 'tools/test_gallery_cache_builder_offline.py': "Module updated: October 26, 2026, evening, with Anthropic's Claude Opus 5.5"}
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
