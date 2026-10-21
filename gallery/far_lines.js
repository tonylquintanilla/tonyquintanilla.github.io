// gallery/far_lines.js -- a drawn line that reaches far past the view is
// cut to the view's box before the phone draws it (L-463).
//
// WHY. The Sun room's Galactic Plane is a ring and a pole line at 100,000
// AU, the outer edge of the Oort cloud. With the view framed on the Sun's
// corona, a tenth of an AU across, those points sit about a million times
// farther out than the box. A desktop's graphics chip draws such a line
// and cuts it at the box (gl-plot3d's clipToBounds). Tony's phone drew it
// as a wide pink band across the view (2026-10-21, three screenshots).
// Phone chips work at lower precision, so the GPU's own cut cannot be
// relied on for points that far out. The cure is to never hand the chip a
// line point far outside the box: the page cuts each far line to the box
// itself, every time the frame changes, and puts the full line back when
// the frame is large enough to hold it.
//
// WHAT IT CHANGES ON A DESKTOP. Nothing a visitor can see: the part cut
// away is the part gl-plot3d was already hiding at the box's edge.
//
// WHAT IT TOUCHES. Only traces drawn as lines ("lines" in their mode)
// whose farthest point lies more than FAR_FACTOR times the box's
// half-width from its centre. Markers are not touched. A line's point
// count never changes, so anything kept per point (a hover text) stays
// lined up: a point outside the box is either moved onto the box's edge,
// along the one segment that reaches the box, or blanked (null), which
// breaks the line there.
//
// WHY IT IS ITS OWN FILE. Logic that needs no browser lives in its own
// file (L-338), and documentation/smoke_far_lines.js tests it as a file.
//
// Written October 21, 2026 with Anthropic's Claude Opus 5.5.

(function (global) {
  "use strict";

  // A line is cut once its farthest point is this many half-widths from
  // the box's centre. Below it the line is left exactly as served. The
  // band appeared at about 700 (a 50 AU grid) and a million (0.1 AU); a
  // line just past the box is never touched.
  var FAR_FACTOR = 20;

  // The part of segment a->b inside the box lo..hi, as [t0, t1] along it
  // (0 at a, 1 at b), or null when the segment misses the box.
  // Liang-Barsky, one axis at a time.
  function segmentInBox(a, b, lo, hi) {
    var t0 = 0, t1 = 1;
    for (var k = 0; k < 3; k++) {
      var d = b[k] - a[k];
      if (d === 0) {
        if (a[k] < lo[k] || a[k] > hi[k]) { return null; }
        continue;
      }
      var ta = (lo[k] - a[k]) / d;
      var tb = (hi[k] - a[k]) / d;
      if (ta > tb) { var s = ta; ta = tb; tb = s; }
      if (ta > t0) { t0 = ta; }
      if (tb < t1) { t1 = tb; }
      if (t0 > t1) { return null; }
    }
    return [t0, t1];
  }

  function inside(p, lo, hi) {
    return p[0] >= lo[0] && p[0] <= hi[0] && p[1] >= lo[1] &&
           p[1] <= hi[1] && p[2] >= lo[2] && p[2] <= hi[2];
  }

  function at(a, b, t) {
    return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t];
  }

  // Cut one line to the box. xs, ys, zs: the line's points as served
  // (null entries are gaps and stay gaps). Returns new arrays of the same
  // length.
  function clipLine(xs, ys, zs, lo, hi) {
    var n = xs.length;
    var pts = [];
    for (var i = 0; i < n; i++) {
      var ok = xs[i] != null && ys[i] != null && zs[i] != null;
      pts.push(ok ? [xs[i], ys[i], zs[i]] : null);
    }
    var out = [];
    for (var j = 0; j < n; j++) {
      var p = pts[j];
      if (p === null || inside(p, lo, hi)) { out.push(p); continue; }
      // p is outside. Which of its two segments reach the box, and where
      // does each one meet it nearest p?
      var hits = [];
      var nb = [j - 1, j + 1];
      for (var m = 0; m < 2; m++) {
        var q = (nb[m] >= 0 && nb[m] < n) ? pts[nb[m]] : null;
        if (q === null) { continue; }
        var seg = segmentInBox(p, q, lo, hi);
        if (seg) { hits.push(at(p, q, seg[0])); }
      }
      if (hits.length === 0) { out.push(null); continue; }
      // One segment reaches the box: p moves onto its edge. Both do (the
      // line leaves the box for this one point and comes back): p moves
      // onto the first one's edge, and the second segment is drawn from
      // there. That piece is inside the box only near its ends; it is
      // rare, and only for a line with very few points.
      out.push(hits[0]);
    }
    return {
      x: out.map(function (p) { return p ? p[0] : null; }),
      y: out.map(function (p) { return p ? p[1] : null; }),
      z: out.map(function (p) { return p ? p[2] : null; })
    };
  }

  // How far a line's points reach from the box's centre, in half-widths:
  // the largest of |coordinate - centre| / half-width over the axes.
  function reach(xs, ys, zs, lo, hi) {
    var arrs = [xs, ys, zs], r = 0;
    for (var k = 0; k < 3; k++) {
      var c = (lo[k] + hi[k]) / 2, h = (hi[k] - lo[k]) / 2;
      if (!(h > 0)) { continue; }
      var a = arrs[k] || [];
      for (var i = 0; i < a.length; i++) {
        if (a[i] == null) { continue; }
        var v = Math.abs(a[i] - c) / h;
        if (v > r) { r = v; }
      }
    }
    return r;
  }

  // For every line trace in `served` (the traces as first drawn, never
  // the cut copies), what x, y and z it should be drawn with in the box
  // lo..hi. Returns { indices, x, y, z } ready for Plotly.restyle, listing
  // only the far lines: cut ones, and ones put back whole. `served` is an
  // object keyed by trace index; `lo` and `hi` are [x, y, z].
  function plan(served, lo, hi) {
    var res = { indices: [], x: [], y: [], z: [] };
    var keys = Object.keys(served);
    for (var i = 0; i < keys.length; i++) {
      var t = served[keys[i]];
      var far = reach(t.x, t.y, t.z, lo, hi) > FAR_FACTOR;
      var drawn = far ? clipLine(t.x, t.y, t.z, lo, hi)
                      : { x: t.x.slice(), y: t.y.slice(), z: t.z.slice() };
      res.indices.push(Number(keys[i]));
      res.x.push(drawn.x);
      res.y.push(drawn.y);
      res.z.push(drawn.z);
    }
    return res;
  }

  // The traces this file looks after, chosen once when the room is drawn:
  // lines whose points reach past FAR_FACTOR of the given box, or of any
  // box the room can frame. Kept by index, with a copy of their points as
  // served. A line that is never far is not kept and never restyled.
  function servedLines(traces, minHalf) {
    var kept = {};
    for (var i = 0; i < traces.length; i++) {
      var t = traces[i];
      if (!t || !/lines/.test(t.mode || "") || !t.x || !t.y || !t.z) { continue; }
      var lo = [-minHalf, -minHalf, -minHalf], hi = [minHalf, minHalf, minHalf];
      if (reach(t.x, t.y, t.z, lo, hi) <= FAR_FACTOR) { continue; }
      kept[i] = { x: t.x.slice(), y: t.y.slice(), z: t.z.slice() };
    }
    return kept;
  }

  global.GalleryFarLines = {
    FAR_FACTOR: FAR_FACTOR,
    segmentInBox: segmentInBox,
    clipLine: clipLine,
    reach: reach,
    plan: plan,
    servedLines: servedLines
  };

})(typeof window !== "undefined" ? window : globalThis);
