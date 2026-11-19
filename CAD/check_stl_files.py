"""
Every shipped STL, judged AS THE FILE a slicer reads, not as the solid the generator held in memory.

    python3 CAD/check_stl_files.py [ROOT]

An STL is a triangle soup: every reader merges vertices by position. manifold3d keeps coincident vertices
distinct where two pieces of a solid touch along an edge, so its in-memory mesh is "watertight" while the file,
once merged, has edges shared by 4, 6 or more faces (a pinch). The generators' own watertight checks read the
in-memory mesh and cannot see that; this check reloads each file as a slicer does (trimesh.load merges) and
fails on any edge not shared by exactly two faces, a non-positive volume (inside out), or a shell count other
than the part's own. Found 2026-11-18 by the 3d-print-cad skill's mesh_gates.py: v21.0.0 shipped 171 / 336 /
1084 pinched edges in Part_A_Mount / Part_A_Test / Part_B_Emblem_Cthulhu.
"""

import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stl_io import judge_file

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELLS = {"Part_B_FitGauge": 4}  # four separate gauge pieces on one plate; every other part is one body


def judge(path):
    name = os.path.splitext(os.path.basename(path))[0]
    faults, tm = judge_file(path, SHELLS.get(name, 1))
    n = tm.body_count
    head = f"{'FAIL' if faults else 'OK  '} {name}: {n} {'body' if n == 1 else 'bodies'}, {tm.volume:.1f} mm3"
    print(head + "".join(f"; {x}" for x in faults))
    return not faults


paths = sorted(glob.glob(os.path.join(ROOT, "STLs", "*.stl")))
assert paths, f"no STLs under {ROOT}/STLs"  # a check over nothing passes nothing
ok = [judge(p) for p in paths]
if not all(ok):
    raise SystemExit(f"x {ok.count(False)} of {len(ok)} STL files fail as a slicer reads them")
print(f"GATE all {len(ok)} STL files are closed 2-manifolds as written")
