"""
draw_lobby_strips.py -- draw the two pictures on the lobby's "More to
explore" strips, Earth System Science and Stars, from the site's own
cards.

L-517 (the lobby for a first-time phone visitor), part 2, from the
brief documentation/COORD_L517_lobby_brief_20261108.md in the orrery:
"draw them from the site's own cards, with a small script kept in the
gallery's tools/ beside the other headless tools, so they can be
redrawn."

Run from the gallery root (VS Code's Run button works too, since the
script finds the gallery root from its own place):
    python tools/headless/draw_lobby_strips.py

It needs Pillow, which is in requirements.txt. It reads two cards
and writes two pictures, and changes nothing else:

  gallery/warming_stripes.json            -> gallery/pictures/lobby_earth_system.jpg
  gallery/3d_stars_distance_20ly_social.json -> gallery/pictures/lobby_stars.jpg

EARTH SYSTEM: one stripe per year, the mean of that year's monthly
anomalies in the card's heatmap (its z, one row per year), coloured by
the card's own colour scale between the card's own zmin and zmax,
with no colour bar. A month the card serves as empty is left out of
its year's mean; a year with no months is reported and drawn black.

STARS: the card's stars laid flat, x against y at one scale for both,
on black, in the card's own marker colours (its colour scale over its
cmin to cmax) and its own marker sizes, doubled so they read at phone
size (STAR_SIZE_SCALE); the Sun as the card draws it,
green with a yellow ring. The strip is as wide as the card's x range,
so it holds the stars within a band about the Sun's plane; the last
line says how many of the card's stars fall inside.

Neither picture carries a number. Each one's alt text, in index.html's
LOBBY_MORE, names the card it comes from. Pictures are written as
1200 x 400 JPEGs.

Claude-only tooling, like the rest of tools/headless/: Tony never needs
to run it, and the maintenance run does not.

Role: devtool
Domain: gallery

Written November 8, 2026 with Anthropic's Claude Opus 5.5.
"""

import json
import os
import sys

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GALLERY = os.path.join(ROOT, "gallery")
STRIPES = os.path.join(GALLERY, "warming_stripes.json")
STARS = os.path.join(GALLERY, "3d_stars_distance_20ly_social.json")
OUT_EARTH = os.path.join(GALLERY, "pictures", "lobby_earth_system.jpg")
OUT_STARS = os.path.join(GALLERY, "pictures", "lobby_stars.jpg")
OUT_PX = (1200, 400)
SUPER = 3                    # drawn at three times the size, then reduced
STAR_SIZE_SCALE = 2.0        # the card's marker sizes doubled: the strip is shown
                             # about 350 px wide on a phone, a third of its 1200,
                             # so the card's sizes as drawn would read as specks.
                             # A drawing choice, Tony's to judge (Mode 5).
NAMED = {"gray": (128, 128, 128), "grey": (128, 128, 128), "white": (255, 255, 255),
         "yellow": (255, 255, 0)}   # CSS colour names, as the browser draws them


def parse_rgb(text):
    """'rgb(5,48,97)' or 'rgb(5, 48, 97)' -> (5, 48, 97)."""
    inner = text.strip()[text.index("(") + 1:text.rindex(")")]
    return tuple(int(round(float(p))) for p in inner.split(",")[:3])


def scale_colour(scale, t):
    """Plotly's colour scale, linear between its stops, t clipped to 0..1."""
    t = min(1.0, max(0.0, t))
    stops = [(float(s), parse_rgb(c)) for s, c in scale]
    for (s0, c0), (s1, c1) in zip(stops, stops[1:]):
        if t <= s1:
            f = 0.0 if s1 == s0 else (t - s0) / (s1 - s0)
            return tuple(int(round(c0[i] + f * (c1[i] - c0[i]))) for i in range(3))
    return stops[-1][1]


def draw_earth():
    card = json.load(open(STRIPES, encoding="utf-8"))
    heat = [t for t in card["data"] if t.get("type") == "heatmap"]
    if len(heat) != 1:
        raise SystemExit("expected one heatmap in %s, found %d" % (STRIPES, len(heat)))
    heat = heat[0]
    zmin, zmax = float(heat["zmin"]), float(heat["zmax"])
    years = heat["y"]
    means, empty = [], []
    for year, row in zip(years, heat["z"]):
        vals = [float(v) for v in row if v is not None]
        if not vals:
            empty.append(year)
            means.append(None)
        else:
            means.append(sum(vals) / len(vals))
    w, h = OUT_PX
    img = Image.new("RGB", OUT_PX, (0, 0, 0))
    d = ImageDraw.Draw(img)
    n = len(means)
    for i, m in enumerate(means):
        x0 = int(round(i * w / n))
        x1 = int(round((i + 1) * w / n))
        colour = (0, 0, 0) if m is None else scale_colour(
            heat["colorscale"], (m - zmin) / (zmax - zmin))
        d.rectangle([x0, 0, x1 - 1, h - 1], fill=colour)
    img.save(OUT_EARTH, quality=88, optimize=True, progressive=True)
    print("ok %s: %d stripes, %s to %s, the card's scale %.2f to %.2f"
          % (os.path.relpath(OUT_EARTH, ROOT), n, years[0], years[-1], zmin, zmax))
    if empty:
        print("note: years with no months, drawn black: %s" % ", ".join(empty))


def draw_stars():
    card = json.load(open(STARS, encoding="utf-8"))
    by_name = {t.get("name"): t for t in card["data"]}
    stars, sun = by_name.get("Stars"), by_name.get("Sun")
    if stars is None or sun is None:
        raise SystemExit("expected traces named Stars and Sun in %s" % STARS)
    half = float(card["layout"]["scene"]["xaxis"]["range"][1])
    w, h = OUT_PX[0] * SUPER, OUT_PX[1] * SUPER
    px_per = (w / 2.0) / half                 # one scale for x and y
    img = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(img)
    m = stars["marker"]
    cmin, cmax = float(m.get("cmin", 0)), float(m.get("cmax", 1))
    sizes = m["size"] if isinstance(m["size"], list) else [m["size"]] * len(stars["x"])
    order = sorted(range(len(stars["x"])), key=lambda i: -sizes[i])   # big first
    inside = 0
    for i in order:
        x = w / 2.0 + stars["x"][i] * px_per
        y = h / 2.0 - stars["y"][i] * px_per
        r = sizes[i] * STAR_SIZE_SCALE * SUPER / 2.0
        if 0 <= y <= h:
            inside += 1
        c = m["color"][i]
        if isinstance(c, str):
            # The card names a few colours outright ("gray": a star the
            # orrery has no temperature for); drawn as the browser would.
            colour = NAMED.get(c.lower())
            if colour is None:
                raise SystemExit("star %d: colour %r is not one this script knows" % (i, c))
        else:
            colour = scale_colour(m["colorscale"], (c - cmin) / (cmax - cmin))
        d.ellipse([x - r, y - r, x + r, y + r], fill=colour)
    sm = sun["marker"]
    sx = w / 2.0 + sun["x"][0] * px_per
    sy = h / 2.0 - sun["y"][0] * px_per
    sr = sm["size"] * STAR_SIZE_SCALE * SUPER / 2.0
    ring = sm.get("line", {})
    rw = float(ring.get("width", 0)) * SUPER
    if rw:
        d.ellipse([sx - sr - rw, sy - sr - rw, sx + sr + rw, sy + sr + rw],
                  fill=ring.get("color", "yellow"))
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=parse_rgb(sm["color"]))
    img = img.resize(OUT_PX, Image.LANCZOS)
    img.save(OUT_STARS, quality=88, optimize=True, progressive=True)
    print("ok %s: %d of the card's %d stars inside the strip, and the Sun; x range +-%.2f ly"
          % (os.path.relpath(OUT_STARS, ROOT), inside, len(stars["x"]), half))


def main():
    os.makedirs(os.path.dirname(OUT_EARTH), exist_ok=True)
    draw_earth()
    draw_stars()


if __name__ == "__main__":
    main()
    sys.exit(0)
