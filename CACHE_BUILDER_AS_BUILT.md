<!-- Doc-Kind: hand | What the website's cache builder and Daily Run do now, section by section, moved whole from the gallery-cache-builder skill (L-522, its split); the skill keeps the rules. -->
# The cache builder and the Daily Run: as built

This page says what `tools/gallery_cache_builder.py` and `daily_run.py`
do NOW: which function or setting does each thing, in what order, with
the numbers measured. A build that changes them changes this page in
the same commit. Changed text is replaced, never appended to, and git
keeps the old.

The rules a session follows are in the orrery's
`skills/gallery-cache-builder/SKILL.md`, under the same titles; read
the section here for the part a build changes. Moved here whole from
that skill's 1.21 on 2026-11-24 (L-522, document caps), in its own
words: a remark inside a sentence on how a thing used to be moved with
its sentence, and a later build that changes a paragraph drops such
remarks then. The section on a capture craft's box was written new from
the code at gallery 727ebf79. The check `tools/check_as_built_names.py`
(the gallery run's "As-built names" row) holds every code name below in
backticks to the code.

## What this page holds

- The Builder Reads the Period's Centre
- A Spacecraft Is Fetched by Its Plan
- A Lagrange Point Is Served as a Point
- The Clock Block and Its Witness
- A Small Body's Own Uncertainty Is Served
- Every Question Is Asked of JPL, Fresh
- A Body That Fails Its Test Is Held
- A Capture Craft's Box Never Claims Less Than Its Miss
- The Daily Run's Steps

## The Builder Reads the Period's Centre

Built 2026-10-14 (L-431 build 3), at the rule horizons-orbital-mechanics
calls The Drawn Orbit Follows the Period's Centre.

- Each object in `data/objects_config.json` carries a `period` block,
  copied by `tools/mirror_objects.py` from the orrery's export, never by
  hand. `kind` is `fetched`, `typed` or `none`; a fetched one names its
  `center`, the Horizons centre JPL's period was taken around.
- The served `osculating` block, its positions and its trust stay
  Sun-centred and unchanged. Where a fetched period's centre is the
  solar system's barycentre ('@0') and the body is drawn from its
  elements around the Sun (not a comet, not a spacecraft), the builder
  ALSO fetches the body's elements around that centre at the SAME date
  as the Sun-centred ones, and serves them as `drawn_orbit` (centre
  slug `ssb`, `paired_with: osculating`). The room pairs the two sets
  at that date to find where the barycentre sits seen from the Sun, and
  draws the ellipse there (`render_orbits.drawn_orbit_offset`). No
  perturbation lines are drawn for it (Tony, 2026-10-13).
- A set from another date is never paired: `build_drawn_orbit_block`
  raises, and the pre-swap check #D aborts a `drawn_orbit` that is
  around the stored centre, is not at the `osculating` date, or has no
  mean motion. `tools/check_cache_in_step.py` asks the same question
  from the other side, with the same rule (`drawn_centre_wanted`):
  every object whose period wants a drawn orbit has one, and no other
  object does.
- A comet whose period is around another centre is drawn from its
  elements of today, around the Sun (since 2026-10-22, L-443: every
  comet is anchored at today; until then "at perihelion"), and the
  builder WARNS rather than fetching. Encke, today, is around the Sun.
- Which bodies this touches is decided by the orrery's period records,
  not here. On 2026-10-14 no served body's period was around the
  barycentre (Sedna is not served), so the first live `drawn_orbit` may
  come from a planet whose period the orrery fetches around '@0' when
  Tony plots it.

## A Spacecraft Is Fetched by Its Plan

Built 2026-10-25 (L-443 build B), on the method horizons-orbital-mechanics
calls How a Path's Events Are Found. Design: ruling 1 of
`documentation/DESIGN_L443_slice2_rulings_20261023.md`, "One path rule,
the orrery's."

- THE PLAN IS THE ORRERY'S. `path_plan.py` makes each served
  spacecraft's plan in the orrery's maintenance run; the objects export
  carries it; `tools/mirror_objects.py` copies onto the entry in
  `data/objects_config.json` what the builder and the room need: its
  `made` date, its `span` (JPL's own, launch to the end of JPL's data,
  or to the day an ended mission ended, its `mission_end`, since v1.17),
  its `backbone` (step and thinning), and each event's body, kind,
  moment, distance, window and step. Never by hand.
- THE WHOLE PATH, WHEN THE PLAN IS NEW (`fetch_path_by_plan`): the
  backbone across the span at its step (7 days), thinned by
  Douglas-Peucker at its tolerance (0.02 AU); each event's window at the
  event's own step, clipped to the span, thinned at the event's own
  scale (`WINDOW_THIN_FRACTION`, 1% of its passing distance) and merged
  after the backbone's thinning so a flyby is never thinned away; then
  the daily tail. JPL's predicted part is fetched with the rest; nothing
  is extended past the span. "New" means the raw archive's `plan_made`
  or `plan_span` differs from the entry's, or a first build, or
  --refresh-spacecraft; the archive is cleared first, since JPL revises
  the predicted part.
- OTHERWISE, ONLY THE TAIL (`fetch_path_tail`): daily from the freeze
  window before today to two days after (`PATH_TAIL_AHEAD_DAYS`), inside
  the span, so the room, drawing the minute it is opened, finds a point
  either side of it until the next build.
- AN ENDED MISSION'S LAST DAY IS ASKED FOR ITSELF (`fetch_path_last_day`,
  v1.17, L-507). A path whose span ended before today also gets the
  first two minutes of its last day, asked as 00:00 and 00:01 UTC (they
  come back a minute later on JPL's clock, which labels them), merged
  with the rest, whole fetch and tail alike. The room puts an ended
  mission's marker on the path's last served point and its text box
  says the mission ended that day, but the 7-day backbone from the
  launch can stop up to six days short of it: Galileo's would have
  stopped on a day the box would then print as its end. The span's end
  is a day, inside JPL's data by path_plan's own clipping
  (horizons-orbital-mechanics, An Ended Mission Ends on Its
  mission_end), so the two minutes are too. Where the path stops
  before the mission ended (Akatsuki: cut on 2024-04-26, the last day
  JPL's solution is fitted to tracking, its `path_cutoff`; JAXA's end
  2025-09-18; v1.18, L-507 more voyages), the span ends on that day, the
  same two minutes are its last served point, and the room's box says
  the path is drawn to it. `{}` for a path
  still running. Such a path serves no `as_of_today`. The offline suite holds
  it (the last point on the span's last day; planted fault, the last
  day not asked, leaving 2003-09-23 for an end of 2003-09-29).
- EVERY POINT IS KEYED TO THE MINUTE (`MINUTE_KEY`), since a window's
  step can be a minute; every other object keeps day keys.
- AS_OF_TODAY IS TODAY'S POINT, the latest at or before today, not the
  path's last (which may be in 2100); none when no point lies within two
  days before today, so a path whose data ended serves no "you are here"
  and passes #T.
- THE SHRINK GATE HOLDS A RE-FETCH BY A NEW PLAN OUT OF ITS COUNT, and
  names it, old count and new: its count is its plan's, not the old one.
  The suite shows the gate refusing the same re-fetch without the
  exemption.
- THE SPACECRAFT SANITY BOUND IS 1,000 AU (`SPACECRAFT_SANITY_AU`); the
  Voyagers' JPL data runs to 2100, past 400 AU.
- NO PLAN AND NO TYPED START: the object fails by name ("no path plan
  is served for this spacecraft yet") and is served last-good, never
  asked from 1970. A spacecraft with a typed `overrides.spacecraft`
  start and no plan keeps the old fetch; none does since 2026-10-25,
  Voyager 1's typed windows having been replaced by its plan's events.
- THE OFFLINE SUITE gives a spacecraft with no plan a stand-in plan, as
  it gives stand-in drawings, so it does not depend on a pull: in the
  config as committed, a plan arrives only when the mirror copies it.
- A COMET ON AN OPEN PATH IS A PATH BODY (v1.13, L-443, slice 2, build
  B part 2). `is_path_body` is one test, a spacecraft or an entry with
  `open_path`, and every place above that asked "is this a spacecraft?"
  asks it: the fetch by the plan, last-good serving, structural check
  #2, the trust branch (`fetched_positions`, no window) and the floor on
  points. Such a comet is served positions and no `osculating` block,
  with `open_path: true` on its served entry, which the room reads to
  draw it as a path. Its plan comes from the orrery like a
  spacecraft's (horizons-orbital-mechanics, A Comet on an Open Path);
  its span is a year before its perihelion to a year after today, so
  "nothing extended past the span" means past that. With no plan yet it
  fails by name, "no path plan is served for this comet yet". The
  mirror copies `open_path` from the export (`INSERTED`). The offline
  suite gives such a comet a stand-in plan and the fake answers it with
  a straight line past the Sun; four checks hold it, among them one
  fetched inside its plan's span and no further.
  A body changes side by itself (v1.18, L-510; gallery 3660993): the
  orrery draws a small body as a path or an orbit by its database e
  (horizons-orbital-mechanics), and `tools/mirror_objects.py` follows it
  across e = 1 both ways (WHEN A BODY CHANGES SIDE): to an orbit it
  removes `path` and `open_path`, sets availability analytic, frame
  heliocentric and trace none, and inserts the export's period; to a
  path, the reverse. It rewrites the entry's note with the day, prints
  every change, refuses a side change over an entry whose three fields
  were set by hand, and leaves the drawer row for a person to check. The
  offline suite compares its comets on open paths with the export BY
  NAME (no count to bump), and gives a body newly drawn as an orbit a
  stand-in orbit, named when used.

## A Lagrange Point Is Served as a Point

v1.20, L-297: the fourth shape, `serving_shape` 'point' (category
'lagrange_point'). A point has no mass and no orbit, so no elements
are fetched: only JPL's positions around the centre it is served
around (Earth for the Earth-Moon points, the Sun for the Earth-Sun
ones), a day apart across the served window and a day past each edge,
and an hour apart from yesterday to the day after tomorrow (`POINT_*`;
Tony, 2026-11-19). Fetched last, once the window is known
(`point_window`); a point never takes part in the window
(`served_window_from`), so it cannot narrow it. JPL's answer is held to
the point's own name: asked for 3013, JPL answers an asteroid. A failed
fetch serves the saved days (`serve_last_good_point`), today's point
nulled; the validator's #L (`point_problems`) refuses elements, a short
span, a missing day or hour, each planted.

## The Clock Block and Its Witness

v1.21, L-541. A served `jd` is on JPL's clock (TDB) and a visitor's
minute is UTC, so each build serves the difference in the index.
- THE CLOCK BLOCK (`build_clock`, "clock"). JPL is asked its TDB-UT (a
  vectors query for Mercury; the Horizons manual: "After 1962, UT means
  UTC") at the window's first and last minute and the build's own;
  astropy works out TDB minus UTC at the same minutes. The build stops,
  by name, when JPL does not answer or names another body, when the two
  differ by more than 0.001 s, or when JPL's moves by more than 0.004 s
  across the window (a leap second inside it). Served: JPL's at the
  build's minute, 69.1829 s on 2026-11-22.
- THE WITNESS (`build_witness`). Each build serves JPL's places of
  Mercury (from its orbit) and 3I/ATLAS (from served points) at its own
  minute; the gallery run's Room clock row compares the room's places
  with them. A witness does not share its clock with what it tests.
- OPEN ON L-541: daily points are asked at 00:01:00 on JPL's clock, 9 s
  before UTC midnight; keys and plan windows read as UTC.

## A Small Body's Own Uncertainty Is Served

Built 2026-10-29 (L-399), on the method horizons-orbital-mechanics calls
A Small Body's Uncertainty Comes With Its Position.

- EACH SMALL BODY IS ASKED JPL'S OWN UNCERTAINTY: an asteroid, a comet
  or a dwarf planet asked as a small body (`is_small_body_target`, the
  orrery's own test), by Horizons' vector table 2xr, read by column
  name, at the moment of its served "you are here" point. What is
  served is `position_uncertainty` on its entry
  (`build_position_uncertainty`): the 3-sigma of its distance from the
  Sun. The planets and Pluto keep JPL's planetary report, from the
  config (`position_accuracy`). It is cache data, so unlike
  `position_accuracy` it reaches a visitor only after a build.
- AN ANSWER THAT CANNOT BE SERVED HONESTLY SERVES NOTHING, NAMED, and
  never costs the orbit: no point to ask at, a body not measured from
  the Sun, an empty position column, no R_s ("JPL gives no range
  uncertainty (R_s) for it" -- Bennu, Halley and Ikeya-Seki, whose
  column reads "n.a."), or a position that does not match. The index's
  `position_uncertainty` lists who was asked and why each missing one
  is missing.
- THE MATCH RULE (`uncertainty_match_tolerance`, corrected
  2026-10-29). The 2xr answer's position must sit within the body's own
  3-sigma of the served point, 3 x R_s, R_s read first, floored at
  1e-7 AU (`UNCERTAINTY_MATCH_AU`, about 15 km, the earlier fixed
  tolerance, which Ceres and Apophis keep) and capped at 1e-3 AU
  (`UNCERTAINTY_MATCH_CAP_AU`, about 150,000 km). THE CAP IS SET BY
  THE CLOSEST COMET PIECES, the one case where another record sits
  close: C/2025 K1's pieces B and D were 0.0042 AU apart on 2026-10-29
  and D's own 3-sigma was 0.0043 AU, so D's answer standing in for B's
  would pass the 3-sigma alone; the cap is under half the closest pair
  measured that day, the parent and C at 0.0024 AU. Every other body
  asked had no neighbour nearer than 0.117 AU.
- A REFUSAL NAMES ITS NUMBERS. The line says how far JPL's 2xr answer
  sits from the served point against the tolerance, and the run
  record keeps the refused answer's items under
  `position_uncertainty.refused` -- the id asked, JPL's X, Y, Z, the
  served point -- so a refusal can be read later.
- WHY IT WAS CORRECTED: the fixed 1e-7 AU refused 2026 ED138 at the
  21:57 UTC build of 2026-10-29, its answer 8.88e-05 AU (13,000 km)
  from a served point read from astroquery's saved answers after JPL
  had revised the orbit -- a thirtieth of its own 3-sigma (next).

## Every Question Is Asked of JPL, Fresh

`HORIZONS_CACHE = False` (L-399, 2026-10-29), passed as `cache=` at
every astroquery call the builder makes. astroquery keeps each answer
on disk for a week (`astroquery.cache_conf.cache_timeout`, 604800 s,
in `~/.astropy/cache/astroquery/Horizons`) and hands it back when the
same question is asked again, so a second build on the same day served
the first build's orbit and positions under a new "retrieved" stamp.
The 2xr question, sent directly, was always fresh, which is how the
two came to disagree. The offline suite holds every call to the
setting. The orrery made the same choice the same night (L-504,
`utc_clock.HORIZONS_CACHE`; horizons-orbital-mechanics).

A REQUEST JPL DID NOT ANSWER GETS ONE SECOND TRY (L-553, 2026-11-24).
Every JPL question the builder asks goes through `ask_jpl`. When
`jpl_did_not_answer` says the request got no answer -- a connection
that failed or timed out, or JPL's own 503, "Service Temporarily
Unavailable" -- it is asked once more after `SECOND_TRY_PAUSE_S`
(10 seconds: long enough for a passing blip, short beside a build of
about three minutes). An answer JPL gave, of any kind (no data, an
unknown id, an error in its reply), is never asked again. `SECOND_TRY_CAP`
(10) bounds the second tries of one build: on a night JPL is down, the
build waits at most about 7 minutes more (10 times the pause plus
astroquery's 30-second timeout), then every further miss raises at once,
as before, and more than `HOLD_LIMIT` held stops the build. A normal
night costs nothing. Before, every question had one try: run #58 of
2026-11-24 lost its night to one connect timeout for Deimos. The
build's summary prints `second_try_line` every build, zero included:
"[SECOND TRY] 0 second tries made, 0 answered (cap 10 a build)", and
"the cap refused N more" when it did; the run record keeps the counts
(`second_tries`). The clock's questions ride it like any other.

## A Body That Fails Its Test Is Held

Built 2026-11-11 (L-525; Tony: "Hold the bad data and report, then
continue."). Before, one failed test cut the site's window to 0.3 days.

- WHO (`trust_held`). A Sun-centred body drawn from its elements
  (`held_by_test`) when either test sample is more than
  `TRUST_TOLERANCE_DEG` (0.5) from JPL, or the test could not be made
  (`trust_verdict`). Any other body when JPL did not answer its test's
  question: worked out by that same rule at each build, never from a
  list (on 2026-11-24 they were the Moon, Phobos, Deimos, Io, Titan,
  Pluto and Charon; a moon added later joins them with no edit here)
  (`measure_trust` marks the null block `unanswered`; L-553, run #58's
  Deimos). A moon, or any body with its own span, is NOT held for a
  number over the limit: the Moon runs 0.10 to 0.18 degrees on ordinary
  nights from the Sun's pull, so over it is likely physics, and an older
  orbit draws it worse; and a test that cannot apply (no mean motion, an
  open orbit) keeps its own treatment, served with a null window.
  Replayed on the 186 committed indexes of Jul 11 to Nov 11: Halley on
  Nov 10 and 11, only. And any body JPL does not answer at all.
- HOW (`hold_from_prior`). Served from its entry in the replaced cache,
  whole, `as_of_today` cleared as A-3 does, with a `hold` block (since,
  kind, why, from_generated, passed_before), copied forward each build
  while it lasts, so it outlives any number of swaps; `.prev` is never
  the store. It leaves the served window, which the bodies that passed
  set. Tested every build, it ends when it passes. No entry to hold at:
  not served, named -- also for a body JPL did not answer (L-553; until
  then such a body was served its last elements from the raw archive
  with no measured error, which no box could print).
- WHAT IS SERVED LAST-GOOD FROM ITS OWN ARCHIVE IS HELD TOO (L-553,
  `last_good_hold`): a path JPL did not answer ("drawn from the last path
  JPL gave it"), a Lagrange point served its saved days ("placed from
  its saved days"), a capture craft on its saved layer or with none
  (`capture_hold`, kind 'capture'). Each is on the index's `holds`, so the
  night's title names it and `HOLD_LIMIT` counts it. Their boxes read as
  before: the page prints no held sentence for a path or a point.
- THE HOLD RUNS TO THE NIGHT'S GATE (L-553). No row after the build is
  red because a body is held. The Solar System figures check accepts a
  drawer body, a path, a point or a moon with something missing only by
  the hold its entry names and the index's list (`heldIssue`), the held
  sentence printable and a measured error served for the orbit held at,
  and prints "Held bodies accepted by their named hold (N): ...";
  Curve error accepts a capture craft served last-good the same way
  (`hold_captures`); Artifact 1's T1 accepts Earth held (`t1_line`).
  Something missing and no hold named stays red, by name.
- REPORTED, NOT RED. The index's `holds` gives each body's line, "HELD
  Halley since 2026-11-11: its accuracy test was 21.6 degrees from JPL
  at 30 days (the limit is 0.5); drawn from the build of 2026-11-10",
  and "HOLD ENDED". `daily_run.py` prints them in both summaries; its
  `--held-title` starts the night's commit title, "HELD Halley --
  Nightly run ...", and an unreadable index stops the commit.
- More than `HOLD_LIMIT` (5) held is a failed build: ABORT, no swap.
  Before, JPL answering nothing still swapped, 94 of 102 last-good.
- A fault in the maths, not the data, is held while drawn wrong; the
  title is then the only signal.
- CHECKED: the suite's `hold_checks` (11; 1 of 10 on the old builder),
  `night_hold_checks` (15, L-553: planted nights with the night's rows
  run on the planted folder; 13 of 15 red on the old code, the other two
  guards) and `daily_run.py --check`. The page: interactive-exhibit. NOT
  BUILT: L-508's quiet half (a ledger handle on the line); it stays loud.
- THE CLOCK IS NOT A BODY: JPL not answering the clock or its witness
  still stops the build (L-541), after its second try.

## A Capture Craft's Box Never Claims Less Than Its Miss

Built 2026-11-24 (L-538, the orbiters' printed error), in the gallery
at 727ebf79. The builder's part is the block headed THE ORBITERS in
`tools/gallery_cache_builder.py`; the room's part is `position_at` in
`gallery/assembler/render_spacecraft.py`; the check is
`tools/test_curve_error.py`, the gallery run's "Curve error" row.

- WHO IS IN A CAPTURE (`captures_of`, `capture_of`, `capture_span`).
  `captures_of` lists every arrival in the plan the entry carries, in
  time order. Each capture starts at its arrival's moment and ends at
  the first of: its departure from the same body, the next arrival, the
  end of the plan's span. With the served window, `capture_of` takes the
  last capture whose stretch meets it, else the last one.
  `capture_span` gives the fine layer's days: from a day before the
  window's first day, or the arrival's day if later, to a day after its
  last day, or the last whole day before the capture ends if earlier;
  none when they do not meet (an ended mission, an arrival after the
  window). The build takes the captures after every other body and the
  window are known, before the Lagrange points, skips a craft with no
  span, and prints one line naming each craft, its body and its
  arrival's day, or that no craft is in a capture inside the window. A
  comet on an open path has none.
- THE FIRST QUESTIONS (`build_capture_layer`). A point a day across the
  span; a point an hour across the band near today (`point_near_span`,
  yesterday at 00:00 UTC to the end of the day after tomorrow, the
  Lagrange points' band); and JPL's check points, one every
  `CAPTURE_CHECK_STEP_MIN` (37) minutes, a step no served step divides,
  from an offset worked from the build's date (`capture_check_offset`),
  so they meet a loop at other places each night. Every question counts
  against `CAPTURE_QUESTION_LIMIT` (80).
- THE ROUNDS. Each round, up to `CAPTURE_ROUNDS` (12), runs both tests
  below on the served rows with the chord's figure alone, and makes
  every UTC day where a case is over finer by one rung: a day down
  `CAPTURE_LADDER`, 1440, 720, 360, 180, 90, 45, 15, 5, 1 minutes; the
  band down `CAPTURE_BAND_LADDER`, 60, 30, 15, 5, 1. So a day's step
  halves down to 45 minutes, then goes to 15, 5 and 1. Each step divides
  the one above, so a day asked again keeps the minutes it had. Failing
  days up to `CAPTURE_RUN_GAP_DAYS` (7) apart share one question at the
  finest step any of them needs, under `CAPTURE_ROWS_PER_QUESTION`
  (40,000) rows; each day keeps only the points on its own grid, found
  by their order in JPL's answer, never by their clock.
- THE TWO SHAPES (`CAPTURE_FINE_LIMIT`, 3,000). A craft starts 'whole':
  every day of its span is made finer where it fails. In a round where
  the fine points across the window would pass the limit, it turns
  'band': every day outside the band goes back to a point a day, its
  finer points are dropped, only the band's days are made finer from
  then on, and the served block's `why` says so. The comment beside the
  setting gives the measure of 2026-11-24: Juno's fine layer 71 to 614
  points for every week to the end of JPL's data; BepiColombo's would
  be 13,138.
- WHEN THE FLOOR STILL FAILS. A failing day already at
  `CAPTURE_FLOOR_MIN` (1 minute), a twelfth round still failing, or the
  question limit raises `CaptureFailed`; JPL not answering ends the
  layer the same way (after its second try, `ask_jpl`). `process_capture`
  then serves the craft's saved fine layer from the raw archive, clipped
  to tonight's span, its block marked `last_good` with the reason in
  `last_good_why`, `saved_layer` true; with none saved, the plan's own
  points, `saved_layer` false. A DAY WITH NO FINE POINTS PRINTS NO
  DISTANCE (L-553; Tony, 2026-11-24: "with the no-distance option"):
  `no_figure_days` lists each UTC day of the span that no fine points
  cover whole and that carries no loop's reach -- every day with no
  saved layer, and the window's last day with a saved layer a night old
  -- served as the block's `no_figure_days` and in the positions file as
  `data.nofig_t` (each day's 00:00 UTC, JD), the plan's points kept on
  those days. The room's `position_at` (`nofig_of`) then gives no
  figure on a trio that reaches into such a day, `err_from`
  'no_figure', and the box prints no distance there: a missing figure
  never claims less than the miss. So #O no longer aborts the build for
  one craft (it still refuses a `missing` block, which nothing makes
  now). The build's warnings name it: "<slug>: CAPTURE FAILED (...);
  served its saved fine layer, last-good; no distance on <days>", or "no
  saved fine layer: served its plan's points, no distance on N day(s)";
  the run record's line says the same. The craft is HELD by name
  (`capture_hold`, kind 'capture'), so the night's title names it and
  `HOLD_LIMIT` counts it, and the hold ends, by name, on the night its
  layer is made. Tonight's check points are not written.
- THE LOOP'S REACH, for a craft served in the band only. After the
  rounds, JPL is asked for the craft around its planet's own centre
  (`_centre_of_body`, from the planet's config entry; none fails the
  craft), every 10 minutes (`CAPTURE_REACH_STEP`), 50 days to a
  question, and each UTC day's farthest distance is kept, rounded up to
  the metre, for the days a point a day apart only. The positions file
  serves it beside t, x, y, z as `data.reach_t` (the JD of each day's
  00:00 UTC) and `data.reach_km` (`build_position_file`); the raw
  archive keeps it with the fine layer.
- THE FLOOR, IN THE ROOM (`reach_of`, `position_at`, `_loop_term`). The
  room reads the reach with `reach_of` and hands it to `position_at`.
  For three served points the figure is the chord's PLUS R x (1 + L): R
  the largest reach of the days the three points' stretch overlaps by
  more than `REACH_EDGE_DAYS` (two minutes) at either end, L the sum of
  the sizes of the parabola's three weights at the minute; with only two
  points, the straight line's two. Where the loop's term is the larger
  part, `err_from` is 'loop'. Three points inside the band carry no
  reach and keep the chord's figure.
- THE TWO TESTS, IN THE BUILD, after the rounds, with the figure the box
  prints: every served point inside the span held out and worked out
  from the four on each side (`capture_held_out`), and every check point
  worked out from the served rows (`capture_check_misses`). A case is
  over when its miss passes its figure by more than
  `CAPTURE_MISS_ROOM_KM` (a metre). The capture block serves both counts,
  their overs, `over_without_floor` (the check points outside the band
  over with the chord's figure alone, the floor's witness) and the
  worst ratio of miss to figure. The pre-swap check #O
  (`capture_problems`) refuses a craft served counts over, a span not
  covered, a day or an hour missing, a day without its loop's reach, a
  reach inside the band, or a reach for a craft served whole.
- THE FINE LAYER IS REPLACED WHOLE each night, kept in the raw archive
  apart from the plan's points; the positions file is the plan's points
  outside the fine span and the fine layer inside it. JPL's own header
  for the path is read once a night (`fetch_path_revised`) and served on
  the block as `jpl`, with its "Data fit through" sentence where JPL
  prints one.
- THE CHECK POINTS (`save_capture_checks`). The build tests all of them;
  every fourth (`CAPTURE_CHECK_SAVE_EVERY`) is saved under the served
  cache's raw/checks/, one file a craft, as the Curve error row's
  witness, and the block serves both counts (`saved`, `saved_every`).
  The website's .gitignore names that folder, so they are never
  committed (Tony, 2026-11-24, 14:00); the night's run holds them where
  its own build wrote them.
- THE CURVE ERROR ROW (`hold_captures`). It finds the capture craft by
  the builder's own rule (`capture_craft`) and holds each across its
  fine span with the box's figure and the served reach
  (`capture_cases`): its served points held out, and the saved check
  points. With them, the craft's line gives both counts and the worst
  ratio, then its own self-test (`capture_self_test`): its check points
  moved by ten times the figure and a kilometre must each be caught;
  and for a band-only craft, its reach taken away, its point a day must
  miss somewhere outside the band. "Thinned to a point a day" is
  printed, not gated. A CRAFT SERVED LAST-GOOD (L-553) has no check
  points from tonight: it is accepted only by the hold its entry names
  and the index's list, its line saying "HELD since ..., served
  last-good (...); its JPL half not held tonight; no distance on N
  day(s)", its held-out half still gating on every day that prints a
  figure; the row prints "capture craft accepted by their named hold
  (N): ..."; with no hold named it is red, by name. WITHOUT THE CHECK
  POINTS, for a craft served fresh: with --night, which only
  the night's pass hands this row (`NIGHT_ARGS`, `night_checkers` in
  `gallery_maintenance_run.py`), the craft is red by name; anywhere else
  its line says its JPL half is NOT HELD HERE, with the night's own test
  as its block records it (`not_held_here`), it is not counted as held,
  its held-out half still gates, and the row's last line names it, "JPL's
  points not held here for ... (the night holds them)".

## The Daily Run's Steps

`daily_run.py`, Tony's design of 2026-09-27 (L-281), is FOUR steps
since 2026-10-15 (L-446), and the order is the point:

  1. The guest book updater. First, because it needs Tony's answers,
     and what he approves is saved at once.
  2. The pulls from the orrery: `gallery_maintenance_run.py --pull`,
     which runs only the five pull-and-mirror rows of its GENERATORS
     (constants export, config mirror, objects export, objects mirror,
     drawings). BEFORE the builder, so the build reads what the orrery
     exported today and the served `frame_constants.orrery_sha` names
     that export. Until 2026-10-15 the pulls ran only in step 4, after
     the build, so every build read the previous run's pull and its
     stamp was one step behind (L-380).
  3. This builder, with no flags.
  4. The gallery maintenance run, offline. Its pull rows run again and
     print "no change", which is the proof step 2 did the work.

The pull list has ONE home, the maintenance run's GENERATORS; `--pull`
reads it through `PULL_ROWS`. Do not add the pulls to `daily_run.py`'s
STEPS as rows of their own: that is a second copy of the list, and five
more dashboard buttons for Dashboard Parity to hold.

A PULL THAT CANNOT FETCH FAILS, AND THE DAILY RUN STOPS (Tony's option
A, 2026-10-15). Each pull prints one line starting `FAIL:` naming what
it could not fetch, from which address and why, writes nothing, and
exits 1 (L-388; until 2026-10-15 it printed N-A and exited 0, the
maintenance run read that as PASS "no change", and the mirror wrote the
config from the old export). The maintenance run does not run a mirror
whose pull failed (`FED_BY`): its row is red and names the pull. A
failed generator fails the whole run and is named in the summary. And
`daily_run.py` stops after step 2: the builder and the checks do not
run, and the summary quotes `--pull`'s "=== PULLS:" line. Nothing is
built on yesterday's export; Tony runs it again later. The builder
needs the network for Horizons anyway, so a day with no network builds
nothing either way. Option B -- build on the previous pull and say so
in red -- was declined. `tools/test_pull_failures.py` ("Pull failures",
gating) runs each pull with its network replaced by one that fails,
three ways, so these branches are tested every day and not only on the
day the network is down.

A PULL THAT DOES NOT MATCH THE PUSH IS A FAILED PULL (L-461; Tony,
2026-10-25: "stop. confirmed."). After the pulls, `daily_run.py`
compares each pull's recorded orrery commit (`data/constants_export.sha`,
`data/objects_export.sha`, `data/drawings/pulled_at.sha`) with the newest
commit in Tony's orrery folder, the folder `palomas_orrery_for_github`
beside the website's, read from its `.git` folder (HEAD, then the
branch's loose ref or packed-refs), so no git command is needed. When
they differ, the run STOPS before the builder, naming both commits and
the two likely causes -- the orrery's work is not pushed, or GitHub has
not finished serving a push -- and says to push, or wait a minute if the
push just went, then run the Daily Run again. SINCE THE ORRERY'S NIGHT
COMMITS (L-461's second honest cause, v1.15): Tony's orrery folder is
behind GitHub every morning the orrery's night committed, until he
clicks Pull origin, so the pulls (GitHub's copy) and his folder differ
for that reason too -- not yet pulled. The cure is Pull origin, orrery
then website, then the Daily Run again. No retry, no wait: the one
time it happened (2026-10-21) the cause was an unpushed orrery, which
waiting cannot fix, and a run that waits hides the common cause behind
the rare one. A folder or commit it cannot read stops it too, saying
where it looked. `python daily_run.py --check` runs the comparison on
five made-up cases and two planted faults (one that always matches, one
that ignores the drawings' pull).

THE RUN RECORDS ARE KEPT, AND CHECKED AFTER THE BUILDER (L-449). Each
build writes one record to `data/solar-system/raw/runs/`, and the builder copies the old
ones forward. Records went missing after builds on 2026-10-15 and
2026-10-16, cause unknown, and were put back from `.prev` on Tony's
word. Tony's rulings: keep EVERY record until the cause is found, then
a deliberate limit, its number set at that time, with the builder naming
each record it removes (2026-10-16); and on a loss, stop and name
(2026-10-17). So:

- The builder prints two `[RUNS]` lines at its copy-forward: how many
  records `data/solar-system/raw/runs` held before the copy and how many the staging
  copy holds after it, with both paths. It removes no record. These
  two lines are what the next loss is read from; record them in L-449.
- `daily_run.py` compares `data/solar-system/raw/runs/` with the
  replaced cache's `data/solar-system.prev/raw/runs/` between the
  builder and the maintenance run. On success it prints what it
  compared ("carried 85 of 85, plus tonight's"). A record in the old
  and not the new STOPS the Daily Run before the maintenance run,
  naming each lost record with its copy's path; Tony copies them back
  in File Explorer, then runs the maintenance run. The copies stay in
  `.prev` only until the next build clears it. A missing folder is
  "could not compare", reported as a problem, never as a pass; it does
  not stop the run, since it is what a failed or rolled-back build
  leaves.
- It is not a step of its own and has no dashboard button: it runs no
  script, and it means something only straight after a build. The
  builder's offline suite runs the comparison on its own builds and
  plants a loss, which must stop it by name.

THE NIGHT FORM (v1.15, L-485; `python daily_run.py --night`, run by the
gallery's workflow at 08:17 UTC). The same steps with no keyboard,
ending in one gate:

- The guest book is SKIPPED, by name: it needs Tony's answers and stays
  his morning's (Tony's ruling of 2026-10-31, 10:20). Nothing is read
  from Google on the runner.
- The pulls run as by day, asking GitHub's interface with the run's own
  token.
- PULL MATCHES PUSH, THE RUNNER FORM (`pull_matches_remote`): there is
  no orrery folder beside the website on GitHub's computer, so the three
  pulled commits must agree with each other and with the orrery's
  GitHub copy, read live with `git ls-remote`. A difference stops the
  night before the builder: no retry, no wait.
- The builder with no flags, never `--commit`; its swap read back off
  the swap log as tonight's, outcome ok. The run records check: a loss,
  or "could not compare", is red at night.
- The maintenance run's night pass (`gallery_maintenance_run.py
  --night`), an UNREACHABLE row red.
- THE GATE (`night_gate`), exit 0 only when ALL hold, each failure named
  on the last line, "NIGHT RUN: RED -- ...": the pulls passed and match
  the orrery's GitHub copy, and did not move after the build; the
  builder exited 0 and tonight's swap is ok; the run records were
  carried; the night pass passed with nothing UNREACHABLE; git sees
  nothing changed or new outside the allow-list (`night_allow_list`);
  every changed file is ASCII; and the change under
  `data/solar-system/` is not deletions only.
- The commit title starts with every held body, "HELD Halley -- "
  (`--held-title`, v1.19, L-525); a hold is not red.
- A clean night writes `data/nightly_run_record.json`; a red night
  writes nothing, and its record is the run's log. `python daily_run.py
  --check` judges made-up nights and planted faults for the gate and
  the runner form.
- THE MORNING DOES NOT WAIT FOR THE NIGHT (v1.16, L-485; Tony's ruling
  of 2026-11-01, 12:04 Chicago): Tony pulls first and does not wait for
  the run, and a run that lands later in the day comes with his next
  Pull origin -- because GitHub's schedule is best-effort. Its page
  "Events that trigger workflows", read 2026-11-01: "The schedule event
  can be delayed during periods of high loads of GitHub Actions
  workflow runs" and "If the load is sufficiently high enough, some
  queued jobs may be dropped." Both nights started about seven hours
  late on 2026-11-01. A dropped night is caught the same day by a
  second scheduled line: the orrery's at 11:17 UTC, the website's at
  12:17 (each `.github/workflows/nightly.yml`). A second firing is
  harmless: the concurrency group queues it, and a clean second run
  commits only its night record. The times stay (no reschedule): the
  lag is GitHub's, not the clock's.

Apart from the pulls and the records, a step that reports a problem
does not stop the next: the guest book's problems still do not stop the
build. Nothing in the Daily Run commits or pushes. The gallery's
"Horizons confirmations" row still reads the dates JPL confirmed each
object, from the pulled export, offline, and goes red, naming the
objects, on the day a confirmation turns 30 days old: the cure is the
orrery's maintenance run, then the push, then the pull here. `python
daily_run.py --check` lists the steps and fails if a script is missing;
the maintenance run runs it.

Written November 2026 with Anthropic's Claude Opus 5.5.
