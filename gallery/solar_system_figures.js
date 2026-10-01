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
// A body with no "position_accuracy" (an asteroid, until L-399 fetches
// its own uncertainty) prints by its drift alone, and its text box says
// so in the sentence Tony approved on 2026-10-01. That sentence is
// printed exactly when the row is absent, so the words and the data
// cannot disagree.
//
// Written October 1, 2026 with Anthropic's Claude Opus 5.5, from the
// functions L-363 step 3a built inside interactive.html on 2026-09-30.

(function (global) {
  "use strict";

  // Half a kilometre: the room prints whole kilometres at most.
  var FINEST_KM = 0.5;

  // Tony's words, 2026-10-01 (L-399).
  var NO_SOURCE_ACCURACY =
    "JPL's own uncertainty for this position is not yet included.";

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

  // pos: {x, y, z} in AU about the Sun, as the assembler drew it.
  // trust: {rate_deg_per_day, element_epoch_jd} from the served cache.
  // epochJd: the minute drawn. accuracy: the served node, or null.
  // kmPerAu: from the served cache's frame constants.
  function distanceLine(pos, trust, epochJd, accuracy, kmPerAu) {
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
    var src = sourcePlaceKm(accuracy);
    var sourceKm = (src.km === null) ? 0 : src.km / 2;
    var errKm = Math.max(driftKm, sourceKm, FINEST_KM);
    var governs = (errKm === FINEST_KM) ? "whole kilometres"
                : (errKm === sourceKm) ? "JPL's accuracy" : "drift";
    var km = roundTo(rKm, reportPlace(errKm));
    var au = roundTo(rAu, reportPlace(errKm / kmPerAu));
    var auText = au.place < 0 ? au.value.toFixed(-au.place)
                              : withCommas(au.value);
    return {
      line: auText + " AU from the Sun (" + withCommas(km.value) + " km)",
      note: (src.km === null) ? NO_SOURCE_ACCURACY : null,
      accuracyWhy: src.why,
      governs: governs,
      kmPlace: km.place,
      auPlace: au.place,
      driftKm: driftKm,
      sourceKm: sourceKm
    };
  }

  global.SolarSystemFigures = {
    FINEST_KM: FINEST_KM,
    NO_SOURCE_ACCURACY: NO_SOURCE_ACCURACY,
    reportPlace: reportPlace,
    roundTo: roundTo,
    withCommas: withCommas,
    sourcePlaceKm: sourcePlaceKm,
    distanceLine: distanceLine
  };

})(typeof window !== "undefined" ? window : globalThis);
