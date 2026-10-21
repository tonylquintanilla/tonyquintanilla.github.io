#!/usr/bin/env python3
"""
patch_L456_5_addresses_website_20261021.py -- L-456, the website's own
citations: the open addresses of the works they name, each re-opened on
2026-10-21, in the six citations the website writes itself (the mirror
writes the rest from the orrery).

Built on orrery 6a8d04c2ca0ba94a5fb2f5b70c3ebd82c0d934e3 at
https://github.com/tonylquintanilla/palomas_orrery and gallery
30db99fb5ec7c5f996f5adbbf10c23cad1c416a4 at
https://github.com/tonylquintanilla/tonyquintanilla.github.io.
Tony's local folders: orrery
C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\palomas_orrery_for_github\\
gallery C:\\Users\\tonyq\\OneDrive\\Desktop\\python_work\\tonyquintanilla.github.io\\
Written October 21, 2026 with Anthropic's Claude Opus 5.5. Record, in
the orrery: documentation/HANDOFF_L456_addresses_build_20261021.md.

RUN COMMAND

    python patch_L456_5_addresses_website_20261021.py

    Save this file in the GALLERY folder above, open it in VS Code and
    click Run. It takes no arguments and asks no questions. Run the
    orrery's patch_L456_4 and push it first, so the Daily Run pulls the
    orrery's new export.

WHAT IT DOES, all or nothing

    data/objects_config.json       seven edits, in place: the galactic
                                   pole (Murray's and Liu, Zhu and Hu's
                                   addresses, written twice: the tide's
                                   and the plane's), the galactic tide
                                   (Matese and Whitmire's, Higuchi's),
                                   Sgr A*'s place (Liu, Zhu and Hu's),
                                   the magnetotail (Slavin et al. 1985's
                                   DOI and the two NTRS copies),
                                   and Earth's fallback pole (the IERS
                                   Conventions and the Horizons manual)

    The file is checked only at the lines this patch edits; the mirror
    and the store editor write other lines of it and never make this
    patch refuse. Nothing is written unless every edit fits. The file
    is written LF. A visitor sees the change after the Daily Run's
    cache builder. Once this has run, move it into documentation/.

WHAT IT PRINTS

    Success: one "ok" line, then "patch applied" and what to do next.
    Failure: one ERROR or ANCHOR FAIL line and "NOTHING was written."

Undo is Discard Changes in GitHub Desktop.

Role: devtool
Domain: dev_tools
"""

FOLDER_WORD = "the gallery's"
NEXT = [
    "NEXT:",
    "  1. Move this script into documentation/ now, before the Daily",
    "     Run, which would otherwise list it as a module.",
    "  2. The Daily Run. Expect 31 of 31 gating and 'Source list' PASS;",
    "     the Config mirror writes the orrery's new addresses. Commit;",
    "     push; then the live run.",
    "  3. Your phone: the Sun and Earth i panels, tap a link in each.",
]

import hashlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

FILES = [
    {'path': 'data/objects_config.json', 'mode': 'edit', 'anchors_only': True, 'base_md5': None, 'new_md5': None, 'zone': None, 'edits': [('              "source_note": "drawn at the far end of that range",\n              "orrery_constant": "constants_new.py::OUTER_OORT_CLOUD_AU" },\n            "galactic_pole": {\n              "ra": { "value": 192.85948125, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_RA_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200." },\n              "dec": { "value": 27.128251111111112, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_DEC_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200.; NIST Special Publication 811, sec. 5.1.1, Table 6 -- the second of arc is one sixtieth of the minute of arc, which is one sixtieth of the degree, so a degree is 3600 arcseconds by definition." },\n              "source": "Murray (1989), the standard adopted for Hipparcos, as printed in Liu, Zhu and Hu, arXiv:1110.6268, eq. (2) -- the north galactic pole of J2000"', '              "source_note": "drawn at the far end of that range",\n              "orrery_constant": "constants_new.py::OUTER_OORT_CLOUD_AU" },\n            "galactic_pole": {\n              "ra": { "value": 192.85948125, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_RA_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200." },\n              "dec": { "value": 27.128251111111112, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_DEC_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200.; NIST Special Publication 811, sec. 5.1.1, Table 6 -- the second of arc is one sixtieth of the minute of arc, which is one sixtieth of the degree, so a degree is 3600 arcseconds by definition." },\n              "source": "Murray (1989), A&A 218, 325, sect. 7.1, https://ui.adsabs.harvard.edu/abs/1989A&A...218..325M/abstract, the standard adopted for Hipparcos, as printed in Liu, Zhu and Hu, A&A 536, A102, https://doi.org/10.1051/0004-6361/201116947 (arXiv:1110.6268), eq. (2) -- the north galactic pole of J2000"'), ('                "orrery_constant": "constants_new.py::OUTER_OORT_CLOUD_AU" },\n            "galactic_pole": {\n              "ra": { "value": 192.85948125, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_RA_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200." },\n              "dec": { "value": 27.128251111111112, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_DEC_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200.; NIST Special Publication 811, sec. 5.1.1, Table 6 -- the second of arc is one sixtieth of the minute of arc, which is one sixtieth of the degree, so a degree is 3600 arcseconds by definition." },\n              "source": "Murray (1989), the standard adopted for Hipparcos, as printed in Liu, Zhu and Hu, arXiv:1110.6268, eq. (2) -- the north galactic pole of J2000"', '                "orrery_constant": "constants_new.py::OUTER_OORT_CLOUD_AU" },\n            "galactic_pole": {\n              "ra": { "value": 192.85948125, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_RA_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200." },\n              "dec": { "value": 27.128251111111112, "unit": "deg", "figures": "exact",\n                "orrery_constant": "constants_new.py::GALACTIC_NORTH_POLE_DEC_J2000_DEG", "source": "Liu, Zhu and Hu, \\"Constructing a Galactic coordinate system based on near-infrared and radio catalogs\\", arXiv:1110.6268, eq. (2) -- the north galactic pole at J2000.0, alpha = 12h 51m 26.2755s, delta = +27 deg 07\' 41.704\\", as derived by Murray (1989) and adopted by the Hipparcos team as the standard transformation. The layer below: Murray, C. A. 1989, A&A 218, 325; ESA 1997, The Hipparcos and Tycho Catalogues, ESA SP-1200.; NIST Special Publication 811, sec. 5.1.1, Table 6 -- the second of arc is one sixtieth of the minute of arc, which is one sixtieth of the degree, so a degree is 3600 arcseconds by definition." },\n              "source": "Murray (1989), A&A 218, 325, sect. 7.1, https://ui.adsabs.harvard.edu/abs/1989A&A...218..325M/abstract, the standard adopted for Hipparcos, as printed in Liu, Zhu and Hu, A&A 536, A102, https://doi.org/10.1051/0004-6361/201116947 (arXiv:1110.6268), eq. (2) -- the north galactic pole of J2000"'), ("Matese and Whitmire, arXiv:1004.4584, sec. 2.2 -- the tide's main term goes as |sin B cos B|. Higuchi (2020), AJ 160:134, reads the pattern differently", "Matese and Whitmire, https://arxiv.org/abs/1004.4584, sec. 2.2 -- the tide's main term goes as |sin B cos B|. Higuchi (2020), AJ 160:134, https://arxiv.org/abs/2008.04324, reads the pattern differently"), ('near-infrared and radio catalogs\\", arXiv:1110.6268, sec. 3.2, eq. (8) -- the position of Sgr A*', 'near-infrared and radio catalogs\\", A&A 536, A102, https://doi.org/10.1051/0004-6361/201116947 (arXiv:1110.6268), sec. 3.2, eq. (8) -- the position of Sgr A*'), ("Geophys. Res. Lett. 10(10):973, doi:10.1029/GL010i010p00973 -- observed to 220 R_E. The tail's shape: Sibeck and Lin (2014), J. Geophys. Res. Space Physics 119, doi:10.1002/2013JA019471 -- the distant tail", "Geophys. Res. Lett. 10(10):973, doi:10.1029/GL010i010p00973, https://ntrs.nasa.gov/citations/19830066648 -- observed to 220 R_E. The tail's shape: Sibeck and Lin (2014), J. Geophys. Res. Space Physics 119, doi:10.1002/2013JA019471, https://ntrs.nasa.gov/api/citations/20140009185/downloads/20140009185.pdf -- the distant tail"), ("IERS Conventions (2010), IERS Technical Note 36, sec. 2.1.1, holds within about 0.02 arcseconds of Earth's mean pole at J2000.0, and which the Horizons manual's reference frames section describes", "IERS Conventions (2010), IERS Technical Note 36, sec. 2.1.1, https://iers-conventions.obspm.fr/content/tn36.pdf, holds within about 0.02 arcseconds of Earth's mean pole at J2000.0, and which the Horizons manual's reference frames section, https://ssd.jpl.nasa.gov/horizons/manual.html, describes"), ('Slavin et al. (1985), J. Geophys. Res. 90(A11):10875, doi:10.1029/JA090iA11p10875 -- ISEE-3:', 'Slavin et al. (1985), J. Geophys. Res. 90(A11):10875, https://doi.org/10.1029/JA090iA11p10875 -- ISEE-3:')]},
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
