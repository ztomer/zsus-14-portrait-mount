"""
Accessory parts for CAD/build_part_b_blender_v21.py: the fit gauge (cut from the finished Lower) and the
press-fit chin inserts. Imported by that script; runs only inside Blender.
"""

import bmesh
import bpy
from partb_mesh import apply_bool, bm_rounded_prism, duplicate, make_obj_from_bm


def build_fit_gauge(part_b_lower, H, LEDGE, Z_THIN_LIP, XW1, LIP_T):
    """Fit gauge: 15 mm of the Lower's thick-side channel plus three thin-side channels with stepped slots
    (taken before mirroring, so it mirrors with the parts). The thin panel is 5.7 mm by hand measurement but
    6.1..6.8 mm scaled from the owner's side photo (2026-11-18), with no caliper to settle it: the first thin
    piece is the Lower's own channel, the other two raise its lip. The notches on each piece's back count the step.
    Returns the Part_B_FitGauge object (four shells)."""
    GAUGE_SLOTS = (
        Z_THIN_LIP - LEDGE,
        Z_THIN_LIP - LEDGE + 0.4,
        Z_THIN_LIP - LEDGE + 0.8,
    )  # 6.2 / 6.6 / 7.0
    GAUGE_DX, GAUGE_DY = (
        -190.0,
        20.0,
    )  # thin pieces sit beside the thick one, 20 mm apart in Y
    part_b_gauge = duplicate(part_b_lower, "Part_B_FitGauge")
    apply_bool(
        part_b_gauge,
        bm_rounded_prism(-20.0, 100.0, 100.0, 115.0, -5.0, H + 5.0),
        "INTERSECT",
        "Gauge_Slice_Thick",
    )
    for k, slot in enumerate(GAUGE_SLOTS):
        thin = duplicate(part_b_lower, f"Gauge_Thin_{k}")
        apply_bool(
            thin,
            bm_rounded_prism(100.0, 260.0, 100.0, 115.0, -5.0, H + 5.0),
            "INTERSECT",
            f"Gauge_Slice_Thin_{k}",
        )
        if k:
            apply_bool(
                thin,
                bm_rounded_prism(210.0, XW1, 99.0, 116.0, LEDGE + 0.5, H + 1.0),
                "DIFFERENCE",
                f"Gauge_Lip_Off_{k}",
            )
            apply_bool(
                thin,
                bm_rounded_prism(218.3, XW1 + 0.5, 100.0, 115.0, LEDGE + slot, LEDGE + slot + LIP_T),
                "UNION",
                f"Gauge_Lip_{k}",
            )
        for n in range(k + 1):  # step label: 1, 2, 3 notches, 0.8 mm deep in the back face
            y0 = 107.5 - (k + 1) * 1.2 + n * 2.4 + 0.6
            apply_bool(
                thin,
                bm_rounded_prism(231.0, 236.0, y0, y0 + 1.2, H - 0.8, H + 1.0),
                "DIFFERENCE",
                f"Gauge_Notch_{k}_{n}",
            )
        bm = bmesh.new()
        bm.from_mesh(thin.data)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(GAUGE_DX, k * GAUGE_DY, 0.0))
        bpy.data.objects.remove(thin, do_unlink=True)
        apply_bool(part_b_gauge, bm, "UNION", f"Gauge_Add_Thin_{k}")
    print("GAUGE thin-side slots " + " / ".join(f"{s:.1f}" for s in GAUGE_SLOTS) + " mm (1 / 2 / 3 notches)")

    return part_b_gauge


def build_chin_inserts():
    """Part_B_Badge (14 mm window) and Part_B_LED (6 x 2 mm window): 0.8 mm flange, stem, two crush ribs."""
    part_b_badge = make_obj_from_bm("Part_B_Badge", bm_rounded_prism(0.0, 15.4, 0.0, 15.4, 0.0, 0.8, r=0.4, segs=4))
    apply_bool(
        part_b_badge,
        bm_rounded_prism(0.82, 14.58, 0.82, 14.58, 0.75, 3.8, r=0.2, segs=4),
        "UNION",
        "Badge_Stem",
    )
    apply_bool(
        part_b_badge,
        bm_rounded_prism(0.62, 0.90, 4.0, 11.4, 0.8, 3.8, r=0.0),
        "UNION",
        "Badge_Rib_L",
    )
    apply_bool(
        part_b_badge,
        bm_rounded_prism(14.50, 14.78, 4.0, 11.4, 0.8, 3.8, r=0.0),
        "UNION",
        "Badge_Rib_R",
    )

    part_b_led = make_obj_from_bm("Part_B_LED", bm_rounded_prism(0.0, 7.4, 0.0, 3.4, 0.0, 0.8, r=0.3, segs=4))
    apply_bool(
        part_b_led,
        bm_rounded_prism(0.82, 6.58, 0.82, 2.58, 0.75, 3.8, r=0.1, segs=4),
        "UNION",
        "LED_Stem",
    )
    apply_bool(
        part_b_led,
        bm_rounded_prism(0.62, 0.90, 1.2, 2.2, 0.8, 3.8, r=0.0),
        "UNION",
        "LED_Rib_L",
    )
    apply_bool(
        part_b_led,
        bm_rounded_prism(6.50, 6.78, 1.2, 2.2, 0.8, 3.8, r=0.0),
        "UNION",
        "LED_Rib_R",
    )

    return part_b_badge, part_b_led
