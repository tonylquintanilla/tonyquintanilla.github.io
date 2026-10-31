// gallery/solar_system_figures.js -- the figures a body's distance
// prints with in the Solar System room (L-398; moved here from
// interactive.html by the same patch).
//
// WHY IT IS ITS OWN FILE. Tony's ruling, 2026-09-18 (L-338): logic that
// needs no browser lives in its own file, and it moves out when a build
// already touches it. This build touched it. A check can now reach it
// as a file: documentation/smoke_solar_system_figures.js.
//
// WHAT IT DOES. A body's distance from the Sun is worked out in the
// browser from its served elements, for the minute the room was opened.
// It prints to the place the larger of two errors earns
// (provenance-discipline 2.23, A Computed Position Prints What Its
// Errors Earn; Tony's ruling of 2026-10-01, "use whichever is larger"):
//
//   DRIFT    how far the worked-out position may have moved from what
//            JPL Horizons would say: the builder's measured rate, in
//            degrees per day, times the days since the elements' date,
//            taken as a distance at the body's distance. The rate
//            checks direction, not distance; it is the only measure the
//            cache holds, so it serves for both.
//   SOURCE   how well JPL knows where the body is at all, from the
//            planet's group in JPL's 2014 ephemeris report: a row in the
//            orrery's constants_new.py, served on the body's entry in
//            data/objects_config.json as "position_accuracy". The row
//            stores the PLACE JPL's words report to (1 km, 100 km,
//            10,000 km), so the error used is half a unit of it, which
//            by the Report test gives back that place.
//
// The place printed is the Report test's: the one whose half unit is
// nearest the error on a log scale, a tie going coarser. Never finer
// than whole kilometres, and never fewer than one figure. Each unit is
// placed by its own error, so the AU and the km can carry different
// counts. Numbers are written out, never as exponents (Tony,
// 2026-09-30).
//
// A SMALL BODY'S OWN UNCERTAINTY (L-399, October 29, 2026). An asteroid,
// a comet or a dwarf planet asked as a small body has no group in JPL's
// ephemeris report; JPL states its own uncertainty with its position
// instead (Horizons' vector table 2xr). The cache builder asks it the way
// the orrery does and serves it on the body's cached record as
// "position_uncertainty", the 3-sigma of its distance from the Sun in km.
// That figure IS the error, so it is used whole, where a planet's row is
// a place and half a unit of it is used. The larger of it and the drift
// then sets the print, as for a planet. Written October 29, 2026 with
// Anthropic's Claude Opus 5.5.
//
// A body with neither (until the builder has served it, or when JPL's
// answer could not be had) prints by its drift alone, and its text box
// says so in the sentence Tony approved on 2026-10-01. That sentence is
// printed exactly when no source error is served, so the words and the
// data cannot disagree.
//
// WHY NO FIGURE, IN TRUE WORDS (L-484, October 31, 2026). "Not yet
// included" is true only when JPL's figure was not fetched or not asked.
// When JPL answered and its uncertainty column reads "n.a." (Bennu,
// Halley and Ikeya-Seki), JPL states none, and the box prints the
// orrery's sentence, "JPL states no accuracy for this position."; when
// JPL answered and the builder refused the answer, it says so. The
// builder's reason is served in the index's position_uncertainty.missing
// and the room's driver passes it here (provenance-discipline 2.36: a
// sentence saying why a figure is missing says the true reason). The
// digits are unchanged: a body with no source error prints to what its
// drift earns, never finer than whole kilometres -- whole kilometres on
// the elements' own day, then coarser as the days since grow (tens of
// kilometres for those three within a day or two). The orrery prints
// the whole kilometre for them because it asks JPL for the moment drawn
// and has no drift; the website works the position out from elements
// and does. Updated October 31, 2026 with Anthropic's Claude Opus 5.5.
//
// Written October 1, 2026 with Anthropic's Claude Opus 5.5, from the
// functions L-363 step 3a built inside interactive.html on 2026-09-30.
//
// THE ORBITAL PERIOD (L-431, build 3, October 14, 2026). Every body's
// hover prints its orbital period -- Tony, 2026-10-11: "periods are
// basic data, for all bodies and should be part of the hover text" -- in
// the sentence the build's brief gives: "Orbital period: N years (M
// days), around <centre>, from JPL Horizons, fetched <date>." The period
// is the orrery's, by the orrery's fallback order and digits rule,
// served on the body's entry in data/objects_config.json as "period",
// which tools/mirror_objects.py copies from the orrery's export. Years
// and days are each served with their value and figure count; this file
// prints the value AT THAT COUNT and never recounts it
// (interactive-exhibit, A figure count is READ from the served entry),
// with thousands separators from 10,000 up where the period is JPL's, as
// the orrery's hover prints it; a typed value prints as typed. The served "text" is the orrery's own print, and
// documentation/smoke_solar_system_figures.js holds this print to it. A
// typed period says so in the orrery's words, "Typed value, not fetched
// from JPL."; none says it has not been fetched yet; the Sun has none.
//
// WHOSE PERIOD (L-445, October 15, 2026). Earth's period is JPL's for the
// Earth-Moon barycentre, not Earth's centre (Tony's ruling of
// 2026-10-15: "Confirmed as recommended, the barycenter."). The orrery
// serves "target_label" on a period asked of another body than the one
// shown, and null otherwise, and this file prints it before the centre,
// as the orrery's hover does: "..., for the Earth-Moon center of mass,
// around the Sun, from JPL Horizons, fetched <date>." A period served
// with no target_label prints as before.

// THE ORBIT'S NEAR AND FAR DISTANCE (L-479, October 24, 2026). Tony,
// offered "Its orbit runs from 76 to 1,000 AU from the Sun.": "It would
// be informative but may be too long. It would also give an intuitive
// sense of the eccentricity." Offered one short line, "Orbit: 76 to
// 1,000 AU from the Sun.": "Yes". orbitLine works the two distances out
// from the body's served Sun-centred elements, perihelion a(1 - e) and
// aphelion a(1 + e), at full digits, and prints each in AU, never typed.
// HOW MANY FIGURES. Each prints three significant figures, the length of
// the AU in brackets on the room's shell hovers (Tony's ruling of
// 2026-09-28: a comparison aid kept short), and never finer than the
// Report test's place for the same error the body's distance line uses
// (A Computed Position Prints What Its Errors Earn): two points on the
// drawn orbit are not known better than the body on it. Only a closed
// orbit (0 <= e < 1) has an aphelion; an open path prints no line, and
// the room's notes say why.

// A SPACECRAFT'S DISTANCE (L-443 build B, October 25, 2026). A spacecraft
// is drawn from its served positions, and its marker is worked out between
// them (gallery/assembler/render_spacecraft.py), which hands the room how
// far that working-out may be off. pathDistanceLine prints the distance
// to the place that error earns, never finer than whole kilometres, and
// always with Tony's sentence of 2026-10-01: JPL's own uncertainty for a
// spacecraft is not served.

(function (global) {
  "use strict";

  // Half a kilometre: the room prints whole kilometres at most.
  var FINEST_KM = 0.5;

  // Tony's words, 2026-10-01 (L-399). Printed when JPL's figure was not
  // fetched or not asked (a question that failed, a body never asked).
  var NO_SOURCE_ACCURACY =
    "JPL's own uncertainty for this position is not yet included.";

  // L-484, October 31, 2026: a sentence saying why a figure is missing
  // says the TRUE reason (provenance-discipline 2.36). JPL answered and
  // its uncertainty column reads "n.a." (Bennu, Halley, Ikeya-Seki): the
  // orrery's own sentence since 2026-10-29 (position_accuracy._side).
  var JPL_STATES_NONE = "JPL states no accuracy for this position.";
  // JPL answered, and the answer could not be matched to this position,
  // so it was refused (the builder's match rule, or an empty column).
  var JPL_ANSWER_REFUSED =
    "JPL was asked for its own uncertainty for this position, but its " +
    "answer did not match this position, so it is not included.";

  // The builder's reason (tools/gallery_cache_builder.py,
  // build_position_uncertainty), served in the index's
  // position_uncertainty.missing, sorted into the three. Each prefix is
  // the builder's own words; documentation/smoke_solar_system_figures.js
  // finds every one in the builder and fails on a served reason none of
  // them matches, so a new reason cannot fall silently to the default.
  var MISSING_KINDS = [
    ["JPL gives no range uncertainty", "none"],
    ["JPL's 2xr answer for", "refused"],
    ["JPL's answer has an empty position column", "refused"],
    ["could not reach JPL", "not fetched"],
    ['no "you are here" point is served', "not asked"],
    ["it is not served measured from the Sun", "not asked"]
  ];

  function missingKind(why) {
    if (typeof why !== "string" || !why) { return null; }
    for (var i = 0; i < MISSING_KINDS.length; i++) {
      if (why.indexOf(MISSING_KINDS[i][0]) === 0) { return MISSING_KINDS[i][1]; }
    }
    return null;
  }

  // The sentence for a body with no source error, from the builder's
  // reason. No reason, or one not known here, keeps Tony's sentence.
  function noSourceSentence(why) {
    var kind = missingKind(why);
    if (kind === "none") { return JPL_STATES_NONE; }
    if (kind === "refused") { return JPL_ANSWER_REFUSED; }
    return NO_SOURCE_ACCURACY;
  }

  // The Report test: the place whose half unit is nearest the error on
  // a log scale, a tie going to the coarser place.
  function reportPlace(uncertainty) {
    return Math.floor(Math.log10(2 * uncertainty) + 0.5);
  }

  // Round to a power-of-ten place, but never to fewer than one figure.
  function roundTo(value, place) {
    var lead = Math.floor(Math.log10(Math.abs(value)));
    var p = Math.min(place, lead);
    var unit = Math.pow(10, p);
    return { value: Math.round(value / unit) * unit, place: p };
  }

  function withCommas(n) {
    return String(Math.round(n)).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  // The source's place in kilometres, read from a served
  // "position_accuracy" node. Its own unit when that is km, otherwise
  // the served "in" km entry; nothing is converted here.
  function sourcePlaceKm(node) {
    if (node === undefined || node === null) {
      return { km: null, why: null };
    }
    var v = null;
    if (node.unit === "km" && typeof node.value === "number") {
      v = node.value;
    } else if (node["in"] && node["in"].km &&
               typeof node["in"].km.value === "number") {
      v = node["in"].km.value;
    }
    if (!(typeof v === "number" && v > 0 && isFinite(v))) {
      return { km: null,
               why: "its position_accuracy serves no kilometres, so JPL's " +
                    "accuracy was not applied" };
    }
    return { km: v, why: null };
  }

  // L-399: the source's error in kilometres, from either kind of served
  // node. A "position_uncertainty" (range_3sigma_km) is the error itself;
  // a "position_accuracy" row is a place, so half a unit of it.
  function sourceError(node) {
    if (node && typeof node === "object" &&
        node.range_3sigma_km !== undefined) {
      var u = node.range_3sigma_km;
      if (!(typeof u === "number" && u > 0 && isFinite(u))) {
        return { km: null, errKm: 0, kind: "uncertainty",
                 why: "its position_uncertainty serves no kilometres, so " +
                      "JPL's uncertainty was not applied" };
      }
      return { km: u, errKm: u, kind: "uncertainty", why: null };
    }
    var p = sourcePlaceKm(node);
    return { km: p.km, errKm: (p.km === null) ? 0 : p.km / 2,
             kind: "place", why: p.why };
  }

  // pos: {x, y, z} in AU about the Sun, as the assembler drew it.
  // trust: {rate_deg_per_day, element_epoch_jd} from the served cache.
  // epochJd: the minute drawn. accuracy: the served node -- a planet's
  // "position_accuracy" or a small body's "position_uncertainty" -- or null.
  // kmPerAu: from the served cache's frame constants. missingWhy: the
  // builder's reason no uncertainty is served, from the index (L-484),
  // or nothing; it chooses the sentence printed when no source error is.
  function distanceLine(pos, trust, epochJd, accuracy, kmPerAu, missingWhy) {
    if (!(typeof kmPerAu === "number" && kmPerAu > 0)) {
      return { line: null, why: "kilometres per AU is not served" };
    }
    var x = pos && pos.x, y = pos && pos.y, z = pos && pos.z;
    var rAu = Math.sqrt(x * x + y * y + z * z);
    if (!(rAu > 0 && isFinite(rAu))) {
      return { line: null, why: "its position is not a number" };
    }
    if (!trust || typeof trust.rate_deg_per_day !== "number" ||
        typeof trust.element_epoch_jd !== "number" ||
        typeof epochJd !== "number") {
      return { line: null, why: "no measured error is served for it, " +
                                "so no figures are earned" };
    }
    var rKm = rAu * kmPerAu;
    var days = Math.abs(epochJd - trust.element_epoch_jd);
    var driftKm = rKm * trust.rate_deg_per_day * days * Math.PI / 180;
    var src = sourceError(accuracy);
    var sourceKm = src.errKm;
    var errKm = Math.max(driftKm, sourceKm, FINEST_KM);
    var governs = (errKm === FINEST_KM) ? "whole kilometres"
                : (errKm === sourceKm)
                  ? (src.kind === "uncertainty" ? "JPL's uncertainty"
                                                : "JPL's accuracy")
                  : "drift";
    var km = roundTo(rKm, reportPlace(errKm));
    var au = roundTo(rAu, reportPlace(errKm / kmPerAu));
    var auText = au.place < 0 ? au.value.toFixed(-au.place)
                              : withCommas(au.value);
    return {
      line: auText + " AU from the Sun (" + withCommas(km.value) + " km)",
      note: (src.km === null) ? noSourceSentence(missingWhy) : null,
      missingKind: (src.km === null) ? missingKind(missingWhy) : null,
      accuracyWhy: src.why,
      governs: governs,
      kmPlace: km.place,
      auPlace: au.place,
      driftKm: driftKm,
      sourceKm: sourceKm
    };
  }

  // L-443 build B: a spacecraft's distance. Its position is not worked
  // out from elements but between its served points (render_spacecraft),
  // so the error is that working-out's -- errKm, handed to the marker by
  // the assembler -- and never finer than whole kilometres. JPL's own
  // uncertainty for a spacecraft is not served, so the text box says so,
  // in the sentence of 2026-10-01, every time.
  function pathDistanceLine(pos, errKm, kmPerAu) {
    if (!(typeof kmPerAu === "number" && kmPerAu > 0)) {
      return { line: null, why: "kilometres per AU is not served" };
    }
    var x = pos && pos.x, y = pos && pos.y, z = pos && pos.z;
    var rAu = Math.sqrt(x * x + y * y + z * z);
    if (!(rAu > 0 && isFinite(rAu))) {
      return { line: null, why: "its position is not a number" };
    }
    if (!(typeof errKm === "number" && errKm >= 0 && isFinite(errKm))) {
      return { line: null, why: "no error is served for its worked-out " +
                                "position, so no figures are earned" };
    }
    var useKm = Math.max(errKm, FINEST_KM);
    var km = roundTo(rAu * kmPerAu, reportPlace(useKm));
    var au = roundTo(rAu, reportPlace(useKm / kmPerAu));
    var auText = au.place < 0 ? au.value.toFixed(-au.place)
                              : withCommas(au.value);
    return {
      line: auText + " AU from the Sun (" + withCommas(km.value) + " km)",
      note: NO_SOURCE_ACCURACY,
      governs: (useKm === FINEST_KM) ? "whole kilometres"
                                     : "working out between points",
      kmPlace: km.place,
      auPlace: au.place,
      errKm: useKm
    };
  }

  // L-479: the orbit's near and far distance. Since L-443 build B part 2
  // (Tony, 2026-10-26: keep JPL's words, perihelion and aphelion, and
  // explain them): "Orbit: perihelion q AU, its closest to the Sun, to
  // aphelion Q AU, its farthest." aAu and e: the body's served
  // Sun-centred elements. errKm: the error the body's distance line used,
  // the larger of its drift and JPL's accuracy, at least half a km.
  var ORBIT_FIGURES = 3;
  function orbitLine(aAu, e, errKm, kmPerAu) {
    if (!(typeof aAu === "number" && aAu > 0 && isFinite(aAu))) {
      return { line: null, why: "no semi-major axis is served for it" };
    }
    if (!(typeof e === "number" && e >= 0 && isFinite(e))) {
      return { line: null, why: "no eccentricity is served for it" };
    }
    if (e >= 1) {
      return { line: null, why: "its orbit is open, so it has no far end" };
    }
    if (!(typeof errKm === "number" && errKm > 0 && isFinite(errKm)) ||
        !(typeof kmPerAu === "number" && kmPerAu > 0)) {
      return { line: null, why: "no measured error is served for it, " +
                                "so no figures are earned" };
    }
    var earned = reportPlace(errKm / kmPerAu);
    var fmt = function (v) {
      var lead = Math.floor(Math.log10(v));
      var r = roundTo(v, Math.max(earned, lead - (ORBIT_FIGURES - 1)));
      return r.place < 0 ? r.value.toFixed(-r.place) : withCommas(r.value);
    };
    return { line: "Orbit: perihelion " + fmt(aAu * (1 - e)) +
                   " AU, its closest to the Sun, to aphelion " +
                   fmt(aAu * (1 + e)) + " AU, its farthest.", why: null };
  }

  // A served value printed at its served figure count: rounded once to
  // that many significant figures, plain digits, and, when asked, the
  // separators the orrery's digits rule prints from 10,000 up.
  function servedFigures(part, separators) {
    if (!part || typeof part.value !== "number" || !isFinite(part.value) ||
        typeof part.figures !== "number" || !(part.figures >= 1)) {
      return null;
    }
    var n = Math.max(1, Math.min(21, Math.round(part.figures)));
    var rounded = Number(part.value.toPrecision(n));
    var decimals = rounded === 0 ? n - 1
        : n - 1 - Math.floor(Math.log10(Math.abs(rounded)));
    if (decimals < 0) { decimals = 0; }
    if (decimals > 20) { decimals = 20; }
    var text = rounded.toFixed(decimals);
    if (separators && Math.abs(rounded) >= 10000) {
      var bits = text.split(".");
      bits[0] = bits[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
      text = bits.join(".");
    }
    return text;
  }

  // The period line(s) for a body's hover, from its served "period".
  // Returns { line, warning }: line is null for the Sun (no period) and
  // for a period that cannot be printed honestly, which is then named in
  // warning rather than shown.
  function periodLine(period) {
    if (period === undefined || period === null) {
      return { line: null, warning: null };
    }
    var kind = period.kind;
    if (kind === "none") {
      var w = (typeof period.words === "string" && period.words)
          ? period.words : "Not yet fetched from JPL.";
      return { line: "Orbital period: " + w.charAt(0).toLowerCase() +
                     w.slice(1), warning: null };
    }
    var shown;
    if (period.open_orbit) {
      shown = "none (open orbit)";
    } else {
      // Separators for JPL's period only, as the orrery prints it; a
      // typed value prints as typed (orbital_period._typed_strings).
      var years = servedFigures(period.years, kind === "fetched");
      var days = servedFigures(period.days, kind === "fetched");
      if (years === null || days === null) {
        return { line: null,
                 warning: "its period is served without a value and figure " +
                          "count for both years and days, so it is not shown" };
      }
      shown = years + " years (" + days + " days)";
    }
    if (kind === "typed") {
      return { line: "Orbital period: " + shown + ". " +
                     ((typeof period.words === "string" && period.words)
                      ? period.words : "Typed value, not fetched from JPL."),
               warning: null };
    }
    if (kind !== "fetched") {
      return { line: null, warning: "its period is served as " +
                                    JSON.stringify(kind) + ", which this " +
                                    "page does not know" };
    }
    if (!period.center || !period.center_label) {
      return { line: null,
               warning: "its period is served from JPL with no centre, so " +
                        "it is not shown" };
    }
    // L-445: whose period it is, when it is another body's.
    var whose = (typeof period.target_label === "string" &&
                 period.target_label) ? "for " + period.target_label + ", "
                                      : "";
    return { line: "Orbital period: " + shown + ", " + whose + "around " +
                   period.center_label + ", from JPL Horizons, fetched " +
                   period.fetched + ".",
             warning: null };
  }

  // Is this period's centre the Sun? (The orrery's two-centre test picks
  // the Sun or the solar system's barycentre, "@0".)
  function periodAroundSun(period) {
    var c = period && period.center;
    return !c || ["@sun", "@10", "sun", "10"].indexOf(String(c).toLowerCase()) >= 0;
  }

  global.SolarSystemFigures = {
    servedFigures: servedFigures,
    periodLine: periodLine,
    orbitLine: orbitLine,
    ORBIT_FIGURES: ORBIT_FIGURES,
    periodAroundSun: periodAroundSun,
    FINEST_KM: FINEST_KM,
    NO_SOURCE_ACCURACY: NO_SOURCE_ACCURACY,
    JPL_STATES_NONE: JPL_STATES_NONE,
    JPL_ANSWER_REFUSED: JPL_ANSWER_REFUSED,
    MISSING_KINDS: MISSING_KINDS,
    missingKind: missingKind,
    noSourceSentence: noSourceSentence,
    reportPlace: reportPlace,
    roundTo: roundTo,
    withCommas: withCommas,
    sourcePlaceKm: sourcePlaceKm,
    sourceError: sourceError,
    distanceLine: distanceLine,
    pathDistanceLine: pathDistanceLine
  };

})(typeof window !== "undefined" ? window : globalThis);
