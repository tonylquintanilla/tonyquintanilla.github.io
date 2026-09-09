"""
patch_L291_12_earth_moon_arc_20260909.py -- Earth exhibit, Mode 5 round 2: the Moon's orbit (gallery repo)

Built on gallery bac5a5ee76ad10ad7d97703b40b30d1860b04892
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).
Ledger: L-291 (step 3, Mode 5). Protocol v3.55.

Tony's round 2, 2026-09-09: GEO in the equator's plane, confirmed. The
Moon's orbit drew as a woven band with no brighter arc visible, and
the span it covered was unclear. Two files edited.

  gallery/earth_geometry.js
  - The faint ellipse is now faint by COLOUR (rgba, alpha 0.45, width
    1.5) with the trace-level `opacity` removed. A 3D line with opacity
    below 1 goes down Plotly's transparent-line path, the one place in
    this scene a band could come from; an opaque trace with an rgba
    colour does not.
  - The trusted arc is WHITE, width 6. It was the Moon's own grey and
    differed from the ellipse only in width, so "brighter" was never
    true on screen.
  - The arc's hover states its dates (start to end, UTC, from the served
    trust window's JD bounds) and says plainly that there is no longer
    span to choose: the scene is one epoch, and the arc is the stretch
    of orbit the served elements are trusted for.

  documentation/smoke_earth_geometry.js -- the Moon check now pins the
  rgba colour, the absence of trace opacity, the white arc and the dates.

HOW TO RUN: save to the GALLERY repo root, Run, then
gallery_maintenance_run.py (expect 6 of 6), commit, push, --live, and
tap the Moon again: expect one thin grey ellipse and one bright white
quarter-arc with the Moon's marker on it.

GUARDS: two files md5-checked (LF) against bac5a5ee; each hunk matches
once; ASCII-only; refuses a second run; writes nothing on failure.

Written September 2026 with Anthropic's Claude Opus 5.
"""
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "gallery/earth_geometry.js": "ed77c588d17b4f2d46272c691ca494cd",
    "documentation/smoke_earth_geometry.js": "53134901e21e6a14449280ba19baf30b"
}

EDITS = {
    'gallery/earth_geometry.js': [
        ('  function isNum(v) { return typeof v === "number" && isFinite(v); }\n\n',
         '  function isNum(v) { return typeof v === "number" && isFinite(v); }\n\n  // Julian date -> calendar date, UTC, to the hour. JD 2440587.5 is the\n  // Unix epoch (1970-01-01T00:00Z), the standard conversion.\n  function jdToDate(jd) {\n    var d = new Date((jd - 2440587.5) * 86400000);\n    return d.toISOString().slice(0, 13).replace("T", " ") + ":00";\n  }\n\n'),
        ('        ".<br>" +\n        "The faint full ellipse is the same orbit swept once around; outside<br>" +\n',
         '        ".<br>" +\n        (isNum(arc.startJd) && isNum(arc.endJd)\n          ? "The arc runs from " + jdToDate(arc.startJd) + " to " + jdToDate(arc.endJd) + " (UTC).<br>" : "") +\n        "There is no longer span to choose: this scene is one epoch, and the<br>" +\n        "arc is the stretch of orbit the served elements are trusted for.<br>" +\n        "The faint full ellipse is the same orbit swept once around; outside<br>" +\n'),
        ('      tolerance_deg: payload.moonArc.tolerance_deg,\n      legendgroup: "moon", color: null\n',
         '      tolerance_deg: payload.moonArc.tolerance_deg,\n      startJd: payload.moonArc.startJd, endJd: payload.moonArc.endJd,\n      legendgroup: "moon", color: null\n'),
        ('          tr.line = { color: tr.line.color, width: 1 };\n          tr.opacity = 0.45;\n',
         '          // Faint by COLOUR, not by trace opacity (Tony, Mode 5\n          // 2026-09-09: the ellipse drew as a woven band). Plotly sends\n          // a 3D line with opacity < 1 down its transparent-line path;\n          // an rgba colour on an opaque trace does not go there.\n          tr.line = { color: "rgba(191, 191, 191, 0.45)", width: 1.5 };\n          delete tr.opacity;\n'),
        ('    if (moonArc) moonArc.color = moonColor || "rgb(200, 200, 200)";\n',
         '    // The arc is BRIGHTER than the ellipse: white, wide, opaque. Before\n    // this it took the Moon\'s own grey and differed only in width.\n    if (moonArc) moonArc.color = "rgb(255, 255, 255)";\n'),
    ],
    'documentation/smoke_earth_geometry.js': [
        ('check("Moon group carries the faint ellipse, the arc, the position and one arc info marker",\n      !!arc && !!ellipse && !!moonMarker && ellipse.line.width === 1 && arc.line.width === 6 &&\n',
         'check("Moon: ellipse faint by rgba (no trace opacity), arc white and wide, dates in the hover",\n      !!arc && !!ellipse && !!moonMarker && ellipse.line.width === 1.5 && arc.line.width === 6 &&\n      ellipse.opacity === undefined && /^rgba\\(/.test(ellipse.line.color) && arc.line.color === "rgb(255, 255, 255)" &&\n      /The arc runs from 2026-09-0\\d \\d\\d:00 to 2026-09-\\d\\d \\d\\d:00 \\(UTC\\)/.test(\n        moonG.find(t => /trusted arc of the orbit/.test((t.text || [""])[0])).text[0]) &&\n'),
    ],
}

NEW_FILES = {}


def main():
    texts = {}
    for name, md5 in FILES.items():
        raw = (ROOT / name).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != md5:
            print("STOP: %s md5 (LF) is %s, expected %s (at bac5a5ee)." % (name, got, md5))
            print("      Either this patch already ran or the file moved. Nothing written.")
            return 1
        texts[name] = lf.decode("utf-8")
    for name in NEW_FILES:
        if (ROOT / name).exists():
            print("STOP: %s already exists. Nothing written." % name)
            return 1
    for name, edits in EDITS.items():
        t = texts[name]
        for i, (old, new) in enumerate(edits, 1):
            c = t.count(old)
            if c != 1:
                print("STOP: %s edit %d matched %d time(s), expected 1. Nothing written." % (name, i, c))
                return 1
        # bottom-up: apply the hunk furthest down the file first
        for old, new in sorted(edits, key=lambda e: -t.index(e[0])):
            new.encode("ascii")
            t = t.replace(old, new)
        texts[name] = t
    for name, txt in NEW_FILES.items():
        txt.encode("ascii")
    for name in FILES:
        (ROOT / name).write_bytes(texts[name].encode("utf-8"))
        print("ok  edited  %s (%d hunks)" % (name, len(EDITS[name])))
    for name, txt in NEW_FILES.items():
        (ROOT / name).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / name).write_bytes(txt.encode("utf-8"))
        print("ok  created %s" % name)
    print("\npatch applied. Next: gallery_maintenance_run.py (expect 6 of 6), commit, push.")
    print("Then tap the Moon again in interactive.html?exhibit=earth.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
