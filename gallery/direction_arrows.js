// gallery/direction_arrows.js -- a small arrowhead on each body's orbit or
// path in the Solar System room, a little ahead of the body, pointing the
// way it travels.
//
// WHY. Tony, 2026-10-26, at his phone: "a small directional arrow right on
// the orbit line near the objects showing the direction of travel of
// objects. This is to make clear what the orbit is." Of two styles drawn
// on the real room he chose B, a flat arrowhead lying in the orbit's own
// plane, "and double the distance from the object so that the arrow is
// not interpreted as part of the object but as a directional arrow."
// Then, from two renders of the opening view, 5 arrow lengths ahead, so
// the arrows clear the bodies' names.
//
// WHERE THE DIRECTION COMES FROM. Never typed. A drawn orbit is served as
// points in order of true anomaly (gallery/assembler/render_orbits.py,
// sweep_conic, 0 to 2 pi), and true anomaly grows in the direction the
// body moves, whichever way that is: Earth's run counterclockwise seen
// from the north, Halley's and Ikeya-Seki's clockwise. A path (a
// spacecraft's, or a comet's on an open path) is served in time order,
// the part flown and then the part predicted. So the arrow points from
// each point to the next.
//
// WHAT IT DRAWS. Three points, wing - tip - wing, as one short line. The
// tip lies on the drawn line, AHEAD arrowhead lengths along it from where
// the body is; the wings sweep back from the tip in the plane holding the
// line's direction and the Sun. The arrowhead's length is SIZE_FRACTION
// of the view's width, so it keeps its size on the screen as the view
// zooms; the page re-places it at every frame change. An arrow whose tip
// falls outside the view is not drawn (its points are null): there is
// nothing to point at, and a phone is never handed a line far outside
// the box (L-463).
//
// WHY IT IS ITS OWN FILE. Logic that needs no browser lives in its own
// file (L-338), and documentation/smoke_direction_arrows.js tests it as a
// file.
//
// Written October 26, 2026 with Anthropic's Claude Opus 5.5.

(function (global) {
  "use strict";

  // MODE-5 KNOBS.
  // The arrowhead's length, as a fraction of the view's width.
  var SIZE_FRACTION = 0.035;
  // How far ahead of the body its tip sits, in arrowhead lengths. The
  // trial render of 2026-10-26 had 1.6; Tony: "double the distance". At
  // 3.2 the inner planets' arrows fell under their own names in the
  // opening view, and Tony chose 5 from two renders of it (B).
  var AHEAD = 5;
  // The wings: how far back from the tip, and how far out to each side,
  // in arrowhead lengths.
  var WING_BACK = 0.9;
  var WING_SIDE = 0.55;

  function sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
  function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
  function len(a) { return Math.sqrt(dot(a, a)); }
  function cross(a, b) {
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  }
  function finite(p) {
    return p && isFinite(p[0]) && isFinite(p[1]) && isFinite(p[2]) &&
      p[0] !== null && p[1] !== null && p[2] !== null;
  }

  // The body's drawn lines as one list of points, in the served order,
  // with gaps (null) and repeated points dropped.
  function points(lines) {
    var out = [];
    (lines || []).forEach(function (l) {
      var n = Math.min((l.x || []).length, (l.y || []).length, (l.z || []).length);
      for (var i = 0; i < n; i++) {
        var p = [l.x[i], l.y[i], l.z[i]];
        if (!finite(p)) { continue; }
        var q = out[out.length - 1];
        if (q && q[0] === p[0] && q[1] === p[1] && q[2] === p[2]) { continue; }
        out.push(p);
      }
    });
    return out;
  }

  // A drawn orbit comes back to its first point; a path does not.
  function isClosed(P) {
    if (P.length < 4) { return false; }
    var a = P[0], b = P[P.length - 1];
    var size = Math.max(len(a), len(b), 1e-12);
    return len(sub(a, b)) <= 1e-6 * size;
  }

  // Where the body is on the line: the nearest point of any segment, as
  // {seg: index of the segment's first point, t: 0..1 along it}.
  function locate(P, m) {
    var best = null;
    for (var i = 0; i + 1 < P.length; i++) {
      var d = sub(P[i + 1], P[i]), dd = dot(d, d);
      var t = dd > 0 ? Math.max(0, Math.min(1, dot(sub(m, P[i]), d) / dd)) : 0;
      var q = [P[i][0] + d[0] * t, P[i][1] + d[1] * t, P[i][2] + d[2] * t];
      var e = len(sub(m, q));
      if (!best || e < best.err) { best = { seg: i, t: t, err: e }; }
    }
    return best;
  }

  // The point `dist` along the line from the body, forward (in the
  // served order), with the direction of travel there. A closed orbit
  // wraps round; a path that ends too soon gives null.
  function along(P, at, dist, closed) {
    var i = at.seg;
    var a = P[i], b = P[i + 1];
    var p = [a[0] + (b[0] - a[0]) * at.t, a[1] + (b[1] - a[1]) * at.t, a[2] + (b[2] - a[2]) * at.t];
    var s = 0, segs = P.length - 1;
    for (var k = 0; k <= segs; k++) {
      var q = P[i + 1];
      var d = sub(q, p), L = len(d);
      if (L > 0 && s + L >= dist) {
        var f = (dist - s) / L;
        return { tip: [p[0] + d[0] * f, p[1] + d[1] * f, p[2] + d[2] * f],
                 dir: [d[0] / L, d[1] / L, d[2] / L] };
      }
      s += L;
      p = q;
      i += 1;
      if (i + 1 >= P.length) {
        if (!closed) { return null; }
        i = 0;
      }
    }
    return null;
  }

  // The same, backward from the body, for a path the body is near the end
  // of: the tip sits behind the body, still pointing the way it travels.
  function behind(P, at, dist) {
    var R = P.slice().reverse();
    var back = { seg: R.length - 2 - at.seg, t: 1 - at.t };
    var r = along(R, back, dist, false);
    if (!r) { return null; }
    return { tip: r.tip, dir: [-r.dir[0], -r.dir[1], -r.dir[2]] };
  }

  // The arrowhead at `tip` pointing along `dir`, `L` long: three points.
  function head(tip, dir, L) {
    // The side direction: in the plane of the line and the Sun, square
    // to the line. A line pointing straight at the Sun has no such plane,
    // so then any direction square to it serves.
    var toSun = [-tip[0], -tip[1], -tip[2]];
    var k = dot(toSun, dir);
    var side = [toSun[0] - k * dir[0], toSun[1] - k * dir[1], toSun[2] - k * dir[2]];
    if (len(side) < 1e-9 * Math.max(len(toSun), 1e-12)) {
      side = cross(dir, Math.abs(dir[2]) < 0.9 ? [0, 0, 1] : [1, 0, 0]);
    }
    var n = len(side);
    side = [side[0] / n, side[1] / n, side[2] / n];
    var w1 = [], w2 = [];
    for (var c = 0; c < 3; c++) {
      var base = tip[c] - dir[c] * WING_BACK * L;
      w1.push(base + side[c] * WING_SIDE * L);
      w2.push(base - side[c] * WING_SIDE * L);
    }
    return { x: [w1[0], tip[0], w2[0]], y: [w1[1], tip[1], w2[1]], z: [w1[2], tip[2], w2[2]] };
  }

  var NONE = { x: [null, null, null], y: [null, null, null], z: [null, null, null] };

  // spec: {lines: [{x, y, z}, ...] as served, marker: [x, y, z]}.
  // lo, hi: the view's box. Returns the arrow's three points, all null
  // when it is not drawn, and why in .why.
  function place(spec, lo, hi) {
    var P = points(spec && spec.lines);
    var m = spec && spec.marker;
    if (P.length < 2 || !finite(m)) { return Object.assign({ why: "no line or no body" }, NONE); }
    var width = Math.max(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]);
    if (!(width > 0)) { return Object.assign({ why: "no view" }, NONE); }
    var L = SIZE_FRACTION * width;
    var at = locate(P, m);
    var closed = isClosed(P);
    var r = along(P, at, AHEAD * L, closed) || (closed ? null : behind(P, at, AHEAD * L));
    if (!r) { return Object.assign({ why: "the line is too short for the arrow" }, NONE); }
    for (var c = 0; c < 3; c++) {
      if (r.tip[c] < lo[c] || r.tip[c] > hi[c]) {
        return Object.assign({ why: "outside the view" }, NONE);
      }
    }
    var h = head(r.tip, r.dir, L);
    h.why = null;
    h.dir = r.dir;
    return h;
  }

  global.GalleryArrows = {
    place: place,
    points: points,
    isClosed: isClosed,
    SIZE_FRACTION: SIZE_FRACTION,
    AHEAD: AHEAD,
    WING_BACK: WING_BACK,
    WING_SIDE: WING_SIDE
  };
})(typeof window !== "undefined" ? window : this);
