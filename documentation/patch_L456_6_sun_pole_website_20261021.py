#!/usr/bin/env python3
"""
patch_L456_6_sun_pole_website_20261021.py -- L-456, the one website
citation the earlier copy of patch_L456_5 did not carry: the Sun's north
pole, re-homed to NASA NAIF's open planetary constants file, which gives
the IAU report's values (Archinal et al. 2018 is not free to read).

Built on gallery 53f17b6cb26e5be5ebd0256ffa2309c6e8901b7f at
https://github.com/tonylquintanilla/tonyquintanilla.github.io and orrery
6a8d04c2ca0ba94a5fb2f5b70c3ebd82c0d934e3 at
https://github.com/tonylquintanilla/palomas_orrery.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 21, 2026 with Anthropic's Claude Opus 5.5. Record, in
the orrery: documentation/HANDOFF_L456_addresses_build_20261021.md.

RUN COMMAND

    python patch_L456_6_sun_pole_website_20261021.py

    Save this file in the GALLERY folder above, open it in VS Code and
    click Run. It takes no arguments and asks no questions.

WHAT IT DOES

    data/objects_config.json       one edit, in place: the Sun's
                                   orientation citation names NASA NAIF's
                                   pck00011.tpc, with its address, and the
                                   IAU report as the layer below

    Checked only at the line it edits. Nothing is written unless the edit
    fits. Written LF. A visitor sees it after the Daily Run's cache
    builder. Once it has run, move it into documentation/.

WHAT IT PRINTS

    Success: one "ok" line, then "patch applied" and what to do next.
    Failure: one ANCHOR FAIL line and "NOTHING was written."

Undo is Discard Changes in GitHub Desktop.

Role: devtool
Domain: dev_tools
"""

FOLDER_WORD = "the gallery's"
NEXT = [
    "NEXT:",
    "  1. Move this script into documentation/ now.",
    "  2. Run the Daily Run AFTER the orrery's patch_L456_3 and patch_L456_4",
    "     are run and pushed, so its pull brings the orrery's addresses.",
    "     Commit; push; then the live run.",
]

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    {'path': 'data/objects_config.json', 'mode': 'edit', 'anchors_only': True, 'base_md5': None, 'new_md5': None, 'zone': None, 'edits': [('"source": "IAU 2018 (Archinal et al.), solar north pole in ICRF equatorial coordinates"', '"source": "NASA NAIF, planetary constants kernel pck00011.tpc (N. Bachman, 2022), https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/pck00011.tpc -- the Sun\'s north pole in ICRF equatorial coordinates (BODY10_POLE_RA, BODY10_POLE_DEC), as given in the IAU Working Group report of Archinal et al. (2018), Celest. Mech. Dyn. Astron. 130:22"')]},
]


def md5(text):
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def outside(text, zone):
    if not zone:
        return text
    i = text.index(zone[0])
    j = text.index(zone[1]) + len(zone[1])
    return text[:i] + text[j:]


def fail(message):
    print(message)
    print("NOTHING was written.")
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
                    print("ok  %-50s already present, the same" % rel)
                    continue
                return fail("ERROR: %s already exists and differs from what "
                            "this patch adds." % rel)
            planned.append((rel, path, f["content"]))
            print("ok  %-50s new file" % rel)
            continue
        if not os.path.exists(path):
            return fail("ERROR: %s is not here. Save this patch in %s "
                        "root folder." % (rel, FOLDER_WORD))
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
        zone = f.get("zone")
        have = md5(outside(text, zone))
        anchors_only = f.get("anchors_only", False)
        # A file Tony annotates (the ledger, Where We Are) is checked only
        # at the lines this patch edits, never by a fingerprint of the
        # whole file, so his notes never make the patch refuse.
        if anchors_only:
            pass
        elif have == f["new_md5"]:
            return fail("ERROR: %s already carries this patch's change. "
                        "It has run before." % rel)
        if not anchors_only and have != f["base_md5"]:
            return fail("ERROR: %s is not the version this patch was built "
                        "on (base moved). Compare it with the repository in "
                        "GitHub Desktop." % rel)
        for n, (old, new) in enumerate(f["edits"], 1):
            count = text.count(old)
            if count != 1:
                first = old.strip().splitlines()[0][:60] if old.strip() else ""
                return fail("ANCHOR FAIL: %s edit %d matched %d times: %r"
                            % (rel, n, count, first))
            text = text.replace(old, new)
        if not anchors_only and md5(outside(text, zone)) != f["new_md5"]:
            return fail("ERROR: %s came out different from the tested "
                        "result." % rel)
        planned.append((rel, path, text))
        print("ok  %-50s %d edit(s)" % (rel, len(f["edits"])))

    for rel, path, text in planned:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
    for note in notes:
        print(note)
    print("patch applied (%d file(s) written)" % len(planned))
    print("")
    for line in NEXT:
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
