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

    pulled      data/drawings/<name>.json exists, is dots in AU, and its
                x, y and z each hold "dots" numbers
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
    the SHA     data/drawings/pulled_at.sha names the orrery commit the
                drawings were pulled at

    A check that passes is only worth something if it can fail, so three
    faults are planted first, in memory, and each must be caught: a dot
    moved, the served copy differing from the pulled one, and the frame
    turned (x and z swapped) so the plane's tilt moves.

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


def check_one(name, pulled_text, served_text, paper_tilt):
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
    if not isinstance(recorded, (int, float)) or abs(round(tilt, 1) - recorded) > 0.05:
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


def planted(name, pulled_text, paper_tilt):
    """Three faults, in memory, each with the words that must catch it."""
    out = []
    moved = json.loads(pulled_text)
    moved["x"][0] += 1000
    out.append(("one dot moved by 1,000 AU", json.dumps(moved), pulled_text,
                "served copy is not the pulled one"))
    out.append(("the served copy differs", pulled_text, pulled_text + " ",
                "served copy is not the pulled one"))
    turned = json.loads(pulled_text)
    turned["x"], turned["z"] = turned["z"], turned["x"]
    text = json.dumps(turned)
    out.append(("the frame turned (x and z swapped)", text, text,
                "plane through the dots is tilted"))
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
    first = names[0]
    if texts[first][0] is not None:
        for label, pulled_text, served_text, expect in planted(
                first, texts[first][0], paper):
            total += 1
            fails, _ = check_one(first, pulled_text, served_text, paper)
            hit = any(expect in line for line in fails)
            caught += hit
            print("  planted: %-38s %s" % (label, "caught" if hit else "MISSED"))
            if not hit:
                problems.append("planted fault not caught: " + label)
        print("")

    for name in names:
        fails, info = check_one(name, texts[name][0], texts[name][1], paper)
        problems.extend(fails)
        if info:
            print("  %-14s %d dots, plane tilted %.1f deg (served tilt row %s), "
                  "served copy %s, sha256 %s"
                  % (name, info["dots"], info["tilt"], paper,
                     "MISSING" if texts[name][1] is None else
                     "matches" if texts[name][1] == texts[name][0] else "DIFFERS",
                     info["sha256"][:12]))
            if not fails:
                named.append("%s %d dots, tilt %.1f deg, sha256 %s"
                             % (name, info["dots"], info["tilt"],
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
