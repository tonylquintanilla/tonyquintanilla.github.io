"""patch_L283_2_wall_art_label_20260925.py -- L-283, the wall art's AI label.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run.

WHAT IT CHANGES -- one file, all-or-nothing

    palomas_orrery_wall.jpg
        Puts back the machine-readable label that says the image was made
        with AI. Tony's original, Gemini_palomas_orrery_logo.png, carries
        it as a short XMP text block written by Google; saving the crop
        as a JPEG on 2026-09-24 dropped it. This copies Google's block
        from the original, unchanged, into the JPEG. It reads:
            credit              Edited with Google AI
            digital source type composite with trained algorithmic media
                                (the IPTC code for an image made or
                                changed by AI)
            date created        2025-11-28 05:51:15 UTC
        Tony, 2026-09-25: Gemini made the first image and then his
        requested changes, so the version in use is Gemini's edit of its
        own earlier work, which is what Google's label says.

        The picture itself does not change: the block goes in beside it,
        and the patch checks that the decoded image is the same. The file
        grows from 96,687 to 97,516 bytes. index.html is not touched.

    NOT carried across: Google's signed Content Credentials (C2PA). Their
    signature is tied to the original file's exact bytes, and cropping
    breaks it. The original PNG in the repo keeps them.

TESTED BEFORE DELIVERY on a copy of the gallery at 199b8d9f: the result
is byte-identical to the file built here, a JPEG reader finds the four
fields above in it, and its decoded pixels match the served file's.

Built on gallery 199b8d9f at
https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded in the orrery's run record for the gallery card pass, section 3i.

Written September 25, 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

ART = "palomas_orrery_wall.jpg"
ORIGINAL = "Gemini_palomas_orrery_logo.png"
ART_BEFORE = "b030e3fa73292f7641f88fe4c20285cc"
ART_AFTER = "b76c025fd3890868890ef7cba598abb3"
ORIGINAL_MD5 = "bc78758ca42d011938c42b670adefeb0"
XMP_MD5 = "7866dbf887bb33666fc2345c034e3e6e"
XMP_HEADER = b"http://ns.adobe.com/xap/1.0/\x00"


def fail(msg):
    print("")
    print("FAILURE: %s" % msg)
    print("NOTHING was written.")
    print("Undo is Discard Changes in GitHub Desktop.")
    return 1


def xmp_from_png(data):
    """Google's XMP text block from the PNG's iTXt chunk, unchanged."""
    pos = 8
    while pos < len(data):
        size = int.from_bytes(data[pos:pos + 4], "big")
        kind = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + size]
        if kind == b"iTXt":
            keyword, rest = body.split(b"\x00", 1)
            if keyword == b"XML:com.adobe.xmp" and rest[0] == 0:
                rest = rest[2:]
                _language, rest = rest.split(b"\x00", 1)
                _translated, text = rest.split(b"\x00", 1)
                return text
        pos += 12 + size
    return None


def main():
    here = os.path.basename(os.path.abspath(os.getcwd())).lower()
    if not os.path.isfile("index.html") or here in ("documentation", "gallery", "tools"):
        return fail(
            "index.html is not here (%s).\n"
            "         Run this from the GALLERY repo root -- the folder that\n"
            "         holds index.html -- not from gallery/, tools/ or\n"
            "         documentation/, and not from the orrery repo."
            % os.getcwd())
    for name in (ART, ORIGINAL):
        if not os.path.isfile(name):
            return fail("%s is not at the repo root." % name)

    original = open(ORIGINAL, "rb").read()
    if hashlib.md5(original).hexdigest() != ORIGINAL_MD5:
        return fail("%s is not the original committed at a2f84a0.\n"
                    "         Tell Claude." % ORIGINAL)
    xmp = xmp_from_png(original)
    if xmp is None or hashlib.md5(xmp).hexdigest() != XMP_MD5:
        return fail("the label in %s is not the one this patch expects." % ORIGINAL)
    print("  ok  Google's label read from %s (%d bytes)" % (ORIGINAL, len(xmp)))

    art = open(ART, "rb").read()
    actual = hashlib.md5(art).hexdigest()
    if actual == ART_AFTER:
        return fail("this patch has already been applied: %s already\n"
                    "         carries the label." % ART)
    if actual != ART_BEFORE:
        return fail("BASE MOVED. %s is not the file this patch was built\n"
                    "         against (gallery 199b8d9f).\n"
                    "         expected %s\n"
                    "         found    %s\n"
                    "         Tell Claude; do not edit the file by hand."
                    % (ART, ART_BEFORE, actual))
    # The label goes in as an APP1 segment straight after the JFIF header,
    # which is where JPEG readers look for it.
    if art[:4] != b"\xff\xd8\xff\xe0" or art[6:11] != b"JFIF\x00":
        return fail("%s does not start the way this patch expects." % ART)
    app0_end = 4 + int.from_bytes(art[4:6], "big")
    payload = XMP_HEADER + xmp
    segment = b"\xff\xe1" + (len(payload) + 2).to_bytes(2, "big") + payload
    out = art[:app0_end] + segment + art[app0_end:]
    print("  ok  label placed after the JFIF header; image data unchanged")
    if hashlib.md5(out).hexdigest() != ART_AFTER:
        return fail("the result is not the file this patch was built and\n"
                    "         tested to produce.")
    print("  ok  the result is the file that was tested")

    with open(ART, "wb") as handle:
        handle.write(out)
    print("  wrote %s (%d bytes, was %d)" % (ART, len(out), len(art)))

    print("")
    print("patch applied to 1 file")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into documentation/. It has run.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect every gating checker to pass, as before.")
    print("  3. In GitHub Desktop the change list should show exactly two")
    print("     files: palomas_orrery_wall.jpg and this script under")
    print("     documentation/. Commit and push.")
    print("  4. After the push: python gallery_maintenance_run.py --live")
    print("  5. On the phone, after about ten minutes, close the page and")
    print("     open it again: the lobby should look exactly as before.")
    print("  6. Tell Claude the new gallery SHA.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 6 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
