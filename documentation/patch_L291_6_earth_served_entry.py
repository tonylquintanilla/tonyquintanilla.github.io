"""
patch_L291_6_earth_served_entry.py -- Earth's served entry, measured shape (L-291 step 2, gallery half)

Built on gallery e6c39a00dc4e0f9cdba0f5153e86b835b8f40b78
at https://github.com/tonylquintanilla/tonyquintanilla.github.io (main)
against orrery 5aed0590592802abaa73a7f06b16cbca5c649a88
at https://github.com/tonylquintanilla/palomas_orrery (main),
whose constants_new.py Earth exhibit block every value below is copied from.

WHAT THIS DOES -- seven files, one commit, applied only if all seven guards pass.

1. data/objects_config.json -- Earth's entry rewritten in the measured shape
   the interactive-exhibit skill requires: every rendered number is
   {value, unit, source, orrery_constant}; colours, opacities, point counts
   and drawing parameters sit in the DECLARED zone. Groups:
     earth_interior       inner core, outer core, lower mantle, upper mantle,
                          crust (PREM / Ishii 2019 / IERS 2010) -- km
     earth_atmosphere     stratopause, thermopause (NOAA JetStream, NASA) --
                          Earth radii
     earth_exosphere      geocorona, at least 100 R_E (Baliukin et al. 2019).
                          The exosphere has no boundary; this is its
                          detected extent, and the row says so (L-292).
     earth_orbital_zones  LEO inner and outer edges (IADC-02-01 Rev. 3)
     earth_geostationary  the GEO ring (derived from GM and rotation rate)
                          -- shape "equatorial_ring", NO RENDERER YET
     earth_magnetosphere  magnetopause standoff (Shue 1998; Lugaz 2016),
                          bow shock standoff (Lugaz 2016, 11-14 midpoint),
                          magnetotail (declared) -- NO RENDERER YET
     van_allen_belts      inner and outer flux peaks (Baker 2018; JGR 2025)
     hill_sphere          234.6 R_E, derived from the two GMs
     orientation          pole RA/Dec from idealized_orbits.py::planet_poles
   The orrery's single magnetosphere call becomes four served rows:
   magnetopause, bow shock, inner belt, outer belt.

2. gallery/feature_renderers.js -- the shell-set renderer learns two units
   and one more body radius so the Earth groups draw TODAY in the Explorer
   room, with their sources in the hover:
     - measuredRadiusAu accepts "km" and "R_earth" (beside "au", "R_sun")
     - a group's body radius may be served as planet_radius, not only
       sun_radius
     - the hover names the unit it was served in (solar radii / Earth radii
       / km) before the km-and-AU line
     - the four Earth shell groups and hill_sphere dispatch to it
     - renderBelts accepts measured distances {value, unit "R_earth", source,
       orrery_constant} as well as the bare numbers Jupiter still uses, and
       appends each belt's source to its hover
   The old atmosphere_shell renderer is left in place, unused by Earth.
   earth_geostationary and earth_magnetosphere have no renderer: the
   dispatch reports "no renderer for this feature key" for each, by name,
   as it should. Their renderers are step 3.

3. gallery_maintenance_run.py -- the store-drift checker learns Earth radii.
   Its unit table read every *_RADII constant as solar radii, which was true
   while the Sun was the only exhibit. Now: an EARTH_-prefixed *_RADII name
   is in Earth radii, and the factor comes FROM THE STORE
   (EARTH_EQUATORIAL_RADIUS_KM / KM_PER_AU), never typed here.

4. documentation/payload_earth.json -- the smoke fixture's Earth feature
   list is regenerated from the new entry, so the smoke test checks the
   shape that is served rather than the shape that used to be.

5. documentation/smoke_features.js -- Earth pins updated: 12 geometry
   traces drawn (5 interior + 2 atmosphere + 1 geocorona + 2 LEO + 2 belts
   + 1 Hill = 13, of which the Hill sphere is drawn; it exceeds no frame in
   a scene with no halfRange), exactly two warnings and both named, the
   lower atmosphere at the STRATOPAUSE radius read from the fixture itself.

6. tools/gallery_cache_builder.py -- the feature-shape validator's belt rule
   compared bare numbers and threw on measured entries; it now reads the
   number from either shape (found by the Cache builder suite in the
   sandbox, which is what the suite is for).

7. tools/test_gallery_cache_builder_offline.py -- the M1 pins on Earth's
   old shape (atmosphere_shell, bare inner_belt_distance == 1.5) become
   pins on the served shape: the nine groups by name, the measured belt
   entry, and the absence of the old group.

WHAT IT DOES NOT DO
   Draw the GEO ring or the magnetosphere (step 3 renderers). Build the
   Earth exhibit branch in interactive.html (step 3). Touch the Sun.

HOW TO RUN
   Save to the GALLERY repo root. Open in VS Code and press Run. Then
   run gallery_maintenance_run.py (offline) -- Feature renderers must read
   ALL CHECKS PASSED with the new pins -- then commit, push, and run
   gallery_maintenance_run.py --live: Store drift must list every Earth
   pointer as MATCH, by name. Then open the Explorer room and look at
   Earth: the old two shells and two belts become interior stack,
   atmosphere, geocorona, LEO edges, belts, Hill sphere, each hover ending
   in its source.

GUARDS
   Seven md5s at e6c39a00. Every text edit must match exactly once. ASCII, LF.

Written September 2026 with Anthropic's Claude Fable 5.1.
"""
import hashlib
import json
import sys
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILES = {
    "data/objects_config.json": "a6f19904581b2768337ce4645682334f",
    "gallery/feature_renderers.js": "5b75e6ca4e310469d99e2f0e7a5495cf",
    "gallery_maintenance_run.py": "62ef8ee319937e30d5571f44cfd82ca9",
    "documentation/smoke_features.js": "aef376168de4a1e0d964aebc3d40587b",
    "documentation/payload_earth.json": "43a9c0f2b5bf4225f785e0cc0bc424fa",
    "tools/gallery_cache_builder.py": "e280cedc5094fefcc184eea4152b6b60",
    "tools/test_gallery_cache_builder_offline.py": "f19232594f5bcd576e370a43ea0fba49",
}

# ---------------------------------------------------------------------------
# 1. The Earth entry. Every value is the store's exact float (repr) at
#    orrery 5aed0590; the live drift check compares them exactly.
# ---------------------------------------------------------------------------

IERS = ("IERS Conventions (2010), Petit & Luzum (eds.), IERS Technical Note "
        "No. 36, Table 1.1")
PREM = ("Dziewonski & Anderson (1981), Preliminary Reference Earth Model, "
        "Phys. Earth Planet. Inter. 25:297")
D660 = ("Ishii, Kumagai, Sugiura & Tsuchiya (2019), Nature Geoscience 12:869 "
        "-- the 660-km discontinuity")
NOAA = ("NOAA JetStream, \"Layers of the Atmosphere\"; NASA, \"Earth's "
        "Atmospheric Layers\"")
IADC = ("IADC Space Debris Mitigation Guidelines, IADC-02-01 Rev. 3 (June "
        "2021), sec. 3.3.2 -- the LEO Protected Region extends to 2,000 km "
        "altitude")
BAKER = ("Baker et al. (2018), Space Sci. Rev. 214:17, "
         "doi:10.1007/s11214-017-0452-7 -- inner-zone proton fluxes peak near "
         "r ~ 1.5 R_E")
CIRBE = ("J. Geophys. Res. Space Physics (2025), doi:10.1029/2024JA033504 -- "
         "the outer belt is most intense around L = 4 and 5; Kellerman et al. "
         "(2014) as cited in arXiv:1809.00902 -- maximum electron flux at "
         "L = 4-5. Drawn at the midpoint.")
SHUE = ("Shue et al. (1998), J. Geophys. Res. 103:17691, doi:10.1029/98JA01103 "
        "-- r0 = 10.2 R_E at Bz = 0 nT, Dp = 2 nPa; Lugaz et al. (2016), "
        "doi:10.1038/ncomms13001 -- typical subsolar magnetopause 9-11 R_E")
LUGAZ = ("Lugaz et al. (2016), Nat. Commun. 7:13001, doi:10.1038/ncomms13001 "
         "-- under normal solar wind the bow shock forms at 11-14 R_E "
         "subsolar. Drawn at the midpoint of that range.")
BALIUKIN = ("Baliukin, Bertaux, Quemerais, Izmodenov & Schmidt (2019), "
            "J. Geophys. Res. Space Physics 124:861, doi:10.1029/2018JA026136 "
            "-- the hydrogen geocorona is detected to at least 100 Earth radii")
HILL_SRC = ("Derived: r_H = a (GM_E / 3 GM_Sun)^(1/3) with a = 1 AU; GM_E from "
            "IERS Conventions (2010) TN36 Table 1.1, GM_Sun from IAU 2015 "
            "Resolution B3")
GEO_SRC = ("Derived: (GM_E / omega^2)^(1/3) from IERS Conventions (2010) TN36 "
           "Table 1.1 -- GM_E = 3.986004418e14 m^3 s^-2, nominal mean angular "
           "velocity 7.292115e-5 rad s^-1")

PLANET_RADIUS = OrderedDict([
    ("value", 6378.1366), ("unit", "km"), ("source", IERS),
    ("orrery_constant", "constants_new.py::EARTH_EQUATORIAL_RADIUS_KM"),
])


def shell(name, value, unit, source, const, color, opacity, url, n_points=20,
          marker_size=3.0, note=None):
    d = OrderedDict()
    d["name"] = name
    d["radius"] = OrderedDict([("value", value), ("unit", unit)])
    d["info_url"] = url
    d["color"] = color
    d["opacity"] = opacity
    d["n_points"] = n_points
    d["marker_size"] = marker_size
    d["source"] = source
    d["orrery_constant"] = "constants_new.py::" + const
    if note:
        d["note"] = note
    return d


def measured(value, unit, source, const, note=None):
    d = OrderedDict([("value", value), ("unit", unit), ("source", source),
                     ("orrery_constant", "constants_new.py::" + const)])
    if note:
        d["note"] = note
    return d


W = "https://en.wikipedia.org/wiki/"

FEATURES = OrderedDict()

FEATURES["earth_interior"] = OrderedDict([
    ("inner_core", shell("Inner Core", 1221.5, "km", PREM, "EARTH_INNER_CORE_KM",
                         "rgb(255, 180, 140)", 1.0, W + "Earth%27s_inner_core", 25, 10)),
    ("outer_core", shell("Outer Core", 3480.0, "km", PREM, "EARTH_OUTER_CORE_KM",
                         "rgb(255, 140, 0)", 1.0, W + "Earth%27s_outer_core", 25, 7)),
    ("lower_mantle", shell("Lower Mantle", 5711.0, "km", D660, "EARTH_LOWER_MANTLE_KM",
                           "rgb(230, 100, 20)", 1.0, W + "Lower_mantle", 25, 7)),
    ("upper_mantle", shell("Upper Mantle", 6346.6, "km", PREM + " -- Moho",
                           "EARTH_UPPER_MANTLE_KM", "rgb(205, 85, 85)", 1.0,
                           W + "Upper_mantle", 25, 7)),
    ("crust", shell("Crust", 1.0, "R_earth", IERS + " -- equatorial radius",
                    "EARTH_EQUATORIAL_RADIUS_KM", "rgb(70, 120, 160)", 1.0,
                    W + "Earth%27s_crust", 40, 3.0,
                    note="Drawn at the equatorial radius. Crust thickness (5-10 km oceanic, 30-50 km continental) is below the drawn resolution.")),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["earth_atmosphere"] = OrderedDict([
    ("lower_atmosphere", shell("Lower Atmosphere (to the stratopause)",
                               1.0078392802060714, "R_earth", NOAA + " -- stratopause at about 50 km",
                               "EARTH_STRATOPAUSE_RADII", "rgb(150, 200, 255)", 0.5,
                               "https://science.nasa.gov/earth/earth-atmosphere/earths-atmosphere-a-multi-layered-cake/",
                               note="Troposphere and stratosphere, 99% of atmospheric mass. Drawn at the physical boundary since 2026-09-07 (L-295); before that at a visibility fraction its own hover contradicted.")),
    ("upper_atmosphere", shell("Upper Atmosphere (to the thermopause)",
                               1.0940713624728577, "R_earth", NOAA + " -- thermosphere to about 600 km",
                               "EARTH_THERMOPAUSE_RADII", "rgb(100, 150, 255)", 0.3,
                               "https://www.nasa.gov/image-article/earths-upper-atmosphere/",
                               note="Mesosphere and thermosphere. The thermopause moves with solar activity over roughly 500-1,000 km; 600 km is the nominal figure.")),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["earth_exosphere"] = OrderedDict([
    ("geocorona", shell("Exosphere / Geocorona (hydrogen halo, detected extent)",
                        100.0, "R_earth", BALIUKIN, "EARTH_GEOCORONA_RADII",
                        "rgb(200, 200, 255)", 0.15, W + "Geocorona", 20, 3.0,
                        note="The exosphere has no boundary: it thins into space. This shell is the sourced DETECTION FLOOR, not an edge, and it encloses the Moon's orbit at about 60 Earth radii. The orrery folds the exosphere into its upper-atmosphere hover; growing it a shell of its own is L-292.")),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["earth_orbital_zones"] = OrderedDict([
    ("leo_inner", shell("Low Earth Orbit, inner edge (200 km)",
                        1.031357120824286, "R_earth",
                        "Drawing floor: the LEO region begins at the surface (IADC-02-01 Rev. 3); 200 km marks where orbits stop decaying within days. Declared, not measured.",
                        "EARTH_LEO_INNER_RADII", "rgb(255, 248, 220)", 0.25,
                        W + "Low_Earth_orbit", 30, 2.5)),
    ("leo_outer", shell("Low Earth Orbit, outer edge (2,000 km)",
                        1.313571208242859, "R_earth", IADC, "EARTH_LEO_OUTER_RADII",
                        "rgb(255, 248, 220)", 0.25, W + "Low_Earth_orbit", 30, 2.5)),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["earth_geostationary"] = OrderedDict([
    ("geostationary_ring", OrderedDict([
        ("name", "Geostationary Belt (GEO)"),
        ("shape", "equatorial_ring"),
        ("radius", OrderedDict([("value", 6.610735325291913), ("unit", "R_earth")])),
        ("info_url", W + "Geostationary_orbit"),
        ("color", "rgb(220, 220, 255)"),
        ("opacity", 0.6),
        ("n_points", 120),
        ("marker_size", 2.0),
        ("source", GEO_SRC),
        ("orrery_constant", "constants_new.py::EARTH_GEOSTATIONARY_RADII"),
        ("note", "A ring in the equatorial plane, not a sphere: needs the orientation block and its own renderer (step 3). 42,164 km from Earth's centre, 35,786 km up."),
    ])),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["earth_magnetosphere"] = OrderedDict([
    ("_comment", "The orrery emits magnetopause, bow shock, inner belt and outer belt from ONE call. Served as four rows: the two standoffs here, the two belts in van_allen_belts. Renderer for the standoff shapes is step 3."),
    ("magnetopause", OrderedDict([
        ("name", "Magnetopause (sunward standoff)"),
        ("shape", "magnetopause"),
        ("standoff", OrderedDict([("value", 10.0), ("unit", "R_earth")])),
        ("info_url", W + "Magnetopause"),
        ("color", "rgb(180, 180, 255)"),
        ("opacity", 0.25),
        ("source", SHUE),
        ("orrery_constant", "constants_new.py::EARTH_MAGNETOPAUSE_STANDOFF_RADII"),
        ("note", "Quiet-time nominal. Under storm compression it can fall inside geostationary orbit (6.6 R_E)."),
    ])),
    ("bow_shock", OrderedDict([
        ("name", "Bow Shock (sunward standoff)"),
        ("shape", "bow_shock"),
        ("standoff", OrderedDict([("value", 12.5), ("unit", "R_earth")])),
        ("info_url", W + "Bow_shocks_in_astrophysics"),
        ("color", "rgb(255, 200, 150)"),
        ("opacity", 0.25),
        ("source", LUGAZ),
        ("orrery_constant", "constants_new.py::EARTH_BOW_SHOCK_STANDOFF_RADII"),
        ("note", "Model form: Farris & Russell (1994), J. Geophys. Res. 99:17681. The orrery drew 15 R_E (textbook) until 2026-09-07; store and shells now agree."),
    ])),
    ("magnetotail", OrderedDict([
        ("_declared", "Drawing parameters, not measurements: the orrery's tail is drawn to 100 Earth radii with a 15-radius base and 25-radius end; the real tail extends past 1,000 radii and the hover must say so (Show the Envelope)."),
        ("length_radii", 100.0),
        ("base_radii", 15.0),
        ("end_radii", 25.0),
        ("color", "rgb(180, 180, 255)"),
        ("opacity", 0.15),
    ])),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["van_allen_belts"] = OrderedDict([
    ("inner_belt_distance", measured(1.5, "R_earth", BAKER, "EARTH_VAN_ALLEN_INNER_RADII",
                                     note="A flux PEAK, not an edge; the inner belt spans roughly L = 1.1 to 2.")),
    ("outer_belt_distance", measured(4.5, "R_earth", CIRBE, "EARTH_VAN_ALLEN_OUTER_RADII",
                                     note="A flux PEAK, not an edge; the outer belt spans roughly L = 3 to 7 and moves with geomagnetic activity.")),
    ("belt_thickness", 0.5),
    ("n_rings", 5),
    ("n_points", 80),
    ("colors", ["rgb(255, 100, 100)", "rgb(100, 200, 255)"]),
    ("names", ["Inner Radiation Belt", "Outer Radiation Belt"]),
    ("info_urls", ["https://science.nasa.gov/biological-physical/stories/van-allen-belts/",
                   "https://science.nasa.gov/biological-physical/stories/van-allen-belts/"]),
    ("_declared", "belt_thickness, n_rings, n_points, colours and names are drawing choices."),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["hill_sphere"] = OrderedDict([
    ("hill_sphere", shell("Hill Sphere (gravitational dominance over the Sun)",
                          234.6388338020614, "R_earth", HILL_SRC, "EARTH_HILL_SPHERE_RADII",
                          "rgb(0, 255, 0)", 0.2, W + "Hill_sphere", 20, 3.0,
                          note="About 1.50 million km. The Moon at about 60 Earth radii sits well inside it, which is why it stays bound. a = 1 AU exactly; Earth's semi-major axis is 1.00000011 AU (NASA Earth Fact Sheet).")),
    ("planet_radius", PLANET_RADIUS),
])

FEATURES["orientation"] = OrderedDict([
    ("pole", OrderedDict([
        ("ra", OrderedDict([("value", 0.0), ("unit", "deg")])),
        ("dec", OrderedDict([("value", 90.0), ("unit", "deg")])),
    ])),
    ("source", "IAU 2018 (Archinal et al.) -- Earth's north pole is the J2000 celestial north pole in ICRF equatorial coordinates"),
    ("orrery_constant", "idealized_orbits.py::planet_poles['Earth']"),
    ("note", "Same shape as the Sun's orientation block; read by poleBasis(). The equator plane and the GEO ring both hang off this."),
])

EARTH_ENTRY = OrderedDict([
    ("slug", "earth"), ("name", "Earth"), ("horizons_id", "399"), ("id_type", "majorbody"),
    ("category", "planet"), ("availability", "analytic"), ("parent", "sun"),
    ("canonical_center", "@sun"), ("center_slug", "sun"), ("canonical_frame", "heliocentric"),
    ("trajectory_of", None), ("trace_policy", "none"),
    ("_comment", "L-291 (2026-09-07): entry rebuilt in the measured shape. Every rendered number carries value/unit/source/orrery_constant and is the orrery store's exact value at 5aed0590; the live store-drift run checks each by name. Groups earth_geostationary and earth_magnetosphere have no renderer yet (step 3) and the dispatch says so. Earth-Moon Lagrange points are L-297 and are not here."),
    ("features", FEATURES),
])

# ---------------------------------------------------------------------------
# 2-5. Text edits.
# ---------------------------------------------------------------------------

JS_EDITS = [
    (
        "  var SHELL_SET_KEYS = [\"sun_structures\", \"solar_atmosphere\",\n"
        "                        \"solar_wind\", \"oort_cloud\", \"hill_sphere\"];\n",
        "  var SHELL_SET_KEYS = [\"sun_structures\", \"solar_atmosphere\",\n"
        "                        \"solar_wind\", \"oort_cloud\", \"hill_sphere\",\n"
        "                        // L-291: Earth's groups are the same shape.\n"
        "                        \"earth_interior\", \"earth_atmosphere\",\n"
        "                        \"earth_exosphere\", \"earth_orbital_zones\"];\n",
    ),
    (
        "    if (node.unit === \"au\") {\n"
        "      return node.value;\n"
        "    }\n"
        "    if (node.unit === \"R_sun\") {\n"
        "      if (typeof starRadiusKm !== \"number\") {\n"
        "        warn(where + \": radius is in R_sun but no star radius was served \" +\n"
        "             \"for this group -- nothing drawn\");\n"
        "        return null;\n"
        "      }\n"
        "      return node.value * starRadiusKm / KM_PER_AU;\n"
        "    }\n"
        "    warn(where + \": unit is \" + JSON.stringify(node.unit) +\n"
        "         \", expected \\\"R_sun\\\" or \\\"au\\\" -- refusing to guess a conversion\");\n"
        "    return null;\n",
        "    if (node.unit === \"au\") {\n"
        "      return node.value;\n"
        "    }\n"
        "    if (node.unit === \"km\") {\n"
        "      return node.value / KM_PER_AU;  // L-291: Earth's interior is served in km\n"
        "    }\n"
        "    // L-291: \"R_sun\" and \"R_earth\" both mean \"radii of the group's body\";\n"
        "    // the body radius is served in the group as sun_radius or planet_radius.\n"
        "    if (node.unit === \"R_sun\" || node.unit === \"R_earth\") {\n"
        "      if (typeof starRadiusKm !== \"number\") {\n"
        "        warn(where + \": radius is in \" + node.unit + \" but no body radius \" +\n"
        "             \"(sun_radius / planet_radius) was served for this group -- nothing drawn\");\n"
        "        return null;\n"
        "      }\n"
        "      return node.value * starRadiusKm / KM_PER_AU;\n"
        "    }\n"
        "    warn(where + \": unit is \" + JSON.stringify(node.unit) +\n"
        "         \", expected \\\"R_sun\\\", \\\"R_earth\\\", \\\"km\\\" or \\\"au\\\" -- refusing to guess a conversion\");\n"
        "    return null;\n",
    ),
    (
        "    var starRadiusKm = null;\n"
        "    if (params.sun_radius !== undefined) {\n"
        "      starRadiusKm = measured(params.sun_radius, \"km\",\n"
        "                              where + \"/sun_radius\", warn);\n"
        "    }\n",
        "    // The group's body radius, in km: the Sun serves sun_radius, a planet\n"
        "    // serves planet_radius (L-291). Radii in R_sun / R_earth scale by it.\n"
        "    var starRadiusKm = null;\n"
        "    if (params.sun_radius !== undefined) {\n"
        "      starRadiusKm = measured(params.sun_radius, \"km\",\n"
        "                              where + \"/sun_radius\", warn);\n"
        "    } else if (params.planet_radius !== undefined) {\n"
        "      starRadiusKm = measured(params.planet_radius, \"km\",\n"
        "                              where + \"/planet_radius\", warn);\n"
        "    }\n",
    ),
    (
        "      if (cfg.radius.unit === \"R_sun\") {\n"
        "        hover += \"Radius: \" + cfg.radius.value + \" solar radii<br>\";\n"
        "      }\n",
        "      if (cfg.radius.unit === \"R_sun\") {\n"
        "        hover += \"Radius: \" + cfg.radius.value + \" solar radii<br>\";\n"
        "      } else if (cfg.radius.unit === \"R_earth\") {\n"
        "        // L-291: Earth radii, with the altitude the hover convention asks for.\n"
        "        hover += \"Radius: \" + cfg.radius.value.toFixed(4) + \" Earth radii<br>\";\n"
        "        if (typeof starRadiusKm === \"number\" && cfg.radius.value > 1) {\n"
        "          hover += \"Altitude: \" + kmAndAu((cfg.radius.value - 1) * starRadiusKm) + \"<br>\";\n"
        "        }\n"
        "      }\n",
    ),
    (
        "    var distances, names, colors;\n"
        "    if (Array.isArray(params.belt_distances)) {\n"
        "      distances = params.belt_distances;\n"
        "    } else if (typeof params.inner_belt_distance === \"number\" &&\n"
        "               typeof params.outer_belt_distance === \"number\") {\n"
        "      distances = [params.inner_belt_distance, params.outer_belt_distance];\n"
        "    } else {\n",
        "    var distances, names, colors;\n"
        "    var sources = [];\n"
        "    // L-291: a belt distance may be a measured entry {value, unit\n"
        "    // \"R_earth\", source, orrery_constant} (Earth) or a bare number in\n"
        "    // planet radii (Jupiter, unchanged). Read either; carry the source.\n"
        "    function beltDistance(node, label) {\n"
        "      if (typeof node === \"number\") return node;\n"
        "      if (isDict(node) && typeof node.value === \"number\") {\n"
        "        if (node.unit !== \"R_earth\" && node.unit !== undefined) {\n"
        "          warn(slug + \"/\" + featureKey + \"/\" + label + \": unit is \" +\n"
        "               JSON.stringify(node.unit) + \", expected \\\"R_earth\\\" -- not drawn\");\n"
        "          return null;\n"
        "        }\n"
        "        sources.push(node.source || null);\n"
        "        return node.value;\n"
        "      }\n"
        "      return null;\n"
        "    }\n"
        "    var innerD = beltDistance(params.inner_belt_distance, \"inner_belt_distance\");\n"
        "    var outerD = beltDistance(params.outer_belt_distance, \"outer_belt_distance\");\n"
        "    if (Array.isArray(params.belt_distances)) {\n"
        "      distances = params.belt_distances;\n"
        "    } else if (typeof innerD === \"number\" && typeof outerD === \"number\") {\n"
        "      distances = [innerD, outerD];\n"
        "    } else {\n",
    ),
    (
        "        \"Band thickness: \" + thickness.toFixed(1) + \" radii<br>\" +\n"
        "        \"Trapped-particle region; band is illustrative in shape.\";\n",
        "        \"Band thickness: \" + thickness.toFixed(1) + \" radii<br>\" +\n"
        "        \"Trapped-particle region; band is illustrative in shape.\";\n"
        "      if (sources[i]) {\n"
        "        hover += \"<br><br>\" + wrapHover(\"Source: \" + sources[i]);\n"
        "      }\n",
    ),
]

RUNNER_EDITS = [
    (
        "UNIT_BY_SUFFIX = ((\"_RADII\", \"r_sun\"), (\"_AU\", \"au\"), (\"_KM\", \"km\"))\n",
        "UNIT_BY_SUFFIX = ((\"_RADII\", \"r_sun\"), (\"_AU\", \"au\"), (\"_KM\", \"km\"))\n"
        "\n"
        "\n"
        "def unit_of_constant(name):\n"
        "    \"\"\"The unit a constant's NAME declares, or None.\n"
        "\n"
        "    L-291 (2026-09-07): *_RADII meant solar radii while the Sun was the\n"
        "    only exhibit. An EARTH_-prefixed *_RADII is in Earth radii. The\n"
        "    factor for r_earth comes from the store (store_conversions), never\n"
        "    from a number typed here.\n"
        "    \"\"\"\n"
        "    if name.startswith(\"EARTH_\") and name.endswith(\"_RADII\"):\n"
        "        return \"r_earth\"\n"
        "    for suffix, unit_name in UNIT_BY_SUFFIX:\n"
        "        if name.endswith(suffix):\n"
        "            return unit_name\n"
        "    return None\n",
    ),
    (
        "    orrery_unit = None\n"
        "    for suffix, unit_name in UNIT_BY_SUFFIX:\n"
        "        if name.endswith(suffix):\n"
        "            orrery_unit = unit_name\n"
        "            break\n"
        "    if orrery_unit is None:\n",
        "    orrery_unit = unit_of_constant(name)\n"
        "    if orrery_unit is None:\n",
    ),
    (
        "    return {\"au\": 1.0, \"km\": 1.0 / km_per_au, \"r_sun\": solar_radius_au}\n",
        "    factors = {\"au\": 1.0, \"km\": 1.0 / km_per_au, \"r_sun\": solar_radius_au}\n"
        "    # L-291: Earth radii, from the store's equatorial radius. Absent from\n"
        "    # the store means the unit is absent here, and an r_earth pointer then\n"
        "    # reports NO UNIT -- the announcement, not a silence.\n"
        "    if \"EARTH_EQUATORIAL_RADIUS_KM\" in constants:\n"
        "        earth_km = constants[\"EARTH_EQUATORIAL_RADIUS_KM\"][0]\n"
        "        if earth_km:\n"
        "            factors[\"r_earth\"] = earth_km / km_per_au\n"
        "    return factors\n",
    ),
]

BUILDER_EDITS = [
    (
        "    if 'inner_belt_distance' in node and 'outer_belt_distance' in node:\n"
        "        inn, out = node['inner_belt_distance'], node['outer_belt_distance']\n"
        "        if not (0 < inn < out):\n",
        "    if 'inner_belt_distance' in node and 'outer_belt_distance' in node:\n"
        "        # L-291 (2026-09-07): a belt distance may be served as a MEASURED\n"
        "        # entry {value, unit, source, orrery_constant} (Earth) as well as a\n"
        "        # bare number (Jupiter). Compare the number either way; a measured\n"
        "        # entry with no numeric value is a config error and aborts here.\n"
        "        inn, out = _shape_number(node['inner_belt_distance']), _shape_number(node['outer_belt_distance'])\n"
        "        if inn is None or out is None:\n"
        "            raise ValidationAbort(\n"
        "                \"feature-shape (%s): belt distance is neither a number nor a \"\n"
        "                \"measured {value, unit} entry (%r, %r)\"\n"
        "                % (slug, node['inner_belt_distance'], node['outer_belt_distance']))\n"
        "        if not (0 < inn < out):\n",
    ),
    (
        "def _validate_feature_shapes(slug, node):\n",
        "def _shape_number(x):\n"
        "    \"\"\"The number a shape rule compares: a bare number, or a measured\n"
        "    entry's value. Anything else is None (L-291).\"\"\"\n"
        "    if isinstance(x, (int, float)) and not isinstance(x, bool):\n"
        "        return x\n"
        "    if isinstance(x, dict) and isinstance(x.get('value'), (int, float)):\n"
        "        return x['value']\n"
        "    return None\n"
        "\n"
        "\n"
        "def _validate_feature_shapes(slug, node):\n",
    ),
]

SUITE_EDITS = [
    (
        "        ef = feats['earth']\n"
        "        check('van_allen_belts' in ef and 'atmosphere_shell' in ef,\n"
        "              \"M1: earth has van_allen_belts + atmosphere_shell\")\n"
        "        check(ef['van_allen_belts']['inner_belt_distance'] == 1.5,\n"
        "              \"M1: earth van_allen_belts.inner_belt_distance == 1.5\")\n"
        "        check('atmosphere' in ef['atmosphere_shell']\n"
        "              and 'upper_atmosphere' in ef['atmosphere_shell'],\n"
        "              \"M1: earth atmosphere_shell has atmosphere + upper_atmosphere\")\n",
        "        ef = feats['earth']\n"
        "        # L-291 (2026-09-07): Earth's entry is in the measured shape. These\n"
        "        # pins describe what is SERVED; the numbers are read against the\n"
        "        # orrery store by the live drift run, not re-typed here.\n"
        "        for grp in ('earth_interior', 'earth_atmosphere', 'earth_exosphere',\n"
        "                    'earth_orbital_zones', 'earth_geostationary',\n"
        "                    'earth_magnetosphere', 'van_allen_belts', 'hill_sphere',\n"
        "                    'orientation'):\n"
        "            check(grp in ef, \"M1: earth serves group '%s'\" % grp)\n"
        "        ibd = ef['van_allen_belts']['inner_belt_distance']\n"
        "        check(isinstance(ibd, dict) and ibd.get('unit') == 'R_earth'\n"
        "              and 'orrery_constant' in ibd and 'source' in ibd,\n"
        "              \"M1: earth inner_belt_distance is a measured entry in R_earth with source and pointer\")\n"
        "        check('lower_atmosphere' in ef['earth_atmosphere']\n"
        "              and 'upper_atmosphere' in ef['earth_atmosphere'],\n"
        "              \"M1: earth earth_atmosphere has lower_atmosphere + upper_atmosphere\")\n"
        "        check('atmosphere_shell' not in ef,\n"
        "              \"M1: the pre-L-291 atmosphere_shell group is gone (no second home)\")\n",
    ),
]

SMOKE_OLD = (
    "check(\"no unread inputs reported for earth\", r1.warnings.length === 0, r1.warnings.join(\" | \"));\n"
    "const geo1 = r1.traces.filter(t => t.showlegend === true);\n"
    "const geoEarth = geo1.filter(t => t.name.indexOf(\"Earth:\") === 0);\n"
    "check(\"2 atmosphere shells + 2 Van Allen belts = 4 Earth geometry traces\",\n"
    "      geoEarth.length === 4, \"got \" + geoEarth.length);\n"
)
SMOKE_NEW = (
    "// L-291: Earth's entry is in the measured shape. Two groups have no renderer\n"
    "// yet (earth_geostationary, earth_magnetosphere) and the dispatch must SAY\n"
    "// so, by name -- those two warnings are expected and nothing else is.\n"
    "const expectedWarn = [\"earth/earth_geostationary\", \"earth/earth_magnetosphere\"];\n"
    "check(\"earth reports exactly the two no-renderer groups, by name\",\n"
    "      r1.warnings.length === 2 &&\n"
    "      expectedWarn.every(k => r1.warnings.some(w => w.indexOf(k) === 0 && /no renderer/.test(w))),\n"
    "      r1.warnings.join(\" | \"));\n"
    "const geo1 = r1.traces.filter(t => t.showlegend === true);\n"
    "const geoEarth = geo1.filter(t => t.name.indexOf(\"Earth:\") === 0);\n"
    "check(\"5 interior + 2 atmosphere + 1 geocorona + 2 LEO + 2 belts + 1 Hill = 13 Earth geometry traces\",\n"
    "      geoEarth.length === 13, \"got \" + geoEarth.length + \": \" + geoEarth.map(t => t.name).join(\", \"));\n"
    "// Info markers carry an empty name, the group label in legendgroup and the\n"
    "// hover in text (an array); read them where they are.\n"
    "const earthSourced = r1.traces.filter(t => t.showlegend !== true &&\n"
    "                                          String(t.legendgroup || \"\").indexOf(\"Earth:\") === 0 &&\n"
    "                                          /Source:/.test(JSON.stringify(t.text || t.hovertext || \"\")));\n"
    "check(\"every Earth info marker carries a Source line (13 of 13)\",\n"
    "      earthSourced.length === 13, \"got \" + earthSourced.length);\n"
)
SMOKE_OLD2 = (
    "const lower = geo1.find(t => t.name === \"Earth: Lower Atmosphere\");\n"
    "const ePos = p1.bodies.earth.position;\n"
    "let sr = 0;\n"
    "for (let i = 0; i < lower.x.length; i++) {\n"
    "  sr = Math.max(sr, Math.hypot(lower.x[i]-ePos[0], lower.y[i]-ePos[1], lower.z[i]-ePos[2]));\n"
    "}\n"
    "check(\"lower atmosphere at 1.05 Earth radii\",\n"
    "      Math.abs(sr * KM / 6378.1366 - 1.05) < 0.001, (sr*KM/6378.1366).toFixed(4));\n"
)
SMOKE_NEW2 = (
    "const lower = geo1.find(t => t.name.indexOf(\"Earth: Lower Atmosphere\") === 0);\n"
    "const ePos = p1.bodies.earth.position;\n"
    "let sr = 0;\n"
    "for (let i = 0; i < lower.x.length; i++) {\n"
    "  sr = Math.max(sr, Math.hypot(lower.x[i]-ePos[0], lower.y[i]-ePos[1], lower.z[i]-ePos[2]));\n"
    "}\n"
    "// The expected radius is read from the fixture, not typed: the fixture is a\n"
    "// copy of the served entry, and the served entry is checked against the\n"
    "// store by the live drift run. Nothing here is a second home for the value.\n"
    "const atmo = p1.features.find(f => f.object === \"earth\" && f.feature === \"earth_atmosphere\").params;\n"
    "const expectLower = atmo.lower_atmosphere.radius.value;\n"
    "const rEarthKm = atmo.planet_radius.value;\n"
    "check(\"lower atmosphere at the served stratopause radius (\" + expectLower.toFixed(4) + \" R_earth)\",\n"
    "      Math.abs(sr * KM / rEarthKm - expectLower) < 0.001, (sr*KM/rEarthKm).toFixed(4));\n"
)


def replace_once(text, old, new, label):
    c = text.count(old)
    if c != 1:
        raise RuntimeError("%s: anchor matched %d time(s), expected 1; begins %r" % (label, c, old[:60]))
    return text.replace(old, new, 1)


def new_earth_text():
    body = json.dumps(EARTH_ENTRY, indent=2, ensure_ascii=True)
    # objects[] items sit at four spaces of indent in the file
    return "\n".join(("    " + ln if ln else ln) for ln in body.splitlines())


def main():
    texts = {}
    for name, md5 in FILES.items():
        lf = (ROOT / name).read_bytes().replace(b"\r\n", b"\n")
        got = hashlib.md5(lf).hexdigest()
        if got != md5:
            print("STOP: %s md5 (LF) is %s, expected %s (at e6c39a00)." % (name, got, md5))
            print("      Either this patch already ran or the file moved. Nothing written.")
            return 1
        texts[name] = lf.decode("utf-8")

    try:
        # 1. objects_config.json: replace the Earth object's text span.
        cfg = texts["data/objects_config.json"]
        key = "\n    {\n      \"slug\": \"earth\", \"name\": \"Earth\""
        if cfg.count(key) != 1:
            raise RuntimeError("Earth object start not unique/found in objects_config.json")
        start = cfg.index(key) + 1              # keep the preceding newline
        end = cfg.index("\n    },\n", start)     # end of the Earth object
        cfg = cfg[:start] + new_earth_text() + "," + cfg[end + len("\n    },"):]
        json.loads(cfg)                           # must still parse
        texts["data/objects_config.json"] = cfg

        # 2. renderers
        js = texts["gallery/feature_renderers.js"]
        for i, (old, new) in enumerate(JS_EDITS, 1):
            js = replace_once(js, old, new, "feature_renderers.js edit %d" % i)
        texts["gallery/feature_renderers.js"] = js

        # 3. runner
        py = texts["gallery_maintenance_run.py"]
        for i, (old, new) in enumerate(RUNNER_EDITS, 1):
            py = replace_once(py, old, new, "gallery_maintenance_run.py edit %d" % i)
        texts["gallery_maintenance_run.py"] = py

        # 3b. builder shape validator
        bd = texts["tools/gallery_cache_builder.py"]
        for i, (old, new) in enumerate(BUILDER_EDITS, 1):
            bd = replace_once(bd, old, new, "gallery_cache_builder.py edit %d" % i)
        texts["tools/gallery_cache_builder.py"] = bd

        # 3c. offline suite pins
        st = texts["tools/test_gallery_cache_builder_offline.py"]
        for i, (old, new) in enumerate(SUITE_EDITS, 1):
            st = replace_once(st, old, new, "test_gallery_cache_builder_offline.py edit %d" % i)
        texts["tools/test_gallery_cache_builder_offline.py"] = st

        # 4. fixture: regenerate Earth's feature list from the new entry
        fixture = json.loads(texts["documentation/payload_earth.json"], object_pairs_hook=OrderedDict)
        kept = [f for f in fixture["features"] if f["object"] != "earth"]
        earth_feats = [OrderedDict([("object", "earth"), ("feature", k), ("params", v)])
                       for k, v in FEATURES.items()]
        fixture["features"] = earth_feats + kept
        # The fixture is serialised at indent=1 with no trailing newline; keep
        # that so the diff is the Earth features and nothing else.
        texts["documentation/payload_earth.json"] = json.dumps(fixture, indent=1, ensure_ascii=True)

        # 5. smoke pins
        sm = texts["documentation/smoke_features.js"]
        sm = replace_once(sm, SMOKE_OLD, SMOKE_NEW, "smoke edit 1")
        sm = replace_once(sm, SMOKE_OLD2, SMOKE_NEW2, "smoke edit 2")
        texts["documentation/smoke_features.js"] = sm
    except RuntimeError as exc:
        print("STOP: %s. Nothing written." % exc)
        return 1

    for name, t in texts.items():
        t.encode("ascii")
        (ROOT / name).write_bytes(t.encode("utf-8"))
        print("Patched %-36s new md5 (LF) %s" % (name, hashlib.md5(t.encode("utf-8")).hexdigest()))
    pointers = sorted({v["orrery_constant"].split("::")[-1]
                       for g in FEATURES.values() if isinstance(g, dict)
                       for v in list(g.values()) + [g]
                       if isinstance(v, dict) and "orrery_constant" in v})
    print("Earth pointers into the store (%d), each to read MATCH on the live run:" % len(pointers))
    for p in pointers:
        print("  " + p)
    print("Next: gallery_maintenance_run.py (offline; Feature renderers must pass),")
    print("  commit, push, then gallery_maintenance_run.py --live (Store drift MATCH by name),")
    print("  then look at Earth in the Explorer room.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
