// gallery/view_centre.js -- where the Solar System room's view is centred,
// as logic that needs no browser (L-515 step 2b, part 2; L-338: logic
// that needs no browser lives in its own file, so a check can reach it).
//
// WHAT IT DECIDES. Tony's rulings of 2026-11-09 (L-515):
//   15  "Centre on <body>" moves the view so the body sits in the middle
//       (picture A): every orbit still drawn around what JPL measured it
//       around; nothing new is asked of JPL and nothing is measured from
//       the centre.
//   16  It opens the body's OWN served opening (its arrival block; the
//       Sun's is ?exhibit=sun's, the photosphere and the rotation axis).
//       What was ticked stays ticked; Home and Reset return to the Sun's
//       view.
//   17  The three axis lines and their x marks run through the middle, in
//       the Sun's directions; the frame note says where they cross.
//   20  The drawer's top line is a path down the tree: every part but the
//       last a centre, a link to that centre's opening, ticks kept; the
//       last what is in focus, bold, no link; "Solar system" alone on
//       opening.
//
// THE SHIFT (method, the brief's). A phone's WebGL holds positions as
// 32-bit floats, about seven digits: measured with Math.fround on the
// served positions of 2026-11-10, Earth sits 5 km off at 0.99 AU, Jupiter
// 18 km at 5.3 AU, the Pluto system 121 km at 35.6 AU, and Charon 170 km
// -- against Pluto's 1,188 km radius. So before a centred or close view is
// drawn the page moves the WHOLE drawing so the middle sits at the scene's
// origin, in 64-bit numbers: every trace's absolute points, kept once,
// minus the middle (shifted). Moving our own drawing is not the retired
// subtraction of two JPL answers: the absolute points are kept whole and
// every shifted copy is made from them. Every reader of a trace's
// positions agrees on the shift by reading the shifted plot: the frame
// (ranges always [-r, r] about the plot's origin, the middle), the count
// line, the axis lines, the text box's anchor. The two that keep copies
// of their own -- the direction arrows and the far lines -- are handed the
// view's box in absolute points (absBox) and give back shifted ones
// (shiftedParts).
//
// Written November 10, 2026 with Anthropic's Claude Opus 5.5. Updated
// November 10, 2026, afternoon, with Anthropic's Claude Opus 5.5 (Tony's
// phone look of step 2b: throughPoint, a body's place put into its own
// drawn line so a centred orbit runs through its body).

(function (global) {
  "use strict";

  var ROOT_KEY = "center";   // the Sun's row and the Sun's view

  var WORDS = {
    root: "Solar system",
    sep: " > ",
    // Ruling 17's line for the frame note; words for Tony's phone look.
    cross: function (name) { return "In this view the lines cross at " + name + "."; }
  };

  function isNum(v) { return typeof v === "number" && isFinite(v); }

  // One axis's points less the middle's; a gap (null) stays a gap.
  function shiftLine(arr, d) {
    if (!Array.isArray(arr)) { return arr; }
    var out = new Array(arr.length);
    for (var i = 0; i < arr.length; i++) {
      var v = arr[i];
      out[i] = (v === null || v === undefined || !isNum(v)) ? v : v - d;
    }
    return out;
  }

  // {x, y, z} absolute -> the same moved so `mid` is the origin.
  function shifted(abs, mid) {
    var m = mid || [0, 0, 0];
    return { x: shiftLine(abs.x, m[0]), y: shiftLine(abs.y, m[1]),
             z: shiftLine(abs.z, m[2]) };
  }

  // The view's box, given in the plot's (shifted) points, in absolute ones.
  function absBox(lo, hi, mid) {
    var m = mid || [0, 0, 0];
    return { lo: [lo[0] + m[0], lo[1] + m[1], lo[2] + m[2]],
             hi: [hi[0] + m[0], hi[1] + m[1], hi[2] + m[2]] };
  }

  // A list of absolute {x, y, z} parts (an arrow, a cut line) shifted.
  function shiftedParts(xs, ys, zs, mid) {
    var m = mid || [0, 0, 0];
    return { x: xs.map(function (a) { return shiftLine(a, m[0]); }),
             y: ys.map(function (a) { return shiftLine(a, m[1]); }),
             z: zs.map(function (a) { return shiftLine(a, m[2]); }) };
  }

  // How far a 32-bit float puts a point from where it is, in km (the
  // precision measurement, Math.fround on each coordinate).
  function float32ErrorKm(pos, kmPerAu) {
    var s = 0;
    for (var i = 0; i < 3; i++) {
      var d = Math.fround(pos[i]) - pos[i];
      s += d * d;
    }
    return Math.sqrt(s) * kmPerAu;
  }

  // THE TRAIL (ruling 20). The path down the tree to what is in focus:
  // the root, then each row above the focus (a row's "under", its parent
  // body), then the focus. rowOf(key) gives the drawer's row, or null; the
  // Sun's own shells sit directly under the root. A focus of null, or the
  // Sun, is the root alone. A loop stops at the first repeat.
  function trailPath(rowOf, focus) {
    if (!focus || focus === ROOT_KEY) { return [ROOT_KEY]; }
    var chain = [];
    var k = focus;
    while (k && k !== ROOT_KEY && chain.indexOf(k) < 0) {
      chain.unshift(k);
      var r = rowOf(k);
      k = r && r.under ? r.under : null;
    }
    return [ROOT_KEY].concat(chain);
  }

  // The parts the page draws: [{text, key, link, bold}]. Every part but
  // the last links to its centre's opening (the root's is the Sun's view);
  // the last is bold and links nowhere. nameOf(key) is the row's name; a
  // name opening with its parent's name and ": " (the Sun's shells, "Sun:
  // Photosphere") is shown without it.
  function trailParts(path, nameOf) {
    var out = [];
    for (var i = 0; i < path.length; i++) {
      var key = path[i];
      var text = key === ROOT_KEY ? WORDS.root : String(nameOf(key) || key);
      if (i > 0) {
        var parent = path[i - 1] === ROOT_KEY ? "Sun" : String(nameOf(path[i - 1]) || "");
        if (parent && text.indexOf(parent + ": ") === 0) { text = text.slice(parent.length + 2); }
      }
      var last = i === path.length - 1;
      out.push({ text: text, key: key, link: !last, bold: last });
    }
    return out;
  }

  // WHAT CENTRE ON TICKS (ruling 16): the centre's own row (its symbol;
  // the Sun's is fixed and always drawn), each of its shells its opening
  // names, its frame elements (the Sun's rotation axis, drawn with its
  // opening as ?exhibit=sun draws it), and, where its opening serves moon
  // true, what circles it. Nothing is unticked: what was ticked stays
  // ticked. rows: the drawer's rows; arrival: the centre's served block or
  // null; shellsOf: [{key, shellKey, frameElement}] for the centre's shell
  // rows; children: the row keys folded under it. Returns {keys, focus,
  // unknown}: focus the row the opening is about (the first shell it names,
  // else the centre), unknown the names in drawn that are no shell row.
  function openingKeys(centre, arrival, shellsOf, children) {
    var keys = [], unknown = [];
    var drawn = (arrival && Array.isArray(arrival.drawn)) ? arrival.drawn : [];
    if (centre !== ROOT_KEY) { keys.push(centre); }
    var focus = null;
    drawn.forEach(function (name) {
      var hit = (shellsOf || []).filter(function (s) { return s.shellKey === name; })[0];
      if (!hit) { unknown.push(name); return; }
      if (keys.indexOf(hit.key) < 0) { keys.push(hit.key); }
      if (!focus) { focus = hit.key; }
    });
    if (drawn.length) {
      (shellsOf || []).forEach(function (s) {
        if (s.frameElement && keys.indexOf(s.key) < 0) { keys.push(s.key); }
      });
    }
    if (arrival && arrival.moon === true) {
      (children || []).forEach(function (c) { if (keys.indexOf(c) < 0) { keys.push(c); } });
    }
    return { keys: keys, focus: focus || centre, unknown: unknown };
  }

  // THE ORBIT THROUGH ITS BODY (Tony's phone look of 2026-11-10, run
  // record 12:11: "centering on Jupiter, i see that the orbit line does not
  // go precisely through the center"). A drawn orbit is 360 straight
  // pieces (render_orbits.sweep_conic), and a straight piece cuts inside
  // the true curve: measured on the served lines of 2026-11-10, the piece
  // beside Jupiter passes 27,957 km from Jupiter's marker, against 27,349
  // km for the curve's bend there worked out from the piece's ends (Earth
  // 5,098 against 5,153; Saturn 9,780 against 11,685). The marker is on
  // the curve; the piece is not. Seen from the Sun the gap is far under a
  // pixel; with Jupiter at the middle, framed on Io, it is a twelfth of the
  // view. So the body's own place is put into its own line, between the
  // two points it lies between: the line then runs through the body, and
  // within a centred view's box keeps to the curve (a piece half as long,
  // its bend a quarter). A point is put in only where it lies within the
  // piece's span, off it by under tol of the piece's length (the curve's
  // bend is 0.2 percent of a piece's length; a mean orbit, or a path the
  // body is not on, is left alone), and never where it is already a point.
  // line {x, y, z} (absolute, gaps null), p [x, y, z]; returns a new line
  // or null when nothing is put in.
  function throughPoint(line, p, tol) {
    if (!line || !Array.isArray(line.x) || !Array.isArray(p) || !p.every(isNum)) { return null; }
    var lim = (isNum(tol) && tol > 0) ? tol : 0.02;
    var best = -1, bestOff = Infinity;
    for (var j = 0; j + 1 < line.x.length; j++) {
      var a = [line.x[j], line.y[j], line.z[j]];
      var b = [line.x[j + 1], line.y[j + 1], line.z[j + 1]];
      if (!a.every(isNum) || !b.every(isNum)) { continue; }
      var ab = [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
      var L2 = ab[0] * ab[0] + ab[1] * ab[1] + ab[2] * ab[2];
      if (!(L2 > 0)) { continue; }
      var ap = [p[0] - a[0], p[1] - a[1], p[2] - a[2]];
      var u = (ap[0] * ab[0] + ap[1] * ab[1] + ap[2] * ab[2]) / L2;
      if (!(u > 0 && u < 1)) { continue; }
      var f = [a[0] + u * ab[0] - p[0], a[1] + u * ab[1] - p[1], a[2] + u * ab[2] - p[2]];
      var off = Math.sqrt(f[0] * f[0] + f[1] * f[1] + f[2] * f[2]) / Math.sqrt(L2);
      if (off < bestOff) { bestOff = off; best = j; }
    }
    if (best < 0 || !(bestOff <= lim)) { return null; }
    var put = function (arr, v) { return arr.slice(0, best + 1).concat([v], arr.slice(best + 1)); };
    return { x: put(line.x, p[0]), y: put(line.y, p[1]), z: put(line.z, p[2]) };
  }

  global.ViewCentre = {
    throughPoint: throughPoint,
    ROOT_KEY: ROOT_KEY,
    WORDS: WORDS,
    shiftLine: shiftLine,
    shifted: shifted,
    absBox: absBox,
    shiftedParts: shiftedParts,
    float32ErrorKm: float32ErrorKm,
    trailPath: trailPath,
    trailParts: trailParts,
    openingKeys: openingKeys
  };

})(typeof window !== "undefined" ? window : globalThis);
