"""
Travel over open air in a sliced plate: where a PLA print strings.

A string is ooze the nozzle drags across a gap while it travels without extruding. Over the part it is buried by the
next layer; over open air (the bezel's 200 x 300 mm screen opening, the gap between two walls) it is left as a
hair, which is what the first v21 bezel print came off the plate with (2026-11-19). So the measure is the travel the
G-code makes more than NEAR mm from anything that layer extrudes, read from the G-code the printer runs.

    air_travel(gcode_text) -> {"total_mm", "longest_mm", "spans", "layers"}
    python3 CAD/gcode_travel.py plate.gcode ...      prints the numbers for each file

Bambu Studio G-code: absolute XY (G90), relative E (M83), layers start at "; CHANGE_LAYER", arcs as G2/G3 with I/J.
A move counts as extrusion when it moves in XY with E > 0; a wipe (E < 0 while moving) and a plain move are travel.
"""

import math
import re
import sys

import numpy as np
from scipy import ndimage

CELL = 0.5  # mm, the raster the layer's extrusion is drawn on
NEAR = 2.0  # mm: travel closer than this to the layer's own extrusion stays over the part (or its sparse infill)
STEP = 0.25  # mm between samples along a move
_WORD = re.compile(r"([XYZEIJ])(-?\d*\.?\d+)")


def _arc(x0, y0, x1, y1, i, j, cw):
    cx, cy = x0 + i, y0 + j
    a0, a1 = math.atan2(y0 - cy, x0 - cx), math.atan2(y1 - cy, x1 - cx)
    r = math.hypot(x0 - cx, y0 - cy)
    sweep = a1 - a0
    if cw and sweep >= 0:
        sweep -= 2 * math.pi
    if not cw and sweep <= 0:
        sweep += 2 * math.pi
    n = max(2, int(abs(sweep) * r / STEP) + 1)
    t = np.linspace(0.0, 1.0, n)
    return np.c_[cx + r * np.cos(a0 + sweep * t), cy + r * np.sin(a0 + sweep * t)]


def _line(x0, y0, x1, y1):
    n = max(2, int(math.hypot(x1 - x0, y1 - y0) / STEP) + 1)
    t = np.linspace(0.0, 1.0, n)
    return np.c_[x0 + (x1 - x0) * t, y0 + (y1 - y0) * t]


def layers(gcode):
    """Per layer: (extruded sample points, [travel polylines]) in bed mm."""
    out, ext, trav = [], [], []
    x = y = 0.0
    started = False
    for raw in gcode.splitlines():
        if raw.startswith(("; MACHINE_END_GCODE_START", "; EXECUTABLE_BLOCK_END")):  # park and present: not the part
            break
        if raw.startswith("; CHANGE_LAYER"):
            if started:
                out.append((ext, trav))
            ext, trav, started = [], [], True
            continue
        if not raw.startswith(("G0", "G1", "G2", "G3")):
            continue
        code = raw.split(None, 1)[0]
        w = dict(_WORD.findall(raw.split(";", 1)[0]))
        if "X" not in w and "Y" not in w:
            continue
        nx, ny = float(w.get("X", x)), float(w.get("Y", y))
        if not started:  # the start G-code (purge line, bed level): only where the head ends up counts
            x, y = nx, ny
            continue
        pts = (
            _arc(x, y, nx, ny, float(w.get("I", 0)), float(w.get("J", 0)), code == "G2")
            if code in ("G2", "G3")
            else _line(x, y, nx, ny)
        )
        (ext if float(w.get("E", 0)) > 0 else trav).append(pts)
        x, y = nx, ny
    if started:
        out.append((ext, trav))
    return out


def air_travel(gcode, near=NEAR):
    tot, longest, spans, n_layers = 0.0, 0.0, 0, 0
    for ext, trav in layers(gcode):
        if not ext or not trav:
            continue
        n_layers += 1
        e = np.concatenate(ext)
        allp = np.concatenate([e, *trav])
        lo = allp.min(0) - 2 * near
        shape = tuple((np.ceil((allp.max(0) + 2 * near - lo) / CELL)).astype(int) + 1)
        grid = np.ones(shape, bool)
        idx = np.floor((e - lo) / CELL).astype(int)
        grid[idx[:, 0], idx[:, 1]] = False
        dist = ndimage.distance_transform_edt(grid) * CELL  # mm from the nearest extruded cell
        for pts in trav:
            ii = np.floor((pts - lo) / CELL).astype(int)
            air = dist[ii[:, 0], ii[:, 1]] > near
            seg = np.hypot(*np.diff(pts, axis=0).T)
            on = air[1:] & air[:-1]
            tot += float(seg[on].sum())
            run = 0.0
            for s, a in zip(seg, on, strict=True):
                if a:
                    run += s
                else:
                    if run > 0:
                        spans += 1
                        longest = max(longest, run)
                    run = 0.0
            if run > 0:
                spans += 1
                longest = max(longest, run)
    return {"total_mm": round(tot, 1), "longest_mm": round(float(longest), 1), "spans": spans, "layers": n_layers}


if __name__ == "__main__":
    for path in sys.argv[1:]:
        with open(path, errors="ignore") as fh:
            print(path, air_travel(fh.read()))
