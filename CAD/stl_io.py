"""
The one way a manifold3d solid becomes an STL file here, and the one judgement of an STL file as a slicer reads it.

An STL is a float32 triangle soup that every reader re-merges by vertex position. manifold3d keeps coincident
vertices distinct where pieces of a solid touch along an edge, and keeps slivers finer than float32 can hold, so its
in-memory mesh is a clean manifold while the merged file has pinched edges (shared by 4 or more faces). So write_stl
simplifies the solid to SIMPLIFY_TOL (surfaces move less than that: 1 um, far below a 0.4 mm nozzle), rounds and
welds it to float32 (as_float32) and writes exactly those arrays, then reads the file back
as a slicer does and refuses it if it is not a closed 2-manifold of the expected body count. Every shipped STL,
the Blender bezel parts (CAD/partb_mesh.py) included, is judged again by gates_of_heck's CAD layer
(checks/cad_mesh.py, the push gate and CAD/build_all.sh).
"""

from collections import Counter

import numpy as np

SIMPLIFY_TOL = 1e-3  # mm


def judge_file(path, shells=1):
    """Faults of the STL at `path` read as a slicer reads it (vertices joined by exact float32 equality); [].
    shells=None skips the body count (an intermediate relief may be several islands)."""
    import trimesh

    # Merge as a slicer's reader does: admesh (PrusaSlicer, Bambu Studio) joins facets by EXACT float32 vertex
    # equality and runs its nearby-vertex repair only when facets are left unconnected. trimesh.load's own merge
    # rounds to 8 decimals, which near zero joins float32-distinct points no slicer joins (a stricter, different
    # instrument: it reported pinches in files every edge of which admesh connects).
    raw = trimesh.load(path, process=False)
    uniq, inv = np.unique(np.asarray(raw.vertices, np.float32), axis=0, return_inverse=True)
    tm = trimesh.Trimesh(uniq, inv.reshape(-1)[raw.faces], process=False)
    uses = Counter(Counter(map(tuple, np.sort(tm.edges, axis=1))).values())
    faults = []
    bad = sum(n for k, n in uses.items() if k != 2)
    if bad:
        faults.append(f"{bad} edges not shared by exactly 2 faces {dict(sorted(uses.items()))}")
    if tm.volume <= 0:
        faults.append(f"volume {tm.volume:.1f} mm3 (inside out)")
    n = tm.body_count  # bodies joined through shared vertices (face adjacency would split at a pinch)
    if shells is not None and n != shells:
        faults.append(f"{n} bodies, want {shells}")
    return faults, tm


def as_float32(man):
    """(vertices, triangles) as the float32 file will hold them: vertices rounded to float32 and welded where
    rounding made them one point, the triangles that collapsed to zero area (a repeated vertex) dropped. These are
    the arrays written, so nothing re-splits them afterwards (manifold3d's to_mesh would). If rounding joined two
    separate surfaces (a real touch, not a sliver), an edge is still not shared by exactly two faces and write_stl
    refuses the file: this removes slivers finer than the format, never a defect of the shape."""
    mesh = man.simplify(SIMPLIFY_TOL).to_mesh()
    v32 = np.asarray(mesh.vert_properties)[:, :3].astype(np.float32)
    uniq, inv = np.unique(v32, axis=0, return_inverse=True)  # exact float32 equality: how admesh matches
    f = inv.reshape(-1)[np.asarray(mesh.tri_verts)]
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    return uniq, f.astype(np.uint32)


def write_stl(man, path, header="ZSUS v21", shells=1):
    """Round to float32 (as_float32), write binary, read back, refuse a file a slicer would read as broken."""
    v, f = as_float32(man)
    tri = v[f]
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = nrm, tri
    with open(path, "wb") as fh:
        fh.write(header.encode()[:80].ljust(80, b" "))
        fh.write(np.uint32(len(f)).tobytes())
        fh.write(rec.tobytes())
    faults, _ = judge_file(path, shells)
    if faults:
        raise SystemExit(f"x {path} as a slicer reads it: " + "; ".join(faults))
