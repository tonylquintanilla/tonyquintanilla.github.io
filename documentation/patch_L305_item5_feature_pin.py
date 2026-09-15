"""Move the Feature renderers pin: the magnetosphere has a renderer now.

Target: documentation/smoke_features.js  (gallery repo)
Built against gallery c2155b4525c7a27716abde3926ec7da376d31675.
Handle: L-305 item 5 follow-up.  2026-09-15, with Anthropic's Claude Opus 5.

THE GATE IS RED AND THIS TURNS IT GREEN.

One leg asserted that Earth reports exactly one group with NO RENDERER, the
magnetosphere, by name.  L-305 item 5 gave it a renderer on 2026-09-15, so
that leg can never pass again.  The comment above it had said, since L-291,
that this pin moves in the same commit as the renderer.  It did not, because
I ran smoke_earth_geometry.js and never ran this one.

WHAT IT NOW ASSERTS
-------------------
The DEGRADED path, which is what this harness actually exercises.  It calls
buildFeatureTraces with no opts, so no Sun direction reaches the renderer.
The magnetopause and the bow shock are surfaces of revolution about the Sun
line, so saying so and drawing nothing is the only honest answer -- one
aimed at a fixed axis would be wrong on every day of the year but one, and
would look entirely plausible.  That puts the leg in the same family as the
missing-pole and missing-planet_radius legs below it.

A second leg is added: no magnetosphere trace is emitted in that state.

The DRAWN surfaces are checked in smoke_earth_geometry.js, which composes
through earth_geometry.js and therefore has a Sun direction.

A gate that fails every run on a stale expectation is the alarm nobody
reads.  That is what let the white-outline finding be waved off twice.

AFTER RUNNING
-------------
  node documentation/smoke_features.js gallery/feature_renderers.js
  Expect ALL CHECKS PASSED.

UNDO: Discard Changes on documentation/smoke_features.js in GitHub Desktop."""

import hashlib
import os
import sys

FINGERPRINTS = {'documentation/smoke_features.js': '0237c412f84e3626a2ccf073bdc975a4'}

EDITS = [
    ('documentation/smoke_features.js', [
        (b"""// L-291: Earth's entry is in the measured shape. Two groups have no renderer
// yet (earth_geostationary, earth_magnetosphere) and the dispatch must SAY
// so, by name -- those two warnings are expected and nothing else is.
// L-291 step 3: the geostationary ring draws now. The magnetosphere stays a
// NAMED expected absence until L-305 rebuilds it on a sourced model; this
// pin moves in the same commit as that renderer.
const expectedWarn = ["earth/earth_magnetosphere"];
check("earth reports exactly one no-renderer group, the magnetosphere, by name",""",
         b"""// L-291: Earth's entry is in the measured shape. Two groups had no renderer
// (earth_geostationary, earth_magnetosphere) and the dispatch had to SAY so
// by name. Step 3 gave the geostationary ring one. L-305 item 5 gave the
// magnetosphere one on 2026-09-15, and this pin moves with it, exactly as
// the comment that used to sit here said it would.
//
// What is asserted now is the DEGRADED path, which is what this harness
// exercises: buildFeatureTraces is called with no opts, so no Sun direction
// reaches the renderer. The magnetopause and the bow shock are surfaces of
// revolution about the Sun line, so drawing nothing and saying why is the
// only honest answer -- a magnetosphere aimed at a fixed axis would be
// wrong on every day of the year but one and would look plausible. Same
// family as the missing-pole and missing-planet_radius legs below.
// The drawn surfaces are checked in smoke_earth_geometry.js, which composes
// through earth_geometry.js and therefore HAS a Sun direction.
check("earth's magnetosphere reports the missing Sun direction and draws nothing","""),
        (b"""      expectedWarn.every(k => r1.warnings.some(w => w.indexOf(k) === 0 && /no renderer/.test(w))),""",
         b"""      r1.warnings[0].indexOf("earth/earth_magnetosphere") === 0 &&
      /no Sun direction reached the renderer/.test(r1.warnings[0]),"""),
        (b"""      r1.warnings.join(" | "));
const geo1 = r1.traces.filter(t => t.showlegend === true);""",
         b"""      r1.warnings.join(" | "));
check("...and no magnetosphere trace is emitted in that state",
      r1.traces.every(t => !/Magnetopause|Bow Shock/.test(t.name || "")),
      r1.traces.filter(t => /Magnetopause|Bow Shock/.test(t.name || "")).length + " emitted");
const geo1 = r1.traces.filter(t => t.showlegend === true);"""),
    ]),
]

GUARD = [('documentation/smoke_features.js', 'missing Sun direction and draws nothing')]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    files = {}
    for path, expected in FINGERPRINTS.items():
        if not os.path.isfile(path):
            print("FAILURE: %s not found. Run this from the gallery repo root."
                  % path)
            print("NOTHING was written.")
            return 1
        with open(path, "rb") as handle:
            files[path] = handle.read()
        actual = content_md5(files[path])
        if actual != expected:
            print("FAILURE: BASE MOVED for %s." % path)
            print("  expected content md5 %s" % expected)
            print("  found                %s" % actual)
            print("  This patch is built against gallery c2155b45.")
            print("NOTHING was written.")
            return 1

    for path, needle in GUARD:
        if needle.encode("utf-8") in files[path]:
            print("FAILURE: this patch is already applied (%s in %s)."
                  % (needle, path))
            print("NOTHING was written.")
            return 1

    crlf = {p: files[p].count(b"\r\n") > 0 for p in files}

    def fit(path, block):
        return block.replace(b"\n", b"\r\n") if crlf[path] else block

    for path, edits in EDITS:
        staged = files[path]
        for n, (old, new) in enumerate(edits):
            count = staged.count(fit(path, old))
            if count != 1:
                print("FAILURE: in %s, hunk %d matched %d times, expected 1."
                      % (path, n + 1, count))
                print("NOTHING was written.")
                return 1
            staged = staged.replace(fit(path, old), fit(path, new))
        files[path] = staged

    for path in sorted(files):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: %d file(s) written." % len(files))
    for path in sorted(files):
        print("    %-42s (%s)" % (path, "CRLF" if crlf[path] else "LF"))
    print()
    print("Next: node documentation/smoke_features.js gallery/feature_renderers.js")
    return 0


if __name__ == "__main__":
    sys.exit(main())
