"""
ZSUS 14" Portrait Glue-On Ball Socket (v21) -- headless generator (Python + manifold3d).

Generates STLs/Part_A_Test.stl and STLs/Part_A_Mount.stl from ONE collet-boss definition,
so the calibration coupon always tests exactly the socket the mount carries.

Why v21 exists (v20 defect, measured on the v20 STL):
  * The v20 cup was a sphere CLIPPED by a flat floor 0.5 mm above the boss base. A 17.0 mm
    ball cannot reach the design centre (z = base + 6.2); it sits on the floor with its centre
    at base + 9.0, i.e. its equator level with the cup rim (base + 8.95). Nothing wrapped over
    the ball, the 8 micro-ribs pressed BELOW the equator, so tightening the collar squeezed the
    ball up and out ("pops off").
  * v21: an unclipped spherical seat (the ball really sits at the design centre) and eight leaves
    that rise 5.6 mm above the ball centre and close to a 16.4 mm mouth, so every leaf contacts
    the ball ABOVE its equator. Collar pressure on the leaf crown now drives the ball INTO the
    seat. The leaf crown has an external cone for the collar's top aperture to ride on.
  * Leaf strain (2026-11-18): the first print had six leaves and a 15.6 mm mouth, and in PLA they snapped as
    the ball went in (~3.1 % bending strain across the layer lines). Eight leaves, a 16.4 mm mouth and deeper
    slots bring it to ~1.0 %; check_leaf_strain() gates <= 1.5 %.
  * Collar relief (2026-11-18): the collar's top aperture (~19.6 mm, from the owner's photos) meets
    the crown 9.7 mm above the boss base, and the collar is 9.8 mm tall, so on a flat pedestal it
    bottomed out before it squeezed anything. The area under the collar is cut 3 mm lower and the
    thread runs down into it; check_collar_travel() gates >= 1.5 mm travel for 19.2..19.95 mm apertures.

Run:   python3 CAD/build_part_a_v21.py            (needs: pip install manifold3d trimesh numpy)
The Part_A_Mount base (VHB pad, step index, pedestal) has no surviving parametric source; it is
read from CAD/assets/Part_A_Mount_base_v20.stl (the v20 mount with its boss removed, made once by
`--extract-base <v20 Part_A_Mount.stl>`).
"""

import math
import os
import sys

import manifold3d as m3
import numpy as np
import trimesh

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stl_io import write_stl

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BASE_ASSET = os.path.join(HERE, "assets", "Part_A_Mount_base_v20.stl")

# ---------------------------------------------------------------- design parameters (mm)
SEG = 96  # circular segments
BALL_D = 17.0  # Polbecky ball stud
NECK_D = 9.5  # Polbecky ball neck
CUP_R = 8.60  # spherical seat radius (0.10 mm radial clearance on the ball)
BALL_C = 6.2  # ball centre above boss base (unchanged from v20)
MOUTH_R = 8.20  # leaf mouth radius: 16.4 mm mouth on a 17.0 ball = 0.3 mm snap per leaf (v21 first print: 0.7)
LEAD_IN = 0.5  # 45-deg lead-in chamfer on the mouth
# M22 x 2.0 external thread (identical to v20, which the collar is known to accept)
PITCH = 2.0
R_MAJOR = 21.95 / 2.0
R_MINOR = 19.95 / 2.0
ROOT_HALF = 0.15  # half-width of the flat thread root
FLANK_TAN = math.tan(math.radians(30.0))  # 60-deg thread
# Collar relief: everything around the boss is cut RELIEF below the boss base out to RELIEF_R, so the collar
# (9.8 mm tall, ~19.6 mm top aperture measured from photos) reaches the crown cone with travel to spare instead
# of bottoming on the pedestal first. Owner photos 2026-11-18; gated by check_collar_travel().
RELIEF = 3.0
RELIEF_R = 21.5  # 41.3 mm collar wing span + 0.85 mm
Z_THREAD_BOT = -RELIEF - 0.6  # thread runs down into the relief floor
Z_CREST_END = 8.3  # full crest until here, 45-deg runout to the minor radius at Z_THREAD_TOP
Z_THREAD_TOP = 9.3
# leaf crown above the thread (collar lip rides this cone)
Z_TIP = 11.8
R_TIP = 8.95
# leaves
# The first PLA print snapped its leaves pushing the ball in (owner, 2026-11-18): 6 leaves, 0.7 mm snap, slots to
# z 1.3 bent them to ~3.1 % strain at the thin band under the equator, across the layer lines (the leaves stand
# vertical in the print), where PLA tears near 1.5 %. 8 leaves, a 0.3 mm snap and slots 2.3 mm deeper: ~1.0 %.
# check_leaf_strain() gates it.
N_SLOTS = 8
SLOT_W = 1.4
Z_SLOT = -1.0  # slot root height (keyhole centre); the cup bottom is at z -2.4, the relief floor at -3.0
LEAF_STRAIN_MAX = 1.5  # % bending strain across PLA layer lines, the leaves' worst direction
KEYHOLE_R = 1.1
PLUG_R = 15.5  # v20 boss region stripped by --extract-base
# Polbecky collar (Monitor_Dimensions_and_Ports.md section 4; aperture from the owner's photos, +/-0.4 mm)
COLLAR_H = 9.8
COLLAR_R_IN = 22.3 / 2.0  # internal thread major
COLLAR_R_OUT = 41.3 / 2.0  # wing tips
COLLAR_APERTURES = (
    19.2,
    19.6,
    19.95,
)  # top-aperture diameters the socket must work with
MIN_TRAVEL = 1.5  # collar travel left after it first touches the crown
SLOT_ANG0 = 90.0 / N_SLOTS  # first slot angle (deg); leaf centres sit half a pitch further
LEAF_ANGS = [SLOT_ANG0 + 180.0 / N_SLOTS + k * 360.0 / N_SLOTS for k in range(N_SLOTS)]


def _mesh_to_manifold(tm):
    mesh = m3.Mesh(
        vert_properties=np.asarray(tm.vertices, dtype=np.float32),
        tri_verts=np.asarray(tm.faces, dtype=np.uint32),
    )
    man = m3.Manifold(mesh)
    if man.status() != m3.Error.NoError:
        raise SystemExit(f"input mesh is not a manifold: {man.status()}")
    return man


def _manifold_to_trimesh(man):
    mm = man.to_mesh()
    return trimesh.Trimesh(
        vertices=np.asarray(mm.vert_properties)[:, :3],
        faces=np.asarray(mm.tri_verts),
        process=False,
    )


def revolve(profile_rz):
    return m3.Manifold.revolve(m3.CrossSection([profile_rz]), circular_segments=SEG)


def thread_solid(z0, z1):
    """Right-hand single-start M22x2 thread as a twisted extrusion of its axial-slice outline."""
    n = 144  # 2.5 deg steps
    pts = []
    for i in range(n):
        th = 2 * math.pi * i / n
        u = (-PITCH * th / (2 * math.pi)) % PITCH  # axial offset from groove centre at z = 0
        u = min(u, PITCH - u)
        r = R_MINOR if u <= ROOT_HALF else min(R_MAJOR, R_MINOR + (u - ROOT_HALF) / FLANK_TAN)
        pts.append((r * math.cos(th), r * math.sin(th)))
    h = z1 - z0
    turns = h / PITCH
    # a groove at angle th sits at height z = PITCH*th/2pi, so the pattern turns +360 deg per pitch (CCW from above)
    sol = m3.Manifold.extrude(
        m3.CrossSection([pts]),
        h,
        n_divisions=int(turns * 48),
        twist_degrees=360.0 * turns,
    )
    # re-phase so the groove passes theta = 0 at z = 0 regardless of z0
    return sol.rotate((0, 0, 360.0 * z0 / PITCH)).translate((0, 0, z0))


def collet_boss():
    """Outer solid of the boss (thread + crown), local frame: boss base at z = 0, axis = z."""
    env = revolve(
        [
            (0, Z_THREAD_BOT),
            (R_MAJOR + 0.5, Z_THREAD_BOT),
            (R_MAJOR + 0.5, Z_CREST_END),
            (R_MINOR, Z_THREAD_TOP),
            (0, Z_THREAD_TOP),
        ]
    )
    thr = thread_solid(Z_THREAD_BOT, Z_THREAD_TOP) ^ env
    crown = revolve(
        [
            (0, Z_THREAD_TOP - 0.01),
            (R_MINOR, Z_THREAD_TOP - 0.01),
            (R_TIP, Z_TIP),
            (0, Z_TIP),
        ]
    )
    # No separate core: the thread's slice outline is filled from the axis out, so it already holds the core. A core
    # cylinder at R_MINOR touched the thread's root along lines (two polygons of one radius, different facets), and
    # the STL came out with pinched edges once a slicer merged its vertices (CAD/check_stl_files.py).
    return thr + crown


def collet_cuts():
    """Everything removed from boss + pedestal: spherical seat, mouth, lead-in, leaf slots with keyholes."""
    seat = m3.Manifold.sphere(CUP_R, SEG).translate((0, 0, BALL_C))
    z_mouth = BALL_C + math.sqrt(CUP_R**2 - MOUTH_R**2)
    mouth = m3.Manifold.cylinder(Z_TIP + 1.0 - BALL_C, MOUTH_R, MOUTH_R, SEG).translate((0, 0, BALL_C))
    # the chamfer's 45-deg line runs on 0.5 mm into the mouth's void: a lead-in cut that STARTED on the mouth
    # cylinder shared its corner circle with it, and the STL pinched along that circle (CAD/check_stl_files.py)
    lead = revolve(
        [
            (0, Z_TIP - LEAD_IN - 0.5),
            (MOUTH_R - 0.5, Z_TIP - LEAD_IN - 0.5),
            (MOUTH_R + LEAD_IN + 1.0, Z_TIP + 1.0),
            (0, Z_TIP + 1.0),
        ]
    )
    cuts = seat + mouth + lead
    slot_len = R_MAJOR + 2.0
    for k in range(N_SLOTS):
        ang = SLOT_ANG0 + k * 360.0 / N_SLOTS  # slots between, not on, the X/Y axes
        slot = m3.Manifold.cube((slot_len, SLOT_W, Z_TIP + 1.0 - Z_SLOT)).translate((0, -SLOT_W / 2, Z_SLOT))
        key = m3.Manifold.cylinder(slot_len, KEYHOLE_R, KEYHOLE_R, 32).rotate((0, 90, 0)).translate((0, 0, Z_SLOT))
        cuts += (slot + key).rotate((0, 0, ang))
    return cuts, z_mouth


def socket_on(base, cx, cy, bz):
    """Add the v21 boss at (cx, cy, bz), clear the collar relief (radius RELIEF_R, down to bz - RELIEF)
    and cut the seat."""
    clear = m3.Manifold.cylinder(40.0, RELIEF_R, RELIEF_R, SEG).translate((cx, cy, bz - RELIEF))
    part = base - clear
    cuts, z_mouth = collet_cuts()
    part = part + collet_boss().translate((cx, cy, bz))
    return part - cuts.translate((cx, cy, bz)), z_mouth


def rounded_square(w, r, h):
    cs = m3.CrossSection.square((w - 2 * r, w - 2 * r), center=True).offset(r, m3.JoinType.Round, circular_segments=48)
    return m3.Manifold.extrude(cs, h)


TEST_BASE_H = 3.6  # coupon plate; its top is the relief floor, as on the mount
TEST_BZ = TEST_BASE_H + RELIEF  # boss base (seat bottom 2.4 below it: 4.2 mm floor under the ball)
MOUNT_AXIS = (
    28.0,
    50.0,
    9.5,
)  # on the v20 base: X 104 / Y 155 on the monitor, pedestal top


def build_test():
    base = rounded_square(26.0, 3.0, TEST_BASE_H)
    part, _ = socket_on(base, 0.0, 0.0, TEST_BZ)
    return part


def build_mount():
    if not os.path.exists(BASE_ASSET):
        raise SystemExit(f"missing {BASE_ASSET}; run with --extract-base <v20 Part_A_Mount.stl> once")
    base = _mesh_to_manifold(trimesh.load(BASE_ASSET))
    part, _ = socket_on(base, *MOUNT_AXIS)
    return part


def extract_base(v20_stl):
    """One-time: strip the v20 boss (everything inside the plateau radius above z = 7.9) from the v20 mount."""
    man = _mesh_to_manifold(trimesh.load(v20_stl))
    clear = m3.Manifold.cylinder(30.0, PLUG_R, PLUG_R, SEG).translate((28.0, 50.0, 7.9))
    base = man - clear
    os.makedirs(os.path.dirname(BASE_ASSET), exist_ok=True)
    _manifold_to_trimesh(base).export(BASE_ASSET)
    print("wrote", BASE_ASSET)


def check_seat(name, tm, cx, cy, bz):
    """The v20 failure, as a gate: a rigid 17 mm ball must FIT at the design centre (nothing closer than
    the ball radius) and be CAPTURED there (the leaves' mouth reaches back inside the ball radius above
    the equator), so collar pressure pushes it down, never out."""
    pq = trimesh.proximity.ProximityQuery(tm)
    c = np.array([[cx, cy, bz + BALL_C]])
    clearance = -pq.signed_distance(c)[0] if pq.signed_distance(c)[0] < 0 else pq.signed_distance(c)[0]
    assert BALL_D / 2 <= clearance <= CUP_R + 0.05, f"{name}: ball centre clearance {clearance:.3f}"
    # capture (parameter-free): a vertical ray rising from the equator 0.2 mm inside the ball's silhouette,
    # along a leaf centre, must hit leaf material within 6 mm (the 0.3 mm snap leaves 0.1 mm of margin).
    a = math.radians(LEAF_ANGS[0])
    rr = BALL_D / 2 - 0.2
    o = np.array([[cx + rr * math.cos(a), cy + rr * math.sin(a), bz + BALL_C]])
    locs, _, _ = tm.ray.intersects_location(o, np.array([[0.0, 0.0, 1.0]]))
    above = [hit[2] - o[0][2] for hit in locs if 0 < hit[2] - o[0][2] < 6.0]
    assert above, f"{name}: no leaf material over the ball above the equator"
    print(
        f"{'':14s} seat OK: ball fits at design centre (clearance {clearance:.3f}), leaves capture it above the equator"
    )


def check_collar_travel(name, tm, cx, cy, bz):
    """The collar must reach the crown and still have MIN_TRAVEL left before it bottoms out, for every
    plausible top aperture. Parameter-free on the mesh: the crown radius profile comes from horizontal rays
    along leaf centres, the stop is the highest material under the collar's footprint (thread bore to wings)."""
    zs = np.arange(Z_TIP + 0.2, 0.0, -0.01)
    angs = np.radians(LEAF_ANGS)  # leaf centres
    origins = np.array([[cx + 30 * math.cos(a), cy + 30 * math.sin(a), bz + z] for z in zs for a in angs])
    dirs = np.array([[-math.cos(a), -math.sin(a), 0.0] for z in zs for a in angs])
    locs, idx, _ = tm.ray.intersects_location(origins, dirs, multiple_hits=False)
    r_surf = np.zeros(len(origins))
    r_surf[idx] = np.hypot(locs[:, 0] - cx, locs[:, 1] - cy)
    r_prof = r_surf.reshape(len(zs), len(angs)).max(axis=1)
    rs = np.linspace(COLLAR_R_IN, COLLAR_R_OUT, 12)
    down = np.array(
        [[cx + r * math.cos(t), cy + r * math.sin(t), bz + 40.0] for r in rs for t in np.radians(np.arange(0, 360, 5))]
    )
    locs2, _, _ = tm.ray.intersects_location(down, np.tile([0.0, 0.0, -1.0], (len(down), 1)), multiple_hits=False)
    stop = locs2[:, 2].max() - bz
    out = []
    for ap in COLLAR_APERTURES:
        k = np.argmax(r_prof >= ap / 2.0)
        assert r_prof[k] >= ap / 2.0, f"{name}: a {ap} mm aperture never meets the crown"
        travel = (zs[k] - COLLAR_H) - stop
        assert travel >= MIN_TRAVEL, (
            f"{name}: a {ap} mm collar aperture meets the crown at +{zs[k]:.2f} with its bottom "
            f"{travel:.2f} mm above the stop (+{stop:.2f}); needs {MIN_TRAVEL}"
        )
        out.append(f"{ap}: {travel:.2f}")
    print(
        f"{'':14s} collar OK: travel left after crown contact (aperture mm: travel mm) "
        f"{', '.join(out)}; stop {stop:+.2f}"
    )


def check_leaf_strain():
    """Peak bending strain in a leaf as the ball's equator passes the mouth (each leaf pushed out by the snap,
    ball radius - MOUTH_R). The leaf is a cantilever from the keyhole up to the load near the mouth; each
    section is the annular sector between the seat and the thread core (teeth ignored), bent radially. For an
    imposed tip deflection d: strain(z) = d * arm(z) c(z) / I(z) / integral(arm^2 / I dz). A model, not a test:
    it explains the first print's break (3.1 % with 6 leaves and a 0.7 mm snap) and gates the class."""

    def r_in(z):
        s = CUP_R**2 - (z - BALL_C) ** 2
        r = math.sqrt(s) if s > 0 else 0.0
        return max(r, MOUTH_R) if z > BALL_C else r

    def r_out(z):
        return (
            R_MINOR if z <= Z_THREAD_TOP else R_MINOR + (R_TIP - R_MINOR) * (z - Z_THREAD_TOP) / (Z_TIP - Z_THREAD_TOP)
        )

    z_load = Z_TIP - LEAD_IN - 0.7  # where the ball's widest band meets the mouth
    zs = np.linspace(Z_SLOT, z_load, 200)
    inertia, reach = [], []
    for z in zs:
        ri, ro = r_in(z), r_out(z)
        half = math.pi / N_SLOTS - (SLOT_W / 2) / ((ri + ro) / 2)
        rg, tg = np.meshgrid(np.linspace(ri, ro, 50), np.linspace(-half, half, 100))
        y, da = rg * np.cos(tg), rg * ((ro - ri) / 49) * (2 * half / 99)
        yb = (y * da).sum() / da.sum()
        inertia.append(((y - yb) ** 2 * da).sum())
        reach.append(abs(y - yb).max())
    inertia, reach = np.array(inertia), np.array(reach)
    arm = z_load - zs
    d = BALL_D / 2 - MOUTH_R
    eps = d * arm * reach / inertia / np.trapezoid(arm**2 / inertia, zs) * 100
    k = int(np.argmax(eps))
    assert eps[k] <= LEAF_STRAIN_MAX, (
        f"leaf strain {eps[k]:.2f} % at z {zs[k]:.1f} snapping the ball in, "
        f"over {LEAF_STRAIN_MAX} % (PLA across layers)"
    )
    print(
        f"{'':14s} leaves OK: {N_SLOTS} leaves, {d:.2f} mm snap per leaf, "
        f"peak strain {eps[k]:.2f} % at z {zs[k]:.1f} "
        f"(<= {LEAF_STRAIN_MAX} %)"
    )


def check(name, man):
    tm = _manifold_to_trimesh(man)
    assert man.status() == m3.Error.NoError, (name, man.status())
    assert tm.is_watertight and tm.is_winding_consistent and tm.volume > 0, name
    assert len(man.decompose()) == 1, f"{name}: {len(man.decompose())} shells"
    print(f"{name:14s} {tm.extents.round(2)} mm  vol {tm.volume / 1000:.2f} cm3  genus {man.genus()}  watertight")
    return tm


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--extract-base":
        extract_base(sys.argv[2])
        sys.exit(0)
    out = os.path.join(ROOT, "STLs")
    os.makedirs(out, exist_ok=True)
    for name, fn, axis in (
        ("Part_A_Test", build_test, (0.0, 0.0, TEST_BZ)),
        ("Part_A_Mount", build_mount, MOUNT_AXIS),
    ):
        man = fn()
        tm = check(name, man)
        check_seat(name, tm, *axis)
        check_collar_travel(name, tm, *axis)
        check_leaf_strain()
        write_stl(man, os.path.join(out, name + ".stl"), header=f"ZSUS v21 {name}")
    z_mouth = BALL_C + math.sqrt(CUP_R**2 - MOUTH_R**2)
    wrap = math.degrees(math.asin((z_mouth - BALL_C) / CUP_R))
    print(
        f"seat: ball centre z=+{BALL_C} above boss base; leaves wrap to +{z_mouth - BALL_C:.2f} mm above the "
        f"equator ({wrap:.0f} deg latitude), mouth {2 * MOUTH_R:.1f} mm on a {BALL_D} mm ball; crown tip +{Z_TIP}"
    )
