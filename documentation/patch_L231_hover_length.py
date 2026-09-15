"""Shorten the hovers: the citation's head in the hover, the rest in the panel.

Targets, in the gallery repo:
  gallery/feature_renderers.js
  interactive.html
Built against gallery c2155b4525c7a27716abde3926ec7da376d31675.
Handle: L-231 follow-up.  2026-09-15, with Anthropic's Claude Opus 5.
Tony's report from the phone: the hover boxes are larger than the screen can
handle even at the best position.

WHAT WAS WRONG
--------------
Measured on the composed scene: the magnetopause hover ran to 29 lines, the
bow shock 32, the outer belt 27.  The house ceiling among the shells is 14
(the geostationary belt) and a plain shell is 6.  The biggest single block
in each was a full citation the information panel was ALREADY showing, so
the hover was duplicating it at length.

THREE CHANGES
-------------
1. sourceHead(): the hover carries everything before the first " -- ", which
   is the house separator between a citation and what was taken from it.
   The full string still rides in meta and the panel still shows all of it,
   unchanged.  Applied at every place a hover composes a Source line, not
   just the new ones.
2. The model's own equations leave the hover and ride in meta.detail, and
   interactive.html now renders that in the panel under the source.  That is
   where Tony asked for it: the panel is a click away and it scrolls.
3. The bow shock's three-line comparison with the magnetopause leaves the
   hover.  It is a remark rather than a figure; the served note carries it
   and the panel shows the note.

RESULT, measured the same way
-----------------------------
  magnetopause  29 -> 16 lines
  bow shock     32 -> 17
  outer belt    27 -> 23

WHAT IS STILL LONG, and why I stopped
-------------------------------------
The belt's remaining bulk is its served NOTE, not its citation -- about
seven lines of caveat.  Moving notes to the panel as well would bring
everything to about ten lines, but a caveat is the kind of thing a visitor
should meet at a glance rather than find behind a click.  That is a
judgment about what a reader must see, so it is Tony's call and not mine.

AFTER RUNNING
-------------
  node documentation/smoke_earth_geometry.js gallery/feature_renderers.js \
       gallery/earth_geometry.js
  node documentation/smoke_features.js gallery/feature_renderers.js
  Both: ALL CHECKS PASSED.  Then look at a hover on the phone, and open the
  information panel on the magnetopause to see the equations there.

UNDO: Discard Changes on the two files in GitHub Desktop."""

import hashlib
import os
import sys

FINGERPRINTS = {'gallery/feature_renderers.js': '85b7f31c5a72499437938b4fbfb1df70', 'interactive.html': '34a204cfe8fde6bf74a38aca80d13f22'}

EDITS = [
    ('gallery/feature_renderers.js', [
        (b"""        hover += "<br><br>" + wrapHover("Source: " + sources[i]);""",
         b"""        hover += "<br><br>" + wrapHover("Source: " + sourceHead(sources[i]));"""),
        (b"""   */
  function stampLink(traceList, cfg) {""",
         b"""   */
  /*
   * The head of a served source string: everything before the first " -- ",
   * which is the house separator between a citation and the explanation of
   * what was taken from it. L-231 follow-up, 2026-09-15: hovers had grown to
   * 27 and 32 lines on a phone against a house ceiling of about 14, and the
   * biggest single block was a citation the information panel was already
   * showing in full. So the HOVER carries the citation's head and the PANEL
   * carries the whole thing -- it rides in meta either way, unchanged.
   * A string with no " -- " is returned as it stands.
   */
  function sourceHead(src) {
    if (typeof src !== "string") return src;
    var cut = src.indexOf(" -- ");
    return (cut > 0) ? src.slice(0, cut) : src;
  }

  function stampLink(traceList, cfg) {"""),
        (b"""      meta.source = cfg.source;
    }""",
         b"""      meta.source = cfg.source;
    }
    // L-231 follow-up (2026-09-15): longer reference prose -- the model's
    // own equations, say -- rides here for the i-panel and stays OUT of the
    // hover, which has a phone-sized budget the panel does not.
    if (typeof cfg.detail === "string" && cfg.detail) {
      meta = meta || {};
      meta.detail = cfg.detail;
    }"""),
        (b"""             "keep pace with Earth's turning and hang over one longitude.";
    if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + cfg.source);
    if (cfg.note) hover += "<br>" + wrapHover(cfg.note);""",
         b"""             "keep pace with Earth's turning and hang over one longitude.";
    if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + sourceHead(cfg.source));
    if (cfg.note) hover += "<br>" + wrapHover(cfg.note);"""),
        (b"""      if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + cfg.source);""",
         b"""      if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + sourceHead(cfg.source));"""),
        (b"""      if (mpS._model) mpHover += "<br><br>" + wrapHover(mpS._model);
      if (mp.source) mpHover += "<br><br>" + wrapHover("Source: " + mp.source);""",
         b"""      if (mp.source) mpHover += "<br><br>" + wrapHover("Source: " + sourceHead(mp.source));"""),
        (b"""                { info_url: mp.info_url, source: mp.source });""",
         b"""                { info_url: mp.info_url, source: mp.source,
                  detail: mpS._model });"""),
        (b"""        "Ends wider and shorter than the magnetopause here -- that is<br>" +
        "two papers' drawing limits, not a fact about the two boundaries." +
        "<br>Not tilted: the fit is symmetric about the Sun line.";
      if (bsS._model) bsHover += "<br><br>" + wrapHover(bsS._model);
      if (bs.source) bsHover += "<br><br>" + wrapHover("Source: " + bs.source);""",
         b"""        // The three-line comparison with the magnetopause used to sit here.
        // It is a remark rather than a figure and the hover has a
        // phone-sized budget, so it moved to the served note, which the
        // i-panel shows in full.
        "Not tilted: the fit is symmetric about the Sun line.";
      if (bs.source) bsHover += "<br><br>" + wrapHover("Source: " + sourceHead(bs.source));"""),
        (b"""                { info_url: bs.info_url, source: bs.source });""",
         b"""                { info_url: bs.info_url, source: bs.source,
                  detail: bsS._model });"""),
    ]),
    ('interactive.html', [
        (b"""                source: (t.meta && typeof t.meta.source === "string") ? t.meta.source : null,
                indices: [],""",
         b"""                source: (t.meta && typeof t.meta.source === "string") ? t.meta.source : null,
                detail: (t.meta && typeof t.meta.detail === "string") ? t.meta.detail : null,
                indices: [],"""),
        (b"""            if (t.meta && typeof t.meta.source === "string") { byName[g].source = t.meta.source; }
        }""",
         b"""            if (t.meta && typeof t.meta.source === "string") { byName[g].source = t.meta.source; }
            if (t.meta && typeof t.meta.detail === "string") { byName[g].detail = t.meta.detail; }
        }"""),
        (b"""        box.appendChild(src);
    }
}
""",
         b"""        box.appendChild(src);
    }
    // L-231 follow-up (2026-09-15): longer reference prose -- a model's own
    // equations, say -- rides in meta.detail and is shown HERE rather than
    // in the hover. The hover has a phone-sized budget; this panel scrolls.
    if (grp.detail) {
        const det = document.createElement("div");
        det.className = "info-focus-empty";
        det.textContent = grp.detail;
        box.appendChild(det);
    }
}
"""),
    ]),
]

GUARD = [('gallery/feature_renderers.js', 'function sourceHead')]


def content_md5(data):
    return hashlib.md5(data.replace(b"\r\n", b"\n")).hexdigest()


def main():
    files = {}
    for path, expected in FINGERPRINTS.items():
        if not os.path.isfile(path):
            print("FAILURE: %s not found. Run this from the gallery repo root."
                  % path)
            print("NOTHING was written.")
            return 1
        with open(path, "rb") as handle:
            files[path] = handle.read()
        actual = content_md5(files[path])
        if actual != expected:
            print("FAILURE: BASE MOVED for %s." % path)
            print("  expected content md5 %s" % expected)
            print("  found                %s" % actual)
            print("  This patch is built against gallery c2155b45.")
            print("NOTHING was written.")
            return 1

    for path, needle in GUARD:
        if needle.encode("utf-8") in files[path]:
            print("FAILURE: this patch is already applied (%s in %s)."
                  % (needle, path))
            print("NOTHING was written.")
            return 1

    crlf = {p: files[p].count(b"\r\n") > 0 for p in files}

    def fit(path, block):
        return block.replace(b"\n", b"\r\n") if crlf[path] else block

    for path, edits in EDITS:
        staged = files[path]
        for n, (old, new) in enumerate(edits):
            count = staged.count(fit(path, old))
            if count != 1:
                print("FAILURE: in %s, hunk %d matched %d times, expected 1."
                      % (path, n + 1, count))
                print("NOTHING was written.")
                return 1
            staged = staged.replace(fit(path, old), fit(path, new))
        files[path] = staged

    for path in sorted(files):
        with open(path, "wb") as handle:
            handle.write(files[path])

    print("OK: %d file(s) written." % len(files))
    for path in sorted(files):
        print("    %-42s (%s)" % (path, "CRLF" if crlf[path] else "LF"))
    print()
    print("Next: run both node checkers, then look at a hover on the phone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
