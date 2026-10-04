"""
draw_room_still.py -- draw the picture on the Solar System room's wide
card in the lobby, from the room's own payload.

Claude-only tooling (L-363, 2026-10-04), like the rest of
tools/headless/. Tony never needs to run this, and the maintenance run
does not. It needs plotly 5.24.1 (which carries plotly.js 2.35.2, the
page's version), kaleido 0.2.1 and Pillow, none of which the gallery
needs otherwise.

Run from the gallery root, after run_room_driver.py:
    python3 tools/headless/run_room_driver.py SOLAR_SYSTEM_DRIVER \\
        2026-10-04T12:00:00Z /tmp/payload_solar_system.json
    python3 tools/headless/draw_room_still.py \\
        /tmp/payload_solar_system.json gallery/pictures/solar_system_room.jpg

What it draws is what the room opens on, read rather than restated:
the Sun and the bodies in data/objects_config.json's rooms section,
arrival "drawn"; framed by the room's rule (Tony, 2026-10-02), the
farthest drawn body's distance now times 1.2; the camera, background
and axis-line colours of interactive.html's buildSunLayout and
SUN_AXIS_COLORS. Tick numbers are left off, since they cannot be read
at card size. The square scene is then cut to a 2:1 strip round the
orbits and saved as a 1200 x 600 JPEG.

It is NOT a screenshot: the sandbox cannot run the browser's 3D
drawing. Plotly draws the same traces from the same payload. Tony
judges the picture on his phone (L-363, 2026-10-03: "Tony judges it at
Mode 5").

The picture shows the planets where they were at the moment given to
run_room_driver.py; the room always shows now. The card's picture_alt
in gallery/gallery_metadata.json says the date; redraw both together.

Role: devtool
Domain: gallery

Written October 4, 2026 with Anthropic's Claude Opus 5.5.
"""

import json
import math
import sys

import plotly.graph_objects as go
from PIL import Image

# interactive.html, SUN_AXIS_COLORS and buildSunLayout, at gallery df8bbab.
AXIS_COLORS = {"x": "#e06c6c", "y": "#5dbb7a", "z": "#6fa8ff"}
BACKGROUND = "#060a12"
EYE = {"x": 1.25, "y": -1.25, "z": 0.75}
FRAME_MARGIN = 1.2          # the room's EXHIBITS row, frameMargin
SCENE_PX = 1000             # drawn square, then scale 2
CROP = (0.213, 0.215, 0.787, 0.789)   # the 2:1 strip round the orbits
OUT_PX = (1200, 600)


def main(argv):
    if len(argv) != 3:
        raise SystemExit("usage: draw_room_still.py PAYLOAD.json OUT.jpg")
    payload = json.load(open(argv[1], encoding="utf-8"))
    config = json.load(open("data/objects_config.json", encoding="utf-8"))
    drawn = set(config["rooms"]["solar-system"]["arrival"]["drawn"])
    bodies = payload["bodies"]

    traces, far = [], 0.0
    for t in payload["figure"]["data"]:
        group = t.get("legendgroup")
        if group != "center" and group not in drawn:
            continue
        t = dict(t)
        t.pop("meta", None)
        t["hoverinfo"] = "skip"
        t["showlegend"] = False
        name = bodies.get(group, {}).get("name")
        if t.get("mode") == "markers" and t.get("name") == name:
            far = max(far, math.sqrt(t["x"][0] ** 2 + t["y"][0] ** 2 + t["z"][0] ** 2))
        traces.append(go.Scatter3d(**t))
    if far <= 0:
        raise SystemExit("no drawn body's position marker was found in the payload")

    r = far * FRAME_MARGIN
    axis = dict(range=[-r, r], showgrid=True, gridcolor="rgba(255,255,255,0.06)",
                zerolinecolor="rgba(255,255,255,0.1)", showbackground=True,
                backgroundcolor=BACKGROUND, showticklabels=False,
                title=dict(text=""), showspikes=False, showline=True, linewidth=2)
    fig = go.Figure(traces)
    fig.update_layout(
        width=SCENE_PX, height=SCENE_PX // 2, margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor=BACKGROUND, plot_bgcolor=BACKGROUND, showlegend=False,
        font=dict(family="DM Sans, system-ui", color="#e8e6e3"),
        scene=dict(xaxis=dict(axis, linecolor=AXIS_COLORS["x"]),
                   yaxis=dict(axis, linecolor=AXIS_COLORS["y"]),
                   zaxis=dict(axis, linecolor=AXIS_COLORS["z"]),
                   camera=dict(eye=EYE, center=dict(x=0, y=0, z=0)),
                   aspectmode="manual", aspectratio=dict(x=1, y=1, z=1)))
    png = argv[2] + ".png"
    fig.write_image(png, scale=2)

    image = Image.open(png).convert("RGB")
    w, h = image.size
    box = (int(CROP[0] * w), int(CROP[1] * h), int(CROP[2] * w), int(CROP[3] * h))
    image.crop(box).resize(OUT_PX, Image.LANCZOS).save(
        argv[2], quality=86, optimize=True, progressive=True)
    print("frame half-range %.4f AU (farthest drawn body %.4f AU); %d traces -> %s"
          % (r, far, len(traces), argv[2]))
    print("delete %s, the uncropped intermediate" % png)


if __name__ == "__main__":
    main(sys.argv)
