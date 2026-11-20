"""
Support enforcers for the Bambu project (CAD/build_3mf_v21.py): a part's generator names the boxes where it needs
support (STLs/Part_B_supports.json), each becomes a support_enforcer volume of that object, and the sliced G-code is
gated to have support under every box and none far from one.
"""

import re

import numpy as np

# a tree's foot spreads up to ~10 mm on the plate (the Upper's lap-corner trunk stands 9.5 mm off); tree(auto) put a
# support in the Upper's USB-C nose slot about 150 mm from both regions
REACH = 15.0


def box_object(oid, box, offset):
    """A closed, outward-wound box mesh as a 3MF <object>, in the part's mesh frame (STL coordinates - offset)."""
    x0, x1, y0, y1, z0, z1 = box
    corners = [(x, y, z) for z in (z0, z1) for y in (y0, y1) for x in (x0, x1)]
    tris = [(0, 2, 1), (1, 2, 3), (4, 5, 6), (5, 7, 6), (0, 1, 4), (1, 5, 4),
            (2, 6, 3), (3, 6, 7), (0, 4, 2), (2, 4, 6), (1, 3, 5), (3, 7, 5)]  # fmt: skip
    vs = "".join(
        f'\n     <vertex x="{x - offset[0]:.6f}" y="{y - offset[1]:.6f}" z="{z - offset[2]:.6f}"/>'
        for x, y, z in corners
    )
    ts = "".join(f'\n     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in tris)
    return (
        f'  <object id="{oid}" type="model">\n   <mesh>\n    <vertices>{vs}\n    </vertices>'
        f"\n    <triangles>{ts}\n    </triangles>\n   </mesh>\n  </object>\n"
    )


def add_enforcers(files, oid, regions, next_id):
    """Add one support_enforcer volume per region to wrapper object oid; returns the next free object id."""
    model = files["3D/3dmodel.model"].decode()
    m = re.search(
        rf'<object id="{oid}"[^>]*>\s*<components>\s*'
        r'(<component p:path="([^"]+)" objectid="\d+"[^>]*transform="([^"]+)"/>)',
        model,
    )
    comp, path, tf = m.groups()
    offset = list(map(float, tf.split()))[9:12]
    obj_file = path.lstrip("/")
    sub = files[obj_file].decode()
    ms = files["Metadata/model_settings.config"].decode()
    parts = ""
    for r in regions:
        eid, next_id = next_id, next_id + 1
        sub = sub.replace(" </resources>", box_object(eid, r["box"], offset) + " </resources>", 1)
        model = model.replace(comp, comp + f'\n    <component p:path="{path}" objectid="{eid}" transform="{tf}"/>', 1)
        mat = f"1 0 0 {offset[0]} 0 1 0 {offset[1]} 0 0 1 {offset[2]} 0 0 0 1"
        parts += (
            f'\n    <part id="{eid}" subtype="support_enforcer">'
            f'\n      <metadata key="name" value="support: {r["why"]}"/>'
            f'\n      <metadata key="matrix" value="{mat}"/>\n    </part>'
        )
    ms = re.sub(rf'(<object id="{oid}">.*?</part>)', lambda q: q.group(1) + parts, ms, count=1, flags=re.DOTALL)
    files["3D/3dmodel.model"], files[obj_file] = model.encode(), sub.encode()
    files["Metadata/model_settings.config"] = ms.encode()
    return next_id


def support_points(gcode):
    """(x, y, z) of every extruding move inside a ; FEATURE: Support* section, in plate coordinates."""
    feat, x, y, zc, pts = "", 0.0, 0.0, 0.0, []
    for line in gcode.splitlines():
        if line.startswith("; FEATURE:"):
            feat = line[10:].strip()
        elif line.startswith(("G1 ", "G0 ", "G2 ", "G3 ")):
            w = {t[0]: float(t[1:]) for t in line.split(";")[0].split()[1:] if t[0] in "XYZE" and len(t) > 1}
            zc = w.get("Z", zc)
            nx, ny = w.get("X", x), w.get("Y", y)
            if feat.startswith("Support") and w.get("E", 0) > 0 and ("X" in w or "Y" in w):
                pts.append((nx, ny, zc))
            x, y = nx, ny
    return np.array(pts).reshape(-1, 3)


def gate_regions(gcode, t, origin, regions, name, plate):
    """Support under every region (moves within 0.5 mm of its footprint, at its top), none beyond REACH in XY."""
    local = support_points(gcode) - np.array([t[0] - origin[0], t[1] - origin[1], 0.0])  # plate -> STL coordinates
    boxes = np.array([r["box"] for r in regions])
    dx = np.maximum(np.maximum(boxes[None, :, 0] - local[:, None, 0], local[:, None, 0] - boxes[None, :, 1]), 0)
    dy = np.maximum(np.maximum(boxes[None, :, 2] - local[:, None, 1], local[:, None, 1] - boxes[None, :, 3]), 0)
    dist = np.hypot(dx, dy).min(1) if len(local) else np.zeros(0)
    under = [
        int(((local[:, 0] >= b[0] - 0.5) & (local[:, 0] <= b[1] + 0.5) & (local[:, 1] >= b[2] - 0.5)
             & (local[:, 1] <= b[3] + 0.5) & (local[:, 2] >= b[5] - 1.0)).sum())
        for b in boxes
    ]  # fmt: skip
    print(
        f"    plate {plate} {name}: support moves under each region {under}, "
        f"farthest {dist.max(initial=0):.1f} mm off (max {REACH})"
    )
    bare = [r["why"] for n, r in zip(under, regions, strict=True) if not n]
    assert not bare, f"{name}: a support region got no support: {bare}"
    far = local[dist > REACH]
    assert not len(far), f"{name}: support outside its regions, e.g. at {far[0].round(1).tolist()}"
    return under
