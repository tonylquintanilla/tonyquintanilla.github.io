"""
patch_L286_1_viewer_3d_rotation.py -- 3D cards rotate from the first touch again (gallery repo)

Built on gallery e6c39a00dc4e0f9cdba0f5153e86b835b8f40b78
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).

Found by Tony, 2026-09-07: a served 3D card does not rotate on load. On
the desktop the orbit or reset modebar button revives it; on the phone
there is no modebar, so it never rotates. Studio's own HTML export of
the same figure rotates from the start.

THE CHAIN, each link read out of plotly-2.35.2.min.js, not inferred:
  1. index.html's sweep (L-286) runs applySweep() right after newPlot.
     For a 3D figure whose layout carries no dragmode it wants to
     "restore" null, compares that to the live layout's undefined, and
     -- because undefined !== null -- calls
         Plotly.relayout('plotly-graph', { dragmode: null }).
  2. dragmode has editType "modebar", so that relayout runs Plotly's
     modebar update, and the gl3d module's updateFx does, for every
     scene:  scene.updateFx(fullLayout.dragmode, fullLayout.hovermode)
     -- the LAYOUT-level dragmode, whose default is "zoom".
  3. scene.updateFx(mode) rotates only for "orbit" and "turntable";
     anything else becomes the camera's keyBindingMode, so "zoom" turns
     drag into zoom and the rotation is gone.
  The orbit button sets scene.dragmode directly (fixes it); reset
  rebuilds the camera (fixes it); a phone has neither.

THE FIX, in applySweep only:
  - a 3D figure (layout.scene present) never has its dragmode touched:
    the sweep already excludes 3D in sweepWanted(), so there is nothing
    to give and nothing to restore;
  - for 2D, an absent dragmode reads as null before the comparison, so
    "nothing to restore" no longer produces a relayout.
  Both call sites (after render, and on resize) go through this one
  function, so both are covered.

LESSON FOR THE FIELD NOTES (gallery-assembler, beside L-278): a layout-
level dragmode relayout -- even to null -- rewrites every 3D scene's
drag behaviour from the layout default. Never relayout dragmode on a
figure with a scene unless you mean to set the scene's rotation mode.

HOW TO RUN
  Save to the GALLERY repo root. Open in VS Code and press Run. Offline
  runner, commit, push. Mode 5: open any 3D card on the desktop and drag
  before touching the modebar -- it rotates; then on the phone, both
  orientations, same. The sweep (a landscape 2D card on a portrait
  phone) is unchanged and worth one glance.

GUARDS
  index.html read in binary mode, LF-normalised, md5 checked against
  e6c39a00. The edit must match exactly once. ASCII, LF.

Written September 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "index.html"
EXPECTED_MD5 = "5e42bd1cce40e3436d4c38383a54346d"

OLD = (
    "            if (plotlyGraph.data && typeof Plotly !== 'undefined') {\n"
    "                var want = on ? false : sweepDragmode;\n"
    "                if ((plotlyGraph.layout || {}).dragmode !== want) {\n"
    "                    Plotly.relayout('plotly-graph', { dragmode: want });\n"
    "                }\n"
    "            }\n"
)
NEW = (
    "            // Dragmode is the sweep's to give and take ONLY on a 2D figure.\n"
    "            // A 3D scene is never swept (sweepWanted excludes it) and must\n"
    "            // never see a layout-level dragmode relayout: in Plotly 2.35.2\n"
    "            // that relayout -- even to null -- makes gl3d.updateFx copy the\n"
    "            // LAYOUT dragmode (default \"zoom\") into every scene, and the\n"
    "            // turntable rotation is gone until a modebar button restores\n"
    "            // it, which a phone does not have. (2026-09-07; found by Tony\n"
    "            // on a served card, absent from Studio's HTML export.)\n"
    "            var is3d = !!((plotlyGraph.layout || {}).scene);\n"
    "            if (!is3d && plotlyGraph.data && typeof Plotly !== 'undefined') {\n"
    "                var want = on ? false : sweepDragmode;\n"
    "                var cur = (plotlyGraph.layout || {}).dragmode;\n"
    "                if (cur === undefined) cur = null;   // absent == nothing to restore\n"
    "                if (cur !== want) {\n"
    "                    Plotly.relayout('plotly-graph', { dragmode: want });\n"
    "                }\n"
    "            }\n"
)


def main():
    lf = TARGET.read_bytes().replace(b"\r\n", b"\n")
    got = hashlib.md5(lf).hexdigest()
    if got != EXPECTED_MD5:
        print("STOP: index.html md5 (LF) is %s, expected %s (at e6c39a00)." % (got, EXPECTED_MD5))
        print("      Either this patch already ran or the file moved. Nothing written.")
        return 1
    text = lf.decode("utf-8")
    if text.count(OLD) != 1:
        print("STOP: anchor matched %d time(s), expected 1. Nothing written." % text.count(OLD))
        return 1
    NEW.encode("ascii")
    text = text.replace(OLD, NEW, 1)
    TARGET.write_bytes(text.encode("utf-8"))
    print("Patched index.html, new md5 (LF) %s" % hashlib.md5(text.encode("utf-8")).hexdigest())
    print("applySweep no longer relayouts dragmode on a 3D figure; 2D: absent reads as null.")
    print("Next: offline runner, commit, push; then drag a 3D card before touching the modebar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
