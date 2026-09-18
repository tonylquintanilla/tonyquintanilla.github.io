// gallery/arrival.js -- what a room opens on (L-334, piece 1; moved here
// by stage B).
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file. His reason is the size of
// interactive.html; the second reason is that a check can then reach it
// as a file. documentation/smoke_arrival.js used to test this function
// by cutting the text between two comment lines out of the page and
// running it, which is a check whose subject is a substring and which
// stops being true the moment a comment line moves.
//
// WHAT IT DOES. What is drawn when a room opens is read from the served
// "arrival" block of that room's object in data/objects_config.json.
//
// Tony's ruling, 2026-09-17: a room opens on "the surface shell plus
// frame elements like sun direction, axes, terminator", and the Moon
// starts "with its box not selected".
//
// Three kinds of trace, told apart by what the renderers stamped on
// them:
//   a SERVED SHELL   carries meta.shell_key -- the key it sits under in
//                    this object's served features. Drawn only if the
//                    arrival block's "drawn" list names that key.
//   the MOON         legend group "moon". Drawn only if "moon" is true.
//   a FRAME ELEMENT  no shell key, and not the Moon: the axis with the
//                    equator, the Sun direction, the terminator. Always
//                    drawn.
//
// ONE WAY OF MATCHING, NOT TWO. Until stage B a shell was found by the
// END of its legend group name, which was a second reading of the label
// formula feature_renderers.js builds, and a shell could match either by
// key or by name. feature_renderers.js now stamps the key onto every
// trace belonging to a served shell, so the name match is gone.
//
// THE COST OF THAT, stated because it is the failure this design can
// have: a shell trace that loses its stamp reads as a frame element and
// is DRAWN. documentation/smoke_arrival.js therefore checks that every
// trace the feature renderers build carries a key, and names by legend
// group any that does not.
//
// No arrival block, or one that cannot be read: nothing is changed,
// applied is false, and the page keeps its old arrival rule.
//
// Pure: no page elements and no Plotly, so the smoke check runs it in
// node.
//
// RUN THE CHECK:  node documentation/smoke_arrival.js   (from the root)
//
// Written September 2026 with Anthropic's Claude Opus 5.

(function (global) {
  "use strict";

  function applyArrival(traces, cfgText, slug) {
    var out = { applied: false, minHalfRangeAu: 0, drawn: [], unknown: [] };
    var cfgObj = null;
    try { cfgObj = JSON.parse(cfgText); } catch (e) { return out; }
    var objs = (cfgObj && Array.isArray(cfgObj.objects)) ? cfgObj.objects : [];
    var entry = null;
    for (var i = 0; i < objs.length; i++) {
      if (objs[i] && objs[i].slug === slug) { entry = objs[i]; }
    }
    var arr = entry ? entry.arrival : null;
    if (!arr || !Array.isArray(arr.drawn)) { return out; }

    // Every key the arrival block asks for, and whether anything answered
    // to it. A key nothing answers to is reported, not ignored: it is
    // usually a misspelling, and silence about it would leave the room
    // opening on less than the block says.
    var wanted = {};
    for (var d = 0; d < arr.drawn.length; d++) {
      if (typeof arr.drawn[d] === "string") { wanted[arr.drawn[d]] = false; }
    }

    var drawnGroups = {};
    for (var t = 0; t < traces.length; t++) {
      var trace = traces[t];
      if (!trace || typeof trace !== "object") { continue; }
      var group = trace.legendgroup;
      if (typeof group !== "string" || !group) { continue; }
      var show;
      if (group === "moon") {
        show = arr.moon === true;
      } else {
        var key = (trace.meta && typeof trace.meta === "object" &&
                   typeof trace.meta.shell_key === "string" &&
                   trace.meta.shell_key)
          ? trace.meta.shell_key : null;
        if (key === null) {
          show = true;            // a frame element
        } else {
          show = Object.prototype.hasOwnProperty.call(wanted, key);
          if (show) { wanted[key] = true; }
        }
      }
      trace.visible = show ? true : "legendonly";
      if (show) { drawnGroups[group] = true; }
    }

    out.applied = true;
    out.drawn = Object.keys(drawnGroups);
    for (var w in wanted) {
      if (Object.prototype.hasOwnProperty.call(wanted, w) && !wanted[w]) {
        out.unknown.push(w);
      }
    }
    if (typeof arr.min_half_range_au === "number" &&
        arr.min_half_range_au > 0) {
      out.minHalfRangeAu = arr.min_half_range_au;
    }
    return out;
  }

  global.GalleryArrival = { applyArrival: applyArrival };

})(typeof window !== "undefined" ? window : globalThis);
