"""Hover is the glance, the i panel is the record.

Targets, in the gallery repo:
  gallery/feature_renderers.js
  gallery/earth_geometry.js
  interactive.html
  documentation/smoke_earth_geometry.js
  documentation/smoke_features.js
  documentation/smoke_hover_budget.js
Built against gallery 1e53d9ef96ba861655db2d500a15a41bebd1016a.
Handle: L-231 follow-up.  2026-09-15, with Anthropic\'s Claude Opus 5.
Tony\'s ruling, from the phone: keep the Plotly box, make the hover text
brief, and point at the info "i" button. Uniform on every hover, because
the "i" button also carries the link out and people should learn it.

WHAT MOVES
----------
Every citation, every model equation and every served caveat leaves the
hover and lands in the i panel, which already follows the focus. Each
hover then ends with the same two lines:

  For more information and references please click on the
  info "i" button top right.

Nine hover builders in all -- five in the renderers, four in the scene
composer. The composer\'s four carried NO metadata at all, so the axis,
Sun line, terminator and Moon would have lost their citations in the
move; they now carry them.

NOTHING IS LOST. Checked rather than asserted: every served note reaches
the panel, all four of them, character for character.

RESULT
------
The worst hover in the scene goes from 23 lines to 17, and the surfaces
that started this -- the magnetopause at 29 and the bow shock at 32
earlier today -- are 14 and under. What is left in each hover is its own
prose, which is the author\'s to shorten, not a structural problem.

sourceHead() is gone. It was added this morning to keep a short citation
in the hover; no hover prints a citation now, so it has nothing to do.

FOUR CHECKS FOLLOW THE CONTENT
------------------------------
A leg required a "Source:" line in every Earth hover: it now requires the
pointer, and the leg beside it, unchanged, still requires the citation in
meta. A leg required the axis hover to cite the sense of rotation: it now
checks the hover states the sense in words and the citation is in the
panel. The budget suite gains a leg -- every hover we build points at the
panel -- and its ceiling drops to 17.

That new leg found two renderers I had missed on its first run, the ring
systems and the radius-fraction shells, and then a second pass found that
naming the assembler\'s traces by hand had missed one of two. It now
excludes them by where they came from, the payload\'s figure, rather than
by a name list that would have to be kept in step.

THE BUDGET SUITE IS NOT AN INSTRUCTION TO KEEP CUTTING. Its header now
says so, in Tony\'s words: we should not remove so much information that
it is less useful.

AFTER RUNNING
-------------
  python gallery_maintenance_run.py
  All seven gating checkers. Then Mode 5: a hover on the phone, and the
  "i" button with something focused, to see the citation, the equations
  and the caveat arrive together.

UNDO: Discard Changes on the six files in GitHub Desktop."""

import hashlib
import os
import sys

FINGERPRINTS = {'gallery/feature_renderers.js': '393daf7709fcd00d39acdef4371db696', 'gallery/earth_geometry.js': '8253d5e82d8a0b90d50bcb8feee9be7d', 'interactive.html': 'a50062e6453dea18fa4453d08a289ddf', 'documentation/smoke_earth_geometry.js': 'cb89396a71df47a1d6539df186684b58', 'documentation/smoke_features.js': 'c239e19dc80992118585f1ec1ea6804f', 'documentation/smoke_hover_budget.js': 'd3c3e7827a8bf446178cd880fce212cb'}

EDITS = [
    ('gallery/feature_renderers.js', [
        (b"""        "Drawn from the served cache; radii as measured.";
      traces.push(infoMarker(built.x[0], built.y[0], built.z[0],""",
         b"""        "Drawn from the served cache; radii as measured.";
      hover = withTail(hover);
      traces.push(infoMarker(built.x[0], built.y[0], built.z[0],"""),
        (b"""      if (sources[i]) {
        hover += "<br><br>" + wrapHover("Source: " + sourceHead(sources[i]));
      }
      // L-291 step 3: the served note travels too. Earth's belts are flux
      // PEAKS, not edges, and the hover is where that has to be said.
      if (notes[i]) {
        hover += "<br>" + wrapHover(notes[i]);
      }""",
         b"""      // L-231 follow-up (2026-09-15): the citation and the served note
      // both moved to the i panel. Earth's belts are flux PEAKS rather than
      // edges, which is what that note says, and the panel is where it is
      // said now -- with the pointer below telling the reader so.
      hover = withTail(hover);"""),
        (b"""      if (sources[i]) linkCfg.source = sources[i];
      traces.push(beltMarker);""",
         b"""      if (sources[i]) linkCfg.source = sources[i];
      // L-231 follow-up (2026-09-15): the belt's served note left the hover
      // with its citation. It says these are flux PEAKS rather than edges,
      // which is the whole point of the row, so it travels to the panel.
      if (notes[i]) linkCfg.note = notes[i];
      traces.push(beltMarker);"""),
        (b"""        kmAndAu((cfg.radius_fraction - 1.0) * radiusKm);
      var offPole = (Math.PI / 180) * INFO_MARKER_OFFSET_DEG;""",
         b"""        kmAndAu((cfg.radius_fraction - 1.0) * radiusKm);
      hover = withTail(hover);
      var offPole = (Math.PI / 180) * INFO_MARKER_OFFSET_DEG;"""),
        (b"""    }
    if (cfg.note) hover += "<br><br>" + wrapHover(cfg.note);
    traces.push(infoMarker(center[0] + m[0], center[1] + m[1],""",
         b"""    }
    traces.push(infoMarker(center[0] + m[0], center[1] + m[1],"""),
        (b"""    }
    if (cfg.note) hover += "<br><br>" + wrapHover(cfg.note);
    var color = cfg.color || "rgb(200, 200, 255)";""",
         b"""    }
    var color = cfg.color || "rgb(200, 200, 255)";"""),
        (b"""   * The head of a served source string: everything before the first " -- ",
   * which is the house separator between a citation and the explanation of
   * what was taken from it. L-231 follow-up, 2026-09-15: hovers had grown to
   * 27 and 32 lines on a phone against a house ceiling of about 14, and the
   * biggest single block was a citation the information panel was already
   * showing in full. So the HOVER carries the citation's head and the PANEL
   * carries the whole thing -- it rides in meta either way, unchanged.
   * A string with no " -- " is returned as it stands.""",
         b"""   * Every hover ends with the same line. Tony's ruling, 2026-09-15, after
   * seeing the boxes on a phone: the hover is the glance and the i panel is
   * the record. The citation, the model's own equations and the served
   * caveats all live in the panel now, which follows the focus and also
   * carries the link out. Uniform on EVERY hover, including the short ones
   * that have little waiting for them, because the point is that people
   * learn where the "i" button is.
   *
   * Exported as GalleryFeatures.HOVER_TAIL so earth_geometry.js ends its own
   * four hovers -- axis, Sun line, terminator, Moon -- with the same words
   * rather than a second copy that can drift."""),
        (b"""  function sourceHead(src) {
    if (typeof src !== "string") return src;
    var cut = src.indexOf(" -- ");
    return (cut > 0) ? src.slice(0, cut) : src;""",
         b'  var HOVER_TAIL = "For more information and references please click on " +\n                   "the<br>info \\"i\\" button top right.";\n\n  function withTail(hover) {\n    return hover + "<br><br>" + HOVER_TAIL;'),
        (b"""      meta.detail = cfg.detail;
    }""",
         b"""      meta.detail = cfg.detail;
    }
    // L-231 follow-up (2026-09-15): the served note rides here too, because
    // it left the hover with the citation. Losing it in the move would have
    // taken the caveats with it -- the magnetopause's "under storm
    // compression it can fall inside geostationary orbit", for one.
    if (typeof cfg.note === "string" && cfg.note) {
      meta = meta || {};
      meta.note = cfg.note;
    }"""),
        (b"""    if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + sourceHead(cfg.source));
    if (cfg.note) hover += "<br>" + wrapHover(cfg.note);""",
         b"""    hover = withTail(hover);"""),
        (b"""      if (cfg.source) hover += "<br><br>" + wrapHover("Source: " + sourceHead(cfg.source));
      if (cfg.note) hover += "<br>" + wrapHover(cfg.note);""",
         b"""      hover = withTail(hover);"""),
        (b"""      if (mp.source) mpHover += "<br><br>" + wrapHover("Source: " + sourceHead(mp.source));
      if (mp.note) mpHover += "<br>" + wrapHover(mp.note);""",
         b"""      mpHover = withTail(mpHover);"""),
        (b"""                  detail: mpS._model });""",
         b"""                  detail: mpS._model, note: mp.note });"""),
        (b"""      if (bs.source) bsHover += "<br><br>" + wrapHover("Source: " + sourceHead(bs.source));
      if (bs.note) bsHover += "<br>" + wrapHover(bs.note);""",
         b"""      bsHover = withTail(bsHover);"""),
        (b"""                  detail: bsS._model });""",
         b"""                  detail: bsS._model, note: bs.note });"""),
        (b"""    _KM_PER_AU: KM_PER_AU""",
         b"""    _KM_PER_AU: KM_PER_AU,
    // L-231 follow-up (2026-09-15): earth_geometry.js ends its own hovers
    // with these exact words rather than a second copy.
    HOVER_TAIL: HOVER_TAIL"""),
    ]),
    ('gallery/earth_geometry.js', [
        (b"""    };
    if (extra) { for (var k in extra) { if (extra.hasOwnProperty(k)) t[k] = extra[k]; } }
    return t;
  }

  function infoMarker(p, color, text, group, extra) {""",
         b"""    };
    if (extra) { for (var k in extra) { if (extra.hasOwnProperty(k)) t[k] = extra[k]; } }
    return t;
  }

  /*
   * The same closing line every hover in the scene ends with, read from
   * GalleryFeatures so the words exist once (L-231 follow-up, 2026-09-15).
   * If the renderers are not loaded this is empty rather than wrong, and
   * the hover budget suite's "every hover points at the i panel" leg fails,
   * which is the right way round.
   */
  function tail() {
    var GFx = global.GalleryFeatures;
    return (GFx && typeof GFx.HOVER_TAIL === "string")
      ? "<br><br>" + GFx.HOVER_TAIL : "";
  }

  function infoMarker(p, color, text, group, extra) {"""),
        (b"""        wrap("Sense: IAU WGCCRE, Archinal et al. (2018), Cel. Mech. Dyn. Astron. 130:22 -- Earth's prime-meridian angle W increases with time.") + "<br>" +
        wrap("Source: " + (pole.source || "pole source not served")) +
        (pole.orrery_constant ? "<br>" + wrap("Store: " + pole.orrery_constant) : "");
      traces.push(infoMarker(tip, AXIS_COLOR, hAxis, gAxis));""",
         b"""        tail();
      traces.push(infoMarker(tip, AXIS_COLOR, hAxis, gAxis, { meta: {
        source: "IAU WGCCRE, Archinal et al. (2018), Cel. Mech. Dyn. Astron. 130:22 -- the sense of rotation: Earth's prime-meridian angle W increases with time. Pole: " + (pole.source || "pole source not served"),
        detail: pole.orrery_constant ? "Store: " + pole.orrery_constant : null
      } }));"""),
        (b"""        "Line drawn to the edge of the arrival frame; the Sun is far beyond it.<br><br>" +
        wrap("Source: direction from Earth's heliocentric osculating elements in the served cache, JPL Horizons" +
             (isNum(opts.sun.elementsEpochJd) ? " (elements at JD " + opts.sun.elementsEpochJd.toFixed(1) + ")" : "") +
             ", propagated to the epoch by the assembler's Kepler solver (render_orbits.py).");
      traces.push(infoMarker(tipS, SUN_COLOR, hSun, gSun));""",
         b"""        "Line drawn to the edge of the arrival frame; the Sun is far beyond it." +
        tail();
      traces.push(infoMarker(tipS, SUN_COLOR, hSun, gSun, { meta: {
        source: "Direction from Earth's heliocentric osculating elements in the served cache, JPL Horizons" +
          (isNum(opts.sun.elementsEpochJd) ? " (elements at JD " + opts.sun.elementsEpochJd.toFixed(1) + ")" : "") +
          ", propagated to the epoch by the assembler's Kepler solver (render_orbits.py)."
      } }));"""),
        (b"""        wrap("Source: the Sun direction above, and the crust radius " +
             (opts.planetRadius && opts.planetRadius.source
               ? "(" + opts.planetRadius.source + ")" : "as served") + ".");
      traces.push(infoMarker(onCircle, TERMINATOR_COLOR, hTerm, gTerm));""",
         b"""        tail();
      traces.push(infoMarker(onCircle, TERMINATOR_COLOR, hTerm, gTerm, { meta: {
        source: "The Sun direction above, and the crust radius " +
          (opts.planetRadius && opts.planetRadius.source
            ? "(" + opts.planetRadius.source + ")" : "as served") + "."
      } }));"""),
        (b"""        wrap("Source: JPL Horizons osculating elements for the Moon about Earth, served in coverage_index.json with its measured trust window (two-body rate check against Horizons, gallery-cache-builder).");
      traces.push(infoMarker(pm, arc.color || "rgb(200, 200, 200)", hArc, gMoon));""",
         b"""        tail();
      traces.push(infoMarker(pm, arc.color || "rgb(200, 200, 200)", hArc, gMoon, { meta: {
        source: "JPL Horizons osculating elements for the Moon about Earth, served in coverage_index.json with its measured trust window (two-body rate check against Horizons, gallery-cache-builder)."
      } }));"""),
    ]),
    ('interactive.html', [
        (b"""                detail: (t.meta && typeof t.meta.detail === "string") ? t.meta.detail : null,
                indices: [],""",
         b"""                detail: (t.meta && typeof t.meta.detail === "string") ? t.meta.detail : null,
                note: (t.meta && typeof t.meta.note === "string") ? t.meta.note : null,
                indices: [],"""),
        (b"""            if (t.meta && typeof t.meta.detail === "string") { byName[g].detail = t.meta.detail; }
        }""",
         b"""            if (t.meta && typeof t.meta.detail === "string") { byName[g].detail = t.meta.detail; }
            if (t.meta && typeof t.meta.note === "string") { byName[g].note = t.meta.note; }
        }"""),
        (b"""// way the drawer handle does. It carries the name and the link OUT and
// nothing else: the cross marker's hover already has the radius and
// the citation, and the panel is not a second copy of it. The i button
// keeps one job -- open and close -- so this never opens the panel
// itself; it only keeps the contents current for when it is opened.""",
         b"""// way the drawer handle does. The i button keeps one job -- open and
// close -- so this never opens the panel itself; it only keeps the
// contents current for when it is opened.
//
// L-231 follow-up, 2026-09-15: the split between hover and panel is now
// the OPPOSITE of what this comment used to describe. It used to say the
// panel carried the name and the link and nothing else, because the hover
// already had the radius and the citation. On a phone those hovers ran to
// thirty lines and collided with the navigation cluster, so Tony ruled
// that the hover is the glance and the panel is the record: the hover
// keeps the figures and ends by pointing here, and the citation, the
// model's own equations and the served caveats all arrive below.
// The panel is deliberately a fuller copy now, not a second one."""),
        (b"""        box.appendChild(det);
    }""",
         b"""        box.appendChild(det);
    }
    // The served note -- the caveats. It left the hover with the citation
    // on 2026-09-15 and would have been lost in the move if it did not
    // land here: the magnetopause's "under storm compression it can fall
    // inside geostationary orbit" is a note, and it is the kind of thing a
    // reader should still be able to find.
    if (grp.note) {
        const nte = document.createElement("div");
        nte.className = "info-focus-empty";
        nte.textContent = grp.note;
        box.appendChild(nte);
    }"""),
    ]),
    ('documentation/smoke_earth_geometry.js', [
        (b"""check("axis hover cites the sense of rotation",
      /Archinal/.test(axisG.find(t => t.mode === "markers").text[0]));""",
         b"""// L-231 follow-up (2026-09-15): the CITATION for the sense moved to the i
// panel with every other citation. The hover still states the sense in
// words -- it has to, it is the thing the curved arrows mean -- so this leg
// now checks the statement in the hover and the citation where it went.
check("axis hover states the sense of rotation in words",
      /prograde, west to east/.test(axisG.find(t => t.mode === "markers").text[0]));
check("...and its citation is in the panel entry, not lost",
      /Archinal/.test((axisG.find(t => t.mode === "markers").meta || {}).source || ""));"""),
    ]),
    ('documentation/smoke_features.js', [
        (b"""const earthSourced = r1.traces.filter(t => t.showlegend !== true &&
                                          String(t.legendgroup || "").indexOf("Earth:") === 0 &&
                                          /Source:/.test(JSON.stringify(t.text || t.hovertext || "")));
check("every Earth info marker carries a Source line (14 of 14)",
      earthSourced.length === 14, "got " + earthSourced.length);""",
         b"""// L-231 follow-up (2026-09-15): this leg used to require a "Source:" line
// in every hover. The citations moved to the i panel -- Tony's ruling after
// seeing the boxes on a phone -- so the hover now ends with a pointer to
// the panel instead, and the leg below it, unchanged, is the one that
// asserts the citation itself is there in meta. Both halves still checked:
// the reader is told where to look, and something is waiting when they do.
const earthMarkers = r1.traces.filter(t => t.showlegend !== true &&
                                          String(t.legendgroup || "").indexOf("Earth:") === 0);
const earthPointed = earthMarkers.filter(t =>
    /button top right/.test(JSON.stringify(t.text || t.hovertext || "")));
check("every Earth info marker points the reader at the i panel (14 of 14)",
      earthPointed.length === 14,
      "got " + earthPointed.length + " of " + earthMarkers.length);"""),
    ]),
    ('documentation/smoke_hover_budget.js', [
        (b"""// it to admit a new hover is how the old ones got to 32. The intended
// budget is nearer 14, which is what the geostationary belt costs. What
// stands between here and there is the served NOTES -- the outer belt's
// caveat alone is about seven lines -- and whether a caveat belongs in the
// hover or behind the information panel's click is a judgment about what a
// visitor must see, recorded as open rather than decided here.""",
         b"""// it to admit a new hover is how the old ones got to 32.
//
// 2026-09-15, second pass: Tony ruled the split. The hover is the glance
// and the i panel is the record -- every citation, the model equations and
// the served caveats now live in the panel, and every hover ends with a
// line pointing there. That took the worst from 23 to 17, and the ceiling
// followed it down. What is left is each hover's OWN prose, which is the
// author's to shorten, not a structural problem to fix here.
//
// THIS SUITE IS NOT AN INSTRUCTION TO KEEP CUTTING. Tony, same day: "we
// should not remove so much information that it is less useful." The
// budget exists so a hover does not quietly grow to twice its neighbours
// again, not to grind them all down."""),
        (b"""const CEILING = 23;""",
         b"""const CEILING = 17;"""),
        (b"""const TARGET = 14;
""",
         b"""const TARGET = 14;

// The assembler's own traces (render_orbits.py) arrive inside the payload's
// FIGURE, not from these renderers, so they carry no pointer to the panel
// and it is not this file's business to add one. They are identified by
// being in the figure rather than by a name list: a list would have to be
// kept in step with the assembler, and the first version of this leg named
// one trace when there were two. smoke_features.js excludes the same
// traces from its border leg for the same reason.
"""),
        (b"""function collect(scene, traces) {""",
         b"""function collect(scene, traces, notOurs) {"""),
        (b"""            scene: scene,
            name: t.legendgroup || t.name || "(unnamed)",""",
         b"""            scene: scene,
            // The trace's own name as well as its group: the assembler's
            // marker sits in the "moon" group but is named for itself, and
            // that name is how it is told apart from ours.
            ours: !(notOurs && notOurs.has(t.name)),
            name: t.legendgroup || t.name || "(unnamed)","""),
        (b"""            chars: txt.length""",
         b"""            chars: txt.length,
            pointed: txt.indexOf("button top right") >= 0"""),
        (b"""    collect("earth room", out.traces);""",
         b"""    const fromAssembler = new Set(
        (p.figure && p.figure.data ? p.figure.data : [])
            .map(d => d.name).filter(Boolean));
    collect("earth room", out.traces, fromAssembler);"""),
        (b"""
check("no hover exceeds the ceiling of " + CEILING + " lines",""",
         b"""
check("every hover we build points the reader at the i panel",
      hovers.filter(h => h.ours && !h.pointed).length === 0,
      hovers.filter(h => h.ours && !h.pointed)
            .map(h => h.name).join(", ") || "all of them do");

check("no hover exceeds the ceiling of " + CEILING + " lines","""),
    ]),
]

GUARD = [('gallery/feature_renderers.js', 'HOVER_TAIL')]


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
    print("Next: python gallery_maintenance_run.py, then look at a hover and the i panel on the phone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
