"""
Mesh helpers for CAD/build_part_b_blender_v21.py (Blender bmesh primitives, checked MANIFOLD booleans,
mesh gates and binary STL export). Imported by that script; runs only inside Blender.
"""

import itertools
import math
import struct

import bmesh
import bpy


def new_mesh_obj(name):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def bm_rounded_prism(x0, x1, y0, y1, z0, z1, r=0.0, segs=8):
    bm = bmesh.new()
    if r <= 0.001:
        v = [
            bm.verts.new((x0, y0, z0)),
            bm.verts.new((x1, y0, z0)),
            bm.verts.new((x1, y1, z0)),
            bm.verts.new((x0, y1, z0)),
            bm.verts.new((x0, y0, z1)),
            bm.verts.new((x1, y0, z1)),
            bm.verts.new((x1, y1, z1)),
            bm.verts.new((x0, y1, z1)),
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


def bm_profiled_prism(x0, x1, y0, y1, r, rings, segs=8):
    """Closed solid through rounded-rectangle rings (z, inset): chamfers and rounds on the perimeter edges."""
    bm = bmesh.new()
    loops = []
    for z, d in rings:
        rr = max(r - d, 0.05)
        cs = [
            (x1 - d - rr, y1 - d - rr, 0.0),
            (x0 + d + rr, y1 - d - rr, 0.5),
            (x0 + d + rr, y0 + d + rr, 1.0),
            (x1 - d - rr, y0 + d + rr, 1.5),
        ]
        loop = []
        for cx, cy, a0 in cs:
            for i in range(segs + 1):
                a = math.pi * (a0 + 0.5 * i / segs)
                loop.append(bm.verts.new((cx + rr * math.cos(a), cy + rr * math.sin(a), z)))
        loops.append(loop)
    bm.faces.new(list(reversed(loops[0])))
    bm.faces.new(loops[-1])
    n = len(loops[0])
    for lo_, hi_ in itertools.pairwise(loops):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo_[i], lo_[j], hi_[j], hi_[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_frustum_rect(x0_b, x1_b, y0_b, y1_b, z0, x0_t, x1_t, y0_t, y1_t, z1):
    bm = bmesh.new()
    vb = [
        bm.verts.new((x0_b, y0_b, z0)),
        bm.verts.new((x1_b, y0_b, z0)),
        bm.verts.new((x1_b, y1_b, z0)),
        bm.verts.new((x0_b, y1_b, z0)),
    ]
    vt = [
        bm.verts.new((x0_t, y0_t, z1)),
        bm.verts.new((x1_t, y0_t, z1)),
        bm.verts.new((x1_t, y1_t, z1)),
        bm.verts.new((x0_t, y1_t, z1)),
    ]
    bm.faces.new((vb[0], vb[3], vb[2], vb[1]))
    bm.faces.new((vt[0], vt[1], vt[2], vt[3]))
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_prism_xy(pts_xy, z0, z1):
    """Vertical prism over an XY polygon."""
    bm = bmesh.new()
    vb = [bm.verts.new((px, py, z0)) for (px, py) in pts_xy]
    vt = [bm.verts.new((px, py, z1)) for (px, py) in pts_xy]
    bm.faces.new(list(reversed(vb)))
    bm.faces.new(vt)
    n = len(pts_xy)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vb[i], vb[j], vt[j], vt[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_prism_yz(pts_yz, x0, x1):
    """Prism along X over a YZ polygon."""
    bm = bmesh.new()
    vl = [bm.verts.new((x0, py, pz)) for (py, pz) in pts_yz]
    vr = [bm.verts.new((x1, py, pz)) for (py, pz) in pts_yz]
    bm.faces.new(list(reversed(vl)))
    bm.faces.new(vr)
    n = len(pts_yz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((vl[i], vl[j], vr[j], vr[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def bm_prism_xz(pts_xz, y0, y1):
    """Prism along Y over an XZ polygon."""
    bm = bmesh.new()
    va = [bm.verts.new((px, y0, pz)) for (px, pz) in pts_xz]
    vb = [bm.verts.new((px, y1, pz)) for (px, pz) in pts_xz]
    bm.faces.new(list(reversed(va)))
    bm.faces.new(vb)
    n = len(pts_xz)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((va[i], va[j], vb[j], vb[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def mesh_report(me):
    """(non-manifold edge count, shell count) of a mesh datablock."""
    bm = bmesh.new()
    bm.from_mesh(me)
    bad = sum(1 for e in bm.edges if not e.is_manifold)
    seen, shells = set(), 0
    for f in bm.faces:
        if f.index in seen:
            continue
        shells += 1
        stack = [f]
        while stack:
            g = stack.pop()
            if g.index in seen:
                continue
            seen.add(g.index)
            for e in g.edges:
                stack.extend(x for x in e.link_faces if x.index not in seen)
    bm.free()
    return bad, shells


def apply_bool(target_obj, tool_bm, op="DIFFERENCE", name="BoolTool"):
    tool_obj = new_mesh_obj(name)
    tool_bm.to_mesh(tool_obj.data)
    tool_bm.free()
    mod = target_obj.modifiers.new(name=name, type="BOOLEAN")
    mod.operation = op
    mod.solver = "MANIFOLD"
    mod.object = tool_obj
    bpy.context.view_layer.update()
    eval_obj = target_obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    new_mesh = bpy.data.meshes.new_from_object(eval_obj)
    bad, _ = mesh_report(new_mesh)
    if len(new_mesh.polygons) == 0 or bad:
        raise SystemExit(
            f"boolean {name} on {target_obj.name} failed: {len(new_mesh.polygons)} faces, {bad} non-manifold edges"
        )
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


def duplicate(obj, name):
    dup = obj.copy()
    dup.data = obj.data.copy()
    dup.name = name
    bpy.context.collection.objects.link(dup)
    return dup


def write_stl(obj, path):
    me = obj.data
    me.calc_loop_triangles()
    tris = me.loop_triangles
    with open(path, "wb") as fh:
        fh.write(obj.name.encode()[:80].ljust(80, b"\0"))
        fh.write(struct.pack("<I", len(tris)))
        for t in tris:
            n = t.normal
            fh.write(struct.pack("<3f", n.x, n.y, n.z))
            for vi in t.vertices:
                c = me.vertices[vi].co
                fh.write(struct.pack("<3f", c.x, c.y, c.z))
            fh.write(b"\0\0")


def signed_volume(me):
    me.calc_loop_triangles()
    vol = 0.0
    for t in me.loop_triangles:
        a, b, c = (me.vertices[i].co for i in t.vertices)
        vol += a.dot(b.cross(c)) / 6.0
    return vol
