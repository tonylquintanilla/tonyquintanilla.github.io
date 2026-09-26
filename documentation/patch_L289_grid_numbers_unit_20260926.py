"""patch_L289_grid_numbers_unit_20260926.py -- the exhibit grid numbers carry their unit.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

WHAT IT CHANGES -- interactive.html only, all-or-nothing

    Tony, 2026-09-26, after the larger grid numbers went live: "looks
    good. only detail is that we should add the units, AU in this case."

    - Every grid number along the box edges, in the Explorer and every
      exhibit room, ends in " AU": "0.002 AU", "-30 AU".
    - The numbers are written out in full. Plotly's default shorthand
      would have read "50u AU" in Earth's frame (u for micro) and "200k
      AU" at the Oort cloud's edge; now they read "0.00005 AU" and
      "200,000 AU".
    - Size and colour are as the last patch set them: 12 px #9a9a9a
      except on a portrait phone.

    Every axis on the page is in AU: the exhibit rooms' frames, the grid
    chip ("grid 0.002 AU"), and the Explorer's hovers.

TESTED BEFORE DELIVERY on a copy of the gallery at d8bd18e2, as a
desktop, a portrait phone and a sideways phone: both layout builders
carry the unit and the full-number setting, and a drawn plot keeps them.
Plotly's own number formatting was checked from Earth's frame (0.0001
AU) to 200,000 AU. No page errors; the gallery maintenance run passed 16
of 16 on the patched copy. As before, the full rooms could not be drawn
in the sandbox, so the look is for Tony's eyes.

Built on gallery d8bd18e2 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded in the orrery's run record for the gallery card pass, section 3i.

Written September 26, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', '95679929619d7e155adc4347fac74070', 'bc7b001857414c909826ffdbae59dce8', [("the page's Updated stamp", b'        room re-reads it when the window turns)\n     Architecture: Option C viewer', b'        room re-reads it when the window turns)\n     Updated: September 26, 2026 with Anthropic\'s Claude Opus 5.5\n       (the grid numbers carry their unit, Tony\'s ruling of 2026-09-26:\n        "we should add the units, AU in this case." Every axis number in\n        the Explorer and the exhibit rooms ends in " AU", and is written\n        out in full -- 0.00005 AU, 200,000 AU -- rather than in Plotly\'s\n        default shorthand, which would have read 50u AU and 200k AU)\n     Architecture: Option C viewer'), ("the Explorer's axis numbers say AU", b"        title: { text: '', font: { size: 1 } },\n        tickfont: axisTickFont(),", b"        title: { text: '', font: { size: 1 } },\n        tickfont: axisTickFont(),\n        // The unit on every number (Tony, 2026-09-26), written in full.\n        ticksuffix: ' AU',\n        exponentformat: 'none',"), ("the exhibit rooms' axis numbers say AU", b"        tickfont: axisTickFont(),\n        // L-289 (rebuilt 2026-09-05): Plotly's tick numbers are back", b'        tickfont: axisTickFont(),\n        // The unit on every number (Tony, 2026-09-26), written in full:\n        // Plotly\'s shorthand would read 50u AU in Earth\'s frame and 200k\n        // AU at the Oort cloud\'s edge.\n        ticksuffix: " AU",\n        exponentformat: "none",\n        // L-289 (rebuilt 2026-09-05): Plotly\'s tick numbers are back')])]


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile("index.html") or here in ("documentation", "gallery", "tools"):
        return fail(
            "index.html is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % os.getcwd())

    results = []
    for name, expected, result, edits in FILES:
        if not os.path.isfile(name):
            return fail("%s is not here." % name)
        raw = open(name, "rb").read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        actual = hashlib.md5(content).hexdigest()
        if actual == result:
            return fail("this patch has already been applied to %s." % name)
        if actual != expected:
            return fail(
                "BASE MOVED. %s is not the file this patch was built\n"
                "         against (gallery d8bd18e2).\n"
                "         expected %s\n"
                "         found    %s\n"
                "         Tell Claude; do not edit the file by hand."
                % (name, expected, actual))
        out = content
        for label, old, new in edits:
            count = out.count(old)
            if count != 1:
                return fail("ANCHOR FAIL in %s: expected 1 match, found %d for: %s"
                            % (name, count, label))
            out = out.replace(old, new)
            print("  ok  %s: %s" % (name, label))
        if any(byt > 127 for byt in out):
            return fail("non-ASCII text would be written to %s; refusing" % name)
        if hashlib.md5(out).hexdigest() != result:
            return fail("%s would not be the file this patch was built and\n"
                        "         tested to produce." % name)
        print("  ok  %s is the file that was tested, and ASCII" % name)
        results.append((name, out.replace(b"\n", b"\r\n") if was_crlf else out, was_crlf))

    for name, data, was_crlf in results:
        with open(name, "wb") as handle:
            handle.write(data)
        print("  wrote %s (%d bytes)%s" % (name, len(data),
                                            " [CRLF, as found]" if was_crlf else ""))

    print("")
    print("patch applied to 1 file")
    print("")
    print("Stamps updated: the 'Updated' line at the top of interactive.html.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into the GALLERY's documentation/ folder")
    print("     (not the orrery's). It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 16 of 16 gating checkers to pass, as before.")
    print("  3. In GitHub Desktop, in the gallery, the change list should show")
    print("     interactive.html and this script under documentation/, plus")
    print("     whatever the maintenance run rewrites as usual. Commit and push.")
    print("  4. After the push: python gallery_maintenance_run.py --live")
    print("  5. On the desktop, after about ten minutes, reload the Sun: every")
    print("     number along the box edges ends in AU. Then Earth, where the")
    print("     numbers are small (0.00005 AU and the like), and the Explorer.")
    print("  6. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
