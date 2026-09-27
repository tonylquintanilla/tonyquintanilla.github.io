"""patch_L363_2_studio_lists_quoted_room_keys_20260926.py -- GALLERY repo.

RUN COMMAND

    Save this file in the ROOT of the gallery repository
    (tonyquintanilla.github.io), beside index.html. Open it in VS Code
    and click Run. Close Gallery Studio first if it is open.

WHAT IT CHANGES -- one file, all-or-nothing

    tools/json_converter.py
        Studio's New Interactive Card lists the rooms it reads from
        interactive.html's EXHIBITS table. It read only keys written
        without quotes (sun, earth). The Solar System room's key has a
        hyphen, so JavaScript needs it in quotes ("solar-system"), and
        the list skipped it without saying so. It now reads a key with
        or without quotes. The gallery editor's live-link list reads
        the same function, so it gains the room too.

    Nothing the site serves changes.

TESTED BEFORE DELIVERY on a throwaway copy of the gallery at 8545cbd7:
    - The list before: interactive.html (the Explorer), earth, sun.
      After: the same three plus interactive.html?exhibit=solar-system.
    - add_live_card() wrote a card for the new room into Storage, and
      refused a second card for the same room, as it should.
    - Gallery Studio launched headless (xvfb) with no errors.

Built on gallery 8545cbd7d34b98f1de5ff93615c5da5e3e5b75c3
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
Recorded from orrery 907436a80ebf1c6d4b0dbcc0fc7da2ceed721ed6.
Written September 2026 with Anthropic's Claude Opus 5.5.
"""

import hashlib
import os
import sys

FILES = [('tools/json_converter.py', '09991ffaca6868f8f009e04806e9bc8d', '66995ada1409d1a920274329f2f9ae02', [("the module's update stamp", b'pass): a re-export keeps a card\'s shape "none" (not on the phone) instead\nof resetting it from the file\'s slot; that setting is Tony\'s, made in the\ngallery editor.\n\nRole: devtool\nDomain: gallery_pipeline\n', b'pass): a re-export keeps a card\'s shape "none" (not on the phone) instead\nof resetting it from the file\'s slot; that setting is Tony\'s, made in the\ngallery editor.\nModule updated: September 26, 2026 with Anthropic\'s Claude Opus 5.5 (L-363):\nlive_scene_urls() reads a room key written in quotes, as a key with a\nhyphen must be (`"solar-system": {`), so Studio\'s New Interactive Card\nlists the Solar System room.\n\nRole: devtool\nDomain: gallery_pipeline\n'), ('live_scene_urls() reads a quoted room key', b'    keys = set(re.findall(r\'EXHIBIT\\s*===?\\s*["\\\']([a-z0-9_-]+)["\\\']\', src))\n    table = re.search(r\'const EXHIBITS\\s*=\\s*\\{(.*?)\\n\\};\', src, re.S)\n    if table:\n        keys.update(re.findall(r\'^    ([a-z0-9_-]+):\\s*\\{\', table.group(1), re.M))\n    for key in sorted(keys):\n        if m and key == m.group(1):\n            continue\n', b'    keys = set(re.findall(r\'EXHIBIT\\s*===?\\s*["\\\']([a-z0-9_-]+)["\\\']\', src))\n    table = re.search(r\'const EXHIBITS\\s*=\\s*\\{(.*?)\\n\\};\', src, re.S)\n    if table:\n        # L-363 (2026-09-26): a key may be written in quotes. JavaScript\n        # needs them for a key with a hyphen, such as "solar-system", and\n        # the unquoted-only pattern missed that room silently.\n        keys.update(re.findall(r\'^    ["\\\']?([a-z0-9_-]+)["\\\']?:\\s*\\{\',\n                               table.group(1), re.M))\n    for key in sorted(keys):\n        if m and key == m.group(1):\n            continue\n')])]


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
                "         against (gallery 8545cbd7).\n"
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
    print("Stamps updated: the 'Module updated' line in tools/json_converter.py.")
    print("")
    print("WHAT TO DO NEXT, in this order:")
    print("")
    print("  1. Move THIS script into the GALLERY's documentation/ folder.")
    print("  2. Run the gallery maintenance run:")
    print("         python gallery_maintenance_run.py")
    print("     Expect 16 of 16, as before. None of them reads Studio's list.")
    print("  3. Open Gallery Studio. Click New Interactive Card... (the purple")
    print("     button). The scene list now includes")
    print("         interactive.html?exhibit=solar-system")
    print("     Pick it, give the title and placard, and create. The card")
    print("     lands in Storage.")
    print("  4. In the gallery editor: File > Reload from disk FIRST (an open")
    print("     editor does not see Studio's write, and its Save All would")
    print("     write over it). Then place the card in its room.")
    print("  5. Commit and push. Tell Claude the new gallery SHA.")
    print("")
    print("TONY-ACTION ROLLUP for this patch:")
    print("  (do)     steps 1 to 5 above.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
