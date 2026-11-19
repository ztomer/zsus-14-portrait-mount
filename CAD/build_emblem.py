"""
Snap-in chin emblem (v21) -- headless generator (Python + manifold3d). Writes STLs/Part_B_Emblem.stl.

The tile fills the stepped window CAD/chin_spec.py defines (and the bezel generator cuts): its cap sits in the
18.4 mm pocket with the face flush, a 45-deg shoulder lands on the window's 45-deg seat, and two cantilever arms
reach forward from a rear bridge so their barbs catch behind the 3 mm chin plate. It goes in from the front
with a push; it comes out by pressing the bridge forward from behind through the open control bay (the catch
faces lean 35 deg, so the plate cams the arms in). Swap emblems without taking the bezel off.

Tile frame (u, v, w), right-handed: w runs from the face (w = 0) into the part, v is up, and so a viewer of the
face sees u to their LEFT (front-view X = EMBLEM_CX - u, the bezel's own x = -X mirror; CAD/chin_spec.py). The STL
is written face-up (the bridge on the bed, w = TILE_DEPTH at z = 0) so a relief on the face prints as top surfaces.

  python3 CAD/build_emblem.py                 blank face (the shipped default) -> STLs/Part_B_Emblem.stl
  python3 CAD/build_emblem.py --relief R.stl  emblem face: a panel inside a RIM-wide border is recessed RELIEF_D,
                                              and R (a relief already in the tile frame, high points at w = 0) is
                                              clipped to that panel and added back -> Part_B_Emblem_<R>.stl next
                                              to R (art under a personal-use licence stays out of the repo); an
                                              onlay relief (in front of the face, w < 0) is added as it is
  ... --out STLs/Part_B_Emblem_X.stl          write there instead (art the repo may carry, e.g. CC BY)
"""

import math
import os
import sys

import manifold3d as m3
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from chin_spec import CHIN_PLATE, EMBLEM_HOLE, EMBLEM_POCKET, EMBLEM_WIN, TILE_DEPTH  # noqa: E402
from stl_io import write_stl  # noqa: E402

# ---------------------------------------------------------------- design parameters (mm)
CAP = EMBLEM_WIN / 2 - 0.2  # cap half-width: 0.2 mm per side in the pocket
SEAT = EMBLEM_WIN / 2 + EMBLEM_POCKET - 0.05  # shoulder line u + w = SEAT, 0.05 inside the window's seat
PASS = EMBLEM_HOLE / 2 - 0.15  # everything that passes the hole: 0.15 mm per side
SPINE = 6.4  # spine half-width in u, between the arms
ARM_T, ARM_W = 0.8, 9.0  # arm thickness (u) and width (v)
ARM_IN = PASS - ARM_T  # arm inner face
TIP_W = CHIN_PLATE  # arm tip / catch-face start, right behind the plate's rear face
TIP_CH = 0.5  # 45-deg chamfer on the tip's inner corner, parallel to the shoulder above it
BARB = 0.5  # barb reach past the arm's outer face
CATCH_DEG = 35.0  # catch-face lean from the plate plane (0 = locking, 45 = as easy out as in)
BRIDGE_W, BRIDGE_T = 9.5, TILE_DEPTH - 9.5  # bridge front face and thickness
RIM, RELIEF_D = 0.8, 1.2  # emblem face: flush border, and the depth the panel inside it is recessed
assert BRIDGE_T >= 1.2, BRIDGE_T


def ccw(poly):
    area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1], strict=True))
    return poly if area > 0 else poly[::-1]


def prism_uw(poly, v0, v1):
    """Extrude a (u, w) polygon along v from v0 to v1 (a rotation: (u, w, e) -> (u, e + v0, w))."""
    sec = m3.CrossSection([ccw(poly)])
    solid = m3.Manifold.extrude(sec, v1 - v0)  # (u, w, e)
    return solid.transform(np.array([[1, 0, 0, 0], [0, 0, 1, v0], [0, 1, 0, 0]], float))


def prism_vw(poly, u0, u1):
    """Extrude a (v, w) polygon along u from u0 to u1 (a rotation: (v, w, e) -> (e + u0, v, w))."""
    sec = m3.CrossSection([ccw(poly)])
    solid = m3.Manifold.extrude(sec, u1 - u0)  # (v, w, e)
    return solid.transform(np.array([[0, 0, 1, u0], [1, 0, 0, 0], [0, 1, 0, 0]], float))


def body():
    """Cap + 45-deg shoulder + spine, as the intersection of its u-profile and v-profile."""
    w_cap = SEAT - CAP  # where the shoulder leaves the cap
    w_sp = SEAT - SPINE  # where it reaches the spine (u)
    w_pv = SEAT - PASS  # where it reaches the pass width (v)
    prof_u = [(-CAP, 0), (CAP, 0), (CAP, w_cap), (SPINE, w_sp), (SPINE, BRIDGE_W + 0.01),
              (-SPINE, BRIDGE_W + 0.01), (-SPINE, w_sp), (-CAP, w_cap)]  # fmt: skip
    prof_v = [(-CAP, 0), (CAP, 0), (CAP, w_cap), (PASS, w_pv), (PASS, BRIDGE_W + 0.01),
              (-PASS, BRIDGE_W + 0.01), (-PASS, w_pv), (-CAP, w_cap)]  # fmt: skip
    return prism_uw(prof_u, -CAP, CAP) ^ prism_vw(prof_v, -CAP, CAP)


def arm(sign):
    """One cantilever: rooted in the bridge, tip at TIP_W with a barb on its outer face."""
    s = sign
    rise = BARB * math.tan(math.radians(CATCH_DEG))
    pts = [
        (ARM_IN, BRIDGE_W + 0.01),
        (ARM_IN, TIP_W + TIP_CH),
        (ARM_IN + TIP_CH, TIP_W),
        (PASS, TIP_W),
        (PASS + BARB, TIP_W + rise),  # catch face, leaning CATCH_DEG from the plate plane
        (PASS + BARB, TIP_W + rise + 0.15),
        (PASS, TIP_W + rise + 0.15 + BARB),  # 45-deg lead-in ramp
        (PASS, BRIDGE_W + 0.01),
    ]
    return prism_uw([(s * u, w) for u, w in pts], -ARM_W / 2, ARM_W / 2)


def is_onlay(relief):
    """An onlay relief stands in front of the face (w < 0); an inlay one lies in the recessed panel (w >= 0)."""
    return relief.bounding_box()[2] < -0.01


PRINTED = np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, TILE_DEPTH]], float)  # face up, bridge on the bed


def seated(t):
    """The tile as it sits in the chin, in the Lower's print frame: printed, then chin_spec.EMBLEM_PLACE."""
    from chin_spec import EMBLEM_PLACE

    place = np.vstack([np.array(EMBLEM_PLACE, float), [0, 0, 0, 1]])
    assert np.linalg.det(place[:3, :3]) > 0.999, "a printed part is moved, never mirrored"
    return t.transform((place @ np.vstack([PRINTED, [0, 0, 0, 1]]))[:3])


def seat_gates(t, relief, gate):
    """Against the real bezel (STLs/Part_B_Lower.stl): it touches nothing seated, a push back meets a stop, and
    an onlay rests on flat chin face all round (0.5 mm of face around its footprint, clear of the window)."""
    lower_stl = os.path.join(ROOT, "STLs", "Part_B_Lower.stl")
    if not os.path.exists(lower_stl):
        gate(False, "seated gates need STLs/Part_B_Lower.stl (build the bezel first)")
        return
    import trimesh

    lm = trimesh.load(lower_stl)
    lower = m3.Manifold(
        m3.Mesh(vert_properties=np.asarray(lm.vertices, np.float32), tri_verts=np.asarray(lm.faces, np.uint32))
    )
    s = seated(t)
    v = (s ^ lower).volume()
    gate(v <= 0.01, f"seated in the Lower: overlap {v:.3f} mm3 (none)")
    v = (s.translate((0, 0, 0.1)) ^ lower).volume()
    gate(v > 0.01, f"pushed back 0.1 mm it meets a stop (overlap {v:.3f} mm3)")
    if relief is None or not is_onlay(relief):
        return
    win = EMBLEM_WIN / 2 + 0.3  # pocket + front chamfer
    foot = relief.project().offset(0.5, m3.JoinType.Round) - m3.CrossSection.square((2 * win, 2 * win)).translate(
        (-win, -win)
    )
    probe = m3.Manifold.extrude(foot, 0.05)  # tile frame, w 0..0.05: the chin face skin under the onlay
    want = foot.area() * 0.05
    got = (seated(probe) ^ lower).volume()
    gate(
        got >= 0.98 * want,
        f"onlay rests on flat chin face all round: {got / want * 100:.1f} % of its footprint + 0.5 mm",
    )


def tile(relief=None):
    bridge = m3.Manifold.cube((2 * PASS, 2 * PASS, BRIDGE_T)).translate((-PASS, -PASS, BRIDGE_W))
    t = body() + bridge + arm(1) + arm(-1)
    if relief is not None and is_onlay(relief):  # proud of the face, possibly past the tile: add it as it is
        return t + relief
    if relief is not None:
        p = CAP - RIM
        panel = m3.Manifold.cube((2 * p, 2 * p, RELIEF_D + 0.1)).translate((-p, -p, -0.1))
        clip = m3.Manifold.cube((2 * p, 2 * p, RELIEF_D + 1.0)).translate((-p, -p, 0.0))  # deep: overlaps the body
        t = (t - panel) + (relief ^ clip)
    return t


# ---------------------------------------------------------------- gates (analytic, then on the solid)
def gates(t, relief=None):
    fails = []

    def gate(ok, msg):
        print(f"{'OK  ' if ok else 'FAIL'} {msg}")
        if not ok:
            fails.append(msg)

    # deflection to pass the hole: the barb has to come in to the hole edge less 0.05
    delta = PASS + BARB - (EMBLEM_HOLE / 2 - 0.05)
    a = BRIDGE_W - (TIP_W + 0.2)  # root to the barb's load point
    strain = 3 * ARM_T * delta / (2 * a * a)
    gate(strain <= 0.02, f"arm strain {strain * 100:.2f} % at {delta:.2f} mm deflection (<= 2 % PLA)")
    grip = PASS + BARB - EMBLEM_HOLE / 2
    gate(grip >= 0.3, f"barb engagement behind the plate {grip:.2f} mm (>= 0.3)")
    # print gap: tip chamfer line u + w = ARM_IN + TIP_CH + TIP_W vs shoulder line u + w = SEAT
    gap = (ARM_IN + TIP_CH + TIP_W - SEAT) / math.sqrt(2)
    gate(gap >= 0.3, f"arm tip under the shoulder: {gap:.2f} mm gap as printed (>= 0.3, no fusing)")
    gate(gap - delta / math.sqrt(2) > 0.0, f"deflected arm tip clears the shoulder ({gap - delta / math.sqrt(2):.2f})")
    gate(ARM_IN - delta - SPINE >= 0.1, f"deflected arm clears the spine ({ARM_IN - delta - SPINE:.2f} mm)")
    # on the solid: one piece, sized to the window, arm separate from the body except at the root
    gate(len(t.decompose()) == 1 and t.status() == m3.Error.NoError, "tile is one manifold solid")
    b = t.bounding_box()
    front = -RELIEF_D - 0.01 if relief is not None and is_onlay(relief) else -1e-6
    gate(
        front <= b[2] < 1e-6 and abs(b[5] - TILE_DEPTH) < 1e-6,
        f"tile depth w {b[2]:.2f}..{b[5]:.2f} (back = TILE_DEPTH)",
    )
    arms = arm(1) + arm(-1)
    free = arms - m3.Manifold.cube((20, 20, 1.0)).translate((-10, -10, BRIDGE_W - 1.0))
    core = body()
    g = free.min_gap(core, 2.0)
    gate(g >= 0.3, f"arms free of the body above the root: min gap {g:.2f} mm (>= 0.3)")
    seat_gates(t, relief, gate)
    return fails


def main(argv):
    relief = None
    if "--relief" in argv:
        import trimesh

        rm = trimesh.load(argv[argv.index("--relief") + 1])
        relief = m3.Manifold(
            m3.Mesh(vert_properties=np.asarray(rm.vertices, np.float32), tri_verts=np.asarray(rm.faces, np.uint32))
        )
    t = tile(relief)
    fails = gates(t, relief)
    if fails:
        sys.exit(f"emblem gate failed: {fails}")
    # face-up print orientation: w = TILE_DEPTH on the bed
    printed = t.transform(PRINTED)
    out = os.path.join(ROOT, "STLs", "Part_B_Emblem.stl")
    if "--out" in argv:
        out = os.path.join(ROOT, argv[argv.index("--out") + 1])
    elif "--relief" in argv:
        src = argv[argv.index("--relief") + 1]
        out = os.path.join(
            os.path.dirname(os.path.abspath(src)), f"Part_B_Emblem_{os.path.splitext(os.path.basename(src))[0]}.stl"
        )
    write_stl(printed, out, header="ZSUS v21 Part_B_Emblem")
    b = printed.bounding_box()
    print(f"wrote {os.path.relpath(out, ROOT)}  {b[3] - b[0]:.2f} x {b[4] - b[1]:.2f} x {b[5] - b[2]:.2f} mm, "
          f"{printed.volume() / 1000:.2f} cm3")  # fmt: skip


if __name__ == "__main__":
    main(sys.argv[1:])
