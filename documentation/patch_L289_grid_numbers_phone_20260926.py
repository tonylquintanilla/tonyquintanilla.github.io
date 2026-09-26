"""patch_L289_grid_numbers_phone_20260926.py -- the larger grid numbers on the upright phone too.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

WHAT IT CHANGES -- interactive.html only, all-or-nothing

    Tony, 2026-09-26, from his own phone, with screenshots of Earth
    upright and sideways: "I think we should add the larger numbers to
    the upright phone view also because this is relevant too."

    - The grid numbers draw at 12 px in #9a9a9a on every screen, the
      upright phone included, where they had stayed at 9 px in #5a5a6a.
    - The numbers do show on an upright phone, along the left and bottom
      edges; the earlier comment said they fell off screen, which Tony's
      screenshot shows was wrong. The comment is corrected.
    - axisTickFont() stays as the one place the setting lives, serving
      the Explorer and the rooms, with the rooms still re-reading it when
      the window turns.

TESTED BEFORE DELIVERY on a copy of the gallery at 93d8ae9, as a desktop,
an upright phone and a sideways phone: both layout builders give 12 px
#9a9a9a with the AU unit on all three, and a drawn plot keeps it. No
page errors; the gallery maintenance run passed 16 of 16 on the patched
copy. The full rooms could not be drawn in the sandbox, so the look is
for Tony's eyes.

Built on gallery 93d8ae9 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded in the orrery's run record for the gallery card pass, section 3i.

Written September 26, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('interactive.html', 'bc7b001857414c909826ffdbae59dce8', '29370ed00a66b49ecdcc6fab65466546', [("the page's Updated stamp", b'        default shorthand, which would have read 50u AU and 200k AU)\n     Architecture: Option C viewer', b'        default shorthand, which would have read 50u AU and 200k AU)\n     Updated: September 26, 2026 with Anthropic\'s Claude Opus 5.5\n       (the portrait phone gets the larger grid numbers too, Tony\'s\n        ruling of 2026-09-26 from his own phone: "I think we should add\n        the larger numbers to the upright phone view also because this is\n        relevant too." The numbers do show on an upright phone, along the\n        left and bottom edges, which the earlier comment had wrong. Every\n        screen now draws them at 12 px in #9a9a9a)\n     Architecture: Option C viewer'), ('every screen gets the larger numbers', b'// The grid numbers along the box edges (Tony\'s ruling of 2026-09-26).\n// On a portrait phone they fall off screen, and the triad and grid chip\n// carry direction and spacing (L-289), so they keep their old small,\n// dim setting. Everywhere else they were too small and faint to read,\n// and draw at 12 px in the page\'s secondary grey (--text-secondary).\nfunction axisTickFont() {\n    return sunPhonePortrait() ? { size: 9, color: "#5a5a6a" }\n                              : { size: 12, color: "#9a9a9a" };\n}', b'// The grid numbers along the box edges (Tony\'s rulings of 2026-09-26).\n// At 9 px in #5a5a6a they were too small and faint to read. They draw at\n// 12 px in the page\'s secondary grey (--text-secondary) on every screen:\n// first everywhere but a portrait phone, then, from Tony\'s own phone,\n// the portrait phone too, where they show along the left and bottom\n// edges beside the triad and the grid chip. One function still serves\n// the Explorer and the rooms, and a room still re-reads it when the\n// window turns, so a later change needs one edit here.\nfunction axisTickFont() {\n    return { size: 12, color: "#9a9a9a" };\n}')])]


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
                "         against (gallery 93d8ae9).\n"
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
    print("  5. On the phone held upright, after about ten minutes, close the")
    print("     page and open it again, then open Earth: the numbers along the")
    print("     left and bottom edges are larger and lighter, as they are")
    print("     sideways. Look at the bottom-left corner, where the labels of")
    print("     two edges meet and were already crowded.")
    print("  6. Tell Claude the new gallery SHA and what you saw.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
