#!/usr/bin/env python3
"""
patch_L342_1_served_figures_formatter_20260919.py -- GALLERY repo.

Run: save this file in the GALLERY repo ROOT (next to index.html), open
it in VS Code and click Run.  Or:
python patch_L342_1_served_figures_formatter_20260919.py

A patch is run from its repository's ROOT and filed in documentation/
AFTER it has run. This script refuses to run from documentation/.

Built on gallery 2ead992b055054956816ddda3544e849e9789d9a
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery 21065c5d95ecb22c79fa1f398644a30b73a9a5ed
at https://github.com/tonylquintanilla/palomas_orrery)

L-342, from Claude Fable 5.1's review of L-322 Stage C1, Finding 1. A
DEFECT THAT IS LIVE: Earth's geocorona hover reads "Radius: 1e+2 Earth
radii". Before C1 it read "100.0000 Earth radii".

THE CAUSE IS ONE CALL. fmtServed used value.toPrecision(figures), and
JavaScript switches toPrecision to exponent notation whenever the
integer part has more digits than the figure count. 100 declared to one
figure prints as "1e+2". C1 declared the first figure counts the store
has ever carried, so it is the first time a served value met that
condition. C2 adds more: any value of 10 or more declared to one
figure, 100 or more to two, and so on.

WHAT IT DOES (two files, four anchored edits):

  gallery/feature_renderers.js
      fmtServed now rounds to the declared figures and prints PLAIN
      DIGITS. It rounds exactly as toPrecision did, then chooses the
      decimal places that show that many significant digits -- so a
      significant trailing zero survives (1 at two figures is "1.0")
      and a number wider than its count does not become an exponent
      (100 at one figure is "100"). Exported as _fmtServed beside
      _poleBasis and _KM_PER_AU, which is this file's existing way of
      handing an internal to a smoke test.

  documentation/smoke_hover_budget.js
      A new check runs EVERY served value that carries a figure count,
      read from data/objects_config.json, through the renderers' own
      formatter, and fails if any comes back in exponent form.

WHY THE CHECK TESTS THE FORMATTER AND NOT THE HOVER PROSE. The review
asked for a check that fails when a built hover contains exponent
notation. Written that way it fails on TWENTY hovers that are correct:
the Oort cloud's "2.00e+3 AU", the Sun's gravitational influence at
"1.50e+5", Jupiter's main ring at "2.01e-7", the Moon at "3.684e+05".
Those are written deliberately by other code, at magnitudes where the
notation is the right way to show a number. A check with twenty
standing exceptions is not a check. Testing the formatter against the
served counts catches exactly the class of fault that hit the geocorona
and cannot fire on prose somebody meant.

WHAT THIS DOES NOT FIX, and the review says so: the same hover gives
the altitude as 631,436 km, six figures beside a one-figure floor. That
predates C1 and is a separate question about what an altitude derived
from a floor should show.

SUCCESS looks like: one "ok" line per edit, then "patch applied".
FAILURE looks like: one ERROR: or ANCHOR FAIL: line, and NOTHING is
written to either file. Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

RENDER = "gallery/feature_renderers.js"
SMOKE = "documentation/smoke_hover_budget.js"

BASE = {
    RENDER: "c73dd8679be59e991b6a5fbdca882631",
    SMOKE: "0fc3a809d72d147af286ed4725b6d366",
}


def fail(msg):
    print(msg)
    print("NOTHING was written to either file. Undo is Discard Changes in "
          "GitHub Desktop.")
    sys.exit(1)


def fingerprint(raw):
    return hashlib.md5(raw.replace(b"\r\n", b"\n")).hexdigest()


EDITS = []

EDITS.append((RENDER, "RENDER  fmtServed prints plain digits, never an exponent",
    b"""  /* Rule 7 of provenance-discipline: a display may show FEWER figures
     than the row declares, never more. With a declared count, format to
     it; without one, keep the format this hover has always used. Every
     served count is null at the time of writing, so nothing printed
     changes until a store row declares one. */
  function fmtServed(value, figures, digits) {
    return (typeof figures === "number")
      ? value.toPrecision(figures) : value.toFixed(digits);
  }
""",
    b"""  /* Rule 7 of provenance-discipline: a display may show FEWER figures
     than the row declares, never more. With a declared count, format to
     it; without one, keep the format this hover has always used. */
  function fmtServed(value, figures, digits) {
    return (typeof figures === "number")
      ? sigFigures(value, figures) : value.toFixed(digits);
  }

  /* Round to `figures` significant figures and print PLAIN DIGITS.

     This was value.toPrecision(figures) until 2026-09-19, and that is
     where Earth's geocorona came to read "Radius: 1e+2 Earth radii".
     JavaScript switches toPrecision to exponent notation whenever the
     integer part has more digits than the figure count, so 100 declared
     to ONE figure prints as an exponent. L-322's Earth walk declared the
     first figure counts this store has ever carried, which is why the
     fault appeared then and not before; any value of 10 or more at one
     figure, or 100 or more at two, meets the same condition.

     The rounding is unchanged -- toPrecision still does it -- and then
     the decimal places are chosen to show exactly that many significant
     digits. So a significant trailing zero survives (1 at two figures is
     "1.0"), and a number wider than its own count stays plain (100 at one
     figure is "100", 5710 at three is "5710").

     Deliberate exponent notation elsewhere in these hovers -- the Oort
     cloud's 2.00e+3 AU, the Moon's distance -- is written by other code
     at magnitudes where it is the right way to show a number, and is not
     touched by this. (L-342, Fable's review of C1, Finding 1.) */
  function sigFigures(value, figures) {
    if (typeof value !== "number" || !isFinite(value)) {
      return String(value);
    }
    var n = Math.max(1, Math.min(21, Math.round(figures)));
    var rounded = Number(value.toPrecision(n));
    if (rounded === 0) { return rounded.toFixed(n - 1); }
    var decimals = n - 1 - Math.floor(Math.log10(Math.abs(rounded)));
    if (decimals < 0) { decimals = 0; }
    if (decimals > 20) { decimals = 20; }
    return rounded.toFixed(decimals);
  }
"""))

EDITS.append((RENDER, "RENDER  _fmtServed exported for the smoke test",
    b"""    _poleBasis: poleBasis,
    _KM_PER_AU: KM_PER_AU,
""",
    b"""    _poleBasis: poleBasis,
    _KM_PER_AU: KM_PER_AU,
    // L-342: the served-figures formatter, so the hover suite can run
    // every declared count through the code the page actually uses
    // rather than a second copy of the same arithmetic.
    _fmtServed: fmtServed,
"""))

EDITS.append((SMOKE, "SMOKE  every served figure count goes through the real formatter",
    b"""console.log("");
console.log(failures ? "=== " + failures + " FAILURE(S) ===" :""",
    b"""// L-342 (2026-09-19), from Fable's review of L-322 Stage C1.
//
// Earth's geocorona hover read "Radius: 1e+2 Earth radii" on the live
// site, and all fourteen gallery checks passed over it, because none of
// them reads the numbers inside a hover. This is the missing one.
//
// IT TESTS THE FORMATTER, NOT THE PROSE, and that is deliberate. A check
// that fails on any hover containing exponent notation fails on twenty
// hovers that are RIGHT: the Oort cloud's "2.00e+3 AU", the Sun's
// gravitational influence at "1.50e+5", Jupiter's main ring at
// "2.01e-7", the Moon at "3.684e+05". Those are written by other code at
// magnitudes where the notation is how a number should be shown. A check
// with twenty standing exceptions is not a check. So this runs every
// served value that DECLARES a figure count through the renderers' own
// fmtServed and fails if that comes back as an exponent -- exactly the
// class of fault that hit the geocorona, and nothing else.
//
// The counts come from data/objects_config.json, so the check grows by
// itself as the store's slices close. C2 adds Earth's magnetosphere.
const declared = [];
(function findDeclared(node, trail) {
    if (Array.isArray(node)) {
        node.forEach(function (item, i) {
            findDeclared(item, trail + "[" + i + "]");
        });
        return;
    }
    if (!node || typeof node !== "object") { return; }
    if (typeof node.figures === "number" && typeof node.value === "number") {
        declared.push({ where: trail, value: node.value,
                        figures: node.figures });
    }
    Object.keys(node).forEach(function (k) {
        findDeclared(node[k], trail + "/" + k);
    });
}(storeObjects, ""));

const EXPONENT = /[eE][+-]?\\d/;
const exponentiated = declared.filter(function (d) {
    return EXPONENT.test(String(GF._fmtServed(d.value, d.figures, 4)));
});
check("no served figure count formats as an exponent",
      exponentiated.length === 0,
      exponentiated.length
          ? exponentiated.map(function (d) {
                return d.where + " " + d.value + " at " + d.figures +
                       " -> " + GF._fmtServed(d.value, d.figures, 4);
            }).join("; ")
          : declared.length + " declared count(s) checked");

console.log("");
console.log(failures ? "=== " + failures + " FAILURE(S) ===" :"""))


def main():
    if os.path.basename(os.getcwd()) == "documentation":
        fail("ERROR: this script is running from documentation/. Move it "
             "to the repository ROOT and run it there.")
    for path in (RENDER, SMOKE):
        if not os.path.exists(path):
            fail("ERROR: " + path + " is not here. Run this from the "
                 "GALLERY repo root.")

    raws = {}
    for path in (RENDER, SMOKE):
        with open(path, "rb") as handle:
            raws[path] = handle.read()
        got = fingerprint(raws[path])
        if got != BASE[path]:
            fail("ERROR: " + path + " is not the file this patch was cut "
                 "against.\n  expected " + BASE[path] + "\n  found    "
                 + got + "\nIf the patch already ran, this is what a "
                 "second run looks like: it refuses.")

    out = dict(raws)
    for path, label, old, new in EDITS:
        is_crlf = raws[path].count(b"\r\n") > 0
        if is_crlf:
            old = old.replace(b"\n", b"\r\n")
            new = new.replace(b"\n", b"\r\n")
        n = out[path].count(old)
        if n != 1:
            fail("ANCHOR FAIL: expected exactly 1 match, found %d -- %s\n"
                 "  anchor began: %r" % (n, label, old[:70]))
        out[path] = out[path].replace(old, new)

    for path, data in out.items():
        try:
            data.decode("ascii")
        except UnicodeDecodeError as exc:
            fail("ERROR: the result for " + path + " is not ASCII (%s)."
                 % exc)

    for path, data in out.items():
        with open(path, "wb") as handle:
            handle.write(data)

    for path, label, _o, _n in EDITS:
        print("  ok  " + label)
    print("")
    for path in sorted(out):
        print("      %-36s %7d -> %7d bytes"
              % (path, len(raws[path]), len(out[path])))
    print("")
    print("patch applied (2 files, %d edits)" % len(EDITS))
    print("")
    print("NOW, in order:")
    print("  1. Run the gallery maintenance run -- offline. The hover")
    print("     suite should report the new check passing over 12")
    print("     declared counts, and Cache in step should be RED,")
    print("     because the renderers changed and the cache has not.")
    print("  2. PAUSE OneDrive syncing, then rebuild the served cache.")
    print("  3. Run the offline run again. Everything green.")
    print("  4. Move this script into documentation/.")
    print("  5. Commit the renderers, the suite AND the cache together,")
    print("     and push.")
    print("  6. Open Earth's room, turn on the geocorona, hover it. It")
    print("     should read 100 Earth radii, not 1e+2.")
    print("")
    print("Undo at any point is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
