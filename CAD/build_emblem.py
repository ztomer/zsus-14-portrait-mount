"""
Snap-in chin emblem (v21) -- headless generator (Python + manifold3d). Writes STLs/Part_B_Emblem.stl.

The tile fills the stepped window CAD/chin_spec.py defines (and the bezel generator cuts): its cap sits in the
18.4 mm pocket with the face flush, a 45-deg shoulder lands on the window's 45-deg seat, and two cantilever arms
reach forward from a rear bridge so their barbs catch behind the 3 mm chin plate. It goes in from the front
with a push; it comes out by pressing the bridge forward from behind through the open control bay (the catch
faces lean 35 deg, so the plate cams the arms in). Swap emblems without taking the bezel off.

Tile frame: u right, v up (front view), w from the face (w = 0) toward the back. The STL is written face-up
(the bridge on the bed, w = TILE_DEPTH at z = 0) so a relief on the face prints as top surfaces.

  python3 CAD/build_emblem.py                 blank face (the shipped default) -> STLs/Part_B_Emblem.stl
  python3 CAD/build_emblem.py --relief R.stl  emblem face: a panel inside a RIM-wide border is recessed RELIEF_D,
                                              and R (a relief already in the tile frame, high points at w = 0) is
                                              clipped to that panel and added back -> Part_B_Emblem_<R>.stl next
                                              to R, never into STLs/ (third-party art stays out of the repo)
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


def tile(relief=None):
    bridge = m3.Manifold.cube((2 * PASS, 2 * PASS, BRIDGE_T)).translate((-PASS, -PASS, BRIDGE_W))
    t = body() + bridge + arm(1) + arm(-1)
    if relief is not None:
        p = CAP - RIM
        panel = m3.Manifold.cube((2 * p, 2 * p, RELIEF_D + 0.1)).translate((-p, -p, -0.1))
        t = (t - panel) + (relief ^ panel.trim_by_plane((0, 0, 1), 0.0))
    return t


# ---------------------------------------------------------------- gates (analytic, then on the solid)
def gates(t):
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
    gate(abs(b[2]) < 1e-6 and abs(b[5] - TILE_DEPTH) < 1e-6, f"tile depth w 0..{b[5]:.2f} = TILE_DEPTH")
    arms = arm(1) + arm(-1)
    free = arms - m3.Manifold.cube((20, 20, 1.0)).translate((-10, -10, BRIDGE_W - 1.0))
    core = body()
    g = free.min_gap(core, 2.0)
    gate(g >= 0.3, f"arms free of the body above the root: min gap {g:.2f} mm (>= 0.3)")
    return fails


def write_stl(man, path):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3].astype(np.float32)
    f = np.asarray(mesh.tri_verts, np.uint32)
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, tri
    with open(path, "wb") as fh:
        fh.write(b"ZSUS v21 Part_B_Emblem".ljust(80, b" "))
        fh.write(np.uint32(len(f)).tobytes())
        fh.write(rec.tobytes())


def main(argv):
    relief = None
    if "--relief" in argv:
        import trimesh

        rm = trimesh.load(argv[argv.index("--relief") + 1])
        relief = m3.Manifold(
            m3.Mesh(vert_properties=np.asarray(rm.vertices, np.float32), tri_verts=np.asarray(rm.faces, np.uint32))
        )
    t = tile(relief)
    fails = gates(t)
    if fails:
        sys.exit(f"emblem gate failed: {fails}")
    # face-up print orientation: w = TILE_DEPTH on the bed
    printed = t.transform(np.array([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, TILE_DEPTH]], float))
    out = os.path.join(ROOT, "STLs", "Part_B_Emblem.stl")
    if "--relief" in argv:
        src = argv[argv.index("--relief") + 1]
        out = os.path.join(
            os.path.dirname(os.path.abspath(src)), f"Part_B_Emblem_{os.path.splitext(os.path.basename(src))[0]}.stl"
        )
    write_stl(printed, out)
    b = printed.bounding_box()
    print(f"wrote {os.path.relpath(out, ROOT)}  {b[3] - b[0]:.2f} x {b[4] - b[1]:.2f} x {b[5] - b[2]:.2f} mm, "
          f"{printed.volume() / 1000:.2f} cm3")  # fmt: skip


if __name__ == "__main__":
    main(sys.argv[1:])
