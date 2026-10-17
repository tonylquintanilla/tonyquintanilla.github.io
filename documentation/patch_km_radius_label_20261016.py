#!/usr/bin/env python3
"""
patch_km_radius_label_20261016.py -- Tony's phone look, 2026-10-16:
the Lower Mantle's hover printed its radius as a bare
"= 5,710 km (0.0000382 AU)" with nothing above it to name it.
Tony: "yes, good catch".

Built on tonyquintanilla.github.io a83b7522 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io

The cause: a shell's hover names its radius on a line of its own when
the radius is served in Earth radii, solar radii or AU, then gives the
kilometres on a line starting "= ". A radius served in km had no first
line, so the "= " line stood alone. Four shells serve km: Earth's
inner core, outer core, lower mantle and upper mantle.

Two files:
- gallery/feature_renderers.js: a radius served in km starts its line
  with "Radius: " instead of "= ". Numbers unchanged.
- documentation/smoke_display_figures.js (the Display figures check):
  expects "Radius: " on those four, and fails if any of them begins a
  line with a bare "= ". Run against the old renderer it fails on all
  four, by name.

The hover is written by the page's own code, so this reaches the phone
on the push alone; no cache rebuild.

Run from VS Code's Run button in the gallery folder. It checks each
file is the one it was built on and writes nothing if not.
Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Each file: how it is checked, and its edits as (old, new), bottom-up.
# "whole": the file must be exactly the base before, and exactly the
# result after. "anchors": checked only at the lines edited, so notes
# elsewhere are kept; the result is still checked whole when the base
# matched. "new": a file this patch adds.
FILES = [
    {
        'path': 'gallery/feature_renderers.js',
        'mode': 'whole',
        'base_md5': 'b40bea23aa9b224a7fa0c095b1e25ab8',
        'new_md5': 'a3fe288ebdeaf2abd594223ea51c4ccd',
        'edits': [
            ('      var kmOnly = (cfg.radius.unit === "au" && servedText(cfg.radius) !== null)\n        ? inText(cfg.radius, "km") : null;\n      hover += "= " + (kmOnly !== null ? kmOnly + " km"\n                       : km ? (km.radiusText ||\n                               kmAndAu(km.radiusKm, km.radiusFigures))\n',
             '      var kmOnly = (cfg.radius.unit === "au" && servedText(cfg.radius) !== null)\n        ? inText(cfg.radius, "km") : null;\n      // A radius served in km has no line above to name it, so its own\n      // line does: "Radius: 5,710 km (0.0000382 AU)" rather than a bare\n      // "= 5,710 km", on Earth\'s four inner shells (Tony, 2026-10-16:\n      // "yes, good catch").\n      hover += (cfg.radius.unit === "km" ? "Radius: " : "= ") + (kmOnly !== null ? kmOnly + " km"\n                       : km ? (km.radiusText ||\n                               kmAndAu(km.radiusKm, km.radiusFigures))\n'),
            (' *   citation and its note with " -- " as their one Source line always\n *   read. No hover changed: a hover carries no citation.)\n */\n\n',
             ' *   citation and its note with " -- " as their one Source line always\n *   read. No hover changed: a hover carries no citation.)\n * Module updated: October 16, 2026 with Anthropic\'s Claude Opus 5.5\n *   (Tony\'s phone look: a shell whose radius is served in km -- the\n *   inner core, outer core, lower mantle and upper mantle -- printed\n *   its radius as a bare "= 5,710 km (...)" with no line above it. It\n *   now reads "Radius: 5,710 km (0.0000382 AU)". Numbers unchanged.)\n */\n\n'),
        ],
    },
    {
        'path': 'documentation/smoke_display_figures.js',
        'mode': 'whole',
        'base_md5': 'b7722e908c8ebf654060a1d8da6adb50',
        'new_md5': '4998ae36d266edf910cf18df6f00ea39',
        'edits': [
            ('    numbersExamined += numbersIn(radiusLine).length;\n  }\n  if (pin.radius && radiusLine.indexOf("= " + pin.radius + " (") !== 0) {\n    fail(label + ": the radius line computes to \\"" + radiusLine +\n         "\\" but the manifest\'s acceptance table says \\"" + pin.radius + "\\"");\n',
             '    numbersExamined += numbersIn(radiusLine).length;\n  }\n  if (shell.radius.unit === "km" && lineStartingWith(hover, "= ")) {\n    fail(label + ": its radius is served in km, so nothing above names " +\n         "it, and yet a line begins with a bare \\"= \\"");\n  }\n  if (pin.radius && radiusLine.indexOf(lead + pin.radius + " (") !== 0) {\n    fail(label + ": the radius line computes to \\"" + radiusLine +\n         "\\" but the manifest\'s acceptance table says \\"" + pin.radius + "\\"");\n'),
            ('  const pin = ACCEPTANCE[label] || {};\n\n  // The radius line, written "= <km> (<au> AU)".\n  const radiusLine = "= " + (want.radiusText ||\n                             kmAndAu(want.radiusKm, want.radiusFig));\n  if (hover.indexOf(radiusLine) < 0) {\n    fail(label + ": the radius line reads\\n        " +\n         (lineStartingWith(hover, "= ") || "(no line starting \\"= \\")") +\n         "\\n      and these rules give\\n        " + radiusLine);\n  } else {\n',
             '  const pin = ACCEPTANCE[label] || {};\n\n  // The radius line, written "= <km> (<au> AU)" under an Earth-radii\n  // line, or "Radius: <km> (<au> AU)" for a radius served in km, which\n  // has no line above it to name it (Tony, 2026-10-16). A line that\n  // begins "= " with nothing above it is the fault this guards against.\n  const lead = (shell.radius.unit === "km") ? "Radius: " : "= ";\n  const radiusLine = lead + (want.radiusText ||\n                             kmAndAu(want.radiusKm, want.radiusFig));\n  if (hover.indexOf(radiusLine) < 0) {\n    fail(label + ": the radius line reads\\n        " +\n         (lineStartingWith(hover, lead) || "(no line starting \\"" + lead +\n                                           "\\")") +\n         "\\n      and these rules give\\n        " + radiusLine);\n  } else {\n'),
        ],
    },
]


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def fail(message):
    print(message)
    print("NOTHING was written. Undo is not needed.")
    return 1


def main():
    planned = []
    notes = []
    for f in FILES:
        rel = f["path"]
        path = os.path.join(HERE, *rel.split("/"))
        if f["mode"] == "new":
            if os.path.exists(path):
                with open(path, "rb") as handle:
                    have = handle.read().decode("utf-8").replace("\r\n", "\n")
                if md5(have) == f["new_md5"]:
                    print("ok  %-58s already present, the same" % rel)
                    continue
                return fail("ERROR: %s already exists and differs from what "
                            "this patch adds." % rel)
            planned.append((rel, path, f["content"]))
            print("ok  %-58s new file" % rel)
            continue
        if not os.path.exists(path):
            return fail("ERROR: %s is not here. Save this patch in the "
                        "repository's root folder." % rel)
        with open(path, "rb") as handle:
            raw = handle.read()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return fail("ERROR: %s is not UTF-8." % rel)
        if "\r\n" in text:
            text = text.replace("\r\n", "\n")
            notes.append("note: %s was CRLF in the working copy; written LF"
                         % rel)
        have = md5(text)
        if have == f["new_md5"]:
            return fail("ERROR: %s already carries this patch's change. "
                        "It has run before." % rel)
        exact = have == f["base_md5"]
        if f["mode"] == "whole" and not exact:
            return fail("ERROR: %s is not the version this patch was "
                        "built on (base moved). Compare it with the "
                        "repository in GitHub Desktop." % rel)
        for n, (old, new) in enumerate(f["edits"], 1):
            count = text.count(old)
            if count != 1:
                first = old.strip().splitlines()[0][:60] if old.strip() else ""
                return fail("ANCHOR FAIL: %s edit %d matched %d times: %r"
                            % (rel, n, count, first))
            text = text.replace(old, new)
        if exact and md5(text) != f["new_md5"]:
            return fail("ERROR: %s edited, but the result is not what this "
                        "patch was built to write." % rel)
        if not exact:
            notes.append("note: %s differed from the base outside the edited "
                         "lines; those lines were kept" % rel)
        planned.append((rel, path, text))
        print("ok  %-58s %d edit(s)" % (rel, len(f["edits"])))

    for rel, path, text in planned:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    for note in notes:
        print(note)
    print("patch applied (%d file(s) written)" % len(planned))
    print("")
    print('Commit and push in GitHub Desktop.')
    print('On the phone, open the Earth room and tap the Lower Mantle: it should read "Radius: 5,710 km (0.0000382 AU)".')
    return 0


if __name__ == "__main__":
    sys.exit(main())
