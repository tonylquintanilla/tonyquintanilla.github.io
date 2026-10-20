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
    dust cloud is flattened, so it gets the turned frame as well.

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


def check_one(name, pulled_text, served_text, paper_tilt, edges=None,
              fades=None):
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


def planted(name, pulled_text, paper_tilt, fades=None):
    """Three faults, in memory, each with the words that must catch it."""
    out = []
    moved = json.loads(pulled_text)
    moved["x"][0] += 1000
    out.append(("one dot moved by 1,000 AU", json.dumps(moved), pulled_text,
                "served copy is not the pulled one"))
    out.append(("the served copy differs", pulled_text, pulled_text + " ",
                "served copy is not the pulled one"))
    turned = json.loads(pulled_text)
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
    for planted_name in names:
        if texts[planted_name][0] is None:
            continue
        for label, pulled_text, served_text, expect in planted(
                planted_name, texts[planted_name][0], paper, fades):
            total += 1
            fails, _ = check_one(planted_name, pulled_text, served_text,
                                 paper, edges, fades)
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
                                edges, fades)
        problems.extend(fails)
        if info:
            shape = ("flattened, middle plane tilted %.1f deg" % info["tilt"]
                     if name in FADES and "tilt" in FADES[name]
                     else "round, centred on the body" if name in FADES
                     else "plane tilted %.1f deg" % info["tilt"])
            print("  %-15s %d dots, %s (%s), "
                  "served copy %s, sha256 %s"
                  % (name, info["dots"], shape,
                     "served tilt row %s" % paper if name == "hills_cloud"
                     else "between the served edges, thinning out"
                     if name in FADES
                     else "the body frame's equator",
                     "MISSING" if texts[name][1] is None else
                     "matches" if texts[name][1] == texts[name][0] else "DIFFERS",
                     info["sha256"][:12]))
            if not fails:
                named.append("%s %d dots, %s, sha256 %s"
                             % (name, info["dots"],
                                "round" if name in FADES and
                                "tilt" not in FADES[name]
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
