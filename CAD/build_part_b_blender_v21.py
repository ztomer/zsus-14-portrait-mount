"""
ZSUS 14" Portrait Apple "Snow White" Open-Back Bezel (v21) -- headless Blender generator.

Run:  blender -b --factory-startup -P CAD/build_part_b_blender_v21.py
Writes STLs/Part_B_{Upper,Lower,Badge,LED,FitGauge}.stl and CAD/Part_B_SnowWhite_Bezel_v21.blend.

v21 changes against v20 (all measured on the v20 STLs):
  * Booleans use Blender's MANIFOLD solver and every step is checked: v20's FLOAT solver silently
    dropped the thick-side rear lip and left the thin-side lip, bottom-right lip, snap arm/barb and
    the insert ribs as loose overlapping shells (non-manifold, Upper inside-out).
  * The Upper/Lower split is a boolean with a half-space box (v20: bisect + hole fill).
  * Fit is parametric (see FIT_*): sliding channels get 0.5 mm per side instead of 0.3 mm, the
    thick-side channel is sized so the ZSUS spec thickness (14.0 mm) still slides in, and the
    frame is 18.6 mm (v20 18.0) so the thick-side lip keeps 1.5 mm of material.
  * The left lap tongue / pocket stop at the pocket wall (v20 protruded 0.2 mm into the monitor edge),
    and the right snap anchor starts at the pocket wall.
  * The LED window gets a rear counterbore so the LED plug sits flush with the chin face
    (v20: an 18 mm-deep 2 mm tunnel; the 3 mm plug ended up 14 mm below the surface).
  * Adds Part_B_FitGauge: a 15 mm slice of the Lower's two side channels to test-slide on the
    monitor before committing ~300 g of filament.
"""

import math
import os
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chin_spec import CHIN_PLATE, EMBLEM_CX, EMBLEM_CY, EMBLEM_HOLE, EMBLEM_POCKET, EMBLEM_WIN, LED_BORE, LED_SLIT
from partb_accessories import build_chin_inserts, build_fit_gauge
from partb_mesh import (
    apply_bool,
    bm_frustum_rect,
    bm_prism_xy,
    bm_prism_yz,
    bm_profiled_prism,
    bm_rounded_prism,
    duplicate,
    make_obj_from_bm,
    mesh_report,
    signed_volume,
    write_stl,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Calibration seam: PARTB_OUT writes the STLs elsewhere, PARTB_FIT_Z overrides the channel play, so the
# fit check can be shown to FAIL on v20's 0.3 mm play (see CAD/check_part_b_fit.py).
OUT = os.environ.get("PARTB_OUT", ROOT)

# ---------------------------------------------------------------- monitor + fit (mm)
# Monitor (Monitor_Dimensions_and_Ports.md, portrait, chin bezel left, front view; ZSUS spec 310 x 220 x 14)
from bezel_spec import BEVEL_FACE, BEVEL_IN, FX0, FX1, FY0, FY1, MICRO, OPENING, grow  # noqa: E402  (the front)
from monitor_spec import FIT_Z as FIT_Z_NOMINAL  # noqa: E402
from monitor_spec import LEDGE, MON_H, MON_THICK, MON_THIN, MON_W  # noqa: E402  (one source: CAD/monitor_spec.py)

H = 18.6  # frame height (v20: 18.0)
FIT_X = 0.5  # per side, along the two long sliding channels
FIT_Y = 0.3  # per end (monitor does not slide on these faces)
FIT_Z = float(os.environ.get("PARTB_FIT_Z", FIT_Z_NOMINAL))  # glass-to-lip channel play
LIP_T = 2.0  # thin-side lip thickness
Z_THIN_LIP = LEDGE + MON_THIN + FIT_Z  # 10.0: a 7.0 mm slot, the gauge's 3-notch piece
Z_THICK_LIP = LEDGE + MON_THICK + FIT_Z  # 17.1 (v20 16.9 -> 0.3 play; spec 14.0 hump still fits)
XW0, XW1 = -FIT_X, MON_W + FIT_X  # pocket walls
SEAM_Y = 177.35
# Outer frame (CAD/bezel_spec.py): placed round the screen opening so the visible borders (face + bevel to the glass)
# are equal, 22.3 mm left / right / top, and the chin is 36 mm. The opening is the photographed image plus a 0.8 mm
# reveal on every side (2026-11-19; v21.1: 2.0 mm round the spec sheet's image, 0.8 / 4.4 / 1.7 as printed).
# Front rim: a 4 mm round in the spirit of the Apple IIc monitor's soft rim. Face-down, the part of a round
# flatter than 45 deg would droop off the plate, so below its 45-deg point it continues as a 45-deg chamfer
# (a teardrop round): it reads as a round and prints clean. Snow White's rule is 2 mm front / 3 mm rear.
FRONT_ROUND = 4.0
BACK_ROUND = 3.0  # rear perimeter round (Snow White: 3 mm)
# Snow White lines: 2 mm wide, 10 mm on centre, set back from the front and the back. Equal depth on both sides
# (v21 before 2026-11-18: 1.0 left / 1.8 right). The left wall is 4.5 mm with the lap pocket at -2.5, so 1.5 is
# the deepest that keeps 1.0 mm of wall there. Only the parting-line groove at SEAM_Y runs through.
GROOVE_W, GROOVE_D, GROOVE_PITCH = 2.0, 1.5, 10.0
GROOVE_Z = (FRONT_ROUND + 1.0, H - BACK_ROUND)
SEAM_FRONT_D = 0.6  # front-face groove that the Upper/Lower parting line sits in
EXPECTED_SHELLS = {
    "Part_B_Upper": 1,
    "Part_B_Lower": 1,
    "Part_B_LED": 1,
    "Part_B_FitGauge": 4,
}

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = "MILLIMETERS"


# ---------------------------------------------------------------- master frame
# Outer frame: FX0..FX1 x FY0..FY1 x H mm (CAD/bezel_spec.py; 242.2 x 356.1, plan R=3.0), teardrop-rounded
# front rim, rounded back edge
t45 = FRONT_ROUND * (1 - math.sqrt(0.5))  # the round's 45-deg point: z = inset = 0.293 R
rings = [(0.0, 2 * t45)]
rings += [
    (FRONT_ROUND * (1 - math.cos(math.radians(a))), FRONT_ROUND * (1 - math.sin(math.radians(a))))
    for a in range(45, 91, 9)
]
rings += [
    (
        H - BACK_ROUND + BACK_ROUND * math.sin(math.radians(a)),
        BACK_ROUND * (1 - math.cos(math.radians(a))),
    )
    for a in range(0, 91, 15)
]
part_b = make_obj_from_bm("Part_B_Master", bm_profiled_prism(FX0, FX1, FY0, FY1, 3.0, rings))
apply_bool(
    part_b,
    bm_frustum_rect(*grow(OPENING, BEVEL_FACE + MICRO), -0.2, *grow(OPENING, BEVEL_FACE), 0.30),
    "DIFFERENCE",
    "CRT_MicroChamfer",
)
apply_bool(
    part_b,
    bm_frustum_rect(*grow(OPENING, BEVEL_FACE), 0.25, *grow(OPENING, -BEVEL_IN), 6.02),
    "DIFFERENCE",
    "CRT_Bevel",
)
apply_bool(
    part_b,
    bm_rounded_prism(*grow(OPENING, -BEVEL_IN), 5.95, H + 0.5, r=0.0),
    "DIFFERENCE",
    "Screen_Through",
)
apply_bool(
    part_b,
    bm_rounded_prism(XW0, XW1, -FIT_Y, MON_H + FIT_Y, LEDGE, H + 0.5, r=6.0 + FIT_X, segs=8),
    "DIFFERENCE",
    "Monitor_Cradle_Pocket",
)

# Rear retaining lips + top-right detent tab (each overlaps its wall by 0.5 mm)
apply_bool(
    part_b,
    bm_rounded_prism(XW0 - 0.5, 1.7, 6.0, 304.0, Z_THICK_LIP, H, r=0.0),
    "UNION",
    "Left_Rear_Lip",
)
apply_bool(
    part_b,
    bm_rounded_prism(218.3, XW1 + 0.5, 6.0, 304.0, Z_THIN_LIP, Z_THIN_LIP + LIP_T, r=0.0),
    "UNION",
    "Right_Rear_Lip",
)
apply_bool(
    part_b,
    bm_rounded_prism(76.0, 214.0, -FIT_Y - 0.5, 1.7, Z_THIN_LIP, Z_THIN_LIP + LIP_T, r=0.0),
    "UNION",
    "BottomRight_Rear_Lip",
)
# (v20 had a 45-deg print chamfer under this tab; it reached 0.2 mm into the monitor top edge.
# A 1.0 mm overhang prints unsupported.)
apply_bool(
    part_b,
    bm_rounded_prism(196.0, 206.0, 309.3, 311.0, Z_THIN_LIP, Z_THIN_LIP + LIP_T, r=0.0),
    "UNION",
    "Detent_Tab",
)
apply_bool(
    part_b,
    bm_rounded_prism(196.0, 206.0, 312.6, 314.2, LEDGE, H + 0.5, r=0.0),
    "DIFFERENCE",
    "Detent_Flex_Slot",
)

# Port & control bays
apply_bool(
    part_b,
    bm_rounded_prism(14.0, 65.0, 310.0, FY1 + 0.6, 6.0, H + 0.5, r=0.0),
    "DIFFERENCE",
    "TopLeft_USBC_Bay",
)
apply_bool(
    part_b,
    bm_rounded_prism(33.0, 47.0, 304.6, FY1 + 0.6, 1.5, 3.1, r=0.0),
    "DIFFERENCE",
    "USBC_Nose_Relief",
)
apply_bool(
    part_b,
    bm_rounded_prism(12.0, 73.0, -30.0, 0.0, LEDGE, H + 0.5, r=0.0),
    "DIFFERENCE",
    "BottomLeft_Control_Bay",
)

# Snow White lines: long sides (pitch from the parting line), top and bottom faces (pitch from the centre),
# skipping the top USB-C bay and the bottom control bay; plus the front-face parting-line groove.
half_w = GROOVE_W / 2
groove_ys = [SEAM_Y + k * GROOVE_PITCH for k in range(-25, 26) if FY0 + 6.0 <= SEAM_Y + k * GROOVE_PITCH <= FY1 - 6.0]
for idx, gy in enumerate(groove_ys):
    z0, z1 = (-0.2, H + 0.2) if gy == SEAM_Y else GROOVE_Z
    apply_bool(
        part_b,
        bm_rounded_prism(FX1 - GROOVE_D, FX1 + 0.5, gy - half_w, gy + half_w, z0, z1),
        "DIFFERENCE",
        f"GR_{idx}",
    )
    apply_bool(
        part_b,
        bm_rounded_prism(FX0 - 0.5, FX0 + GROOVE_D, gy - half_w, gy + half_w, z0, z1),
        "DIFFERENCE",
        f"GL_{idx}",
    )
XC = (FX0 + FX1) / 2
for face, (ya, yb), keep_out in (
    ("T", (FY1 - GROOVE_D, FY1 + 0.5), (12.0, 67.0)),
    ("B", (FY0 - 0.5, FY0 + GROOVE_D), (10.0, 75.0)),
):
    for k in range(-12, 13):
        gx = XC + k * GROOVE_PITCH
        if gx - half_w < FX0 + 8.0 or gx + half_w > FX1 - 8.0 or keep_out[0] <= gx <= keep_out[1]:
            continue
        apply_bool(
            part_b,
            bm_rounded_prism(gx - half_w, gx + half_w, ya, yb, *GROOVE_Z),
            "DIFFERENCE",
            f"G{face}_{k}",
        )
d = SEAM_FRONT_D
apply_bool(
    part_b,
    bm_prism_yz(
        [
            (SEAM_Y - half_w - 0.2, -0.2),
            (SEAM_Y + half_w + 0.2, -0.2),
            (SEAM_Y + half_w - d, d),
            (SEAM_Y - half_w + d, d),
        ],
        FX0 - 1.0,
        FX1 + 1.0,
    ),
    "DIFFERENCE",
    "Front_Seam_Groove",
)

# Chin windows (CAD/chin_spec.py): the 18 mm snap-in emblem window (lower-left, in the 3 mm plate over the
# open control bay) and the vertical slit power light (lower-right), both after the Apple IIc monitor.
h, hh = EMBLEM_WIN / 2, EMBLEM_HOLE / 2
seat = EMBLEM_POCKET + (h - hh)  # 45-deg seat from the pocket down to the hole
assert CHIN_PLATE == LEDGE, "the emblem's barbs are sized for the chin plate the ledge makes"
apply_bool(
    part_b,
    bm_rounded_prism(EMBLEM_CX - h, EMBLEM_CX + h, EMBLEM_CY - h, EMBLEM_CY + h, -0.2, EMBLEM_POCKET, r=0.0),
    "DIFFERENCE",
    "Emblem_Pocket",
)
apply_bool(
    part_b,
    bm_frustum_rect(EMBLEM_CX - h, EMBLEM_CX + h, EMBLEM_CY - h, EMBLEM_CY + h, EMBLEM_POCKET - 0.01,
                    EMBLEM_CX - hh, EMBLEM_CX + hh, EMBLEM_CY - hh, EMBLEM_CY + hh, seat + 0.01),
    "DIFFERENCE",
    "Emblem_Seat",
)  # fmt: skip
apply_bool(
    part_b,
    bm_rounded_prism(EMBLEM_CX - hh, EMBLEM_CX + hh, EMBLEM_CY - hh, EMBLEM_CY + hh, seat - 0.2, H + 0.5, r=0.0),
    "DIFFERENCE",
    "Emblem_Hole",
)
apply_bool(
    part_b,
    bm_frustum_rect(EMBLEM_CX - h - 0.3, EMBLEM_CX + h + 0.3, EMBLEM_CY - h - 0.3, EMBLEM_CY + h + 0.3, -0.1,
                    EMBLEM_CX - h, EMBLEM_CX + h, EMBLEM_CY - h, EMBLEM_CY + h, 0.30),
    "DIFFERENCE",
    "Emblem_Chamfer",
)  # fmt: skip
apply_bool(part_b, bm_rounded_prism(*LED_SLIT, -0.2, H + 0.5, r=0.0), "DIFFERENCE", "LED_Slit")
apply_bool(part_b, bm_rounded_prism(*LED_BORE, LEDGE, H + 0.5, r=0.0), "DIFFERENCE", "LED_Rear_Counterbore")

# ---------------------------------------------------------------- split at the seam (half-space booleans)
part_b_upper = duplicate(part_b, "Part_B_Upper")
part_b_lower = duplicate(part_b, "Part_B_Lower")
bpy.data.objects.remove(part_b, do_unlink=True)
apply_bool(
    part_b_upper,
    bm_rounded_prism(-20.0, 260.0, SEAM_Y, 340.0, -5.0, H + 5.0),
    "INTERSECT",
    "Split_Upper",
)
apply_bool(
    part_b_lower,
    bm_rounded_prism(-20.0, 260.0, -40.0, SEAM_Y, -5.0, H + 5.0),
    "INTERSECT",
    "Split_Lower",
)

# Interlock lip + left 45-deg lap joint + 0.35 mm detent (0.20 mm clearance); tongue face flush with the pocket wall
apply_bool(
    part_b_lower,
    bm_rounded_prism(220.0, 223.0, 177.2, 178.55, 1.2, 2.04, r=0.0),
    "UNION",
    "Interlock_Lip_Lower",
)
apply_bool(
    part_b_upper,
    bm_rounded_prism(220.0, 223.2, 177.2, 178.75, 1.00, 2.24, r=0.0),
    "DIFFERENCE",
    "Interlock_Pocket_Upper",
)
apply_bool(
    part_b_lower,
    bm_prism_yz([(177.2, 3.0), (182.35, 8.0), (182.35, 16.9), (177.2, 16.9)], -2.30, XW0),
    "UNION",
    "Left_Lap_Tongue",
)
apply_bool(
    part_b_lower,
    bm_prism_xy([(-2.15, 179.6), (-2.65, 180.2), (-2.65, 180.8), (-2.15, 181.4)], 9.0, 16.0),
    "UNION",
    "Left_Detent_Bump",
)
apply_bool(
    part_b_upper,
    bm_prism_yz([(177.2, 2.80), (182.55, 8.0), (182.55, 17.10), (177.2, 17.10)], -2.50, XW0),
    "DIFFERENCE",
    "Left_Lap_Pocket",
)
apply_bool(
    part_b_upper,
    bm_prism_xy([(-2.25, 179.5), (-2.80, 180.15), (-2.80, 180.85), (-2.25, 181.5)], 8.8, 16.2),
    "DIFFERENCE",
    "Left_Detent_Recess",
)

# Right-flank screwless compliant snap latch (1.80 mm = 4 x 0.45 mm wall multiple).
# v20 placed the arm and catch inside the SOLID right frame: the arm (Y 171..177.35) collided with the Lower
# and the catch notch was a sealed internal cavity, so the halves could not mate. v21 cuts a back-open
# channel (Z 4.0..H) for the arm through both halves; the arm hangs free from the Upper (root at Y 188.0),
# its barb rides the Lower's catch wall (X 230.2, 0.2 mm off the arm face) via a lead-in and drops into the
# notch; pressing the finger tab -X (toward the screen) releases it.
ARM_X0, ARM_X1 = 228.2, 230.0
CH_X0, CH_X1 = (
    226.0,
    ARM_X1 + 0.2,
)  # 2.2 mm flex room on the -X side, 0.2 mm on the catch side
CH_Z0 = 4.0
apply_bool(
    part_b_upper,
    bm_rounded_prism(CH_X0, 232.5, SEAM_Y - 1.0, 188.0, CH_Z0, H + 0.5, r=0.0),
    "DIFFERENCE",
    "Snap_Relief_Upper",
)
apply_bool(
    part_b_upper,
    bm_rounded_prism(ARM_X0, ARM_X1, 171.0, 188.5, 4.5, 13.5, r=0.0),
    "UNION",
    "Snap_Arm",
)
apply_bool(
    part_b_upper,
    bm_prism_xy(
        [(ARM_X1 - 0.2, 171.0), (231.0, 172.0), (231.0, 173.2), (ARM_X1 - 0.2, 174.2)],
        4.5,
        13.5,
    ),
    "UNION",
    "Snap_Barb",
)
apply_bool(
    part_b_upper,
    bm_rounded_prism(227.7, ARM_X1, 171.0, 173.5, 13.4, 16.8, r=0.0),
    "UNION",
    "Snap_FingerTab",
)
apply_bool(
    part_b_lower,
    bm_rounded_prism(CH_X0, CH_X1, 170.5, SEAM_Y + 1.0, CH_Z0, H + 0.5, r=0.0),
    "DIFFERENCE",
    "Catch_Arm_Channel",
)
apply_bool(
    part_b_lower,
    bm_rounded_prism(CH_X1 - 0.1, 231.4, 170.8, 174.6, CH_Z0, H + 0.5, r=0.0),
    "DIFFERENCE",
    "Catch_Notch",
)
apply_bool(
    part_b_lower,
    bm_prism_xy(
        [
            (CH_X1 - 0.1, SEAM_Y + 1.0),
            (CH_X1 - 0.1, 175.9),
            (CH_X1, 175.9),
            (231.4, SEAM_Y),
            (231.4, SEAM_Y + 1.0),
        ],
        CH_Z0,
        H + 0.5,
    ),
    "DIFFERENCE",
    "Catch_LeadIn",
)

# Fit gauge: cut from the Lower before mirroring, so it mirrors with the parts (CAD/partb_accessories.py)
build_fit_gauge(part_b_lower, H, LEDGE, Z_THIN_LIP, XW1, LIP_T, FX1)

# Mirror X so the Z=0 face-down print has true front-view L/R
for name in ["Part_B_Upper", "Part_B_Lower", "Part_B_FitGauge"]:
    obj = bpy.data.objects[name]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    for v in bm.verts:
        v.co.x = -v.co.x
    for f in bm.faces:  # a mirror inverts winding; flipping restores outward normals exactly
        f.normal_flip()  # (v20 then ran recalc_face_normals, which turned the Upper inside-out)
    bm.to_mesh(obj.data)
    bm.free()

# Chin inserts (CAD/partb_accessories.py)
build_chin_inserts()


# ---------------------------------------------------------------- gate + export
os.makedirs(os.path.join(OUT, "STLs"), exist_ok=True)
failures = []
for name, want_shells in EXPECTED_SHELLS.items():
    obj = bpy.data.objects[name]
    bad, shells = mesh_report(obj.data)
    vol = signed_volume(obj.data)
    xs = [v.co.x for v in obj.data.vertices]
    ys = [v.co.y for v in obj.data.vertices]
    zs = [v.co.z for v in obj.data.vertices]
    ok = bad == 0 and shells == want_shells and vol > 0
    print(
        f"GATE {name:16s} {max(xs) - min(xs):7.2f} x {max(ys) - min(ys):7.2f} x {max(zs) - min(zs):5.2f} mm  "
        f"vol {vol / 1000:7.2f} cm3  shells {shells}/{want_shells}  non-manifold {bad}  {'OK' if ok else 'FAIL'}"
    )
    if not ok:
        failures.append(name)
if failures:  # nothing is written unless every part passes
    raise SystemExit(f"gate failed: {failures}")
for name in EXPECTED_SHELLS:
    write_stl(bpy.data.objects[name], os.path.join(OUT, "STLs", name + ".stl"))
if OUT == ROOT:
    bpy.context.preferences.filepaths.save_version = 0  # no .blend1 backups
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, "CAD", "Part_B_SnowWhite_Bezel_v21.blend"))
print("GATE all Part B meshes manifold, single-shell, outward-facing")
