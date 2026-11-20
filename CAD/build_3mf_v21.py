"""
Build ZSUS_v21_Complete_P1S_PLA.3mf (Bambu Studio project) from STLs/ and CAD/layout.json, and prove it by slicing
every plate.

Run:  python3 CAD/build_3mf_v21.py                  (needs Bambu Studio and gates_of_heck: $GOH_DIR, default
                                                     ~/Projects/gates_of_heck)
      python3 CAD/build_3mf_v21.py --emblem X.stl   one-plate project for an emblem tile, written next to X.stl

The plates, per-object settings, support regions and what the slice must show are data, in CAD/layout.json. The build,
the slice and its gates are gates_of_heck's CAD layer (checks/cad_bambu.py), the same code the push gate runs
(gates/cad_gate.sh): any slicing warning, a support request the G-code does not honour, support missing under a region
the generator named (STLs/Part_B_supports.json) or far from all of them, the wrong nozzle or bed, open-air travel over
its cap.

  plate 1  Fit tests (print first)   Part_A_Test (collar + ball), Part_B_FitGauge (monitor side channels)
  plate 2  Part A mount + accents     Part_A_Mount, Part_B_Emblem (blank snap-in tile), Part_B_LED
  plate 3  Part B lower bezel
  plate 4  Part B upper bezel         tree supports at the snap-arm tip and the left lap corner
  plate 5  Cthulhu emblem (optional)  Part_B_Emblem_Cthulhu: snap-in tile with the CC BY Cthulhu head as an onlay
"""

import json
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GOH = os.environ.get("GOH_DIR", os.path.expanduser("~/Projects/gates_of_heck"))
sys.path.insert(0, os.path.join(GOH, "checks"))
from cad_bambu import run  # noqa: E402  (gates_of_heck's CAD layer)
from cad_project import LayoutError  # noqa: E402

LAYOUT = os.path.join(HERE, "layout.json")


def emblem_layout(lay, stl):
    """One plate, one tile: an onlay (wider than the 18 mm cap) gets tree supports from the plate."""
    with open(stl, "rb") as fh:
        (n,) = struct.unpack("<I", fh.read(84)[80:])
        xs, ys = [], []
        for _ in range(n):
            v = struct.unpack("<12f", fh.read(50)[:48])
            xs += v[3::3]
            ys += v[4::3]
    onlay = max(max(xs) - min(xs), max(ys) - min(ys)) > 18.05
    name = os.path.splitext(os.path.basename(stl))[0]
    preset = "EMBLEM_ONLAY" if onlay else "EMBLEM_FINE"
    obj = {"name": name, "stl": os.path.basename(stl), "plate": 1, "centre": [128.0, 128.0], "preset": preset}
    return dict(
        lay,
        plates={"1": f"1 {name} (0.08 mm)"},
        objects=[obj],
        air_travel={},
        out_3mf=name + "_P1S_PLA.3mf",
        report=name + "_slice_report.json",
    )


def main(argv):
    with open(LAYOUT) as fh:
        lay = json.load(fh)
    root = out_dir = ROOT
    if argv[:1] == ["--emblem"]:
        stl = os.path.abspath(argv[1])
        lay, root = emblem_layout(lay, stl), os.path.dirname(stl)
        out_dir = root
    try:
        rep, fails = run(lay, root, out_dir)
    except (OSError, LayoutError) as e:
        print(f"x {e}")
        return 2
    for f in fails:
        print(f"x {f}")
    if fails:
        return 1
    report = os.path.relpath(os.path.join(out_dir, lay["report"]), ROOT)
    print(f"all {len(rep['plates'])} plates sliced; report in {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
