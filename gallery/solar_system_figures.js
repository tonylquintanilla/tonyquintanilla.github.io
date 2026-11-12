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
// Updated November 10, 2026, afternoon, with Anthropic's Claude Opus 5.5
// (L-515 step 2b, Tony's phone look: a moon's past-span sentence in his
// words, the orbit's date on JPL's clock, epochText).
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

// FROM ANOTHER CENTRE (L-513, November 6, 2026). The Earth room prints the
// Moon's distance from Earth by the same rule. distanceLine takes an
// optional seventh argument, the words for the centre ("Earth"); without
// it the line reads "from the Sun", exactly as before. Written with
// Anthropic's Claude Opus 5.5.

// A PERIOD UNDER A YEAR PRINTS IN DAYS ONLY (L-513, Tony's ruling of
// November 6, 2026: "print them in days only, with no years figure, for
// every moon, in the orrery and on the website"). The orrery decides
// (orbital_period.days_only) and serves the choice as the period's
// "days_only", with "years" null; periodLine prints "M days" for it and
// decides nothing itself. The Moon reads "Orbital period: 27 days, around
// Earth, ...", Mercury "87.969 days". Written with Anthropic's Claude
// Opus 5.5.

// A MOON'S BOX (L-515 step 2b, part 1, November 10, 2026). childBox prints
// a moon's box by the Moon's pattern wherever it is drawn, its distance
// from its parent read from its own elements around the parent, and, past
// the span the builder checked (the trust block's delta_days either side
// of the elements' date), one sentence saying so (ruling 18). Updated
// November 10, 2026 with Anthropic's Claude Opus 5.5.

// A HELD BODY (L-525, hold the bad data, November 11, 2026). heldLine is
// the one sentence a held body's box prints, a Sun-centred body's and a
// moon's alike, from the `hold` block the cache builder serves on its
// entry; holdKnob reads the ?hold= test address. Written with Anthropic's
// Claude Opus 5.5.

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
  function distanceLine(pos, trust, epochJd, accuracy, kmPerAu, missingWhy,
                        fromWords) {
    // L-513: the centre the distance is from; the Sun unless one is given.
    var from = (typeof fromWords === "string" && fromWords) ? fromWords
                                                             : "the Sun";
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
      line: auText + " AU from " + from + " (" + withCommas(km.value) + " km)",
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
      var days = servedFigures(period.days, kind === "fetched");
      if (period.days_only === true) {
        // L-513: under a year, the orrery serves the days alone.
        if (days === null) {
          return { line: null,
                   warning: "its period is served in days only without a " +
                            "value and figure count for the days, so it is " +
                            "not shown" };
        }
        shown = days + " days";
      } else {
        var years = servedFigures(period.years, kind === "fetched");
        if (years === null || days === null) {
          return { line: null,
                   warning: "its period is served without a value and " +
                            "figure count for both years and days, so it " +
                            "is not shown" };
        }
        shown = years + " years (" + days + " days)";
      }
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

  // A MOON'S BOX (L-515 step 2b, part 1; Tony's rulings 8 and 18 of
  // 2026-11-07 and 2026-11-09, by the Moon's pattern, L-513). Wherever a
  // moon is drawn -- the root, where it sits at its planet's place, or a
  // centre -- its box prints its distance from its PARENT, read from its
  // own JPL elements around the parent (rel, in AU), never from the sum the
  // root draws, by the larger of its drift and JPL's published accuracy
  // (distanceLine), and one sentence saying which set the digits. The
  // checked span is the trust block's delta_days either side of its
  // elements' date (element_epoch_jd): the stretch the cache builder
  // compared this page's working-out against JPL over. Past it, one more
  // sentence says so; the digits are then set by the measured drift, as
  // they always are once it is the larger (ruling 18: "past the checked
  // span the moon's box says so, its distance printed only as finely as
  // its measured drift allows"). Its words are proposals for Tony's phone
  // look and stand on the Typed facts check's ALLOWED list.

  // The span as a visitor reads it: whole hours under a day, else days to
  // one decimal. Null for a span not served as a positive number.
  function spanText(days) {
    if (!(typeof days === "number" && days > 0 && isFinite(days))) { return null; }
    if (days < 1) {
      var h = Math.max(1, Math.round(days * 24));
      return h === 1 ? "1 hour" : h + " hours";
    }
    return (Math.round(days * 10) / 10).toFixed(1) + " days";
  }

  // Whether the minute drawn lies outside the checked span.
  function pastSpan(trust, epochJd) {
    return !!trust && typeof trust.delta_days === "number" &&
      typeof trust.element_epoch_jd === "number" &&
      typeof epochJd === "number" && isFinite(epochJd) &&
      Math.abs(epochJd - trust.element_epoch_jd) > trust.delta_days;
  }

  // L-515 step 2b, Tony's phone look of 2026-11-10 (run record 12:11, on
  // Charon's box): "Can we replace 'the date of JPL's orbit' with the actual
  // date ... the explanation is obscure ... Maybe, correct me as you see
  // fit, 'The position show was worked out from JPL's orbit on 9 Nov 2026,
  // 0:00 UTC, but is outside the 19 hour best accuracy window for that
  // orbit.'" His words, with one correction: the orbit's date is printed
  // on JPL's own clock, not converted to UTC, by his ruling of 2026-10-29
  // (L-504) that the i panel's source line already follows ("dated 9
  // November 2026, midnight on JPL's ephemeris clock"). And "either side",
  // since the span runs both ways from that date.
  var SPAN_MONTHS = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"];
  // A Julian date as the source line prints it: "9 November 2026,
  // midnight", read on JPL's clock with no conversion; null if not a date.
  function epochText(jd) {
    if (!(typeof jd === "number" && isFinite(jd))) { return null; }
    var d = new Date(Math.round((jd - 2440587.5) * 86400000));
    if (isNaN(d.getTime())) { return null; }
    var midnight = Math.abs((jd - 0.5) - Math.round(jd - 0.5)) < 1e-9;
    return d.getUTCDate() + " " + SPAN_MONTHS[d.getUTCMonth()] + " " +
      d.getUTCFullYear() + (midnight ? ", midnight" : "");
  }
  var SPAN_WORDS = function (span, dated) {
    return "The position shown was worked out from JPL's orbit dated " +
      dated + " on JPL's clock, but is outside that orbit's " +
      "best-accuracy window of " + span + " either side.";
  };

  // "the Moon's", "Io's": the possessive a sentence about a body's orbit
  // takes. The Moon and the Sun are called "the" in English; no other.
  var THE_NAMES = ["Moon", "Sun"];
  function possessive(name) {
    return (THE_NAMES.indexOf(name) >= 0 ? "the " : "") + name + "'s";
  }

  // A HELD BODY'S SENTENCE (L-525, hold the bad data; Tony's ruling of
  // 2026-11-11, 11:22: "Hold the bad data and report, then continue."). The
  // cache builder serves a body whose newer orbits failed its check against
  // JPL, or that JPL did not answer, from its last good build, with a
  // `hold` block on its entry. Its box says so in one sentence, naming the
  // date of the orbit it is drawn from on JPL's clock, as the span sentence
  // does (Tony, 2026-11-10). Settled by Tony's phone look of 2026-11-11,
  // 19:20 Chicago: "The hover is fine." Held by the Solar System figures
  // check; ?hold=<slug> shows them when nothing is held.
  var HELD_WORDS = {
    failed: function (who, dated) {
      return who + " is drawn from JPL's orbit dated " + dated + " on JPL's " +
        "clock, the last one that passed this page's check against JPL; the " +
        "newer ones have not passed yet.";
    },
    unanswered: function (who, dated) {
      return who + " is drawn from JPL's orbit dated " + dated + " on JPL's " +
        "clock, the last one this page could check against JPL; JPL has not " +
        "answered since.";
    },
    unchecked: function (who, dated) {
      return who + " is drawn from JPL's orbit dated " + dated + " on JPL's " +
        "clock, the last one this page served; it has not passed this page's " +
        "check against JPL.";
    }
  };
  // "Halley", "The Moon": the name a sentence opens on.
  function subject(name) {
    return (THE_NAMES.indexOf(name) >= 0 ? "The " : "") + name;
  }
  // The sentence for a held body, or null when it is not held. hold: the
  // served block; trust: its served trust, whose element_epoch_jd dates the
  // orbit it is drawn from. A hold whose orbit's date is not served is
  // {line: null, why}, so the room can name it rather than print less.
  function heldLine(hold, trust, name) {
    if (!hold || typeof hold !== "object") { return { line: null, why: null }; }
    var dated = epochText(trust && trust.element_epoch_jd);
    if (!dated) {
      return { line: null, why: "held, but the date of the orbit it is drawn " +
                                "from is not served, so the sentence is not shown" };
    }
    var kind = hold.passed_before === false ? "unchecked"
             : (hold.kind === "failed" ? "failed" : "unanswered");
    return { line: HELD_WORDS[kind](subject(name), dated), why: null };
  }
  // The Mode 5 knob, read once at load: ?hold=halley (or several, by
  // commas) has the room treat those bodies as held, so Tony can see the
  // sentence on his phone when nothing is held, as ?freeze=1 does for the
  // freeze. Slugs, lower case; an empty list when the address has none.
  function holdKnob(search) {
    var m = /[?&]hold=([^&]*)/.exec(String(search || ""));
    if (!m) { return []; }
    return decodeURIComponent(m[1]).split(",").map(function (s) {
      return s.trim().toLowerCase();
    }).filter(Boolean);
  }
  // The hold a body is drawn with: its served one, or the knob's made-up
  // one when the address names it; null otherwise.
  function holdFor(served, slug, knob) {
    if (served && typeof served === "object") { return served; }
    if ((knob || []).indexOf(slug) >= 0) {
      return { kind: "failed", passed_before: true, knob: true };
    }
    return null;
  }

  // child: {name, description, info_url, period, accuracy, trust:
  // {rate_deg_per_day, element_epoch_jd, delta_days}}, as the room's driver
  // serves it. rel: [x, y, z], the child around its parent, AU. Returns
  // {lines, meta, warnings, past, unserved}: lines the box's lines, its
  // name first; meta the panel's words (about, info_url); past whether the
  // minute is past the checked span; unserved which of the orrery's
  // description, link and period it has none of yet. hold (L-525,
  // optional): the hold the room draws it with (holdFor); left out, the
  // child's own served hold.
  function childBox(child, rel, epochJd, kmPerAu, parentName, hold) {
    var warnings = [];
    if (!child || typeof child !== "object") {
      return { lines: null, meta: null, past: false,
               warnings: ["no text box words served for this moon"] };
    }
    var name = (typeof child.name === "string" && child.name) ? child.name : "Moon";
    var lines = [name];
    var meta = {};
    // The orrery's words, link and period, copied by the objects mirror;
    // a moon the orrery does not key yet has none: listed in unserved.
    var unserved = [];
    if (typeof child.description === "string" && child.description) {
      lines.push(child.description);
      meta.about = child.description;
    } else {
      unserved.push("description");
    }
    if (typeof child.info_url === "string" && child.info_url) {
      meta.info_url = child.info_url;
    } else {
      unserved.push("link");
    }
    // L-525: a moon JPL did not answer is held at its last build; the
    // room hands the hold in (its served one, or the ?hold= knob's).
    var held = heldLine(hold === undefined ? child.hold : hold, child.trust, name);
    if (held.line) { lines.push(held.line); }
    else if (held.why) { warnings.push(name + ": " + held.why); }
    var past = pastSpan(child.trust, epochJd);
    var dist = distanceLine({ x: rel[0], y: rel[1], z: rel[2] }, child.trust,
                            epochJd, child.accuracy, kmPerAu, null, parentName);
    if (dist.line) {
      lines.push(dist.line + ".");
      var span = spanText(child.trust && child.trust.delta_days);
      var dated = epochText(child.trust && child.trust.element_epoch_jd);
      if (past && span && dated) { lines.push(SPAN_WORDS(span, dated)); }
      else if (past) { warnings.push(name + ": past its checked span, whose length is not served"); }
      var orbit = possessive(name) + " orbit around " + parentName;
      var finer = (dist.note === null) ? " JPL's published accuracy for " + orbit + " is finer." : "";
      if (dist.governs === "drift") {
        lines.push("This distance is rounded to how far this page's " +
          "working-out from JPL's orbit may have drifted by the minute " +
          "shown." + finer);
      } else if (dist.governs === "whole kilometres") {
        lines.push("This distance is shown to the whole kilometer." + finer);
      } else {
        lines.push("This distance is rounded to JPL's published " +
          "accuracy for " + orbit + ".");
      }
      if (dist.note) { lines.push(dist.note); }
      if (dist.accuracyWhy) { warnings.push(name + ": " + dist.accuracyWhy); }
    } else {
      warnings.push(name + ": no distance shown -- " + dist.why);
    }
    var per = periodLine(child.period);
    if (per.line) {
      lines.push(per.line);
    } else if (per.warning) {
      warnings.push(name + ": " + per.warning);
    } else {
      unserved.push("period");
    }
    // Not a warning: the box is honest without them (it prints what it is
    // given), and the room's notes are for what it could not draw. The
    // Solar System figures check prints every moon's list each run, so
    // the gap is seen until the orrery keys the moon (L-514's session 1).
    return { lines: lines, meta: meta, warnings: warnings, past: past,
             unserved: unserved };
  }

  global.SolarSystemFigures = {
    spanText: spanText,
    pastSpan: pastSpan,
    SPAN_WORDS: SPAN_WORDS,
    SPAN_MONTHS: SPAN_MONTHS,
    epochText: epochText,
    possessive: possessive,
    HELD_WORDS: HELD_WORDS,
    subject: subject,
    heldLine: heldLine,
    holdKnob: holdKnob,
    holdFor: holdFor,
    childBox: childBox,
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
