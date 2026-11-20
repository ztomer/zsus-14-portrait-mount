"""Assembly check for Part B: the two halves and the monitor must not overlap, and the lips must capture
the monitor. Monitor model: Monitor_Dimensions_and_Ports.md (portrait, front view, glass on Z = 3.0),
mirrored to the print frame (STL x = -X). Run: python3 CAD/check_part_b_fit.py  (needs manifold3d, trimesh)."""

import os
import sys

import manifold3d as m3
import numpy as np
import trimesh

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bezel_spec import LATCH_CATCH  # noqa: E402
from monitor_spec import HUMP_X1, LEDGE, MON_H, MON_THICK, MON_THIN, MON_W, STEP_X1  # noqa: E402

ZSUS_SPEC_THICK = 14.0  # the hump at the ZSUS spec's maximum thickness must still slide in


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
    # XZ profile (front view X, depth Z), extruded along Y 0..MON_H, plan corners R6
    prof = [(0, 0), (0, thick), (HUMP_X1, thick), (STEP_X1, MON_THIN), (MON_W, MON_THIN), (MON_W, 0)]
    pts = [(-x, LEDGE + z) for x, z in prof]  # print-frame mirror
    body = m3.Manifold.extrude(m3.CrossSection([pts]), MON_H).rotate((90, 0, 0)).translate((0, MON_H, 0))
    plan = (
        m3.CrossSection.square((MON_W - 12.0, MON_H - 12.0))
        .offset(6.0, m3.JoinType.Round, circular_segments=48)
        .translate((6.0 - MON_W, 6.0))
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
HUMPS = ((MON_THICK, f"measured {MON_THICK} mm hump"), (ZSUS_SPEC_THICK, f"ZSUS spec {ZSUS_SPEC_THICK} mm hump"))
for thick, tag in HUMPS:
    mon = monitor(thick)
    b = mon.bounding_box()
    assert abs((b[3] - b[0]) - MON_W) < 0.01 and abs((b[4] - b[1]) - MON_H) < 0.01, b
    report(f"Upper vs monitor ({tag})", (up ^ mon).volume())
    report(f"Lower vs monitor ({tag})", (lo ^ mon).volume())
# capture: lips must sit over the monitor's back (in plan) on both long sides
for x_mon, z_back, side in (
    (-1.0, LEDGE + MON_THICK, "thick-side lip"),
    (-219.0, LEDGE + MON_THIN, "thin-side lip"),
):
    for part, nm, y in ((lo, "Lower", 100.0), (up, "Upper", 250.0)):
        probe = m3.Manifold.cube((0.4, 0.4, 3.0)).translate((x_mon - 0.2, y - 0.2, z_back + 0.05))
        hit = (part ^ probe).volume() > 0
        print(f"{'OK  ' if hit else 'FAIL'} {nm} {side} over the monitor back at y={y:.0f}")
        if not hit:
            fails.append(f"{nm} {side}")


# right latch (thin side): the Upper's snap arm hangs into the Lower's notch. Lifted off its seat along +y (the halves
# parting), the Upper travels LATCH_CATCH (+/- 0.2) before the barb meets the ledge, so the hook still holds with the
# seam that far open; just past that, the barb bears on the ledge across >= 0.6 mm in x. A square hook bears across
# all 0.8 mm of it; v21.2's 40-degree ramp met it at a corner after 0.65 mm and cammed the arm out.
lo_latch = lo ^ m3.Manifold.cube((9.0, 16.0, 9.0)).translate((-233.5, 165.0, 4.5))  # print frame x = -X


def latch_hit(t):
    return up.translate((0.0, t, 0.0)) ^ lo_latch


stop = next((t for t in np.arange(0.05, 3.0, 0.05) if latch_hit(float(t)).volume() > 1e-3), None)
bb = latch_hit(float(stop) + 0.2).bounding_box() if stop is not None else (0.0,) * 6
bear = bb[3] - bb[0]
for what, ok, got in (
    (
        f"latch catches after {LATCH_CATCH:g} mm of parting",
        stop is not None and abs(stop - LATCH_CATCH) <= 0.2,
        "none" if stop is None else f"{stop:.2f} mm",
    ),
    ("latch hook bears >= 0.6 mm on the ledge", bear >= 0.6, f"{bear:.2f} mm"),
):
    print(f"{'OK  ' if ok else 'FAIL'} {what}: {got}")
    if not ok:
        fails.append(what)


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


def open_run(vals, hit, centre):
    """The contiguous run around `centre` where the first hit is behind the glass plane (the screen opening).
    Only that run: the rim round's flanks also first-hit behind z = LEDGE, and must not count as open."""
    is_open = hit > LEDGE
    i = int(np.argmin(np.abs(vals - centre)))
    assert is_open[i], f"no screen opening at {centre}"
    j0 = i
    while j0 > 0 and is_open[j0 - 1]:
        j0 -= 1
    j1 = i
    while j1 + 1 < len(vals) and is_open[j1 + 1]:
        j1 += 1
    return vals[j0 : j1 + 1]


xs = np.arange(bx0 + 0.05, bx1, 0.05)
open_x = open_run(xs, first_z(both, [(x, 150.0) for x in xs]), -118.0)
ys = np.arange(150.0, by1, 0.05)
open_y = open_run(ys, first_z(both, [(-118.0, y) for y in ys]), 160.0)
borders = {
    "front-view left": bx1 - open_x.max(),
    "front-view right": open_x.min() - bx0,
    "top": by1 - open_y.max(),
}
ok = max(borders.values()) - min(borders.values()) <= 0.25 and min(borders.values()) >= 15.0
print(
    f"{'OK  ' if ok else 'FAIL'} borders "
    + ", ".join(f"{k} {v:.2f}" for k, v in borders.items())
    + " mm (equal within 0.25, each >= 15)"
)
if not ok:
    fails.append("borders")

# the reveal: black glass left showing between the image and the bezel's edge where it meets the glass, measured on
# the meshes at every side against the image as photographed (CAD/monitor_spec.py IMAGE), the same on all four
# (fails on v21.1.0: 0.80 left, 4.40 right, 1.70 bottom, 2.00 top against the 2026-11-19 photo)
from monitor_spec import IMAGE, REVEAL  # noqa: E402

ys_b = np.arange(by0 + 0.05, 150.0, 0.05)
open_b = open_run(ys_b, first_z(both, [(-118.0, y) for y in ys_b]), 140.0)
reveal = {
    "left": IMAGE[0] - -open_x.max(),
    "right": -open_x.min() - IMAGE[1],
    "bottom": IMAGE[2] - open_b.min(),
    "top": open_y.max() - IMAGE[3],
}
ok = all(abs(v - REVEAL) <= 0.05 for v in reveal.values())
print(
    f"{'OK  ' if ok else 'FAIL'} reveal round the image "
    + ", ".join(f"{k} {v:.2f}" for k, v in reveal.items())
    + f" mm (each {REVEAL} within 0.05)"
)
if not ok:
    fails.append("reveal")


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
front = {s: side_grooves(4.5, o, d) for s, o, d in (("left", bx1, -1.0), ("right", bx0, 1.0))}
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

# snap-in emblem (CAD/build_emblem.py, window from CAD/chin_spec.py): seated it touches nothing, its face is
# flush, pushed back 0.15 mm it lands on the seat, pushed forward 0.25 mm its barbs catch the plate.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chin_spec import EMBLEM_CX, EMBLEM_PLACE, LED_SLIT  # noqa: E402

# seated as printed: chin_spec.EMBLEM_PLACE, a rigid motion (a mirror would model a part nobody can print)
place = np.array(EMBLEM_PLACE, float)
assert np.linalg.det(place[:, :3]) > 0.999, "EMBLEM_PLACE must move the printed tile, not mirror it"
em = load("Part_B_Emblem").transform(place)
eb = em.bounding_box()
report("Emblem vs Lower (seated)", (em ^ lo).volume())
report(f"Emblem vs monitor ({ZSUS_SPEC_THICK} mm hump)", (em ^ monitor(ZSUS_SPEC_THICK)).volume())
for dz, what in ((0.15, "pushed back 0.15 mm lands on the seat"), (-0.25, "pulled forward 0.25 mm: barbs catch")):
    hit = (em.translate((0, 0, dz)) ^ lo).volume()
    ok = hit > 0.05
    print(f"{'OK  ' if ok else 'FAIL'} emblem {what} (overlap {hit:.3f} mm3)")
    if not ok:
        fails.append(f"emblem {what}")
ok = abs(eb[2]) <= 0.1
print(f"{'OK  ' if ok else 'FAIL'} emblem face flush with the chin: front at z = {eb[2]:+.2f} mm")
if not ok:
    fails.append("emblem face flush")
# placement, measured on the bezel: the emblem window and the slit light sit on the visible chin's centre line,
# and the window's visible edge (pocket + front chamfer) lines up with the screen opening's left edge
ys_lo = np.arange(by0 + 0.05, 150.0, 0.05)
FRONT_RIM = 5.0  # clear of the rim round, whose flanks also lie below the face
chin_top = open_run(ys_lo, first_z(both, [(-118.0, y) for y in ys_lo]), 140.0).min()
chin_cy = (by0 + chin_top) / 2
xs_e = np.arange(-(EMBLEM_CX + 12), -(EMBLEM_CX - 12), 0.02)
win = xs_e[first_z(lo_tm, [(x, chin_cy) for x in xs_e]) > 0.05]  # face lower than flush: chamfer + pocket
win_left = -win.max() if len(win) else np.inf  # front-view X of the window's visible left edge (none: FAIL)
win_x = (win.min() + win.max()) / 2 if len(win) else -EMBLEM_CX
win_y = ys_lo[(first_z(lo_tm, [(win_x, y) for y in ys_lo]) > 0.05) & (ys_lo > by0 + FRONT_RIM) & (ys_lo < 0)]
slit_y = ys_lo[
    (first_z(lo_tm, [(-(LED_SLIT[0] + LED_SLIT[1]) / 2, y) for y in ys_lo]) > 0.05)
    & (ys_lo > by0 + FRONT_RIM)
    & (ys_lo < 0)
]
checks = (
    ("emblem window on the chin centre line", (win_y.min() + win_y.max()) / 2 - chin_cy if len(win_y) else np.inf),
    ("slit light on the chin centre line", (slit_y.min() + slit_y.max()) / 2 - chin_cy if len(slit_y) else np.inf),
    ("emblem edge on the opening edge", win_left - -open_x.max()),  # front-view X = -x
)
for what, err in checks:
    ok = abs(err) <= 0.1
    print(f"{'OK  ' if ok else 'FAIL'} {what}: off by {err:+.2f} mm (chin {by0:.1f}..{chin_top:.1f})")
    if not ok:
        fails.append(what)
if fails:
    sys.exit(f"fit check failed: {fails}")
print("fit check passed")
