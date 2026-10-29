"""
check_drawings.py -- every stored drawing the served config names is
pulled, served, and the drawing it claims to be.

WHAT THIS IS

    Some shapes are dots the orrery places and the website draws as given
    (L-421, Tony's option A, 2026-10-11): the first is the Hills cloud.
    tools/pull_drawings.py copies each one from the orrery into
    data/drawings/; the cache builder copies it into the served cache,
    data/solar-system/drawings/, which is the file the browser fetches.
    This checks that chain, for every drawing data/objects_config.json
    names under a feature's drawing.dots:

    pulled      data/drawings/<name>.json exists, is dots in one of
                pull_drawings.UNITS, and its x, y and z (and any w and
                belt) each hold "dots" numbers
    served      the served copy exists and is the pulled one byte for
                byte (line endings aside). A red line here right after a
                pull that changed the dots is CORRECT: the cache has not
                been rebuilt yet (gallery-cache-builder, a config change
                is not deployed until the cache is rebuilt)
    its tilt    the plane through the served dots, fitted here, is
                tilted to the ecliptic as the file records, to 0.1
                degree -- the one check that fails on the mechanism (a
                frame turned, an axis swapped) rather than on the
                picture. For the Hills cloud it must also lie within 10
                degrees of the served tilt row, the paper's "about 30",
                the orrery sampler's own tolerance
    the belts   (L-330) Earth's radiation belts record no tilt: their
                plane must lie within 1 degree of the body frame's
                equator, and every dot must lie on a dipole field line
                (L = r / cos^2 latitude) between its own belt's served
                edges in the config, to the file's rounding
    the fades   (L-410) Earth's hydrogen exosphere, the Sun's corona and
                the zodiacal dust cloud record no tilt: each one's dots
                must lie between its served edges, be centred on the
                body, and thin out -- per unit volume, fewer in each
                shell outward ten times the volume of the last. The dust
                cloud thins only from its depletion zone outward, and its
                middle plane must lie within 3 degrees of its served tilt
    the outer   (L-434) the outer Oort cloud and the galactic tide
    cloud       record no tilt: every dot must lie between its row's
                served inner_radius and outer_radius, in AU. The tide's
                dots must also follow |sin b cos b| about the SERVED
                galactic pole: counted in five shells of |sin b|, b the
                galactic latitude worked out here from the pole's served
                RA and Dec and the served frame angle, each shell within
                four standard deviations of chance or 15 percent of what
                the rule gives
    the SHA     data/drawings/pulled_at.sha names the orrery commit the
                drawings were pulled at

    A check that passes is only worth something if it can fail, so three
    faults are planted first, in memory, for EVERY drawing, and each must
    be caught: a dot moved, the served copy differing from the pulled one,
    and the frame turned (x and z swapped) so the plane's tilt moves. The
    belts get a fourth: one dot moved off its field lines in both copies.
    A fade gets three of its own in place of the turned frame: the dots
    moved off the body, a dot moved inside the inner edge, and the dots
    spread evenly in volume so they no longer thin out. The exosphere and
    the corona are round, so turning their frame changes nothing; the
    dust cloud is flattened, so it gets the turned frame as well. The
    outer cloud and the tide get a dot moved inside the inner edge, and
    the tide the turned frame, which moves its pole.

    The last line starts "DRAWINGS:", which the maintenance run quotes,
    and names each drawing with its dots, its fitted tilt and its sha256.

RUN COMMAND

    python tools/check_drawings.py

    Open it in VS Code and click Run. gallery_maintenance_run.py runs it
    as a gating checker.

Role: devtool
Domain: gallery

Module created: October 11, 2026 with Anthropic's Claude Opus 5.5
(L-421, the website half of the inner Oort cloud).
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5
(L-330: Earth's radiation belts, the second stored drawing, are checked by
their mechanism -- plane and field lines against the served edges -- and
the planted faults run for every drawing, not only the first.)
Module updated: October 17, 2026 with Anthropic's Claude Opus 5.5
(L-410: Earth's hydrogen exosphere, the third stored drawing, is checked
by its mechanism -- between the served edges, centred, thinning out --
with three faults of its own.)
Module updated: October 20, 2026 with Anthropic's Claude Opus 5.5
(L-410 with L-131: the Sun's corona and the zodiacal dust cloud, the
fourth and fifth stored drawings, are checked the same way, each from
its own served edges (FADES); the dust cloud, which is flattened and
thins only outside the zone near the Sun where its dust is depleted, is
judged from there outward and by its middle plane's tilt, with the
turned frame as a fourth fault.)
Module updated: October 22, 2026 with Anthropic's Claude Opus 5.5
(L-434: the outer Oort cloud and the galactic tide, the sixth and seventh
stored drawings, are checked by their mechanism: between their served
edges, and the tide's dots thickest halfway between the galaxy's plane
and its served pole, as |sin b cos b| gives; with a dot planted inside
the inner edge in each, and the tide's frame turned.)
Module updated: October 29, 2026 with Anthropic's Claude Opus 5.5
(L-503: the main belt's cloud, the eighth stored drawing and the first
that is a room's own row, is checked by its ends: every dot between its
row's distance table's two ends and within its latitude table's last
entry of the ecliptic; with a dot planted inside the near edge and the
frame turned.)
"""

import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from pull_drawings import named_drawings, problem  # noqa: E402

ROOT = os.path.dirname(HERE)
CONFIG = os.path.join(ROOT, "data", "objects_config.json")
PULLED = os.path.join(ROOT, "data", "drawings")
SERVED = os.path.join(ROOT, "data", "solar-system", "drawings")
SHA_FILE = os.path.join(PULLED, "pulled_at.sha")
TILT_TOLERANCE_DEG = 10.0
# L-330: the belts' dots are in Earth's body frame, so their plane is its
# equator, to this much; and each lies on its field line to this many
# Earth radii in L, allowing the file's rounding to 0.01 Earth radii.
BELT_PLANE_DEG = 1.0
BELT_L_SLACK = 0.05
# L-410: the exosphere's dots are round and centred on Earth. Their centre
# may sit off Earth by this share of their mean distance (chance alone
# puts it near 0.03 at 1,500 dots); each lies between the served edges to
# this many Earth radii; and in each tenfold-in-volume step outward the
# dots per unit volume must fall by at least this factor (the profile
# falls by more than 3 in every such step).
FADE_CENTRE_SHARE = 0.1
FADE_R_SLACK = 0.05
FADE_FALL = 1.5
# L-410 with L-131 (2026-10-20): the fades, by drawing name, and where
# each one's edges are served. "inner" is a served node on the entry, or
# a value where no row serves one (the corona starts at the Sun's
# surface, one solar radius, the drawing's own unit); "in_au" reads a
# node's served AU, for a drawing in AU whose edge is served in solar
# radii. "slack" allows for the file's rounding, in the drawing's unit.
# The dust cloud is flattened, so it also serves the tilt its plane must
# lie within FADE_TILT_DEG of, and it thins only outside the zone near
# the Sun where its dust is depleted, so its thinning is judged from
# thin_from outward.
FADES = {
    "earth_exosphere": {"at": ("earth", "earth_exosphere", "geocorona"),
                        "inner": ("node", "inner_radius"),
                        "unit": "Earth radii", "slack": FADE_R_SLACK},
    "sun_corona": {"at": ("sun", "solar_atmosphere", "corona"),
                   "inner": ("value", 1.0),
                   "unit": "solar radii", "slack": 0.005},
    "zodiacal_dust": {"at": ("sun", "solar_atmosphere", "zodiacal_dust"),
                      "inner": ("in_au", "free_zone"),
                      "thin_from": ("in_au", "depletion"),
                      "tilt": "tilt",
                      "unit": "AU", "slack": 0.0005},
}
FADE_TILT_DEG = 3.0
# L-434 (2026-10-22): the outer Oort cloud's two stored drawings, by name,
# and where each one's row is served. The tide's dots are judged about
# the galactic pole its row serves; COVERAGE carries the frame angle that
# turns that pole into the drawing frame, as the page reads it.
OUTER = {
    "outer_oort_cloud": {"at": ("sun", "oort_cloud", "outer_oort_clumpy")},
    "galactic_tide": {"at": ("sun", "oort_cloud", "galactic_tide"),
                      "pole": "galactic_pole"},
}
OUTER_SLACK_AU = 1.0           # the files round each coordinate to 1 AU
# L-503 (2026-10-29): a drawing that is a room's own row, not a body's
# shell -- the main belt's cloud, the Solar System room's row. It records
# no plane; its ends are its row's served tables: every dot between the
# distance table's 0th and 100th entries, and within the latitude table's
# 100th entry of the ecliptic, each allowing half a unit of the entry's
# last declared figure (the tables are served rounded).
ROOM_ROWS = {"main_belt": ("solar-system", "main_belt")}
SIN_B_EDGES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
COVERAGE = os.path.join(ROOT, "data", "solar-system", "coverage_index.json")


def plane_tilt_deg(x, y, z):
    """Tilt to the ecliptic (the drawing frame's x-y plane) of the plane
    through the dots: the plane whose normal is the direction they spread
    least along. The orrery sampler's plane_tilt_deg, written again here
    by its own arithmetic (power iteration on the inverted moment matrix),
    so this check does not lean on the code it checks."""
    n = float(len(x))
    m = [[0.0] * 3 for _ in range(3)]
    for p in zip(x, y, z):
        for i in range(3):
            for j in range(3):
                m[i][j] += p[i] * p[j] / n
    # The smallest eigenvalue's vector of a symmetric positive matrix is
    # the largest of its inverse: invert, then iterate.
    a, b, c = m[0]
    d, e, f = m[1]
    g, h, k = m[2]
    det = a * (e * k - f * h) - b * (d * k - f * g) + c * (d * h - e * g)
    inv = [[(e * k - f * h) / det, (c * h - b * k) / det, (b * f - c * e) / det],
           [(f * g - d * k) / det, (a * k - c * g) / det, (c * d - a * f) / det],
           [(d * h - e * g) / det, (b * g - a * h) / det, (a * e - b * d) / det]]
    v = [1.0, 1.0, 1.0]
    for _ in range(500):
        w = [sum(inv[i][j] * v[j] for j in range(3)) for i in range(3)]
        size = math.sqrt(sum(t * t for t in w))
        v = [t / size for t in w]
    return math.degrees(math.acos(min(1.0, abs(v[2]))))


def read(path):
    with open(path, "rb") as handle:
        return handle.read().replace(b"\r\n", b"\n").decode("utf-8")


def tilt_row(config):
    """The served tilt row's value for the Hills cloud, or None."""
    try:
        sun = [o for o in config["objects"] if o.get("slug") == "sun"][0]
        node = sun["features"]["oort_cloud"]["hills_cloud_torus"]["tilt"]
        return float(node["value"])
    except (IndexError, KeyError, TypeError, ValueError):
        return None


def belt_edges(config):
    """[(inner, outer)] in Earth radii for Earth's two belts, from the
    served config's edge rows, or None."""
    try:
        earth = [o for o in config["objects"] if o.get("slug") == "earth"][0]
        vab = earth["features"]["van_allen_belts"]
        return [(float(vab[p + "inner_edge"]["value"]),
                 float(vab[p + "outer_edge"]["value"]))
                for p in ("inner_belt_", "outer_belt_")]
    except (IndexError, KeyError, TypeError, ValueError):
        return None


def belt_problems(name, content, edges):
    """Failures for a belts drawing: each dot on a field line between its
    belt's served edges, and the dots' plane on the body's equator."""
    out = []
    if edges is None:
        return ["%s: no served belt edges to judge the dots by" % name]
    belts = content.get("belt")
    if not isinstance(belts, list) or len(content.get("belts") or []) != len(edges):
        return ["%s: the file does not say which of %d belts each dot is in"
                % (name, len(edges))]
    off = []
    for x, y, z, b in zip(content["x"], content["y"], content["z"], belts):
        rho2 = x * x + y * y
        r = math.sqrt(rho2 + z * z)
        if not (0 <= b < len(edges)) or rho2 <= 0 or r <= 0:
            off.append((b, None))
            continue
        shell = r * r * r / rho2          # r / cos^2(latitude)
        lo, hi = edges[b]
        if shell < lo - BELT_L_SLACK or shell > hi + BELT_L_SLACK:
            off.append((b, shell))
    if off:
        b, shell = off[0]
        out.append("%s: %d dot(s) lie off the field lines between their "
                   "belt's served edges, e.g. a dot of belt %s at L = %s"
                   % (name, len(off), b,
                      "?" if shell is None else "%.2f" % shell))
    tilt = plane_tilt_deg(content["x"], content["y"], content["z"])
    if tilt > BELT_PLANE_DEG:
        out.append("%s: the plane through the dots is tilted %.1f deg from "
                   "the body frame's equator, not within %.0f deg"
                   % (name, tilt, BELT_PLANE_DEG))
    return out


def _fade_value(entry, how):
    """A served edge: a node's value, a node's served AU, or a value."""
    kind, what = how
    if kind == "value":
        return float(what)
    node = entry[what]
    if kind == "in_au":
        return float(node["in"]["au"]["value"])
    return float(node["value"])


def fade_edges(config, name):
    """{inner, outer, thin_from, tilt} for a fade, in its drawing's unit,
    from the served config, or None."""
    spec = FADES.get(name)
    if spec is None:
        return None
    slug, group, member = spec["at"]
    try:
        body = [o for o in config["objects"] if o.get("slug") == slug][0]
        entry = body["features"][group][member]
        inner = _fade_value(entry, spec["inner"])
        out = {"inner": inner, "outer": float(entry["radius"]["value"]),
               "thin_from": (_fade_value(entry, spec["thin_from"])
                             if "thin_from" in spec else inner),
               "tilt": (float(entry[spec["tilt"]]["value"])
                        if "tilt" in spec else None)}
    except (IndexError, KeyError, TypeError, ValueError):
        return None
    return out


def fade_problems(name, content, edges):
    """Failures for a fade (L-410): every dot between the served edges,
    the dots centred on the body, thinning outward, and for a flattened
    one its plane within FADE_TILT_DEG of the served tilt."""
    if edges is None:
        return ["%s: no served inner and outer edge to judge the dots by"
                % name]
    spec = FADES[name]
    unit, slack = spec["unit"], spec["slack"]
    out = []
    inner, outer = edges["inner"], edges["outer"]
    xs, ys, zs = content["x"], content["y"], content["z"]
    radii = [math.sqrt(x * x + y * y + z * z) for x, y, z in zip(xs, ys, zs)]
    off = [r for r in radii if r < inner - slack or r > outer + slack]
    if off:
        out.append("%s: %d dot(s) lie outside the served edges, %g to %g "
                   "%s, e.g. at %.4g" % (name, len(off), inner, outer, unit,
                                         off[0]))
    n = float(len(radii)) or 1.0
    mean_r = sum(radii) / n
    centre = math.sqrt((sum(xs) / n) ** 2 + (sum(ys) / n) ** 2 +
                       (sum(zs) / n) ** 2)
    if centre > FADE_CENTRE_SHARE * mean_r:
        out.append("%s: the dots are not centred on the body: their centre "
                   "sits %.3g %s off it, against a mean distance of %.3g"
                   % (name, centre, unit, mean_r))
    # Dots per unit volume in shells each ten times the volume of the
    # last, outward from where the drawing thins.
    dens, lo = [], max(inner, edges["thin_from"])
    while lo < outer:
        hi = min(outer, (lo ** 3 + 9 * lo ** 3) ** (1.0 / 3.0))
        count = sum(1 for r in radii if lo <= r < hi)
        dens.append((lo, hi, count / (hi ** 3 - lo ** 3)))
        lo = hi
    for (a, b, d1), (c, e, d2) in zip(dens, dens[1:]):
        if d1 > 0 and d2 * FADE_FALL > d1:
            out.append("%s: the dots do not thin out: per unit volume, %.3g "
                       "between %.3g and %.3g %s against %.3g between "
                       "%.3g and %.3g" % (name, d2, c, e, unit, d1, a, b))
            break
    if edges["tilt"] is not None:
        tilt = plane_tilt_deg(xs, ys, zs)
        if abs(tilt - edges["tilt"]) > FADE_TILT_DEG:
            out.append("%s: the middle plane through the dots is tilted %.1f "
                       "deg, not within %.0f deg of the served tilt's %s"
                       % (name, tilt, FADE_TILT_DEG, edges["tilt"]))
    return out


def obliquity_deg():
    """The served frame angle, EARTH_OBLIQUITY_J2000_DEG, from the served
    cache, or None."""
    try:
        with open(COVERAGE, "r", encoding="utf-8") as handle:
            rows = json.load(handle)["frame_constants"]["rows"]
        return float(rows["EARTH_OBLIQUITY_J2000_DEG"]["value"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def outer_edges(config, name, obliquity):
    """{inner, outer, pole} for an outer cloud drawing, in AU, from the
    served config: pole is the served galactic pole as a unit vector in
    the drawing frame, turned by the served frame angle, or None where
    the row serves no pole. None if a served edge cannot be read."""
    spec = OUTER.get(name)
    if spec is None:
        return None
    slug, group, member = spec["at"]
    try:
        body = [o for o in config["objects"] if o.get("slug") == slug][0]
        entry = body["features"][group][member]
        if (entry["inner_radius"]["unit"] != "au" or
                entry["outer_radius"]["unit"] != "au"):
            return None
        out = {"inner": float(entry["inner_radius"]["value"]),
               "outer": float(entry["outer_radius"]["value"]), "pole": None}
        if "pole" in spec:
            if obliquity is None:
                return None
            gp = entry[spec["pole"]]
            ra = math.radians(float(gp["ra"]["value"]))
            dec = math.radians(float(gp["dec"]["value"]))
            eps = math.radians(obliquity)
            x = math.cos(dec) * math.cos(ra)
            y = math.cos(dec) * math.sin(ra)
            z = math.sin(dec)
            out["pole"] = (x, y * math.cos(eps) + z * math.sin(eps),
                           -y * math.sin(eps) + z * math.cos(eps))
    except (IndexError, KeyError, TypeError, ValueError):
        return None
    return out


def outer_problems(name, content, edges):
    """Failures for an outer cloud drawing (L-434): every dot between the
    served edges; for the tide, the dots in shells of |sin b| about the
    served pole as |sin b cos b| gives -- the share below t is
    1 - (1 - t^2)^(3/2), worked out here, not read from the orrery."""
    if edges is None:
        return ["%s: no served inner and outer edge (and, for the tide, "
                "pole and frame angle) to judge the dots by" % name]
    out = []
    xs, ys, zs = content["x"], content["y"], content["z"]
    radii = [math.sqrt(x * x + y * y + z * z) for x, y, z in zip(xs, ys, zs)]
    off = [r for r in radii if r < edges["inner"] - OUTER_SLACK_AU or
           r > edges["outer"] + OUTER_SLACK_AU]
    if off:
        out.append("%s: %d dot(s) lie outside the served edges, %g to %g AU, "
                   "e.g. at %.0f" % (name, len(off), edges["inner"],
                                     edges["outer"], off[0]))
    pole = edges["pole"]
    if pole is not None:
        n = len(radii)
        sin_b = [abs(pole[0] * x + pole[1] * y + pole[2] * z) / r
                 for x, y, z, r in zip(xs, ys, zs, radii) if r > 0]

        def cum(t):
            return 1.0 - (1.0 - t * t) ** 1.5
        for t0, t1 in zip(SIN_B_EDGES[:-1], SIN_B_EDGES[1:]):
            got = sum(1 for s in sin_b if t0 <= s < t1 or (t1 == 1.0 and s >= 1.0))
            want = n * (cum(t1) - cum(t0))
            allow = max(4.0 * math.sqrt(want), 0.15 * want)
            if abs(got - want) > allow:
                out.append("%s: the dots do not follow the tide's latitude "
                           "rule about the served galactic pole: %d with "
                           "|sin b| from %.1f to %.1f, where |sin b cos b| "
                           "gives %.0f (allowing %.0f)"
                           % (name, got, t0, t1, want, allow))
    return out


def _half_unit(value, figures):
    return 0.5 * 10.0 ** (math.floor(math.log10(abs(value))) - int(figures) + 1)


def room_edges(config, name):
    """L-503: a room row's drawing's edges, from the row's served tables,
    or None when the row or a table is not served."""
    room, drawing = ROOM_ROWS[name]
    rows = ((((config.get("rooms") or {}).get(room) or {}).get("drawer") or {})
            .get("rows") or [])
    row = [r for r in rows if isinstance(r, dict) and r.get("drawing") == drawing]
    if not row:
        return None
    feature = row[0].get("feature") or {}
    dist, lat = feature.get("distance") or {}, feature.get("latitude") or {}
    try:
        near, far = float(dist["value"]["0"]), float(dist["value"]["100"])
        top = float(lat["value"]["100"])
        return {"near": near, "far": far, "lat": top,
                "d_half": _half_unit(far, dist["figures"]),
                "l_half": _half_unit(top, lat["figures"])}
    except (KeyError, TypeError, ValueError):
        return None


def room_problems(name, content, edges):
    """L-503: a room row's drawing held to its row's tables."""
    if edges is None:
        return ["%s: its room's row serves no distance and latitude tables "
                "to judge it by" % name]
    out = []
    r_min, r_max, lat_max = float("inf"), 0.0, 0.0
    for x, y, z in zip(content["x"], content["y"], content["z"]):
        r = math.sqrt(x * x + y * y + z * z)
        r_min, r_max = min(r_min, r), max(r_max, r)
        lat_max = max(lat_max, abs(math.degrees(math.asin(z / r))) if r else 0.0)
    if r_min < edges["near"] - edges["d_half"] or r_max > edges["far"] + edges["d_half"]:
        out.append("%s: its dots run from %.3f to %.3f AU, outside the served "
                   "edges %s to %s AU" % (name, r_min, r_max, edges["near"], edges["far"]))
    if lat_max > edges["lat"] + edges["l_half"]:
        out.append("%s: its dots reach %.1f deg from the ecliptic, past its "
                   "row's latitude %s deg" % (name, lat_max, edges["lat"]))
    return out


def check_one(name, pulled_text, served_text, paper_tilt, edges=None,
              fades=None, outer=None, rooms=None):
    """Failures for one drawing, as sentences, and what was examined."""
    failures = []
    if pulled_text is None:
        return ["%s: data/drawings/%s.json is missing -- run the gallery "
                "maintenance run, whose first step pulls it" % (name, name)], {}
    try:
        content = json.loads(pulled_text)
    except ValueError as exc:
        return ["%s: the pulled copy is not JSON (%s)" % (name, exc)], {}
    why = problem(content)
    if why:
        return ["%s: the pulled copy: %s" % (name, why)], {}
    if served_text is None:
        failures.append("%s: the served copy, data/solar-system/drawings/"
                        "%s.json, is missing -- run the cache builder"
                        % (name, name))
    elif served_text != pulled_text:
        failures.append("%s: the served copy is not the pulled one -- run the "
                        "cache builder, then this again" % name)
    tilt = plane_tilt_deg(content["x"], content["y"], content["z"])
    recorded = content.get("plane_tilt_deg")
    if "belts" in content:
        # L-330: the belts record no tilt; their mechanism is checked.
        failures.extend(belt_problems(name, content, edges))
    elif name in FADES:
        # L-410: a fade records no plane; its mechanism is checked.
        failures.extend(fade_problems(name, content,
                                      (fades or {}).get(name)))
    elif name in OUTER:
        # L-434: the outer cloud records no plane; its mechanism is checked.
        failures.extend(outer_problems(name, content,
                                       (outer or {}).get(name)))
    elif name in ROOM_ROWS:
        # L-503: a room's own row records no plane; its ends are checked.
        failures.extend(room_problems(name, content, (rooms or {}).get(name)))
    elif not isinstance(recorded, (int, float)) or abs(round(tilt, 1) - recorded) > 0.05:
        failures.append("%s: the plane through the dots is tilted %.1f deg; the "
                        "file records %s" % (name, tilt, recorded))
    if name == "hills_cloud":
        if paper_tilt is None:
            failures.append("%s: no served tilt row to judge the plane by"
                            % name)
        elif abs(tilt - paper_tilt) > TILT_TOLERANCE_DEG:
            failures.append("%s: the dots' plane is tilted %.1f deg, not within "
                            "%.0f deg of the served tilt row's %s"
                            % (name, tilt, TILT_TOLERANCE_DEG, paper_tilt))
    return failures, {"dots": content["dots"], "tilt": tilt,
                      "sha256": hashlib.sha256(pulled_text.encode("utf-8")).hexdigest()}


def planted(name, pulled_text, paper_tilt, fades=None, outer=None):
    """Three faults, in memory, each with the words that must catch it."""
    out = []
    moved = json.loads(pulled_text)
    moved["x"][0] += 1000
    out.append(("one dot moved by 1,000 AU", json.dumps(moved), pulled_text,
                "served copy is not the pulled one"))
    out.append(("the served copy differs", pulled_text, pulled_text + " ",
                "served copy is not the pulled one"))
    turned = json.loads(pulled_text)
    if name in ROOM_ROWS:
        # L-503: a dot moved inside the near edge, and the frame turned,
        # which stands the belt on its edge, far from the ecliptic.
        inside = json.loads(pulled_text)
        inside["x"][0], inside["y"][0], inside["z"][0] = 0.5, 0.0, 0.0
        text = json.dumps(inside)
        out.append(("a dot moved inside the near edge", text, text,
                    "outside the served edges"))
        turned["x"], turned["z"] = turned["z"], turned["x"]
        text = json.dumps(turned)
        out.append(("the frame turned (x and z swapped)", text, text,
                    "past its row's latitude"))
        return out
    if name in OUTER:
        # L-434: a dot inside the inner edge, and for the tide the frame
        # turned, which moves its pole away from the served one.
        edges = (outer or {}).get(name) or {"inner": 1.0}
        inside = json.loads(pulled_text)
        inside["x"][0] = 0.9 * edges["inner"]
        inside["y"][0] = inside["z"][0] = 0
        text = json.dumps(inside)
        out.append(("a dot moved inside the inner edge", text, text,
                    "outside the served edges"))
        if "pole" in OUTER[name]:
            turned["x"], turned["z"] = turned["z"], turned["x"]
            text = json.dumps(turned)
            out.append(("the frame turned (x and z swapped)", text, text,
                        "latitude rule"))
        return out
    if name in FADES:
        # A fade: its own three. Turning the frame changes a round fade
        # not at all, so only the flattened dust cloud gets that one too.
        edges = (fades or {}).get(name) or {"inner": 0.0, "outer": 1.0}
        inner, outer = edges["inner"], edges["outer"]
        shifted = json.loads(pulled_text)
        shifted["x"] = [v + 0.2 * outer for v in shifted["x"]]
        text = json.dumps(shifted)
        out.append(("the dots moved off the body", text, text,
                    "not centred on the body"))
        inside = json.loads(pulled_text)
        inside["x"][0], inside["y"][0], inside["z"][0] = 0.5 * inner, 0.0, 0.0
        text = json.dumps(inside)
        out.append(("a dot moved inside the inner edge", text, text,
                    "outside the served edges"))
        even = json.loads(pulled_text)
        for k in range(len(even["x"])):
            r = math.sqrt(even["x"][k] ** 2 + even["y"][k] ** 2 +
                          even["z"][k] ** 2)
            u = (k + 0.5) / len(even["x"])
            want = (inner ** 3 + u * (outer ** 3 - inner ** 3)) ** (1.0 / 3.0)
            for axis in ("x", "y", "z"):
                even[axis][k] = even[axis][k] * want / r
        text = json.dumps(even)
        out.append(("the dots spread evenly, not thinning", text, text,
                    "do not thin out"))
        if "tilt" in FADES[name]:
            turned["x"], turned["z"] = turned["z"], turned["x"]
            text = json.dumps(turned)
            out.append(("the frame turned (x and z swapped)", text, text,
                        "middle plane through the dots"))
        return out
    turned["x"], turned["z"] = turned["z"], turned["x"]
    text = json.dumps(turned)
    out.append(("the frame turned (x and z swapped)", text, text,
                "plane through the dots is tilted"))
    if "belts" in turned:
        offline = json.loads(pulled_text)
        offline["x"][0] *= 3.0
        offline["y"][0] *= 3.0
        text = json.dumps(offline)
        out.append(("a belt dot moved off its field lines", text, text,
                    "lie off the field lines"))
    return out


def main():
    print("=" * 70)
    print("  DRAWINGS -- pulled, served, and the drawing they claim to be")
    print("=" * 70)
    with open(CONFIG, "r", encoding="utf-8") as handle:
        config = json.load(handle)
    names = named_drawings(config)
    paper = tilt_row(config)
    if not names:
        print("DRAWINGS: FAIL -- the config names no stored drawing; the Hills "
              "cloud's should be named (L-421)")
        return 1
    problems, named = [], []
    texts = {}
    for name in names:
        p = os.path.join(PULLED, name + ".json")
        s = os.path.join(SERVED, name + ".json")
        texts[name] = (read(p) if os.path.exists(p) else None,
                       read(s) if os.path.exists(s) else None)

    caught = total = 0
    edges = belt_edges(config)
    fades = dict((n, fade_edges(config, n)) for n in FADES)
    obliquity = obliquity_deg()
    outer = dict((n, outer_edges(config, n, obliquity)) for n in OUTER)
    rooms = dict((n, room_edges(config, n)) for n in ROOM_ROWS)
    for planted_name in names:
        if texts[planted_name][0] is None:
            continue
        for label, pulled_text, served_text, expect in planted(
                planted_name, texts[planted_name][0], paper, fades, outer):
            total += 1
            fails, _ = check_one(planted_name, pulled_text, served_text,
                                 paper, edges, fades, outer, rooms)
            hit = any(expect in line for line in fails)
            caught += hit
            print("  planted in %-15s %-38s %s" % (planted_name + ":", label,
                                                  "caught" if hit else "MISSED"))
            if not hit:
                problems.append("planted fault not caught in %s: %s"
                                % (planted_name, label))
    if total:
        print("")

    for name in names:
        fails, info = check_one(name, texts[name][0], texts[name][1], paper,
                                edges, fades, outer, rooms)
        problems.extend(fails)
        if info:
            shape = ("flattened, middle plane tilted %.1f deg" % info["tilt"]
                     if name in FADES and "tilt" in FADES[name]
                     else "round, centred on the body" if name in FADES
                     else "about the served galactic pole"
                     if name in OUTER and "pole" in OUTER[name]
                     else "random directions" if name in OUTER
                     else "a room's own row" if name in ROOM_ROWS
                     else "plane tilted %.1f deg" % info["tilt"])
            print("  %-15s %d dots, %s (%s), "
                  "served copy %s, sha256 %s"
                  % (name, info["dots"], shape,
                     "served tilt row %s" % paper if name == "hills_cloud"
                     else "between the served edges, thinning out"
                     if name in FADES
                     else "between the served edges" if name in OUTER
                     else "between its row's tables' ends" if name in ROOM_ROWS
                     else "the body frame's equator",
                     "MISSING" if texts[name][1] is None else
                     "matches" if texts[name][1] == texts[name][0] else "DIFFERS",
                     info["sha256"][:12]))
            if not fails:
                named.append("%s %d dots, %s, sha256 %s"
                             % (name, info["dots"],
                                "round" if name in FADES and
                                "tilt" not in FADES[name]
                                else "about the galactic pole"
                                if name == "galactic_tide"
                                else "between its edges" if name in OUTER
                                else "tilt %.1f deg" % info["tilt"],
                                info["sha256"][:12]))
    sha = read(SHA_FILE).strip() if os.path.exists(SHA_FILE) else ""
    if len(sha) != 40:
        problems.append("data/drawings/pulled_at.sha does not name an orrery "
                        "commit")
    print("")
    if problems:
        for line in problems:
            print("FAIL: " + line)
        print("DRAWINGS: FAIL -- %d problem(s)" % len(problems))
        return 1
    print("DRAWINGS: PASS -- %d of %d planted faults caught; pulled at orrery "
          "%s; %s" % (caught, total, sha[:8], "; ".join(named)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
