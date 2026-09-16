"""Add the hover budget checker: the line-width rule's missing twin.

Targets, in the gallery repo:
  documentation/smoke_hover_budget.js   (new)
  documentation/run_hover_budget.py     (new)
  gallery_maintenance_run.py            (one new checker row)
Built against gallery c2155b45 WITH patch_L231_hover_length.py applied.
Handle: L-231 follow-up.  2026-09-15, with Anthropic's Claude Opus 5.

RUN patch_L231_hover_length.py FIRST. This one refuses otherwise, because
its ceiling is measured on the shortened hovers.

WHY
---
A sibling check already asserts that no hover LINE exceeds 90 characters.
On 2026-09-15 the bow shock hover ran to 32 lines and every one of them
passed that rule comfortably, while the box ran off the bottom of Tony's
phone. A hover can be perfectly narrow and still overflow. This is the
missing twin: a budget on the NUMBER of lines.

WHAT IT MEASURES
----------------
Every hover the renderers produce, in every fixture the other Node suites
already carry -- the composed Earth room, Earth's features on their own,
and the two ringed planets. 78 hovers at the time of writing. It prints
the longest ten every run, so the offender is named rather than implied.

A RATCHET. The ceiling is 23 lines, which is the worst hover as it stands
(the outer radiation belt, whose bulk is its served note). It may be
lowered and must never be raised: raising it to admit a new hover is how
the old ones reached 32. When the worst comes down the suite says so and
asks for the ceiling to follow it.

The intended budget is about 14, which is what the geostationary belt
costs. What stands between here and there is whether a served caveat
belongs in the hover or behind the panel's click -- a judgment about what
a visitor must see, left open rather than decided in a checker.

TWO ENTRY POINTS, ON PURPOSE
----------------------------
The maintenance runner calls the Node suite directly, like its four
siblings, so a missing Node reports UNREACHABLE there rather than passing.
The dashboard launches Python, not Node, so run_hover_budget.py wraps it
the way the Artifact 1 pin wraps its test. The wrapper adds nothing but
the shell-out and a plain message if Node is absent.

AFTER RUNNING
-------------
  node documentation/smoke_hover_budget.js gallery/feature_renderers.js \\
       gallery/earth_geometry.js
  python documentation/run_hover_budget.py
  python gallery_maintenance_run.py
  Expect ALL CHECKS PASSED, 78 hovers measured, and SEVEN gating checkers
  in the runner rather than six.

UNDO
----
Delete the two new files and Discard Changes on gallery_maintenance_run.py.
"""

JS = b'// smoke_hover_budget.js -- no hover outgrows the phone.\n//\n// node documentation/smoke_hover_budget.js gallery/feature_renderers.js \\\n//      gallery/earth_geometry.js\n//\n// WHY THIS EXISTS (L-231 follow-up, 2026-09-15)\n//\n// On 2026-09-15 Tony reported from the phone that the hover boxes were\n// larger than the screen could hold at any position. Measured afterwards,\n// the magnetopause hover was 29 lines, the bow shock 32 and the outer belt\n// 27, against a house ceiling of 14 among the shells and 6 for a plain one.\n// Nothing had caught it, because the sibling check that existed measured\n// line WIDTH -- no line over 90 characters -- and every one of those lines\n// was comfortably inside 90. A hover can be perfectly narrow and still run\n// off the bottom of a phone.\n//\n// So this is the width rule\'s missing twin: a budget on the number of\n// lines, checked on every hover the renderers produce, in every fixture\n// the other suites already carry.\n//\n// A RATCHET, NOT A TARGET. The ceiling below is the worst hover in the\n// scene as it stands. It may be lowered and must never be raised: raising\n// it to admit a new hover is how the old ones got to 32. The intended\n// budget is nearer 14, which is what the geostationary belt costs. What\n// stands between here and there is the served NOTES -- the outer belt\'s\n// caveat alone is about seven lines -- and whether a caveat belongs in the\n// hover or behind the information panel\'s click is a judgment about what a\n// visitor must see, recorded as open rather than decided here.\n//\n// Exit code 0 on pass, 1 on failure, the same as its siblings.\n\n"use strict";\n\nconst fs = require("fs");\nconst path = require("path");\n\n// The worst hover in the scene at the time of writing: the outer radiation\n// belt, whose bulk is its served note. LOWER THIS WHEN IT CAN BE LOWERED.\n// Never raise it. If a new hover needs more than this, shorten the hover.\nconst CEILING = 23;\n\n// The intended budget, for the message only. Nothing gates on it.\nconst TARGET = 14;\n\nconst code = fs.readFileSync(process.argv[2], "utf8");\nconst geomPath = process.argv[3];\nglobal.window = global;\neval(code);\nif (geomPath) { eval(fs.readFileSync(geomPath, "utf8")); }\nconst GF = global.GalleryFeatures;\nconst EG = global.EarthGeometry;\n\nlet failures = 0;\nfunction check(label, ok, note) {\n    console.log("  " + (ok ? "OK  " : "FAIL") + " " + label +\n                (note ? "  [" + note + "]" : ""));\n    if (!ok) { failures++; }\n}\n\nfunction fixture(name) {\n    return JSON.parse(fs.readFileSync(path.join(__dirname, name), "utf8"));\n}\n\n// Every trace that carries hover text, from every scene the other suites\n// already compose. A trace with hoverinfo "skip" is not counted: geometry\n// is silent by convention and only the info markers speak.\nconst hovers = [];\nfunction collect(scene, traces) {\n    for (const t of traces) {\n        if (!t || t.hoverinfo === "skip") { continue; }\n        const txt = Array.isArray(t.text) ? t.text[0] : t.text;\n        if (typeof txt !== "string" || !txt.length) { continue; }\n        hovers.push({\n            scene: scene,\n            name: t.legendgroup || t.name || "(unnamed)",\n            lines: txt.split("<br>").length,\n            chars: txt.length\n        });\n    }\n}\n\n// 1. The Earth room, composed the way the page composes it -- this is the\n//    only path with a Sun direction, so it is the only one where the\n//    magnetopause and bow shock hovers exist at all.\nif (EG) {\n    const p = fixture("payload_earth_scene.json");\n    const out = EG.composeScene(p, {\n        GF: GF,\n        halfRangeAu: 6.155e-5,\n        epochIso: "2026-09-15"\n    });\n    collect("earth room", out.traces);\n} else {\n    console.log("  NOTE  no earth_geometry.js given; the Earth room\'s own " +\n                "traces (axis, Sun line, terminator, Moon) are not measured");\n}\n\n// 2. The feature renderers on their own, which is what the other fixtures\n//    exercise: Earth\'s shells and belts, and the two ringed planets.\ncollect("earth features", GF.buildFeatureTraces(\n    fixture("payload_earth.json").features,\n    fixture("payload_earth.json").bodies).traces);\n\nconst js = fixture("payload_jupiter_saturn.json");\ncollect("jupiter+saturn", GF.buildFeatureTraces(js.features, js.bodies).traces);\n\n// ---- the report ------------------------------------------------------\nhovers.sort((a, b) => b.lines - a.lines);\n\nconsole.log("");\nconsole.log("  " + hovers.length + " hovers measured. The longest ten:");\nfor (const h of hovers.slice(0, 10)) {\n    console.log("    " + String(h.lines).padStart(3) + " lines  " +\n                String(h.chars).padStart(5) + " chars  " +\n                h.name + "  (" + h.scene + ")");\n}\nconsole.log("");\n\nconst worst = hovers.length ? hovers[0] : null;\n\ncheck("at least one hover was found to measure", hovers.length > 0,\n      hovers.length + " found");\n\ncheck("no hover exceeds the ceiling of " + CEILING + " lines",\n      !worst || worst.lines <= CEILING,\n      worst ? worst.lines + " lines: " + worst.name : "none");\n\n// Not a failure. A ratchet that has slack should be tightened, and saying\n// so every run is how it gets tightened rather than forgotten.\nif (worst && worst.lines < CEILING) {\n    console.log("  NOTE  the worst hover is " + worst.lines + " lines and " +\n                "the ceiling is " + CEILING + ".");\n    console.log("        Lower CEILING to " + worst.lines +\n                " in this file; it is a ratchet.");\n}\nif (worst && worst.lines > TARGET) {\n    console.log("  NOTE  the intended budget is about " + TARGET +\n                " lines (what the geostationary belt costs).");\n    console.log("        " + (worst.lines - TARGET) + " lines above it, in " +\n                worst.name + ".");\n}\n\nconsole.log("");\nconsole.log(failures ? "=== " + failures + " FAILURE(S) ===" :\n            "=== ALL CHECKS PASSED ===");\nprocess.exit(failures ? 1 : 0);\n'

PY = b'"""Run the hover budget checker from the dashboard.\n\nThe dashboard launches Python, not Node, so a Node suite needs a wrapper\nthe way the Artifact 1 pin wraps its test. This is that wrapper and\nnothing more: it shells out to\n\n    node documentation/smoke_hover_budget.js gallery/feature_renderers.js \\\\\n         gallery/earth_geometry.js\n\nfrom the gallery repo ROOT, forwards everything the checker prints, and\nreturns its exit code unchanged.\n\nThe gallery maintenance runner does NOT go through this file. It calls the\nNode suite directly, like its four siblings, so that a missing Node\nreports UNREACHABLE there rather than being mistaken for a pass. Here a\nmissing Node is simply said out loud, because a person is watching.\n\nRun it yourself from the gallery repo root:\n\n    python documentation/run_hover_budget.py\n\nL-231 follow-up, 2026-09-15, with Anthropic\'s Claude Opus 5.\n"""\n\nimport os\nimport subprocess\nimport sys\n\nSUITE = os.path.join("documentation", "smoke_hover_budget.js")\nARGS = [os.path.join("gallery", "feature_renderers.js"),\n        os.path.join("gallery", "earth_geometry.js")]\n\n\ndef main():\n    missing = [p for p in [SUITE] + ARGS if not os.path.isfile(p)]\n    if missing:\n        print("FAILURE: not found from here: %s" % ", ".join(missing))\n        print("Run this from the gallery repo ROOT, not from documentation/.")\n        return 1\n\n    try:\n        proc = subprocess.run(["node", SUITE] + ARGS)\n    except FileNotFoundError:\n        print("Node is not on the PATH, so the hover budget cannot be")\n        print("measured. Install Node, or run the gallery maintenance run,")\n        print("which reports this suite as UNREACHABLE rather than passing.")\n        return 1\n\n    return proc.returncode\n\n\nif __name__ == "__main__":\n    sys.exit(main())\n'

OLD = b'     ["documentation/smoke_earth_geometry.js", "gallery/feature_renderers.js",\n      "gallery/earth_geometry.js"],'

NEW = b'     ["documentation/smoke_earth_geometry.js", "gallery/feature_renderers.js",\n      "gallery/earth_geometry.js"],\n     ".", "===", False),\n\n    # L-231 follow-up (2026-09-15): the width rule\'s missing twin. Its\n    # sibling checks that no hover LINE exceeds 90 characters, and every\n    # line of the 32-line bow shock hover passed that comfortably while the\n    # box ran off the bottom of the phone. This counts the lines, over every\n    # hover in every fixture the other suites carry, and names the worst.\n    # A ratchet: the ceiling may be lowered, never raised. Gates.\n    ("Hover budget", "node",\n     ["documentation/smoke_hover_budget.js", "gallery/feature_renderers.js",\n      "gallery/earth_geometry.js"],'

import hashlib
import os
import sys

RUNNER = "gallery_maintenance_run.py"
RUNNER_FP = 'c7da3fb5aa7da900a1b8a1c1e68a9f9c'
NEW_FILES = [
    (os.path.join("documentation", "smoke_hover_budget.js"), JS),
    (os.path.join("documentation", "run_hover_budget.py"), PY),
]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    if not os.path.isfile(RUNNER):
        print("FAILURE: %s not found. Run this from the gallery repo root."
              % RUNNER)
        print("NOTHING was written.")
        return 1

    fr = os.path.join("gallery", "feature_renderers.js")
    if not os.path.isfile(fr):
        print("FAILURE: %s not found." % fr)
        print("NOTHING was written.")
        return 1
    with open(fr, "rb") as handle:
        if b"function sourceHead" not in handle.read():
            print("FAILURE: patch_L231_hover_length.py has not been applied.")
            print("  This checker's ceiling is measured on the shortened")
            print("  hovers. Run that patch first, then this one.")
            print("NOTHING was written.")
            return 1

    with open(RUNNER, "rb") as handle:
        data = handle.read()
    actual = content_md5(data)
    if actual != RUNNER_FP:
        print("FAILURE: BASE MOVED for %s." % RUNNER)
        print("  expected content md5 %s" % RUNNER_FP)
        print("  found                %s" % actual)
        print("NOTHING was written.")
        return 1

    for path, _ in NEW_FILES:
        if os.path.exists(path):
            print("FAILURE: %s already exists. NOTHING was written." % path)
            return 1

    is_crlf = data.count(b"\r\n") > 0

    def fit(block):
        return block.replace(b"\n", b"\r\n") if is_crlf else block

    if data.count(fit(OLD)) != 1:
        print("FAILURE: the checker-table anchor did not match exactly once.")
        print("NOTHING was written.")
        return 1
    data = data.replace(fit(OLD), fit(NEW))

    for path, blob in NEW_FILES:
        with open(path, "wb") as handle:
            handle.write(fit(blob))
    with open(RUNNER, "wb") as handle:
        handle.write(data)

    print("OK: two files created, one edited (%s)."
          % ("CRLF" if is_crlf else "LF"))
    for path, _ in NEW_FILES:
        print("    %s" % path)
    print("    %s -- one new gating row, \"Hover budget\"" % RUNNER)
    print()
    print("Next:")
    print("  node documentation/smoke_hover_budget.js \\")
    print("    gallery/feature_renderers.js gallery/earth_geometry.js")
    print("  python gallery_maintenance_run.py")
    print("  Expect 78 hovers measured and SEVEN gating checkers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
