"""
patch_viewer_infocard_tap_20260908.py -- the tap that opens the card must not close it (gallery repo)

Built on gallery 1eb1e0849fef103d4a6db94bd63bc5a516381d82
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main).

Found by Tony, 2026-09-08, on the served portrait Earth-and-Moon card:
  1. phone: tapping a marker shows only the (grey) hover box; the info
     card appears only after a small upward swipe -- a gesture that has
     to be learned;
  2. desktop in mobile mode: a left click shows the card for an instant;
     only a right click makes it stay;
  3. desktop mode is correct.

ONE MECHANISM EXPLAINS ALL THREE. index.html opens the card from
Plotly's plotly_click. The same tap or click then bubbles as an ordinary
DOM "click" to a document-level listener whose rule is "a click anywhere
outside the card dismisses it" -- and it dismisses the card it has just
opened. A right click fires plotly_click but no DOM click (it fires
contextmenu), so the card survives; a tiny drag on release is still a
Plotly click but produces no DOM click, so the card survives. Those are
the two accidental workarounds Tony found.

THE FIX. showInfoCard stamps the time it opened; the document listener
ignores a click that arrives within 400 ms of that stamp. Tapping a
second marker while the card is up re-stamps and swaps the content;
tapping empty canvas or chrome (no plotly_click) still dismisses.

NOT IN THIS PATCH. The grey hover box on the served card is baked into
the portrait FILE, exported 2026-09-07 17:50 before patch_L288_1 changed
Studio. It goes away when that scene is re-exported through Studio and
re-converted; nothing in the viewer can remove it.

HOW TO RUN
  Save to the GALLERY repo root. Open in VS Code and press Run. Offline
  runner, commit, push. Mode 5: phone, tap a marker once -- the card
  rises and stays; tap another marker -- the card changes; tap the sky
  -- it closes. Desktop in mobile mode: left click behaves the same.

ALSO IN THIS PATCH: documentation/pin_artifact1_known_failure.py. The
Artifact 1 checker fails at 1eb1e084 because patch_L291_6 changed Earth's
served feature groups and the 2026-09-08 nightly rebuilt the served cache;
the pin's T3 key list is updated to the 13 keys now served. Same verdict
(T3 FAIL, L-237), new key set.

GUARDS
  Both files md5-checked (LF-normalised) against 1eb1e084. Each edit
  must match exactly once. ASCII, LF.

Written September 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILES = {
    "index.html": "72c617ebbd428f214c8942636ed32f07",
    "documentation/pin_artifact1_known_failure.py": "dabca6e04557893b51a7e80536258312",
}

# Second file: the Artifact 1 pin. patch_L291_6 changed Earth's served
# feature groups (two -> nine) and the nightly of 2026-09-08 rebuilt the
# served cache, so the pinned T3 feature-key set moved. The pin's own
# message says: update PINNED in the same commit as the change. The T3
# verdict is still FAIL for the same reason (L-237: the test expects Earth's
# feature groups alone and sees the Sun's too), so only the key list moves.
PIN_EDITS = [
    (
        "    (\"T3\", \"FAIL\",\n"
        "     \"KNOWN, L-237 -- expects Earth's two feature groups, sees all eight\"),\n",
        "    (\"T3\", \"FAIL\",\n"
        "     \"KNOWN, L-237 -- expects Earth's feature groups alone, sees the Sun's too \"\n"
        "     \"(13 keys since L-291, 2026-09-08)\"),\n",
    ),
    (
        "PINNED_T3_FEATURES = [\n"
        "    \"atmosphere_shell\", \"hill_sphere\", \"oort_cloud\", \"orientation\",\n"
        "    \"solar_atmosphere\", \"solar_wind\", \"sun_structures\", \"van_allen_belts\",\n"
        "]\n",
        "# L-291 (2026-09-08): Earth's entry moved to the measured shape -- nine\n"
        "# groups, atmosphere_shell retired. hill_sphere and orientation are keys\n"
        "# both bodies serve, so the set is 13, not 9 + 6.\n"
        "PINNED_T3_FEATURES = [\n"
        "    \"earth_atmosphere\", \"earth_exosphere\", \"earth_geostationary\",\n"
        "    \"earth_interior\", \"earth_magnetosphere\", \"earth_orbital_zones\",\n"
        "    \"hill_sphere\", \"oort_cloud\", \"orientation\", \"solar_atmosphere\",\n"
        "    \"solar_wind\", \"sun_structures\", \"van_allen_belts\",\n"
        "]\n",
    ),
]

EDITS = [
    (
        "        var infoCardShown = false;\n",
        "        var infoCardShown = false;\n"
        "        var infoCardOpenedAt = 0;     // ms; the tap that opens the card must not dismiss it\n",
    ),
    (
        "                infoCard.classList.add('visible');\n"
        "                infoCardShown = true;\n",
        "                infoCard.classList.add('visible');\n"
        "                infoCardShown = true;\n"
        "                infoCardOpenedAt = Date.now();\n",
    ),
    (
        "            // Click/tap anywhere dismisses info card (except on card itself)\n"
        "            document.addEventListener('click', function(e) {\n"
        "                if (infoCardShown && !infoCard.contains(e.target)) {\n"
        "                    dismissInfoCard();\n"
        "                }\n"
        "            });\n",
        "            // Click/tap anywhere dismisses info card (except on card itself).\n"
        "            // The Plotly click that OPENS the card bubbles here as the same DOM\n"
        "            // click and, until 2026-09-08, closed it in the same instant -- a\n"
        "            // left click flashed the card, a right click (no DOM click) kept\n"
        "            // it, a tap needed a tiny drag. Ignore the click that just opened it.\n"
        "            document.addEventListener('click', function(e) {\n"
        "                if (infoCardShown && !infoCard.contains(e.target) &&\n"
        "                    Date.now() - infoCardOpenedAt > 400) {\n"
        "                    dismissInfoCard();\n"
        "                }\n"
        "            });\n",
    ),
]


def main():
    texts = {}
    for name, md5 in FILES.items():
        lf = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != md5:
            print("STOP: %s md5 (LF) is %s, expected %s (at 1eb1e084)." % (name, got, md5))
            print("      Either this patch already ran or the file moved. Nothing written.")
            return 1
        texts[name] = lf.decode("utf-8")
    for name, edits in (("index.html", EDITS), ("documentation/pin_artifact1_known_failure.py", PIN_EDITS)):
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
        print("Patched %-45s new md5 (LF) %s" % (name, hashlib.md5(t.encode("utf-8")).hexdigest()))
    print("index.html: the click that opens the info card no longer dismisses it (400 ms guard).")
    print("pin_artifact1: T3 feature-key set re-pinned to the 13 keys served since L-291.")
    print("Next: offline runner (5 of 5), commit, push; phone: tap a marker once, the card stays.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
