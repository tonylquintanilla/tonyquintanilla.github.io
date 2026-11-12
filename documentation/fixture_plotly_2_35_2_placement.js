// fixture_plotly_2_35_2_placement.js -- Plotly 2.35.2's own placement of
// a point of a 3D scene on the screen, copied so a check can hold the
// guide's ring to it (L-527).
//
// Copied on 2026-11-12 from the tag v2.35.2 of plotly.js:
//   https://raw.githubusercontent.com/plotly/plotly.js/v2.35.2/src/plots/gl3d/project.js
//     (whole; below as xformMatrix and project, unchanged)
//   https://raw.githubusercontent.com/plotly/plotly.js/v2.35.2/src/plots/gl3d/scene.js
//     lines 433-434, where a picked point's hover box is placed:
//       x: (0.5 + 0.5 * pdata[0] / pdata[3]) * width,
//       y: (0.5 - 0.5 * pdata[1] / pdata[3]) * height,
//     with pdata = project(scene.glplot.cameraParams, selection.dataCoordinate)
//     (line 344), the point already scaled by scene.dataScale, as
//     src/components/annotations3d/draw.js scales a pinned annotation.
// plotly.js is under the MIT License, Copyright (c) 2021 Plotly, Inc.
//
// Nothing loads this file but documentation/smoke_first_guide.js. If the
// page moves to another Plotly, this file is copied again from that tag
// and the guide's sum read against it; the check is red until both agree
// with the page's script line.
//
// Written November 12, 2026 with Anthropic's Claude Opus 5.5 (L-527).
'use strict';

function xformMatrix(m, v) {
    var out = [0, 0, 0, 0];
    var i, j;

    for(i = 0; i < 4; ++i) {
        for(j = 0; j < 4; ++j) {
            out[j] += m[4 * i + j] * v[i];
        }
    }

    return out;
}

function project(camera, v) {
    var p = xformMatrix(camera.projection,
        xformMatrix(camera.view,
        xformMatrix(camera.model, [v[0], v[1], v[2], 1])));
    return p;
}

// scene.js's placement, around project(): the point in data units, the
// scene's dataScale, its box's width and height.
function place(cameraParams, dataScale, point, width, height) {
    var pdata = project(cameraParams, [point[0] * dataScale[0], point[1] * dataScale[1], point[2] * dataScale[2]]);
    return {
        x: (0.5 + 0.5 * pdata[0] / pdata[3]) * width,
        y: (0.5 - 0.5 * pdata[1] / pdata[3]) * height,
        w: pdata[3]
    };
}

module.exports = { VERSION: '2.35.2', project: project, place: place };
