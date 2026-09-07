"""
patch_L288_1_converter_path_and_routed_hover.py -- two Studio-chain defects (gallery repo)

Built on gallery e3a55b8e0180f7ef6e3f6a7deaede2a94338b553
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).

Found by Tony, 2026-09-07, exercising the Studio -> converter -> editor
chain on the Earth-and-Moon export (Trial 5 territory, L-288).

DEFECT 1 -- the converter wrote to tools/gallery/, not gallery/.
  tools/json_converter.py line 53: DEFAULT_OUTPUT_FOLDER = "gallery", a
  bare relative path, resolved against the current working directory.
  The comment above it says "relative to script location"; the code
  never did that. Run from tools/ (which is where the script is), it
  created tools/gallery/, put the card there, and -- finding no metadata
  file there -- wrote a fresh SCHEMA-1 gallery_metadata.json with one
  entry (category/filename/mode) beside the real schema-2 one
  (room/files/shape). The editor reads the real one, so the card was
  invisible. Fix: resolve the default folders against the repo root,
  from the script's own location, so the result is the same from any
  working directory.

DEFECT 2 -- portrait preview hover boxes are grey and empty.
  Portrait routes hover text to the slide-up info card and suppresses
  the tooltip by making it transparent (bgcolor rgba(0,0,0,0), font
  size 1, font colour transparent). That fails twice, both verified
  against plotly.min.js 2.35.2, not inferred:
    (a) Plotly's hover code reads
        combine(opacity(bgcolor) ? bgcolor : defaultLine), so a bgcolor
        with ZERO opacity is replaced by defaultLine, which is #444 --
        an opaque grey box.
    (b) The orrery writes a per-trace hoverlabel {font: {size: 11}} on
        fifteen traces. Per-trace hoverlabel beats the layout's, so the
        invisible text is laid out at full size and the box is large.
  Fix, minimal: strip per-trace hoverlabel in the routing branch, and
  give the layout label opacity 0.01 instead of 0 so Plotly keeps it.
  The existing hoverinfo='text' is KEPT: the code carries a field note
  that hoverinfo='none' kills 3D event detection in some Plotly
  versions, and that lesson stands until a render says otherwise.

RECOVERY (guarded)
  Removes tools/gallery/ if, and only if, it contains exactly the
  stranded card and the one-entry schema-1 metadata. Then Tony re-runs
  the converter on the same export; with the path fixed it finds the
  real metadata and writes a schema-2 Storage entry.

HOW TO RUN
  Save to the GALLERY repo root. Open in VS Code and press Run. Then
  re-run tools/json_converter.py on the Earth-and-Moon export, open the
  editor, and confirm the card is in Storage. Then run the offline
  maintenance runner, commit, push. The portrait hover fix is Mode 5:
  preview a portrait export and tap a point -- the card should rise and
  NO grey box should appear.

GUARDS
  Both files read in binary mode, LF-normalised, md5 checked against
  e3a55b8e. Every edit must match exactly once. Inserted text is
  ASCII-only, LF.

Written September 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "tools/json_converter.py": "1874c870fd5f9998a8a57a25e23569d2",
    "tools/gallery_studio.py": "32b94c57c583cd9267b9dcf30f613628",
}

EDITS = {
    "tools/json_converter.py": [
        (
            "# Default input/output folders (relative to script location)\n"
            "DEFAULT_INPUT_FOLDER = \"images\"\n"
            "DEFAULT_OUTPUT_FOLDER = \"gallery\"\n",
            "# Default input/output folders, resolved against the REPO ROOT from this\n"
            "# script's own location, so the result is the same from any working\n"
            "# directory. (L-288, 2026-09-07: these were bare relative names, so a\n"
            "# run from tools/ created tools/gallery/ and a shadow schema-1\n"
            "# metadata file there; the editor never saw the card.)\n"
            "_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))\n"
            "_REPO_ROOT = os.path.dirname(_TOOLS_DIR)\n"
            "DEFAULT_INPUT_FOLDER = os.path.join(_REPO_ROOT, \"images\")\n"
            "DEFAULT_OUTPUT_FOLDER = os.path.join(_REPO_ROOT, \"gallery\")\n",
        ),
    ],
    "tools/gallery_studio.py": [
        (
            "            # Non-destructive routing: keep trace['text'] intact.\n"
            "            # Tooltip is suppressed visually by transparent hoverlabel\n"
            "            # (set in the hoverlabel config block below).\n"
            "            # Keep hoverinfo='text' so Plotly fires click/hover events\n"
            "            # for the info card. Setting hoverinfo='none' kills 3D\n"
            "            # event detection in some Plotly versions.\n"
            "            trace['hovertemplate'] = '%{text}<extra></extra>'\n"
            "            trace['hoverinfo'] = 'text'\n",
            "            # Non-destructive routing: keep trace['text'] intact.\n"
            "            # Tooltip is suppressed visually by the near-transparent\n"
            "            # hoverlabel set in the hoverlabel config block below.\n"
            "            # Keep hoverinfo='text' so Plotly fires click/hover events\n"
            "            # for the info card. Setting hoverinfo='none' kills 3D\n"
            "            # event detection in some Plotly versions.\n"
            "            trace['hovertemplate'] = '%{text}<extra></extra>'\n"
            "            trace['hoverinfo'] = 'text'\n"
            "            # L-288 (2026-09-07): the orrery writes a per-trace\n"
            "            # hoverlabel {font: {size: 11}} on many traces, and a\n"
            "            # per-trace hoverlabel beats the layout's -- so the size-1\n"
            "            # suppression below never applied and the box drew at\n"
            "            # full size with invisible text. Drop it; the layout rules.\n"
            "            trace.pop('hoverlabel', None)\n",
        ),
        (
            "        layout['hoverlabel'] = {\n"
            "            'bgcolor': 'rgba(0,0,0,0)',\n"
            "            'bordercolor': 'rgba(0,0,0,0)',\n"
            "            'font': {'size': 1, 'color': 'rgba(0,0,0,0)'}\n"
            "        }\n",
            "        # L-288 (2026-09-07): NOT fully transparent. Plotly's hover code\n"
            "        # reads combine(opacity(bgcolor) ? bgcolor : defaultLine), so a\n"
            "        # zero-opacity bgcolor is replaced by defaultLine (#444) and the\n"
            "        # box renders opaque grey. Opacity 0.01 is kept as given and is\n"
            "        # invisible on the black paper. Verified in plotly.min.js 2.35.2.\n"
            "        layout['hoverlabel'] = {\n"
            "            'bgcolor': 'rgba(0,0,0,0.01)',\n"
            "            'bordercolor': 'rgba(0,0,0,0.01)',\n"
            "            'font': {'size': 1, 'color': 'rgba(0,0,0,0.01)'}\n"
            "        }\n",
        ),
    ],
}

STRAY = ROOT / "tools" / "gallery"
STRAY_EXPECTED = {
    "gallery_metadata.json",
    "solar_system_20260907_earth_shells_moon_gallery.json",
}


def remove_stray():
    if not STRAY.is_dir():
        print("Recovery: tools/gallery/ not present; nothing to remove.")
        return
    names = {p.name for p in STRAY.iterdir()}
    if names != STRAY_EXPECTED:
        print("Recovery: tools/gallery/ holds unexpected files; left in place:")
        for n in sorted(names):
            print("  " + n)
        return
    shutil.rmtree(STRAY)
    print("Recovery: removed tools/gallery/ (the stranded card and its schema-1 metadata).")
    print("  Re-run tools/json_converter.py on the Earth-and-Moon export; it now")
    print("  lands in gallery/ as a Storage entry the editor can see.")


def main():
    texts = {}
    for name, md5 in FILES.items():
        lf = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != md5:
            print("STOP: %s md5 (LF) is %s, expected %s (at e3a55b8e)." % (name, got, md5))
            print("      Either this patch already ran or the file moved. Nothing written.")
            return 1
        texts[name] = lf.decode("utf-8")
    for name, edits in EDITS.items():
        t = texts[name]
        for i, (old, new) in enumerate(edits, 1):
            c = t.count(old)
            if c != 1:
                print("STOP: %s edit %d matched %d time(s), expected 1. Nothing written." % (name, i, c))
                return 1
            new.encode("ascii")
            t = t.replace(old, new, 1)
        texts[name] = t
    for name, t in texts.items():
        (ROOT / name).write_bytes(t.encode("utf-8"))
        print("Patched %-26s %d edit(s), new md5 (LF) %s" %
              (name, len(EDITS[name]), hashlib.md5(t.encode("utf-8")).hexdigest()))
    remove_stray()
    print("Next: re-run the converter; editor -> confirm Storage; offline runner;")
    print("  commit; push. Portrait hover fix is Mode 5 on a preview.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
