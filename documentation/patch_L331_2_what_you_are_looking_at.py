#!/usr/bin/env python3
"""
patch_L331_2_what_you_are_looking_at.py -- GALLERY repo.

Run: save this file in the GALLERY repo root (next to interactive.html),
open it in VS Code and click Run.  Or:  python patch_L331_2_what_you_are_looking_at.py
Then:  1. the nightly (tools/gallery_cache_builder.py, as you ran it today)
          so data/solar-system/feature_configs.json carries the new fields
       2. python gallery_maintenance_run.py      (offline; hover budget now
          measures every description and about)
       3. commit, push, python gallery_maintenance_run.py --live
       4. Mode 5, both rooms: every hover opens with one or two plain
          sentences under its name; the i panel opens with a paragraph
          under the shell's name, above its link.

Built on gallery 744ad578ed05bef702cebe5bc7c7aef3069df745
at https://github.com/tonylquintanilla/tonyquintanilla.github.io
(orrery text read at bfc1706b8b0f14ce28cee893381ca3d511fea9ce
at https://github.com/tonylquintanilla/palomas_orrery).

L-331, TONY'S MODE 5 OF 2026-09-16: "it has data but no description of
what we are looking at. this is information we previously had. we cannot
assume the visitor knows what they are looking at at a basic level."
Every gallery hover said a name, a number and the pointer line. The
orrery's own hovers -- solar_visualization_shells.py and
earth_visualization_shells.py, the *_info strings -- say what each thing
IS. That text never crossed into the gallery.

WHAT THIS DOES (four files, all-or-nothing):

  data/objects_config.json -- the served store. Every Sun and Earth
    feature gains two fields:
      "description"  one or two plain sentences: what the visitor is
                     looking at. Shown in the HOVER, under the name,
                     before the numbers.
      "about"        a short paragraph, condensed from the orrery's own
                     info text. Shown in the i PANEL under the shell's
                     name, above its link.
    The belts, whose fields are parallel lists, gain "descriptions" and
    "abouts". The panel field is named `about` rather than `detail`
    because `detail` already carries the magnetopause's and bow shock's
    equations, and the panel shows both. The nightly copies the store
    verbatim (tools/gallery_cache_builder.py validates shapes only), so
    the fields are served after the next run.

  gallery/feature_renderers.js -- every hover the Sun and Earth rooms
    build inserts the description under the label; stampLink() carries
    `about` to the panel; the belt hovers lose "sourced", "drawing
    choice" and "illustrative" (Tony's rule, and the ceiling: with a
    description on top the outer belt would have passed 17 lines).
    Jupiter's and Saturn's rings are untouched: they have no room yet
    and no served names.

  interactive.html -- the drawer reads `about` off the trace meta and
    the panel shows it first.

  documentation/smoke_earth_geometry.js -- its wording pins on the belts
    and the magnetosphere follow the plain phrases; the content they pin
    (the served tilt with model and epoch, the plane, the measured extent,
    the width caveat, the drawing cut) is unchanged and still checked.

  documentation/smoke_hover_budget.js -- its two Earth legs read
    fixtures that predate these fields, so they now overlay
    description/about from data/objects_config.json onto the fixture
    features before rendering; otherwise the suite would measure hovers
    the page no longer shows. The Sun leg already reads the store.

THE WORDING. Tony, 2026-09-16: the orrery's text is already seen and
approved, go to the patch. Each description and about below is condensed
from the named orrery string, in plain words, with no project vocabulary,
and keeps only facts that string states. Nothing is added from memory.
The strings are in one place (WORDING, below) if any wants changing.

FAILURE: a single ERROR: or ANCHOR FAIL line, and NOTHING is written.
Undo is Discard Changes in GitHub Desktop.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))

FILES = {
    'data/objects_config.json': '9f2a11fb5f9a141e656379440b3877bd',
    'gallery/feature_renderers.js': '9a83a3439b05381c8d009b980af64766',
    'interactive.html': 'bae76aad640b17fbf939d015d4fc2aad',
    'documentation/smoke_hover_budget.js': 'ad12d275525b3466c1c7733722348764',
    'documentation/smoke_earth_geometry.js': 'a2854757f1abcdeb910db3aa631fb540',
}

# ======================================================================
# WORDING -- keyed by the feature's served "name" (exact). Each entry:
# (description for the hover, about for the panel, orrery source string)
# ======================================================================
WORDING = {
# ---- Sun -------------------------------------------------------------
"Core": (
  "The Sun's center, where hydrogen fuses into helium and the Sun's light and heat are made.",
  "The core reaches out to about a quarter of the Sun's radius and holds about a third of its mass. It is the hottest place in the solar system, near 15 million kelvin, and about 150 times denser than water under the weight of the layers above. Hydrogen nuclei fuse into helium there in the proton-proton chain, turning a little mass into a great deal of energy, which then works its way outward through the radiative zone and the convection zone to the surface.",
  "solar_visualization_shells.py::core_info"),
"Radiative Zone": (
  "The deep layer around the core where energy crawls outward as light, absorbed and re-emitted countless times.",
  "The radiative zone lies between the core and the convection zone, from about a fifth to about seven tenths of the Sun's radius. It is dense and opaque: a photon made in the core travels only a short distance before it is absorbed and sent on again, so its energy can take millions of years to cross this layer. Temperatures fall from about 7 million kelvin near the core to about 2 million at the top of the zone.",
  "solar_visualization_shells.py::radiative_zone_info"),
"Photosphere": (
  "The Sun's visible surface: the thin, glowing layer that the light we see comes from.",
  "Below the photosphere, in the convection zone, hot gas rises, cools and sinks, carrying energy the last stretch to the surface. At the photosphere, a layer only about 500 km thick, that energy leaves as light, at about 5,500 kelvin. To the eye it is a smooth disk; up close it shows granulation, the tops of the convection cells, and sunspots, cooler patches held by strong magnetic fields that can be larger than Earth.",
  "solar_visualization_shells.py::photosphere_info"),
"Streamer Belt (helmet and stalk)": (
  "The brightest part of the Sun's outer atmosphere, seen at a total eclipse as the pearly white halo, shaped by the Sun's magnetic field.",
  "A streamer is two things stacked. The helmet, a dome of closed magnetic loops, rises only a few solar radii. Above its cusp the field opens and the solar wind draws the gas out into a long thin stalk. The band drawn here is one object with both parts: wide and dense at the base, pinched at the cusp, then thinning until it dissolves into the solar wind. It has no drawn outer edge because there is no edge: what the eye sees at an eclipse is a boundary of brightness, not a surface.",
  "solar_visualization_shells.py::streamer_belt_info"),
"Chromosphere (2,000 km skin)": (
  "A thin, reddish layer of the Sun's atmosphere just above the visible surface, about 2,000 km deep.",
  "The chromosphere sits between the photosphere and the corona and takes its name from the Greek word for color, because the hydrogen in it glows red. It is far less dense than the surface, and its temperature rises with height, from a few thousand kelvin at the bottom to about 20,000 at the top. It is never still: jets of gas called spicules rise and fall like geysers, and cooler prominences hang in it, held up by magnetic fields.",
  "solar_visualization_shells.py::chromosphere_info"),
"Inner Corona": (
  "The lowest part of the Sun's outer atmosphere: a thin gas at millions of degrees, shaped by the Sun's magnetic field.",
  "The inner corona is the part of the corona nearest the surface. It is thin, far thinner than the photosphere, and yet at one to three million kelvin it is much hotter, a puzzle known as the coronal heating problem. The magnetic field rules it: closed loops trap glowing gas in bright arcs, open regions called coronal holes let gas escape as the solar wind, and streamers reach outward. Because it is so faint it is seen directly only at a total eclipse or with special instruments.",
  "solar_visualization_shells.py::inner_corona_info"),
"Roche Limit (Comets)": (
  "The distance inside which the Sun's tides would pull a loosely held comet apart.",
  "Inside the Roche limit the difference in the Sun's pull across a body outweighs the body's own gravity. The limit drawn here is for a comet held together only by its own gravity, at a typical comet density. It is not a hard wall: the strength of the ice and rock can hold a nucleus together well inside it, and several sungrazing comets have survived far closer than this line before breaking up or escaping.",
  "solar_visualization_shells.py::roche_limit_info"),
"Alfven Surface": (
  "The true outer edge of the Sun's atmosphere, where the outflowing gas becomes the solar wind and can no longer signal back to the Sun.",
  "Inside the Alfven surface the gas is tied to the Sun by its magnetic field, and a disturbance there can travel back to the surface. Outside it the gas moves faster than magnetic waves can carry a signal inward, so it is on its own, and is called the solar wind. NASA's Parker Solar Probe crossed this boundary in April 2021, the first spacecraft to fly inside the corona. The surface is not a smooth sphere: it is lower over the poles and higher over the streamer belt.",
  "solar_visualization_shells.py::alfven_surface_info"),
"Outer Corona": (
  "The faint outer reach of the Sun's atmosphere, where sunlight scattered by dust gives a soft glow far beyond the streamers.",
  "At this distance the corona is extremely thin. Sunlight scattered by dust, the F-corona, outshines the light scattered by electrons that dominates nearer the Sun. By here the gas has long since become the solar wind; the shell marks the extent of the faint glow rather than a physical edge.",
  "solar_visualization_shells.py::outer_corona_info"),
"Termination Shock": (
  "The place far beyond the planets where the solar wind slows suddenly from supersonic speed as it meets the gas between the stars.",
  "The solar wind streams outward at supersonic speed until the pressure of the interstellar gas brings it up short. At the termination shock it slows abruptly, and its energy of motion becomes heat. Voyager 1 crossed it at 94 AU and Voyager 2 at 84 AU; beyond it the wind moves at a few hundred kilometers a second through the turbulent region called the heliosheath.",
  "solar_visualization_shells.py::termination_shock_info"),
"Heliopause": (
  "The outer boundary of the Sun's bubble, where the solar wind's push is balanced by the gas between the stars.",
  "The solar wind, a constant stream of charged particles from the Sun, inflates a vast bubble called the heliosphere around the Sun and planets. The bubble is not round: the Sun's motion through interstellar gas gives it a rounded head and a long tail. The heliopause is its outermost boundary, where the wind's pressure equals the pressure of the interstellar medium, and it shields the planets from much of the galaxy's cosmic radiation.",
  "solar_visualization_shells.py::solar_wind_info"),
"Hills Cloud (torus)": (
  "The inner part of the Oort cloud: a thick, flattened ring of icy bodies far beyond the planets, the reservoir that feeds the comets.",
  "The Oort cloud is a vast, unseen swarm of icy bodies surrounding the solar system, thought to be the source of the long-period comets. Its inner part, the Hills cloud, is more tightly bound to the Sun than the outer cloud and, in dynamical models, is flattened into a disk-like or doughnut shape by the pull of the galaxy. Nobody has seen it directly; its existence is inferred from the orbits of comets and from distant objects such as Sedna, which may belong to it.",
  "solar_visualization_shells.py::hills_cloud_torus_info, inner_oort_info"),
"Outer Oort Cloud (clumps)": (
  "The outer Oort cloud: a rough sphere of icy bodies at the very edge of the Sun's reach, drawn here as clumps.",
  "The outer Oort cloud is a roughly spherical shell of icy bodies, cometary nuclei of water ice, ammonia and methane, reaching out to about a light-year and a half from the Sun. Objects here are only loosely held, so passing stars and the galaxy's tide can nudge them inward as long-period comets, the ones that take more than two centuries to circle the Sun. Simulations suggest the cloud is lumpy rather than smooth, which is what the clumps show; where any real lump lies is not known.",
  "solar_visualization_shells.py::outer_oort_clumpy_info, outer_oort_info"),
"Galactic Tide (thinned at the plane)": (
  "How the Milky Way's gravity shapes the Oort cloud: its bodies drawn thinned out near the plane of the galaxy.",
  "The Sun sits inside the Milky Way, and the galaxy's gravity pulls differently on the near and far sides of the Oort cloud. Over millions of years that tide sculpts the cloud, thinning it in some directions and thickening it in others, and it is one of the forces that send outer Oort cloud comets falling toward the Sun. The drawing shows the idea rather than a map: the cloud has never been imaged.",
  "solar_visualization_shells.py::galactic_tide_info"),
"Inner Limit of Oort Cloud": (
  "The inner edge of the Oort cloud, where the swarm of icy bodies is thought to begin.",
  "The Oort cloud is a vast shell of icy bodies surrounding the solar system, believed to be the source of the long-period comets. This sphere marks where its inner part, the Hills cloud, begins; between it and the Kuiper belt lies a sparse gap in which distant objects such as Sedna travel.",
  "solar_visualization_shells.py::inner_limit_oort_info"),
"Inner Oort Cloud": (
  "The outer edge of the inner Oort cloud, where the flattened inner swarm gives way to the spherical outer cloud.",
  "The inner Oort cloud, or Hills cloud, is the more tightly bound part of the cloud, an intermediate zone between the Kuiper belt and the outer cloud. This sphere marks its outer limit. The cloud is made mostly of cometary nuclei, small icy bodies of water ice, ammonia and methane, and no one has observed it directly.",
  "solar_visualization_shells.py::inner_oort_info"),
"Outer Oort Cloud": (
  "The outer edge of the Oort cloud, about a light-year and a half from the Sun, where the Sun's realm gives way to the space between the stars.",
  "At this distance the outer Oort cloud fades out. It is the usual mark for the boundary between the solar system and interstellar space by gravity, far beyond the heliopause where the solar wind stops. Objects here are loosely bound and easily disturbed by passing stars; the long-period comets come from this region.",
  "solar_visualization_shells.py::outer_oort_info"),
"Gravitational Influence": (
  "The outer limit of the Sun's gravitational hold: how far out a body can still belong to the Sun rather than to the galaxy.",
  "The solar system's extent can be defined in more than one way. The heliopause marks where the solar wind ends, but the Sun's gravity reaches much farther, holding Sedna, the Hills cloud and the outer Oort cloud. Astronomers count these as part of the solar system even though the Oort cloud has never been observed directly. This sphere is the outer limit of that gravitational influence.",
  "solar_visualization_shells.py::gravitational_influence_info"),
# ---- Earth -----------------------------------------------------------
"Inner Core": (
  "A solid ball of iron and nickel at Earth's center, nearly at its melting point despite the crushing pressure.",
  "Temperatures near 5,400 degrees Celsius keep the inner core close to melting even under the weight of the whole planet. It turns slightly faster than the rest of Earth, which adds complexity to the magnetic field generated in the liquid layer above it.",
  "earth_visualization_shells.py::earth_inner_core_info"),
"Outer Core": (
  "A liquid layer of iron and nickel whose churning currents generate Earth's magnetic field.",
  "The outer core is molten iron and nickel with lighter elements mixed in, at 4,500 to 5,400 degrees Celsius. Convection in this conducting fluid acts as a dynamo, the geodynamo, and produces the magnetic field that reaches out into space to form the magnetosphere.",
  "earth_visualization_shells.py::earth_outer_core_info"),
"Lower Mantle": (
  "The deep layer of hot, solid rock between the core and the upper mantle, flowing very slowly over millions of years.",
  "The lower mantle is solid silicate rock rich in iron and magnesium, at 2,200 to 4,500 degrees Celsius and under enormous pressure. Although solid, it creeps slowly by convection, and that slow flow is what drives the plates at the surface.",
  "earth_visualization_shells.py::earth_lower_mantle_info"),
"Upper Mantle": (
  "The rock beneath the crust, including the partly molten layer where most magma is born and on which the plates slide.",
  "The upper mantle includes the asthenosphere, a partly molten layer that flows more readily than the mantle below it, letting the tectonic plates move. It reaches from the base of the crust down to the top of the lower mantle, with temperatures from about 500 to 2,200 degrees Celsius.",
  "earth_visualization_shells.py::earth_upper_mantle_info"),
"Crust": (
  "Earth's thin, solid outer skin: the ground we live on, the ocean floors, and everything that has ever lived.",
  "The crust is thin compared with the planet: 5 to 10 km under the oceans, where it is mostly basalt, and 30 to 50 km under the continents, where it is mostly granite. Surface temperatures range from about minus 80 to 60 degrees Celsius. It holds all known life and every resource we can reach.",
  "earth_visualization_shells.py::earth_crust_info"),
"Lower Atmosphere (to the stratopause)": (
  "The air where weather happens and the ozone layer sits: the troposphere and stratosphere, holding nearly all the atmosphere's mass.",
  "The troposphere, the lowest 12 km or so, is where clouds and weather form; above it the stratosphere, to about 50 km, holds the ozone layer. Together they contain 99 percent of the atmosphere's mass, mostly nitrogen and oxygen. Temperature falls from about 15 degrees Celsius at sea level to minus 60 at the top of the troposphere, then warms again toward the stratopause as ozone absorbs sunlight.",
  "earth_visualization_shells.py::earth_atmosphere_info"),
"Upper Atmosphere (to the thermopause)": (
  "The thin upper air where meteors burn up, the aurora glows, and the Space Station orbits, fading toward space.",
  "Above 50 km lie the mesosphere, where most meteors burn up, the thermosphere, where the aurora appears and the International Space Station flies, and, higher still, the beginning of the exosphere. In the thermosphere the gas can reach 2,000 degrees Celsius, yet it is so thin it would feel cold to the skin.",
  "earth_visualization_shells.py::earth_upper_atmosphere_info"),
"Exosphere / Geocorona (hydrogen halo, detected extent)": (
  "A faint halo of hydrogen gas that surrounds Earth and thins out far into space, the outermost trace of the atmosphere.",
  "The exosphere has no top: it simply thins into space. Its hydrogen glows faintly in ultraviolet light, a halo called the geocorona. This shell is drawn where that glow has been detected, not where the atmosphere ends.",
  "earth_visualization_shells.py::earth_upper_atmosphere_info; the served note"),
"Low Earth Orbit, inner edge (200 km)": (
  "The lower edge of low Earth orbit, the band of space where most satellites and the Space Station fly.",
  "Low Earth orbit is the region from roughly 200 to 2,000 km up. Satellites there circle at every angle to the equator, so together they form a shell around Earth rather than a ring, and each completes an orbit in about 90 to 120 minutes. The International Space Station, the Hubble Space Telescope, Starlink and most weather and Earth-observing satellites live here; the moving lights seen at dusk and dawn are usually these.",
  "earth_visualization_shells.py::earth_leo_shell_info"),
"Low Earth Orbit, outer edge (2,000 km)": (
  "The upper edge of low Earth orbit, about 2,000 km up, above which the sky belongs to higher orbits.",
  "Low Earth orbit is the region from roughly 200 to 2,000 km up. Satellites there circle at every angle to the equator, so together they form a shell around Earth rather than a ring, and each completes an orbit in about 90 to 120 minutes. The International Space Station, the Hubble Space Telescope, Starlink and most weather and Earth-observing satellites live here; the moving lights seen at dusk and dawn are usually these.",
  "earth_visualization_shells.py::earth_leo_shell_info"),
"Geostationary Belt (GEO)": (
  "A ring of satellites 35,786 km above the equator that circle exactly as fast as Earth turns, so each hangs over one spot.",
  "Satellites in the geostationary belt orbit once a day, matching Earth's rotation, and so stay fixed over a point on the equator. Several hundred of them carry television, weather imagery and communications for much of the world. In April 2029 the asteroid Apophis will pass inside this ring, a few thousand kilometers below the nearest satellites.",
  "earth_visualization_shells.py::earth_geostationary_belt_info"),
"Magnetopause": (
  "The outer boundary of Earth's magnetic field, where it holds off the solar wind: pressed in by day, trailing a long tail by night.",
  "Earth's magnetic field carves a cavity in the solar wind called the magnetosphere. On the side facing the Sun the wind presses it in; on the night side it stretches into a magnetotail observed far beyond the Moon's distance. The magnetopause is that boundary. It deflects the solar wind and turns aside many of the charged particles that reach Earth from the Sun and from beyond the solar system. The surface drawn is a model for a quiet solar wind; the real boundary moves in and out as the wind's pressure changes.",
  "earth_visualization_shells.py::earth_magnetosphere_info"),
"Bow Shock": (
  "The shock wave where the supersonic solar wind first slows as it hits Earth's magnetic field, like the bow wave of a boat.",
  "The solar wind moves faster than sound travels through the thin gas of space, so when it meets Earth's magnetic field it cannot flow smoothly around it: a standing shock forms upstream, sunward of the magnetopause, where the wind slows and heats. The surface drawn is a model for a quiet solar wind, and real crossings scatter around it.",
  "earth_visualization_shells.py::earth_magnetosphere_info"),
"Hill Sphere (gravitational dominance over the Sun)": (
  "The region where Earth's gravity, not the Sun's, is the stronger hold; the Moon orbits well inside it.",
  "Inside the Hill sphere a body can orbit Earth without being pulled away by the Sun. The Moon lies deep within it. Beyond this sphere the Sun's gravity wins, and an object would drift into its own orbit around the Sun.",
  "earth_visualization_shells.py::earth_hill_sphere_info"),
}

BELT_WORDING = {
"Inner Radiation Belt": (
  "A ring of trapped charged particles, mostly protons, held by Earth's magnetic field close above the atmosphere.",
  "The inner Van Allen belt is a region of energetic protons trapped by Earth's magnetic field. It follows the magnetic equator, which is tilted from the geographic one and turns with Earth once a day; the ring drawn here lies in the daily average of that plane.",
  "earth_visualization_shells.py::earth_magnetosphere_info"),
"Outer Radiation Belt": (
  "A broader ring of trapped electrons farther out, that swells and shrinks with solar storms.",
  "The outer Van Allen belt is mostly energetic electrons, trapped farther out than the inner belt, and it swells and shrinks as the solar wind changes. Like the inner belt it follows the magnetic equator; the ring drawn is the daily average of that tilted plane.",
  "earth_visualization_shells.py::earth_magnetosphere_info"),
}


def jstr(s):
    """A JSON string literal, ASCII only, as the file writes them."""
    return json.dumps(s, ensure_ascii=True)


# ======================================================================
# JSON edits: insert two lines after each feature's "name" line
# ======================================================================
def edit_config(text):
    lines = text.split('\n')
    out = []
    used = set()
    i = 0
    while i < len(lines):
        ln = lines[i]
        out.append(ln)
        m = re.match(r'^(\s*)"name": ("(?:[^"\\]|\\.)*")', ln)
        if m:
            name = json.loads(m.group(2))
            if name in WORDING:
                if name in used:
                    raise ValueError('feature name appears twice: ' + name)
                used.add(name)
                ind = m.group(1)
                d, a, _src = WORDING[name]
                out.append(ind + '"description": ' + jstr(d) + ',')
                out.append(ind + '"about": ' + jstr(a) + ',')
        if re.match(r'^\s*"names": \[\s*$', ln):
            # the belts: copy the list through, then add two parallel lists
            ind = re.match(r'^(\s*)', ln).group(1)
            names = []
            i += 1
            while not re.match(r'^\s*\],?\s*$', lines[i]):
                out.append(lines[i])
                names.append(json.loads(lines[i].strip().rstrip(',')))
                i += 1
            out.append(lines[i])
            for key, idx in (('descriptions', 0), ('abouts', 1)):
                out.append(ind + '"' + key + '": [')
                for k, nm in enumerate(names):
                    if nm not in BELT_WORDING:
                        raise ValueError('no belt wording for ' + nm)
                    out.append(ind + '  ' + jstr(BELT_WORDING[nm][idx]) +
                               (',' if k < len(names) - 1 else ''))
                out.append(ind + '],')
            used.update(names)
        i += 1
    missing = set(WORDING) - used
    if missing:
        raise ValueError('served names not found: ' + ', '.join(sorted(missing)))
    if set(BELT_WORDING) - used:
        raise ValueError('belt names not found')
    result = '\n'.join(out)
    json.loads(result)          # still valid JSON, or nothing is written
    return result


# ======================================================================
# Renderer, page and suite edits
# ======================================================================
EDITS = {}

EDITS['gallery/feature_renderers.js'] = [

(b""" * Module updated: September 16, 2026 with Anthropic's Claude Opus 5
 *   (L-331: the Sun's four custom shapes -- streamer belt, Hills torus,
 *   Oort clumps, galactic tide -- send their citations to the i panel
 *   through withGatheredSource() and end their hovers with the pointer
 *   line like every other hover; each carries its caveat in plain words.
 *   Their served notes reach the panel for the first time).
 */
""",
b""" * Module updated: September 16, 2026 with Anthropic's Claude Opus 5
 *   (L-331: the Sun's four custom shapes -- streamer belt, Hills torus,
 *   Oort clumps, galactic tide -- send their citations to the i panel
 *   through withGatheredSource() and end their hovers with the pointer
 *   line like every other hover; each carries its caveat in plain words.
 *   Their served notes reach the panel for the first time).
 * Module updated: September 16, 2026 with Anthropic's Claude Opus 5
 *   (L-331, Tony's Mode 5: every Sun and Earth hover opens with the
 *   served `description` -- what the visitor is looking at, in plain
 *   words -- under its name, through descLine(); the served `about`
 *   paragraph rides to the i panel in meta. The belt hovers lose their
 *   project vocabulary. Rings untouched: no room, no served names).
 */
"""),

# the helper, next to wrapHover
(b"""  function wrapHover(text) {
""",
b"""  /*
   * L-331 (2026-09-16), Tony's Mode 5: "it has data but no description of
   * what we are looking at." Every hover opens with the served
   * `description`, one or two plain sentences saying what the thing IS,
   * wrapped like any other hover prose. A feature with none served gets
   * nothing here rather than a placeholder; the store is where the words
   * live, so a missing sentence is a store gap and not a rendering one.
   */
  function descLine(cfg) {
    if (isDict(cfg) && typeof cfg.description === "string" && cfg.description) {
      return wrapHover(cfg.description) + "<br><br>";
    }
    return "";
  }

  function wrapHover(text) {
"""),

# stampLink carries about
(b"""    if (typeof cfg.note === "string" && cfg.note) {
      meta = meta || {};
      meta.note = cfg.note;
""",
b"""    // L-331 (2026-09-16): the served `about` paragraph -- what the thing
    // is, condensed from the orrery's own info text -- rides to the panel
    // and is shown first there, above the link.
    if (typeof cfg.about === "string" && cfg.about) {
      meta = meta || {};
      meta.about = cfg.about;
    }
    if (typeof cfg.note === "string" && cfg.note) {
      meta = meta || {};
      meta.note = cfg.note;
"""),

# belts: parallel lists, description in hover, plain words, about to panel
(b"""    names = params.names || declared.names || [];
    colors = params.colors || declared.colors || [];
""",
b"""    names = params.names || declared.names || [];
    colors = params.colors || declared.colors || [];
    // L-331: the belts keep their prose as parallel lists like their names.
    var descs = Array.isArray(params.descriptions) ? params.descriptions : [];
    var abouts = Array.isArray(params.abouts) ? params.abouts : [];
"""),
(b"""      var hover = label + "<br><br>" +
        "Drawn at " + distances[i].toFixed(1) + " " + bodyName +
        " radii, the sourced flux peak" +
        (units[i] === "l_shell"
          ? SOFT_BR + "(served as L = " + distances[i].toFixed(1) + " -- that is the" +
            " radius where the L shell" + SOFT_BR +
            "crosses the magnetic equator)<br>"
          : "<br>") +
        "= " + kmAndAu(distances[i] * radiusKm) + "<br>" +
        (span
          ? "Sourced span: " + span[0].toFixed(1) + " to " +
            span[1].toFixed(1) + " " + bodyName + " radii<br>"
          : "") +
        "Drawn as a band " + thickness.toFixed(1) + " radii wide, which is a" +
        SOFT_BR + "drawing choice and not the belt's width<br>" +
        "The ring lies in " + bodyName + "'s equatorial plane. The belts" +
        " follow the" + SOFT_BR + "magnetic equator, " +
        (tilt === null
          ? "which is tilted from it and turns with" + SOFT_BR
          : "tilted " + tilt.toFixed(1) + " degrees from it (IGRF-13," +
            " epoch" + SOFT_BR + "2020-2025), and turning with ") +
        bodyName + " once a day; this plane is the daily average.<br>" +
        "Trapped-particle region; the band's shape is illustrative.";
""",
b"""      // L-331 (2026-09-16): opens with the served description; "sourced",
      // "drawing choice" and "illustrative" are gone (Tony: no compressed
      // language in the hover), and the closing line with them, since the
      // description says what the belt is. The tilt and the plane stay,
      // in plain words: the tilt is quoted because it is served (L-231),
      // and smoke_earth_geometry.js pins both. The L-shell aside is one
      // line now; that and the width line pay for the description.
      var hover = label + "<br><br>" + descLine({description: descs[i]}) +
        "Drawn at " + distances[i].toFixed(1) + " " + bodyName +
        " radii, where the measured particle flux peaks" +
        (units[i] === "l_shell"
          ? SOFT_BR + "(given as L = " + distances[i].toFixed(1) +
            ": where that field line crosses the magnetic equator)<br>"
          : "<br>") +
        "= " + kmAndAu(distances[i] * radiusKm) + "<br>" +
        (span
          ? "Measured extent: " + span[0].toFixed(1) + " to " +
            span[1].toFixed(1) + " " + bodyName + " radii<br>"
          : "") +
        "Drawn " + thickness.toFixed(1) + " radii wide, a width chosen for" +
        " the picture.<br>" +
        "The ring lies in " + bodyName + "'s equatorial plane, the daily" +
        " average of the" + SOFT_BR + "magnetic equator, " +
        (tilt === null
          ? "which is tilted from it and turns with " + bodyName +
            SOFT_BR + "once a day."
          : "which is tilted " + tilt.toFixed(1) + " degrees from it (IGRF-13," +
            " epoch" + SOFT_BR + "2020-2025) and turns with " + bodyName +
            " once a day.");
"""),
(b"""      if (notes[i]) linkCfg.note = notes[i];
      traces.push(beltMarker);
""",
b"""      if (notes[i]) linkCfg.note = notes[i];
      if (typeof abouts[i] === "string" && abouts[i]) linkCfg.about = abouts[i];
      traces.push(beltMarker);
"""),

# atmosphere shell (radius_fraction)
(b"""      var hover = label + "<br><br>" +
        "Radius: " + cfg.radius_fraction.toFixed(2) + " " + bodyName +
""",
b"""      var hover = label + "<br><br>" + descLine(cfg) +
        "Radius: " + cfg.radius_fraction.toFixed(2) + " " + bodyName +
"""),

# streamer band
(b"""    var hover = label + "<br><br>" +
      "Cusp: " + cuspR + " solar radii<br>= " +
""",
b"""    var hover = label + "<br><br>" + descLine(cfg) +
      "Cusp: " + cuspR + " solar radii<br>= " +
"""),

# oort shapes
(b"""    var pts, marker, label = bodyName + ": " + (cfg.name || shape);
    var hover = label + "<br><br>";
""",
b"""    var pts, marker, label = bodyName + ": " + (cfg.name || shape);
    var hover = label + "<br><br>" + descLine(cfg);
"""),

# equatorial ring (GEO)
(b"""    var hover = label + "<br><br>";
    if (cfg.radius.unit === "R_earth") {
      hover += "Radius: " + cfg.radius.value.toFixed(4) + " Earth radii<br>";
""",
b"""    var hover = label + "<br><br>" + descLine(cfg);
    if (cfg.radius.unit === "R_earth") {
      hover += "Radius: " + cfg.radius.value.toFixed(4) + " Earth radii<br>";
"""),

# shell set
(b"""      var hover = label + "<br><br>";
      if (cfg.radius.unit === "R_sun") {
""",
b"""      var hover = label + "<br><br>" + descLine(cfg);
      if (cfg.radius.unit === "R_sun") {
"""),

# magnetopause and bow shock
(b"""      var mpHover = mpLabel + "<br><br>" +
        "Sunward standoff: " + r0.toFixed(2) + " Earth radii<br>" +
        "= " + kmAndAu(r0 * radiusKm) + "<br>" +
        "Shue et al. (1998), at the scene's declared solar wind:<br>" +
        "Bz " + bz.toFixed(1) + " nT, dynamic pressure " + dp.toFixed(1) +
        " nPa<br>" +
        "Flaring exponent works out to " + alpha.toPrecision(2) + "<br>" +
        "Drawn to " + mpCut.toFixed(0) + " deg from the nose, the furthest " +
        "the paper" + SOFT_BR + "plots its own model. A DRAWING LIMIT, not an " +
        "edge: this" + SOFT_BR +
        "surface has no end, it widens without bound down the tail." +
        "<br>Not tilted: the fit is symmetric about the Sun line.";
""",
b"""      // L-331 (2026-09-16): opens with the served description. The flaring
      // exponent left the hover -- it is model arithmetic, and the panel's
      // `detail` carries the equations -- and "A DRAWING LIMIT" became a
      // sentence (Tony: no compressed language in the hover). With the
      // description on top this hover had reached 18 lines; it is 16.
      var mpHover = mpLabel + "<br><br>" + descLine(mp) +
        "Sunward standoff: " + r0.toFixed(2) + " Earth radii<br>" +
        "= " + kmAndAu(r0 * radiusKm) + "<br>" +
        "Shue et al. (1998), for the solar wind assumed here:<br>" +
        "Bz " + bz.toFixed(1) + " nT, dynamic pressure " + dp.toFixed(1) +
        " nPa<br>" +
        "Drawn to " + mpCut.toFixed(0) + " deg from the nose, as far as the" +
        " paper" + SOFT_BR + "plots its model. That is where the drawing stops," +
        " not where" + SOFT_BR +
        "the surface ends: it widens down the tail without limit.<br>" +
        "Not tilted: the model is symmetric about the Sun line.";
"""),
(b"""                { info_url: mp.info_url, source: mp.source,
                  detail: mpS._model, note: mp.note });
""",
b"""                { info_url: mp.info_url, source: mp.source, about: mp.about,
                  detail: mpS._model, note: mp.note });
"""),
(b"""      var bsHover = bsLabel + "<br><br>" +
        "Sunward standoff: " + S.toFixed(2) + " Earth radii<br>" +
""",
b"""      var bsHover = bsLabel + "<br><br>" + descLine(bs) +
        "Sunward standoff: " + S.toFixed(2) + " Earth radii<br>" +
"""),
(b"""        "<br>A DRAWING LIMIT, not an edge.<br>" +
""",
b"""        "<br>That is where the drawing stops, not where the shock ends.<br>" +
"""),
(b"""                { info_url: bs.info_url, source: bs.source,
                  detail: bsS._model, note: bs.note });
""",
b"""                { info_url: bs.info_url, source: bs.source, about: bs.about,
                  detail: bsS._model, note: bs.note });
"""),
]

EDITS['documentation/smoke_earth_geometry.js'] = [
# L-331: the pins keep their CONTENT and follow the plain wording.
(b"""  check(label + ": the hover says the cut is a drawing limit, not an edge",
        /DRAWING LIMIT, not an edge/.test(mk.text[0]));
""",
b"""  // L-331 (2026-09-16): same pin, plain words -- "A DRAWING LIMIT, not an
  // edge" is now a sentence a visitor can read.
  check(label + ": the hover says the cut is where the drawing stops, not an edge",
        /where the drawing stops, not where(<br[^>]*>| )the/.test(mk.text[0]));
"""),
(b"""  check(label + ": the hover names the drawn width as a drawing choice",
        /drawing choice and not the belt's width/.test(mk.text[0]));
  check(label + ": the hover gives the sourced span from the served edges",
        /Sourced span: \\d/.test(mk.text[0]), mk.text[0].indexOf("Sourced span") >= 0);
""",
b"""  // L-331 (2026-09-16): the same two pins, on the plain wording that
  // replaced "drawing choice" and "Sourced span". The description itself
  // is measured by smoke_hover_budget.js, which overlays the store; this
  // suite renders a fixture that predates the field.
  check(label + ": the hover says the drawn width is chosen for the picture",
        /a width chosen for the picture/.test(mk.text[0]));
  check(label + ": the hover gives the measured extent from the served edges",
        /Measured extent: \\d/.test(mk.text[0]), mk.text[0].indexOf("Measured extent") >= 0);
"""),
]

EDITS['interactive.html'] = [
(b"""     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-331: both rooms' info text stops saying a shell's source is in
        its hover -- it has been in this panel since 2026-09-15 -- and
        Earth's stops saying the magnetosphere is not drawn; the drawer
        sentences say what a tap does since L-318 round 3)
""",
b"""     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-331: both rooms' info text stops saying a shell's source is in
        its hover -- it has been in this panel since 2026-09-15 -- and
        Earth's stops saying the magnetosphere is not drawn; the drawer
        sentences say what a tap does since L-318 round 3)
     Updated: September 16, 2026 with Anthropic's Claude Opus 5
       (L-331, Tony's Mode 5: the i panel opens with the shell's served
        `about` paragraph -- what it is -- above its link; the drawer
        reads it off the trace meta like source, detail and note)
"""),
(b"""                source: (t.meta && typeof t.meta.source === "string") ? t.meta.source : null,
                detail: (t.meta && typeof t.meta.detail === "string") ? t.meta.detail : null,
                note: (t.meta && typeof t.meta.note === "string") ? t.meta.note : null,
                indices: [],
""",
b"""                about: (t.meta && typeof t.meta.about === "string") ? t.meta.about : null,
                source: (t.meta && typeof t.meta.source === "string") ? t.meta.source : null,
                detail: (t.meta && typeof t.meta.detail === "string") ? t.meta.detail : null,
                note: (t.meta && typeof t.meta.note === "string") ? t.meta.note : null,
                indices: [],
"""),
(b"""            if (t.meta && typeof t.meta.source === "string") { byName[g].source = t.meta.source; }
            if (t.meta && typeof t.meta.detail === "string") { byName[g].detail = t.meta.detail; }
""",
b"""            if (t.meta && typeof t.meta.about === "string") { byName[g].about = t.meta.about; }
            if (t.meta && typeof t.meta.source === "string") { byName[g].source = t.meta.source; }
            if (t.meta && typeof t.meta.detail === "string") { byName[g].detail = t.meta.detail; }
"""),
(b"""    head.appendChild(document.createTextNode(grp.name));
    box.appendChild(head);

    if (!grp.link) {
""",
b"""    head.appendChild(document.createTextNode(grp.name));
    box.appendChild(head);

    // L-331 (2026-09-16): what it is comes first, before where the number
    // came from. The served `about` paragraph, condensed from the orrery's
    // own info text; the hover carries its one-sentence `description`.
    if (grp.about) {
        const abt = document.createElement("div");
        abt.className = "info-focus-empty";
        abt.textContent = grp.about;
        box.appendChild(abt);
    }

    if (!grp.link) {
"""),
]

EDITS['documentation/smoke_hover_budget.js'] = [
(b"""// 1. The Earth room, composed the way the page composes it -- this is the
//    only path with a Sun direction, so it is the only one where the
//    magnetopause and bow shock hovers exist at all.
if (EG) {
    const p = fixture("payload_earth_scene.json");
""",
b"""// L-331 (2026-09-16). The two Earth fixtures were captured before the
// store carried `description` and `about`, so on their own they would
// measure hovers the page no longer shows -- shorter ones. Overlay those
// two fields (and the belts' two lists) from the served store onto the
// fixture features by object, feature and shell key, and nothing else:
// the numbers stay the fixture's. A fixture recaptured later carries the
// fields itself and the overlay changes nothing.
const storeObjects = JSON.parse(fs.readFileSync(
    path.join(__dirname, "..", "data", "objects_config.json"), "utf8")).objects;
const PROSE = ["description", "about", "descriptions", "abouts"];
function overlayProse(features) {
    for (const f of features) {
        const obj = storeObjects.find(o => o.slug === f.object);
        const src = obj && obj.features ? obj.features[f.feature] : null;
        if (!src || !f.params) { continue; }
        for (const k of PROSE) { if (k in src) { f.params[k] = src[k]; } }
        for (const key of Object.keys(src)) {
            const sub = src[key];
            if (sub && typeof sub === "object" && !Array.isArray(sub) &&
                f.params[key] && typeof f.params[key] === "object") {
                for (const k of PROSE) { if (k in sub) { f.params[key][k] = sub[k]; } }
            }
        }
    }
    return features;
}

// 1. The Earth room, composed the way the page composes it -- this is the
//    only path with a Sun direction, so it is the only one where the
//    magnetopause and bow shock hovers exist at all.
if (EG) {
    const p = fixture("payload_earth_scene.json");
    overlayProse(p.features);
"""),
(b"""collect("earth features", GF.buildFeatureTraces(
    fixture("payload_earth.json").features,
    fixture("payload_earth.json").bodies).traces);
""",
b"""const pe = fixture("payload_earth.json");
collect("earth features", GF.buildFeatureTraces(
    overlayProse(pe.features), pe.bodies).traces);
"""),
(b"""// 3. The Sun room, from the served store (L-331). The scene half-range is
//    Artifact 1's 1.1 AU, as smoke_sun_shells.js uses; the Oort shapes
//    then arrive visible:"legendonly", which changes nothing about their
//    hover text.
const cfgSun = JSON.parse(fs.readFileSync(
    path.join(__dirname, "..", "data", "objects_config.json"), "utf8"));
const sunObj = cfgSun.objects.find(o => o.slug === "sun");
""",
b"""// 3. The Sun room, from the served store (L-331). The scene half-range is
//    Artifact 1's 1.1 AU, as smoke_sun_shells.js uses; the Oort shapes
//    then arrive visible:"legendonly", which changes nothing about their
//    hover text.
const sunObj = storeObjects.find(o => o.slug === "sun");
"""),
]


def main():
    originals, results = {}, {}
    for rel, fp_expected in FILES.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            print(f'ERROR: {rel} not found next to this script. NOTHING was written.')
            return 1
        raw = open(path, 'rb').read()
        was_crlf = b'\r\n' in raw
        content = raw.replace(b'\r\n', b'\n')
        actual = hashlib.md5(content).hexdigest()
        if actual != fp_expected:
            print(f'ERROR: {rel} is not the file this patch was built against')
            print(f'       expected {fp_expected}, found {actual}{" [CRLF]" if was_crlf else ""}')
            print('       NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
            return 1
        originals[rel] = (content, was_crlf)

    try:
        results['data/objects_config.json'] = edit_config(
            originals['data/objects_config.json'][0].decode('ascii')).encode('ascii')
    except (ValueError, UnicodeError) as e:
        print('ANCHOR FAIL: data/objects_config.json: ' + str(e))
        print('NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
        return 1

    for rel, edits in EDITS.items():
        content, _ = originals[rel]
        for old, new in edits:
            n = content.count(old)
            if n != 1:
                print(f'ANCHOR FAIL: {rel}: expected 1 match, found {n}: {old[:70]!r}')
                print('NOTHING was written. Undo is Discard Changes in GitHub Desktop.')
                return 1
            content = content.replace(old, new)
        results[rel] = content

    for rel, content in results.items():
        if any(c > 127 for c in content):
            print(f'ERROR: {rel} would hold non-ASCII bytes after the patch. NOTHING was written.')
            return 1
        if content == originals[rel][0]:
            print(f'ERROR: {rel} unchanged. NOTHING was written.')
            return 1

    for rel, content in results.items():
        _, was_crlf = originals[rel]
        out = content.replace(b'\n', b'\r\n') if was_crlf else content
        with open(os.path.join(ROOT, rel), 'wb') as f:
            f.write(out)
        print(f'ok  {rel}  ({len(out)} bytes{", CRLF preserved" if was_crlf else ""})')
    print(f'served prose added: {len(WORDING)} features + {len(BELT_WORDING)} belts, '
          'each with a description (hover) and an about (panel)')
    print('stamped: gallery/feature_renderers.js, interactive.html')
    print('patch applied. NEXT: the nightly; gallery_maintenance_run.py; push; --live; Mode 5.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
