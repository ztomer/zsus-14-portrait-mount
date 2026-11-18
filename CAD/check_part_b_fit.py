"""Assembly check for Part B: the two halves and the monitor must not overlap, and the lips must capture
the monitor. Monitor model: Monitor_Dimensions_and_Ports.md (portrait, front view, glass on Z = 3.0),
mirrored to the print frame (STL x = -X). Run: python3 CAD/check_part_b_fit.py  (needs manifold3d, trimesh)."""

import os
import sys

import manifold3d as m3
import numpy as np
import trimesh

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGE = 3.0


def load(name):
    tm = trimesh.load(os.path.join(ROOT, "STLs", name + ".stl"))
    man = m3.Manifold(
        m3.Mesh(
            vert_properties=np.asarray(tm.vertices, np.float32),
            tri_verts=np.asarray(tm.faces, np.uint32),
        )
    )
    assert man.status() == m3.Error.NoError, (name, man.status())
    return man


def monitor(thick):
    # XZ profile (front view X, depth Z), extruded along Y 0..310, plan corners R6
    prof = [(0, 0), (0, thick), (73, thick), (76, 5.7), (220, 5.7), (220, 0)]
    pts = [(-x, LEDGE + z) for x, z in prof]  # print-frame mirror
    body = m3.Manifold.extrude(m3.CrossSection([pts]), 310.0).rotate((90, 0, 0)).translate((0, 310.0, 0))
    plan = (
        m3.CrossSection.square((208.0, 298.0))
        .offset(6.0, m3.JoinType.Round, circular_segments=48)
        .translate((-214.0, 6.0))
    )
    return body ^ m3.Manifold.extrude(plan, 40.0)


up, lo = load("Part_B_Upper"), load("Part_B_Lower")
fails = []


def report(label, vol, limit=0.01):
    ok = vol <= limit
    print(f"{'OK  ' if ok else 'FAIL'} {label:42s} overlap {vol:8.3f} mm3")
    if not ok:
        fails.append(label)


report("Upper vs Lower (assembled)", (up ^ lo).volume())
for thick, tag in ((13.6, "measured 13.6 mm hump"), (14.0, "ZSUS spec 14.0 mm hump")):
    mon = monitor(thick)
    b = mon.bounding_box()
    assert abs((b[3] - b[0]) - 220.0) < 0.01 and abs((b[4] - b[1]) - 310.0) < 0.01, b
    report(f"Upper vs monitor ({tag})", (up ^ mon).volume())
    report(f"Lower vs monitor ({tag})", (lo ^ mon).volume())
# capture: lips must sit over the monitor's back (in plan) on both long sides
for x_mon, z_back, side in (
    (-1.0, LEDGE + 13.6, "thick-side lip"),
    (-219.0, LEDGE + 5.7, "thin-side lip"),
):
    for part, nm, y in ((lo, "Lower", 100.0), (up, "Upper", 250.0)):
        probe = m3.Manifold.cube((0.4, 0.4, 3.0)).translate((x_mon - 0.2, y - 0.2, z_back + 0.05))
        hit = (part ^ probe).volume() > 0
        print(f"{'OK  ' if hit else 'FAIL'} {nm} {side} over the monitor back at y={y:.0f}")
        if not hit:
            fails.append(f"{nm} {side}")


# fit gauge: its first thin-side slot must BE the Lower's slot, the other two 0.4 / 0.8 mm taller (measured
# on the meshes, print frame: thin lip at x = -219.4 on the Lower, shifted +190 in x and 20 mm per step in y)
def slot(tm, x, y):
    locs, _, _ = tm.ray.intersects_location([[x, y, -1.0]], [[0.0, 0.0, 1.0]])
    z = np.sort(np.asarray(locs).reshape(-1, 3)[:, 2])
    return float(z[2] - z[1]) if len(z) >= 4 else None  # ledge exit -> lip bottom


lo_tm = trimesh.load(os.path.join(ROOT, "STLs", "Part_B_Lower.stl"))
ga_tm = trimesh.load(os.path.join(ROOT, "STLs", "Part_B_FitGauge.stl"))
ref = slot(lo_tm, -219.4, 107.5)
got = [slot(ga_tm, -219.4 + 190.0, 107.5 + 20.0 * k) for k in range(3)]
want = [ref + d for d in (0.0, 0.4, 0.8)]
ok = all(g is not None and abs(g - w) < 0.01 for g, w in zip(got, want, strict=True))


def fmt(v):
    return "none" if v is None else f"{v:.2f}"


print(
    f"{'OK  ' if ok else 'FAIL'} gauge thin slots {' / '.join(map(fmt, got))} mm, "
    f"want {' / '.join(map(fmt, want))} (Lower slot {ref:.2f})"
)
if not ok:
    fails.append("gauge thin slots")
# styling (Snow White pass, 2026-11-18), measured on the assembled bezel, print frame (front view X = -x):
# equal visible side/top borders (frame face + bevel down to the glass plane), equal groove depth on both
# sides, grooves set back from the front edge (only the parting-line groove runs through), and the
# front-face parting line sits inside a deliberate groove.
up_tm = trimesh.load(os.path.join(ROOT, "STLs", "Part_B_Upper.stl"))
both = trimesh.util.concatenate([up_tm, lo_tm])
(bx0, by0, _), (bx1, by1, _) = both.bounds


def first_z(tm, pts):
    """First +z hit from the front for each (x, y); inf where the ray passes clean through."""
    origins = np.array([[x, y, -1.0] for x, y in pts])
    out = np.full(len(origins), np.inf)
    rays = np.tile([0.0, 0.0, 1.0], (len(origins), 1))
    locs, idx, _ = tm.ray.intersects_location(origins, rays, multiple_hits=False)
    out[idx] = locs[:, 2]
    return out


ys_mid = (by0 + by1) / 2
xs = np.arange(bx0 + 0.05, bx1, 0.05)
open_x = xs[first_z(both, [(x, 150.0) for x in xs]) > LEDGE]  # behind the glass plane = hidden by the monitor
ys = np.arange(150.0, by1, 0.05)
open_y = ys[first_z(both, [(-118.0, y) for y in ys]) > LEDGE]
borders = {
    "front-view left": bx1 - open_x.max(),
    "front-view right": open_x.min() - bx0,
    "top": by1 - open_y.max(),
}
ok = max(borders.values()) - min(borders.values()) <= 0.25
print(
    f"{'OK  ' if ok else 'FAIL'} borders "
    + ", ".join(f"{k} {v:.2f}" for k, v in borders.items())
    + " mm (equal within 0.25)"
)
if not ok:
    fails.append("borders")


def side_grooves(z, outer, d):
    """(y, depth) of every groove on one long side at height z; d = inward ray direction in x."""
    ys = np.arange(by0 + 3, by1 - 3, 0.1)
    origins = np.array([[outer - 5 * d, y, z] for y in ys])
    rays = np.tile([d, 0.0, 0.0], (len(origins), 1))
    locs, idx, _ = both.ray.intersects_location(origins, rays, multiple_hits=False)
    depth = np.zeros(len(ys))
    depth[idx] = np.abs(locs[:, 0] - outer)
    runs, i = [], 0
    while i < len(ys):
        if depth[i] > 0.3:
            j = i
            while j + 1 < len(ys) and depth[j + 1] > 0.3:
                j += 1
            runs.append((ys[(i + j) // 2], float(np.median(depth[i : j + 1]))))
            i = j + 1
        else:
            i += 1
    return runs


mid = {s: side_grooves(9.0, o, d) for s, o, d in (("left", bx1, -1.0), ("right", bx0, 1.0))}
depths = [g for s in mid.values() for _, g in s]
ok = len(depths) > 10 and max(depths) - min(depths) <= 0.05
print(
    f"{'OK  ' if ok else 'FAIL'} side grooves: left {len(mid['left'])} / right {len(mid['right'])}, depth "
    f"{min(depths, default=0):.2f}..{max(depths, default=0):.2f} mm (equal both sides)"
)
if not ok:
    fails.append("groove depth")
front = {s: side_grooves(2.5, o, d) for s, o, d in (("left", bx1, -1.0), ("right", bx0, 1.0))}
ok = all(len(v) <= 1 for v in front.values())
print(
    f"{'OK  ' if ok else 'FAIL'} grooves reaching the front edge: left {len(front['left'])}, "
    f"right {len(front['right'])} (parting line only)"
)
if not ok:
    fails.append("grooves through the front edge")
for side, x in (("front-view left", bx1 - 8.0), ("front-view right", bx0 + 8.0)):
    yy = np.arange(100.0, 250.0, 0.05)
    gap = yy[first_z(both, [(x, y) for y in yy]) > 0.3]
    lo_face = yy[first_z(lo_tm, [(x, y) for y in yy]) < 0.05]
    up_face = yy[first_z(up_tm, [(x, y) for y in yy]) < 0.05]
    ok = len(gap) > 0 and lo_face.max() <= gap.max() + 0.05 and up_face.min() >= gap.min() - 0.05
    print(
        f"{'OK  ' if ok else 'FAIL'} {side} border: parting line inside a front groove "
        f"(groove {gap.min() if len(gap) else 0:.2f}..{gap.max() if len(gap) else 0:.2f})"
    )
    if not ok:
        fails.append(f"front seam {side}")
if fails:
    sys.exit(f"fit check failed: {fails}")
print("fit check passed")
