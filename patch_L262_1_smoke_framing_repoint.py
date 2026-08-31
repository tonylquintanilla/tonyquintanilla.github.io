"""
patch_L262_1_smoke_framing_repoint.py

Run:  python patch_L262_1_smoke_framing_repoint.py
From: the GALLERY repo root (the folder holding gallery_maintenance_run.py
      and interactive.html).
In VS Code: open this file from that folder and click Run.

Built on gallery 1bf9845035f7ffac9ec2aa6e1e8c72899b2a7962 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io (branch main).

L-262. Two one-line edits. NEITHER TOUCHES A LIVE PAGE, so this needs no
Mode 5.

WHY.
  gallery_maintenance_run.py points the "Page framing" check at
  interactive.html. That page does not contain either of the two strings
  smoke_framing.js slices on -- verified at 1bf98450, zero occurrences of
  `function gridDtick(span) {` and zero of `async function fetchText(url) {`.
  The helpers live in gallery/solar_system_earth_test2.html, which has both.
  So the script exits at its ninth line with "FAIL: helpers not found in
  page", and that row's report_only field is False, which means it GATES.

  The page is not the only thing wrong with the invocation.
  smoke_framing.js also reads a second file at process.argv[3] to build
  window.GalleryFeatures, and the runner passes only one argument. Fixing
  the page alone would move the failure rather than clear it. The
  neighbouring "Sun shells" row already passes gallery/feature_renderers.js
  this way, so the corrected line follows house style.

  Third, smoke_framing.js reads payload_jupiter_saturn.json from the
  working directory. The runner's cwd for this row is the repo root and the
  file is in documentation/.

VERIFIED BEFORE THIS PATCH WAS WRITTEN, at gallery 1bf98450:
  node documentation/smoke_framing.js interactive.html
    -> "FAIL: helpers not found in page", exit 1
  the same script with both fixes, against the test page
    -> 12 checks, all OK, "ALL CHECKS PASSED", exit 0

WHAT THIS DOES NOT FIX, and it is recorded on L-262 rather than implied.
  Pointed correctly, the test guards a TEST page. The live exhibit's own
  framing -- sunRefitFrame in interactive.html -- still has no test, and
  L-267's GUI work adds more framing logic to exactly that file.

BACKUPS are written as .bak_L262, not .bak, on purpose: this repo already
TRACKS gallery_maintenance_run.py.bak, and a plain .bak would overwrite a
committed file. The script names that and two other tracked backups on the
way out.

SUCCESS looks like: two "ok" lines, a byte count each, then "PATCH APPLIED"
and the smoke test's own re-run instruction.
FAILURE looks like: one "ERROR" or "ANCHOR FAIL" line and NOTHING written.
This script is one-shot; a second run aborts on the fingerprints.
"""

import hashlib
import os
import sys

EXPECTED = {
    "gallery_maintenance_run.py": "6ee2a60704915a2f259bb12bbdf88597",
    "documentation/smoke_framing.js": "5874853de02a8fb85c6735b481139fb2",
}

# Backup files this repo TRACKS, which is why we do not write plain .bak.
TRACKED_BAKS = [
    "gallery_maintenance_run.py.bak",
    "interactive.html.bak",
    "gallery/feature_renderers.js.bak2",
]

RUNNER_OLD = b"""    ("Page framing", "node",
     ["documentation/smoke_framing.js", "interactive.html"],
     ".", None, False),"""

RUNNER_NEW = b"""    # L-262: the framing helpers live in the TEST page, not the live one --
    # interactive.html has neither slice marker. The second file supplies
    # window.GalleryFeatures at process.argv[3]; without it the script
    # throws once the page fix lets it get that far.
    ("Page framing", "node",
     ["documentation/smoke_framing.js",
      "gallery/solar_system_earth_test2.html",
      "gallery/feature_renderers.js"],
     ".", None, False),"""

SMOKE_OLD = b"""const p = JSON.parse(fs.readFileSync("payload_jupiter_saturn.json", "utf8"));"""

SMOKE_NEW = b"""// L-262: read relative to the repo root, which is the runner's cwd for
// this check. The payload lives beside this script in documentation/.
const p = JSON.parse(
  fs.readFileSync("documentation/payload_jupiter_saturn.json", "utf8"));"""


def die(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def main():
    if not os.path.exists("gallery_maintenance_run.py"):
        die("run this from the GALLERY repo root "
            "(no gallery_maintenance_run.py here).")

    files = {}
    print("BASE CHECK -- content fingerprints (CRLF-normalised)")
    for path, want in EXPECTED.items():
        if not os.path.exists(path):
            die("not found: %s" % path)
        with open(path, "rb") as f:
            raw = f.read()
        was_crlf = b"\r\n" in raw
        content = raw.replace(b"\r\n", b"\n") if was_crlf else raw
        got = hashlib.md5(content).hexdigest()
        if got != want:
            die("base moved for %s\n  expected %s\n  found    %s\n"
                "  Nothing was written." % (path, want, got))
        tag = "  [CRLF working copy; matched after normalising]" if was_crlf else ""
        print("  ok  %-34s %s%s" % (path, got, tag))
        files[path] = {"content": content, "crlf": was_crlf, "orig": raw}

    inserted = RUNNER_NEW + SMOKE_NEW
    if any(b > 127 for b in inserted):
        die("inserted text is not ASCII.")
    print("  ok  inserted text is ASCII (%d bytes)" % len(inserted))

    edits = [
        ("gallery_maintenance_run.py",
         "Page framing row -> test page + feature_renderers.js",
         RUNNER_OLD, RUNNER_NEW),
        ("documentation/smoke_framing.js",
         "payload path -> documentation/payload_jupiter_saturn.json",
         SMOKE_OLD, SMOKE_NEW),
    ]

    print("\nEDITS")
    for path, label, old, new in edits:
        content = files[path]["content"]
        n = content.count(old)
        if n != 1:
            print("ANCHOR FAIL (%d matches, expected 1): %s -- %s"
                  % (n, path, label))
            print("  anchor head: %r" % old[:70])
            print("NOTHING WAS WRITTEN.")
            sys.exit(1)
        files[path]["content"] = content.replace(old, new)
        print("  ok  %-52s %s" % (label, path))

    print("\nWRITE")
    for path in EXPECTED:
        out = files[path]["content"]
        if files[path]["crlf"]:
            out = out.replace(b"\n", b"\r\n")
        with open(path + ".bak_L262", "wb") as f:
            f.write(files[path]["orig"])
        with open(path, "wb") as f:
            f.write(out)
        print("  wrote %-34s %6d bytes (%+d)  [%s.bak_L262 written]"
              % (path, len(out), len(out) - len(files[path]["orig"]), path))

    print("\nPATCH APPLIED")
    print("\nCONFIRM IT, and this is the whole point of the fix:")
    print("  python gallery_maintenance_run.py")
    print("  The Page framing row should now PASS 12 checks. It has been")
    print("  a GATING row failing on every run that reached it.")

    print("\nSEPARATE FINDING, unrelated to this patch and not fixed by it.")
    print("  Three backup files are TRACKED in this public repo, which is")
    print("  why the backups above use .bak_L262 instead of .bak:")
    for b in TRACKED_BAKS:
        state = "present" if os.path.exists(b) else "listed but not on disk"
        print("    %-40s %s" % (b, state))
    print("  interactive.html.bak sits at the root of a GitHub Pages site,")
    print("  so a stale copy of the live page is served publicly.")
    print("  .gitignore covers *.json.bak only. Deleting them and widening")
    print("  the ignore rule is a Tony call, not this patch's business.")


if __name__ == "__main__":
    main()
