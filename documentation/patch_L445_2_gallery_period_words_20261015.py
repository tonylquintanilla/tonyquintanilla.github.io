#!/usr/bin/env python3
"""
patch_L445_2_gallery_period_words_20261015.py -- L-445 (Earth's period),
the website's half: the period sentence says whose period it is when the
orrery serves one asked of another body. Earth's is the Earth-Moon
barycentre's: "Orbital period: 1.00000 years (365.25 days), for the
Earth-Moon center of mass, around the Sun, from JPL Horizons, fetched
<date>." A period served with no target_label prints as before.

Built on gallery 95713f4912d3e1863390a246d2ba8004bc7cf4c9 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io ("daily
run again"). The orrery's half is patch_L445_1_earth_period_20261015.py,
built on orrery 77245ea8 at
https://github.com/tonylquintanilla/palomas_orrery.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 15, 2026 with Anthropic's Claude Opus 5.5.

RUN COMMAND

    python patch_L445_2_gallery_period_words_20261015.py

    Save this file in the GALLERY folder above, open it in VS Code and
    click Run. It takes no arguments and asks no questions. Run it after
    the orrery's patch is pushed: the gallery's maintenance run pulls the
    orrery's export from GitHub, and that is what carries Earth's new
    period and its words.

WHAT IT DOES, all or nothing, in two files, each checked against the
file at 95713f49 before anything is written

    gallery/solar_system_figures.js
                    periodLine prints "for <whose>, " before the centre
    documentation/smoke_solar_system_figures.js
                    Earth's case, a sixth worked case, and a planted
                    fault: the words dropped

WHAT IT PRINTS

    Success: one "ok" line per file checked and per edit, then "patch
    applied". Failure: one ERROR or ANCHOR FAIL line and "NOTHING was
    written."

Undo is Discard Changes in GitHub Desktop.
"""

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SHA = '95713f49'
ZONES = {}
MARKERS = {}
FINGERPRINTS = {'documentation/smoke_solar_system_figures.js': 'a68cd8aa6dc7abcc648c3aeca260af15', 'gallery/solar_system_figures.js': '38d4432ed5e4cc2cf9c62de26cb115dc'}
RESULTS = {'documentation/smoke_solar_system_figures.js': 'b3fa5bd2c8f596e156ccce6fa26bcf07', 'gallery/solar_system_figures.js': '9a1755e981eba3b9fc5f0636f446bc7e'}
DELETES = {}
NEW_FILES = {}
EDITS = [('documentation/smoke_solar_system_figures.js', 'line 26: //   5. (L-431, build 3) The orbital period: s', "//      copy of the distance functions.\n//   5. (L-431, build 3) The orbital period: five worked cases (a period\n//      from JPL with separators, a typed one, none, one served with no\n//      centre, the Sun's null), and every drawer body's served period\n//      printed exactly as the orrery printed it -- each number the\n", "//      copy of the distance functions.\n//   5. (L-431, build 3) The orbital period: six worked cases (a period\n//      from JPL with separators, one asked of another body (L-445:\n//      Earth's, the Earth-Moon barycentre's, says so), a typed one, none,\n//      one served with no centre, the Sun's null), and every drawer\n//      body's served period\n//      printed exactly as the orrery printed it -- each number the\n"), ('documentation/smoke_solar_system_figures.js', 'line 40: //   period served with no centre shown anyway', "//   period printed to more figures than the export's count, and a\n//   period served with no centre shown anyway.\n//\n", "//   period printed to more figures than the export's count, and a\n//   period served with no centre shown anyway. Since L-445, a third: a\n//   period asked of another body printed as the body's own.\n//\n"), ('documentation/smoke_solar_system_figures.js', "line 45: // Updated October 15, 2026 with Anthropic's C", '// 3: the orbital period, part 5).\n\n', "// 3: the orbital period, part 5).\n// Updated October 15, 2026 with Anthropic's Claude Opus 5.5 (L-445: Earth's\n// period, asked of the Earth-Moon barycentre, says whose it is; a sixth\n// worked case and a planted fault.)\n\n"), ('documentation/smoke_solar_system_figures.js', "line 161: // L-445: Earth's period is the Earth-Moon bar", '    "fetched from JPL.");\n  want("no period", lib.periodLine({ kind: "none",\n', '    "fetched from JPL.");\n  // L-445: Earth\'s period is the Earth-Moon barycentre\'s, and says so;\n  // the orrery\'s hover prints the same words before the centre. Fixture\n  // figures, in the form the orrery prints JPL\'s PR for target 3.\n  want("a period asked of another body", lib.periodLine({\n    kind: "fetched", center: "@sun", center_label: "the Sun",\n    target: "3", target_label: "the Earth-Moon center of mass",\n    fetched: "2026-10-15",\n    years: { value: 1, figures: 6, text: "1.00000" },\n    days: { value: 365.25, figures: 5, text: "365.25" } }),\n    "Orbital period: 1.00000 years (365.25 days), for the Earth-Moon " +\n    "center of mass, around the Sun, from JPL Horizons, fetched " +\n    "2026-10-15.");\n  want("no period", lib.periodLine({ kind: "none",\n'), ('documentation/smoke_solar_system_figures.js', 'line 213: "if (false) {"],', '   "if (!period.center || !period.center_label) {",\n   "if (false) {"]\n].forEach(function (fault) {\n', '   "if (!period.center || !period.center_label) {",\n   "if (false) {"],\n  ["a period asked of another body printed as the body\'s own",\n   "period.target_label) ? \\"for \\" + period.target_label + \\", \\"",\n   "false) ? \\"for \\" + period.target_label + \\", \\""]\n].forEach(function (fault) {\n'), ('documentation/smoke_solar_system_figures.js', 'line 227: "print to more figures than the export\'s count', '            "sentence printed for a body with a row; the period\'s on a " +\n            "print to more figures than the export\'s count and on a " +\n            "period with no centre shown.");\n\n', '            "sentence printed for a body with a row; the period\'s on a " +\n            "print to more figures than the export\'s count, on a " +\n            "period with no centre shown, and on a period asked of " +\n            "another body printed as the body\'s own.");\n\n'), ('documentation/smoke_solar_system_figures.js', 'line 378: "JPL\'s ten-thousands place; 6 period cases and', '            " served distances; Uranus, Neptune and Pluto print to " +\n            "JPL\'s ten-thousands place; 5 period cases and " +\n            periods.length + " served periods printed as the orrery " +\n', '            " served distances; Uranus, Neptune and Pluto print to " +\n            "JPL\'s ten-thousands place; 6 period cases and " +\n            periods.length + " served periods printed as the orrery " +\n'), ('gallery/solar_system_figures.js', 'line 62: //', '// from JPL."; none says it has not been fetched yet; the Sun has none.\n\n', '// from JPL."; none says it has not been fetched yet; the Sun has none.\n//\n// WHOSE PERIOD (L-445, October 15, 2026). Earth\'s period is JPL\'s for the\n// Earth-Moon barycentre, not Earth\'s centre (Tony\'s ruling of\n// 2026-10-15: "Confirmed as recommended, the barycenter."). The orrery\n// serves "target_label" on a period asked of another body than the one\n// shown, and null otherwise, and this file prints it before the centre,\n// as the orrery\'s hover does: "..., for the Earth-Moon center of mass,\n// around the Sun, from JPL Horizons, fetched <date>." A period served\n// with no target_label prints as before.\n\n'), ('gallery/solar_system_figures.js', 'line 225: // L-445: whose period it is, when it is anoth', '    }\n    return { line: "Orbital period: " + shown + ", around " +\n                   period.center_label + ", from JPL Horizons, fetched " +\n', '    }\n    // L-445: whose period it is, when it is another body\'s.\n    var whose = (typeof period.target_label === "string" &&\n                 period.target_label) ? "for " + period.target_label + ", "\n                                      : "";\n    return { line: "Orbital period: " + shown + ", " + whose + "around " +\n                   period.center_label + ", from JPL Horizons, fetched " +\n')]


class PatchError(Exception):
    pass


def read(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        raise PatchError("missing file: %s (is this the right folder?)" % rel)
    raw = open(path, "rb").read()
    return raw.replace(b"\r\n", b"\n").decode("utf-8"), (b"\r\n" in raw)


def fingerprint(rel, text):
    zone = ZONES.get(rel)
    if zone:
        a = text.index(zone[0])
        b = text.index(zone[1]) + len(zone[1])
        text = text[:a] + text[b:]
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def main():
    log, notes, texts, crlf = [], [], {}, {}
    try:
        for rel, content in NEW_FILES.items():
            if os.path.exists(os.path.join(ROOT, rel)):
                have, _c = read(rel)
                if have != content:
                    raise PatchError("%s already exists with other content; "
                                     "nothing was overwritten" % rel)
                notes.append("note: %s already present, identical" % rel)
            else:
                log.append("ok  new     %s" % rel)
        for rel, want in DELETES.items():
            path = os.path.join(ROOT, rel)
            if not os.path.exists(path):
                notes.append("note: %s is already gone" % rel)
                continue
            have, _c = read(rel)
            if hashlib.md5(have.encode("utf-8")).hexdigest() != want:
                raise PatchError("%s is not the file this patch removes "
                                 "(its content changed); nothing was written"
                                 % rel)
            log.append("ok  delete  %s" % rel)
        for rel in sorted(set(e[0] for e in EDITS)):
            texts[rel], crlf[rel] = read(rel)
        for rel, want in FINGERPRINTS.items():
            if fingerprint(rel, texts[rel]) != want:
                raise PatchError("BASE MOVED: %s is not the file this patch "
                                 "was built against (%s)" % (rel, SHA))
            log.append("ok  base    %s matches %s" % (rel, SHA))
        for rel, label, old, new in EDITS:
            text = texts[rel]
            n = text.count(old)
            if n != 1:
                raise PatchError("ANCHOR FAIL [%s %s]: %d matches"
                                 % (rel, label, n))
            mark = MARKERS.get(rel)
            if mark and (text.count(mark) != 1
                         or text.index(old) + len(old) > text.index(mark)):
                raise PatchError("ANCHOR FAIL [%s %s]: not above the "
                                 "run-record marker" % (rel, label))
            texts[rel] = text.replace(old, new)
            log.append("ok  edit    %-44s %s" % (rel, label))
        for rel, want in RESULTS.items():
            if fingerprint(rel, texts[rel]) != want:
                raise PatchError("%s did not come out as built" % rel)
        for rel, text in list(texts.items()) + list(NEW_FILES.items()):
            bad = sum(1 for ch in text if ord(ch) > 127)
            if bad:
                raise PatchError("%s: %d non-ASCII character(s) after the "
                                 "edits" % (rel, bad))
    except PatchError as exc:
        print("ERROR: %s" % exc)
        print("NOTHING was written.")
        print("Undo is not needed. Discard Changes in GitHub Desktop restores "
              "any file you changed by hand.")
        sys.exit(1)

    for rel, content in NEW_FILES.items():
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
    for rel, text in texts.items():
        with open(os.path.join(ROOT, rel), "wb") as handle:
            handle.write(text.encode("utf-8"))
        if crlf[rel]:
            notes.append("note: %s was CRLF in the working copy; written LF"
                         % rel)
    for rel in DELETES:
        path = os.path.join(ROOT, rel)
        if os.path.exists(path):
            os.remove(path)
            folder = os.path.dirname(path)
            if folder != ROOT and not os.listdir(folder):
                os.rmdir(folder)
                log.append("ok  delete  %s/ (now empty)"
                           % os.path.relpath(folder, ROOT).replace(os.sep, "/"))
    for line in log:
        print(line)
    for line in notes:
        print(line)
    print("stamps updated: the header comments of gallery/solar_system_figures.js and documentation/smoke_solar_system_figures.js")
    print("")
    print("patch applied (%d new files, %d edits in %d files, %d deleted)"
          % (len(NEW_FILES), len(EDITS), len(texts), len(DELETES)))
    print("")
    print("NEXT:")
    print('  1. Run gallery_maintenance_run.py. The Objects export pull brings the')
    print("     orrery's new export; look for the Solar System figures row")
    print("     printing Earth 'for the Earth-Moon center of mass'.")
    print('  2. Move this script into documentation/; commit; push.')
    print("  3. Look at Earth's hover in the Solar System room and the Earth room.")
    print("Undo is Discard Changes in GitHub Desktop.")


if __name__ == "__main__":
    main()
