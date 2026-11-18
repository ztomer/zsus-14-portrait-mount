"""
ZSUS 14" Portrait Apple "Snow White" Open-Back Bezel (v20 Final DFM-Tuned)
Run inside Blender (Metric / Millimeters, scale_length = 0.001).
Generates: Part_B_Upper, Part_B_Lower, Part_B_Badge, Part_B_LED and exports STLs.
"""
import bpy, bmesh, math, os, struct
from mathutils import Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 0.001
scene.unit_settings.length_unit = 'MILLIMETERS'

def new_mesh_obj(name):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj

def bm_rounded_prism(x0, x1, y0, y1, z0, z1, r=0.0, segs=8):
    bm = bmesh.new()
    if r <= 0.001:
        v = [
            bm.verts.new((x0, y0, z0)), bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)), bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)), bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)), bm.verts.new((x0, y1, z1)),
        ]
        bm.faces.new((v[0], v[3], v[2], v[1]))
        bm.faces.new((v[4], v[5], v[6], v[7]))
        bm.faces.new((v[0], v[1], v[5], v[4]))
        bm.faces.new((v[1], v[2], v[6], v[5]))
        bm.faces.new((v[2], v[3], v[7], v[6]))
        bm.faces.new((v[3], v[0], v[4], v[7]))
    else:
        corners = [
            (x1 - r, y1 - r, 0.0, math.pi * 0.5),
            (x0 + r, y1 - r, math.pi * 0.5, math.pi),
            (x0 + r, y0 + r, math.pi, math.pi * 1.5),
            (x1 - r, y0 + r, math.pi * 1.5, math.pi * 2.0),
        ]
        bot_verts, top_verts = [], []
        for cx, cy, a0, a1 in corners:
            for i in range(segs + 1):
                a = a0 + (a1 - a0) * (i / segs)
                px, py = cx + r * math.cos(a), cy + r * math.sin(a)
                bot_verts.append(bm.verts.new((px, py, z0)))
                top_verts.append(bm.verts.new((px, py, z1)))
        bm.faces.new(list(reversed(bot_verts)))
        bm.faces.new(top_verts)
        n = len(bot_verts)
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((bot_verts[i], bot_verts[j], top_verts[j], top_verts[i]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def bm_frustum_rect(x0_b, x1_b, y0_b, y1_b, z0, x0_t, x1_t, y0_t, y1_t, z1):
    bm = bmesh.new()
    vb = [
        bm.verts.new((x0_b, y0_b, z0)), bm.verts.new((x1_b, y0_b, z0)),
        bm.verts.new((x1_b, y1_b, z0)), bm.verts.new((x0_b, y1_b, z0)),
    ]
    vt = [
        bm.verts.new((x0_t, y0_t, z1)), bm.verts.new((x1_t, y0_t, z1)),
        bm.verts.new((x1_t, y1_t, z1)), bm.verts.new((x0_t, y1_t, z1)),
    ]
    bm.faces.new((vb[0], vb[3], vb[2], vb[1]))
    bm.faces.new((vt[0], vt[1], vt[2], vt[3]))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def apply_bool(target_obj, tool_bm, op='DIFFERENCE', name="BoolTool"):
    tool_obj = new_mesh_obj(name)
    tool_bm.to_mesh(tool_obj.data)
    tool_bm.free()
    mod = target_obj.modifiers.new(name=name, type='BOOLEAN')
    mod.operation = op
    mod.solver = 'FLOAT'
    mod.object = tool_obj
    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = target_obj.evaluated_get(depsgraph)
    new_mesh = bpy.data.meshes.new_from_object(eval_obj)
    if len(new_mesh.polygons) == 0:
        bpy.data.meshes.remove(new_mesh)
        mod.solver = 'EXACT'
        bpy.context.view_layer.update()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = target_obj.evaluated_get(depsgraph)
        new_mesh = bpy.data.meshes.new_from_object(eval_obj)
    old_mesh = target_obj.data
    target_obj.modifiers.remove(mod)
    target_obj.data = new_mesh
    bpy.data.meshes.remove(old_mesh)
    bpy.data.objects.remove(tool_obj, do_unlink=True)

def make_obj_from_bm(name, bm):
    obj = new_mesh_obj(name)
    bm.to_mesh(obj.data)
    bm.free()
    return obj

# Outer frame: 245.8 x 354.7 x 18.0 mm (X=-4.8..241.0, Y=-29.5..325.2, R=3.0)
part_b = make_obj_from_bm("Part_B_Master", bm_rounded_prism(-4.8, 241.0, -29.5, 325.2, 0.0, 18.0, r=3.0, segs=8))
apply_bool(part_b, bm_frustum_rect(15.34, 220.46, 4.54, 308.36, -0.2, 15.64, 220.16, 4.84, 308.06, 0.30), 'DIFFERENCE', "CRT_MicroChamfer")
apply_bool(part_b, bm_frustum_rect(15.64, 220.16, 4.84, 308.06, 0.25, 19.1, 216.7, 8.3, 304.6, 6.02), 'DIFFERENCE', "CRT_Bevel")
apply_bool(part_b, bm_rounded_prism(19.1, 216.7, 8.3, 304.6, 5.95, 18.5, r=0.0), 'DIFFERENCE', "Screen_Through")
apply_bool(part_b, bm_rounded_prism(-0.3, 220.3, -0.3, 310.3, 3.0, 18.5, r=6.3, segs=8), 'DIFFERENCE', "Monitor_Cradle_Pocket")

# Rear retaining lips + top-right detent tab
apply_bool(part_b, bm_rounded_prism(-1.0, 1.7, 6.0, 304.0, 16.9, 18.0, r=0.0), 'UNION', "Left_Rear_Lip")
apply_bool(part_b, bm_rounded_prism(218.3, 221.0, 6.0, 304.0, 9.0, 11.0, r=0.0), 'UNION', "Right_Rear_Lip")
apply_bool(part_b, bm_rounded_prism(76.0, 214.0, -1.0, 1.7, 9.0, 11.0, r=0.0), 'UNION', "BottomRight_Rear_Lip")
apply_bool(part_b, bm_frustum_rect(196.0, 206.0, 310.3, 311.0, 8.0, 196.0, 206.0, 309.3, 311.0, 9.0), 'UNION', "Detent_Print_Chamfer")
apply_bool(part_b, bm_rounded_prism(196.0, 206.0, 309.3, 311.0, 9.0, 11.0, r=0.0), 'UNION', "Detent_Tab")
apply_bool(part_b, bm_rounded_prism(196.0, 206.0, 312.6, 314.2, 3.0, 18.5, r=0.0), 'DIFFERENCE', "Detent_Flex_Slot")

# Port & control bays
apply_bool(part_b, bm_rounded_prism(14.0, 65.0, 310.0, 325.8, 6.0, 18.5, r=0.0), 'DIFFERENCE', "TopLeft_USBC_Bay")
apply_bool(part_b, bm_rounded_prism(33.0, 47.0, 304.6, 325.8, 1.5, 3.1, r=0.0), 'DIFFERENCE', "USBC_Nose_Relief")
apply_bool(part_b, bm_rounded_prism(12.0, 73.0, -30.0, 0.0, 3.0, 18.5, r=0.0), 'DIFFERENCE', "BottomLeft_Control_Bay")

# Snow White side grooves (2.0 mm wide x 6.0 mm pitch)
groove_ys = []
y_cur = 177.35
while y_cur <= 320.0:
    groove_ys.append(y_cur); y_cur += 6.0
y_cur = 177.35 - 6.0
while y_cur >= -24.0:
    groove_ys.append(y_cur); y_cur -= 6.0
for idx, gy in enumerate(groove_ys):
    apply_bool(part_b, bm_rounded_prism(239.2, 241.5, gy - 1.0, gy + 1.0, -0.2, 18.2, r=0.0), 'DIFFERENCE', f"GR_{idx}")
    apply_bool(part_b, bm_rounded_prism(-5.2, -3.8, gy - 1.0, gy + 1.0, -0.2, 18.2, r=0.0), 'DIFFERENCE', f"GL_{idx}")

# Chin windows: 14x14 badge (lower-left) & 6x2 LED (lower-right)
apply_bool(part_b, bm_rounded_prism(18.0, 32.0, -21.5, -7.5, -0.2, 18.5, r=0.0), 'DIFFERENCE', "Badge_Window")
apply_bool(part_b, bm_frustum_rect(17.7, 32.3, -21.8, -7.2, -0.1, 18.0, 32.0, -21.5, -7.5, 0.30), 'DIFFERENCE', "Badge_Chamfer")
apply_bool(part_b, bm_rounded_prism(204.0, 210.0, -15.5, -13.5, -0.2, 18.5, r=0.0), 'DIFFERENCE', "LED_Window")

# Split at Y = 177.35
part_b_upper = part_b; part_b_upper.name = "Part_B_Upper"
part_b_lower = part_b_upper.copy(); part_b_lower.data = part_b_upper.data.copy(); part_b_lower.name = "Part_B_Lower"
bpy.context.collection.objects.link(part_b_lower)

def bisect_half(obj, keep_upper=True):
    bm = bmesh.new(); bm.from_mesh(obj.data)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], plane_co=(0.0, 177.35, 0.0), plane_no=(0.0, 1.0, 0.0), clear_inner=keep_upper, clear_outer=(not keep_upper))
    open_edges = [e for e in bm.edges if e.is_boundary]
    if open_edges: bmesh.ops.holes_fill(bm, edges=open_edges)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data); bm.free()

bisect_half(part_b_upper, True)
bisect_half(part_b_lower, False)

# Interlock lip + Left 45-deg lap joint + 0.35 mm detent (0.20 mm clearance)
apply_bool(part_b_lower, bm_rounded_prism(220.0, 223.0, 177.2, 178.55, 1.2, 2.04, r=0.0), 'UNION', "Interlock_Lip_Lower")
apply_bool(part_b_upper, bm_rounded_prism(220.0, 223.2, 177.2, 178.75, 1.00, 2.24, r=0.0), 'DIFFERENCE', "Interlock_Pocket_Upper")

bm_lap_tongue = bmesh.new()
poly_yz = [(177.2, 3.0), (182.35, 8.0), (182.35, 16.9), (177.2, 16.9)]
v_l = [bm_lap_tongue.verts.new((-2.30, py, pz)) for (py, pz) in poly_yz]
v_r = [bm_lap_tongue.verts.new((0.2, py, pz)) for (py, pz) in poly_yz]
bm_lap_tongue.faces.new(list(reversed(v_l))); bm_lap_tongue.faces.new(v_r)
for i in range(4): j = (i+1)%4; bm_lap_tongue.faces.new((v_l[i], v_l[j], v_r[j], v_r[i]))
bmesh.ops.recalc_face_normals(bm_lap_tongue, faces=bm_lap_tongue.faces)
apply_bool(part_b_lower, bm_lap_tongue, 'UNION', "Left_Lap_Tongue")

bm_bump = bmesh.new()
pts_xy = [(-2.15, 179.6), (-2.65, 180.2), (-2.65, 180.8), (-2.15, 181.4)]
vb = [bm_bump.verts.new((px, py, 9.0)) for (px, py) in pts_xy]
vt = [bm_bump.verts.new((px, py, 16.0)) for (px, py) in pts_xy]
bm_bump.faces.new(list(reversed(vb))); bm_bump.faces.new(vt)
for i in range(4): j = (i+1)%4; bm_bump.faces.new((vb[i], vb[j], vt[j], vt[i]))
bmesh.ops.recalc_face_normals(bm_bump, faces=bm_bump.faces)
apply_bool(part_b_lower, bm_bump, 'UNION', "Left_Detent_Bump")

bm_lap_pocket = bmesh.new()
poly_yz_p = [(177.2, 2.80), (182.55, 8.0), (182.55, 17.10), (177.2, 17.10)]
vp_l = [bm_lap_pocket.verts.new((-2.50, py, pz)) for (py, pz) in poly_yz_p]
vp_r = [bm_lap_pocket.verts.new((0.2, py, pz)) for (py, pz) in poly_yz_p]
bm_lap_pocket.faces.new(list(reversed(vp_l))); bm_lap_pocket.faces.new(vp_r)
for i in range(4): j = (i+1)%4; bm_lap_pocket.faces.new((vp_l[i], vp_l[j], vp_r[j], vp_r[i]))
bmesh.ops.recalc_face_normals(bm_lap_pocket, faces=bm_lap_pocket.faces)
apply_bool(part_b_upper, bm_lap_pocket, 'DIFFERENCE', "Left_Lap_Pocket")

bm_rec = bmesh.new()
pts_rec = [(-2.25, 179.5), (-2.80, 180.15), (-2.80, 180.85), (-2.25, 181.5)]
vrb = [bm_rec.verts.new((px, py, 8.8)) for (px, py) in pts_rec]
vrt = [bm_rec.verts.new((px, py, 16.2)) for (px, py) in pts_rec]
bm_rec.faces.new(list(reversed(vrb))); bm_rec.faces.new(vrt)
for i in range(4): j = (i+1)%4; bm_rec.faces.new((vrb[i], vrb[j], vrt[j], vrt[i]))
bmesh.ops.recalc_face_normals(bm_rec, faces=bm_rec.faces)
apply_bool(part_b_upper, bm_rec, 'DIFFERENCE', "Left_Detent_Recess")

# Right-flank screwless compliant snap latch (1.80 mm = 4 x 0.45 mm wall multiple)
apply_bool(part_b_upper, bm_rounded_prism(220.2, 230.0, 188.0, 194.0, 2.8, 13.5, r=0.0), 'UNION', "Snap_Anchor")
apply_bool(part_b_upper, bm_rounded_prism(228.2, 230.0, 171.0, 188.2, 4.5, 13.5, r=0.0), 'UNION', "Snap_Arm")
bm_barb = bmesh.new()
barb_xy = [(229.8, 171.0), (231.0, 172.0), (231.0, 173.2), (229.8, 174.2)]
vb_b = [bm_barb.verts.new((px, py, 4.5)) for (px, py) in barb_xy]
vb_t = [bm_barb.verts.new((px, py, 13.5)) for (px, py) in barb_xy]
bm_barb.faces.new(list(reversed(vb_b))); bm_barb.faces.new(vb_t)
for i in range(4): j = (i+1)%4; bm_barb.faces.new((vb_b[i], vb_b[j], vb_t[j], vb_t[i]))
bmesh.ops.recalc_face_normals(bm_barb, faces=bm_barb.faces)
apply_bool(part_b_upper, bm_barb, 'UNION', "Snap_Barb")
apply_bool(part_b_upper, bm_rounded_prism(227.7, 230.0, 171.0, 173.5, 13.4, 16.8, r=0.0), 'UNION', "Snap_FingerTab")

apply_bool(part_b_lower, bm_rounded_prism(230.2, 239.3, 168.0, 177.35, 2.8, 13.5, r=0.0), 'UNION', "Catch_Block")
apply_bool(part_b_lower, bm_rounded_prism(229.8, 231.4, 171.6, 174.4, 4.2, 14.0, r=0.0), 'DIFFERENCE', "Catch_Notch")
apply_bool(part_b_lower, bm_frustum_rect(230.0, 231.5, 175.8, 177.4, 4.2, 230.0, 231.5, 175.8, 177.4, 14.0), 'DIFFERENCE', "Catch_LeadIn")

# Mirror X so Z=0 face-down print has true front-view L/R
for name in ["Part_B_Upper", "Part_B_Lower"]:
    obj = bpy.data.objects[name]
    bm = bmesh.new(); bm.from_mesh(obj.data)
    for v in bm.verts: v.co.x = -v.co.x
    for f in bm.faces: f.normal_flip()
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(obj.data); bm.free()

# Chin inserts
part_b_badge = make_obj_from_bm("Part_B_Badge", bm_rounded_prism(0.0, 15.4, 0.0, 15.4, 0.0, 0.8, r=0.4, segs=4))
apply_bool(part_b_badge, bm_rounded_prism(0.82, 14.58, 0.82, 14.58, 0.75, 3.8, r=0.2, segs=4), 'UNION', "Badge_Stem")
apply_bool(part_b_badge, bm_rounded_prism(0.62, 0.90, 4.0, 11.4, 0.8, 3.8, r=0.0), 'UNION', "Badge_Rib_L")
apply_bool(part_b_badge, bm_rounded_prism(14.50, 14.78, 4.0, 11.4, 0.8, 3.8, r=0.0), 'UNION', "Badge_Rib_R")

part_b_led = make_obj_from_bm("Part_B_LED", bm_rounded_prism(0.0, 7.4, 0.0, 3.4, 0.0, 0.8, r=0.3, segs=4))
apply_bool(part_b_led, bm_rounded_prism(0.82, 6.58, 0.82, 2.58, 0.75, 3.8, r=0.1, segs=4), 'UNION', "LED_Stem")
apply_bool(part_b_led, bm_rounded_prism(0.62, 0.90, 1.2, 2.2, 0.8, 3.8, r=0.0), 'UNION', "LED_Rib_L")
apply_bool(part_b_led, bm_rounded_prism(6.50, 6.78, 1.2, 2.2, 0.8, 3.8, r=0.0), 'UNION', "LED_Rib_R")
