"""
ZSUS 14" Portrait Glue-On Ball Socket (v20) — Autodesk Fusion Python Script
Generates: Part_A_Test and Part_A_Mount (100% dead-flat PEI bottom, M22x2.0 45-deg thread, 17.20 mm ball cup + 8 micro-ribs).
"""
import adsk.core, adsk.fusion, math, os

MM = 0.1  # Fusion internal API units are centimeters

def add_rrect_to_sk(sk, x0, y0, w, h, r):
    lines = sk.sketchCurves.sketchLines
    arcs = sk.sketchCurves.sketchArcs
    x1, y1, x2, y2 = x0, y0, x0 + w, y0 + h
    l_bot = lines.addByTwoPoints(adsk.core.Point3D.create((x1+r)*MM, y1*MM, 0), adsk.core.Point3D.create((x2-r)*MM, y1*MM, 0))
    l_rgt = lines.addByTwoPoints(adsk.core.Point3D.create(x2*MM, (y1+r)*MM, 0), adsk.core.Point3D.create(x2*MM, (y2-r)*MM, 0))
    l_top = lines.addByTwoPoints(adsk.core.Point3D.create((x2-r)*MM, y2*MM, 0), adsk.core.Point3D.create((x1+r)*MM, y2*MM, 0))
    l_lft = lines.addByTwoPoints(adsk.core.Point3D.create(x1*MM, (y2-r)*MM, 0), adsk.core.Point3D.create(x1*MM, (y1+r)*MM, 0))
    if r > 0:
        arcs.addByCenterStartSweep(adsk.core.Point3D.create((x2-r)*MM, (y1+r)*MM, 0), l_bot.endSketchPoint.geometry, math.pi/2)
        arcs.addByCenterStartSweep(adsk.core.Point3D.create((x2-r)*MM, (y2-r)*MM, 0), l_rgt.endSketchPoint.geometry, math.pi/2)
        arcs.addByCenterStartSweep(adsk.core.Point3D.create((x1+r)*MM, (y2-r)*MM, 0), l_top.endSketchPoint.geometry, math.pi/2)
        arcs.addByCenterStartSweep(adsk.core.Point3D.create((x1+r)*MM, (y1+r)*MM, 0), l_lft.endSketchPoint.geometry, math.pi/2)

def make_rounded_rect_sketch(comp, plane, x0, y0, w, h, r, name="rect"):
    sk = comp.sketches.add(plane)
    sk.name = name
    add_rrect_to_sk(sk, x0, y0, w, h, r)
    return sk

def extrude_profile(comp, prof, dist_mm, op=adsk.fusion.FeatureOperations.NewBodyFeatureOperation, offset_mm=0.0, target_body=None):
    ext = comp.features.extrudeFeatures
    inp = ext.createInput(prof, op)
    inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(dist_mm * MM))
    if abs(offset_mm) > 1e-6:
        inp.startExtent = adsk.fusion.OffsetStartDefinition.create(adsk.core.ValueInput.createByReal(offset_mm * MM))
    if target_body is not None and op in (adsk.fusion.FeatureOperations.CutFeatureOperation, adsk.fusion.FeatureOperations.JoinFeatureOperation):
        inp.participantBodies = [target_body]
    return ext.add(inp)

def build_collet_boss(comp, target_body, cx, cy, base_z):
    r_major, r_minor, r_pitch = 21.95/2.0, 19.95/2.0, 20.95/2.0
    h_total, h_thread = 10.8, 9.3
    z_top = base_z + h_total
    z_sphere = base_z + 6.2
    r_sphere, r_rim = 17.20/2.0, 16.30/2.0
    z_rim = z_sphere + math.sqrt(r_sphere**2 - r_rim**2)

    planes = comp.constructionPlanes
    p_inp = planes.createInput()
    p_inp.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(cy * MM))
    xz_plane = planes.add(p_inp)

    sk_rev = comp.sketches.add(xz_plane)
    lines = sk_rev.sketchCurves.sketchLines
    def pt_xz(wx, wz): return sk_rev.modelToSketchSpace(adsk.core.Point3D.create(wx*MM, cy*MM, wz*MM))
    pts = [pt_xz(cx, base_z), pt_xz(cx+r_major, base_z), pt_xz(cx+r_major, base_z+h_thread-1.0), pt_xz(cx+r_minor, base_z+h_thread), pt_xz(cx+r_minor, z_top), pt_xz(cx, z_top)]
    for i in range(len(pts)): lines.addByTwoPoints(pts[i], pts[(i+1)%len(pts)])
    axis_line = lines.addByTwoPoints(pt_xz(cx, base_z), pt_xz(cx, z_top))
    revs = comp.features.revolveFeatures
    r_inp = revs.createInput(sk_rev.profiles.item(0), axis_line, adsk.fusion.FeatureOperations.JoinFeatureOperation)
    r_inp.setAngleExtent(False, adsk.core.ValueInput.createByReal(2*math.pi))
    r_inp.participantBodies = [target_body]
    revs.add(r_inp)

    sk_cut = comp.sketches.add(xz_plane)
    clines, carcs = sk_cut.sketchCurves.sketchLines, sk_cut.sketchCurves.sketchArcs
    def pt_cut(wx, wz): return sk_cut.modelToSketchSpace(adsk.core.Point3D.create(wx*MM, cy*MM, wz*MM))
    z_bot_clip = base_z + 0.5
    r_bot = math.sqrt(max(0.1, r_sphere**2 - (z_sphere - z_bot_clip)**2))
    r_chamf_top = min(r_minor - 0.15, r_rim + (z_top - z_rim))
    z_chamf_start = z_top - (r_chamf_top - r_rim)
    c_axis = clines.addByTwoPoints(pt_cut(cx, z_bot_clip), pt_cut(cx, z_top))
    clines.addByTwoPoints(pt_cut(cx, z_bot_clip), pt_cut(cx+r_bot, z_bot_clip))
    carcs.addByThreePoints(pt_cut(cx+r_bot, z_bot_clip), pt_cut(cx+r_sphere, z_sphere), pt_cut(cx+r_rim, z_rim))
    if z_chamf_start > z_rim + 0.02:
        clines.addByTwoPoints(pt_cut(cx+r_rim, z_rim), pt_cut(cx+r_rim, z_chamf_start))
        clines.addByTwoPoints(pt_cut(cx+r_rim, z_chamf_start), pt_cut(cx+r_chamf_top, z_top))
    else:
        clines.addByTwoPoints(pt_cut(cx+r_rim, z_rim), pt_cut(cx+r_chamf_top, z_top))
    clines.addByTwoPoints(pt_cut(cx+r_chamf_top, z_top), pt_cut(cx, z_top))
    rc_inp = revs.createInput(sk_cut.profiles.item(0), c_axis, adsk.fusion.FeatureOperations.CutFeatureOperation)
    rc_inp.setAngleExtent(False, adsk.core.ValueInput.createByReal(2*math.pi))
    rc_inp.participantBodies = [target_body]
    revs.add(rc_inp)

    p_rib_inp = planes.createInput()
    p_rib_inp.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal((base_z + 1.0) * MM))
    sk_ribs = comp.sketches.add(planes.add(p_rib_inp))
    rlines = sk_ribs.sketchCurves.sketchLines
    rib_profs = adsk.core.ObjectCollection.create()
    for k in range(8):
        ang = math.radians(22.5 + k * 45.0)
        ca, sa = math.cos(ang), math.sin(ang)
        tx, ty = -sa, ca
        r_in, r_out, hw = r_sphere - 0.25, r_sphere + 0.45, 0.30
        c1 = adsk.core.Point3D.create((cx+r_in*ca-hw*tx)*MM, (cy+r_in*sa-hw*ty)*MM, 0)
        c2 = adsk.core.Point3D.create((cx+r_out*ca-hw*tx)*MM, (cy+r_out*sa-hw*ty)*MM, 0)
        c3 = adsk.core.Point3D.create((cx+r_out*ca+hw*tx)*MM, (cy+r_out*sa+hw*ty)*MM, 0)
        c4 = adsk.core.Point3D.create((cx+r_in*ca+hw*tx)*MM, (cy+r_in*sa+hw*ty)*MM, 0)
        rlines.addByTwoPoints(c1, c2); rlines.addByTwoPoints(c2, c3); rlines.addByTwoPoints(c3, c4); rlines.addByTwoPoints(c4, c1)
    for idx in range(sk_ribs.profiles.count): rib_profs.add(sk_ribs.profiles.item(idx))
    extrude_profile(comp, rib_profs, 4.0, adsk.fusion.FeatureOperations.JoinFeatureOperation, offset_mm=3.2, target_body=target_body)

    sk_helix = comp.sketches.add(comp.xYConstructionPlane)
    pts_helix = adsk.core.ObjectCollection.create()
    pitch, z_h_start, z_h_end = 2.0, base_z - 0.4, base_z + h_thread - 0.4
    turns = (z_h_end - z_h_start) / pitch
    total_steps = int(math.ceil(turns * 24))
    for i in range(total_steps + 1):
        t = (i / total_steps) * turns
        ang = t * 2.0 * math.pi
        pts_helix.add(adsk.core.Point3D.create((cx+r_pitch*math.cos(ang))*MM, (cy+r_pitch*math.sin(ang))*MM, (z_h_start+t*pitch)*MM))
    spline = sk_helix.sketchCurves.sketchFittedSplines.add(pts_helix)

    sk_th_prof = comp.sketches.add(xz_plane)
    tlines = sk_th_prof.sketchCurves.sketchLines
    def pt_th(wx, wz): return sk_th_prof.modelToSketchSpace(adsk.core.Point3D.create(wx*MM, cy*MM, wz*MM))
    tp1, tp2, tp3, tp4 = pt_th(cx+r_minor, z_h_start-0.15), pt_th(cx+r_major+0.3, z_h_start-0.90), pt_th(cx+r_major+0.3, z_h_start+0.90), pt_th(cx+r_minor, z_h_start+0.15)
    tlines.addByTwoPoints(tp1, tp2); tlines.addByTwoPoints(tp2, tp3); tlines.addByTwoPoints(tp3, tp4); tlines.addByTwoPoints(tp4, tp1)
    sweeps = comp.features.sweepFeatures
    sw_inp = sweeps.createInput(sk_th_prof.profiles.item(0), comp.features.createPath(spline), adsk.fusion.FeatureOperations.CutFeatureOperation)
    sw_inp.orientation = adsk.fusion.SweepOrientationTypes.PerpendicularOrientationType
    sw_inp.participantBodies = [target_body]
    sweeps.add(sw_inp)

    z_keyhole = base_z + 1.3
    p_slot_inp = planes.createInput()
    p_slot_inp.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z_keyhole * MM))
    sk_slots = comp.sketches.add(planes.add(p_slot_inp))
    slines = sk_slots.sketchCurves.sketchLines
    slot_profs = adsk.core.ObjectCollection.create()
    for ang_deg in [45.0, 135.0, 225.0, 315.0]:
        ang = math.radians(ang_deg); ca, sa = math.cos(ang), math.sin(ang); tx, ty = -sa, ca
        r1, r2, hw = 5.0, r_major + 1.0, 1.1
        p1 = adsk.core.Point3D.create((cx+r1*ca-hw*tx)*MM, (cy+r1*sa-hw*ty)*MM, 0)
        p2 = adsk.core.Point3D.create((cx+r2*ca-hw*tx)*MM, (cy+r2*sa-hw*ty)*MM, 0)
        p3 = adsk.core.Point3D.create((cx+r2*ca+hw*tx)*MM, (cy+r2*sa+hw*ty)*MM, 0)
        p4 = adsk.core.Point3D.create((cx+r1*ca+hw*tx)*MM, (cy+r1*sa+hw*ty)*MM, 0)
        slines.addByTwoPoints(p1, p2); slines.addByTwoPoints(p2, p3); slines.addByTwoPoints(p3, p4); slines.addByTwoPoints(p4, p1)
    for idx in range(sk_slots.profiles.count): slot_profs.add(sk_slots.profiles.item(idx))
    extrude_profile(comp, slot_profs, h_total - 1.3 + 0.5, adsk.fusion.FeatureOperations.CutFeatureOperation, target_body=target_body)

    for ang_deg in [45.0, 135.0]:
        ang = math.radians(ang_deg)
        p_kh_inp = planes.createInput()
        sk_ray = comp.sketches.add(comp.xYConstructionPlane)
        ray_line = sk_ray.sketchCurves.sketchLines.addByTwoPoints(
            adsk.core.Point3D.create((cx-15*math.cos(ang))*MM, (cy-15*math.sin(ang))*MM, 0),
            adsk.core.Point3D.create((cx+15*math.cos(ang))*MM, (cy+15*math.sin(ang))*MM, 0)
        )
        p_kh_inp.setByDistanceOnPath(ray_line, adsk.core.ValueInput.createByReal(0.0))
        sk_kh = comp.sketches.add(planes.add(p_kh_inp))
        c_pt = sk_kh.modelToSketchSpace(adsk.core.Point3D.create((cx-15*math.cos(ang))*MM, (cy-15*math.sin(ang))*MM, z_keyhole*MM))
        sk_kh.sketchCurves.sketchCircles.addByCenterRadius(c_pt, 1.5 * MM)
        extrude_profile(comp, sk_kh.profiles.item(0), 30.0, adsk.fusion.FeatureOperations.CutFeatureOperation, target_body=target_body)
