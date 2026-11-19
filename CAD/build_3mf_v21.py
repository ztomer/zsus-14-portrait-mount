"""
Build ZSUS_v21_Complete_P1S_PLA.3mf (Bambu Studio project) from STLs/ and verify it by slicing every plate
with the Bambu Studio CLI.

Run:  python3 CAD/build_3mf_v21.py        (needs Bambu Studio installed, numpy)

Why a script: the v20 project was hand-edited and drifted from its README (0.2 mm nozzle profile, Part_B_Lower on
no plate and off the bed, plate names swapped, no per-object layer heights, aux fan 70 %, supports on).
Everything below is the README's print table, applied mechanically:

  plate 1  Fit tests (print first)   Part_A_Test (collar + ball), Part_B_FitGauge (monitor side channels)
  plate 2  Part A mount + accents     Part_A_Mount, Part_B_Emblem (blank snap-in tile), Part_B_LED
  plate 3  Part B lower bezel
  plate 4  Part B upper bezel
  plate 5  Cthulhu emblem (optional)  Part_B_Emblem_Cthulhu: snap-in tile with the CC BY Cthulhu head as an onlay

  python3 CAD/build_3mf_v21.py --emblem X.stl   one-plate project for an emblem tile, written next to X.stl
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gcode_travel import air_travel

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_3MF = os.path.join(ROOT, "ZSUS_v21_Complete_P1S_PLA.3mf")
BBS = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
PROFILES = "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL"
MACHINE, PROCESS, FILAMENT = (
    "Bambu Lab P1S 0.4 nozzle",
    "0.20mm Standard @BBL X1C",
    "Generic PLA",
)
BED = 256.0
PLATE_STRIDE = BED * 1.2  # Bambu lays plates out on a grid with a 1/5 bed gap
EXCLUDE = (18.0, 28.0)  # P1S bed_exclude_area, front-left corner

PART_A = {
    "layer_height": "0.16",
    "wall_loops": "5",
    "sparse_infill_density": "40%",
    "sparse_infill_pattern": "gyroid",
}
PART_B = {
    "layer_height": "0.2",
    "wall_loops": "3",
    "sparse_infill_density": "15%",
    "sparse_infill_pattern": "gyroid",
}
ACCENT = {"layer_height": "0.16", "wall_loops": "3", "sparse_infill_density": "100%"}

# Chin emblems: fine layers for the relief. An onlay relief overhangs the tile's cap flat (it rests on the chin face),
# so tree supports rise from the plate to carry it; the snap features are all 45 deg or steeper and take none.
EMBLEM_FINE = {"layer_height": "0.08", "wall_loops": "3", "sparse_infill_density": "100%", "brim_type": "no_brim"}
EMBLEM_ONLAY = dict(EMBLEM_FINE, enable_support="1", support_type="tree(auto)", support_on_build_plate_only="1")

# name, plate (1-based), centre on that plate (x, y), per-object settings
LAYOUT = [
    ("Part_A_Test", 1, (128.0, 90.0), dict(PART_A, brim_type="outer_only")),
    ("Part_B_FitGauge", 1, (128.0, 190.0), dict(PART_B, brim_type="no_brim")),
    ("Part_A_Mount", 2, (110.0, 140.0), dict(PART_A)),
    ("Part_B_Emblem", 2, (200.0, 160.0), dict(ACCENT)),
    ("Part_B_LED", 2, (200.0, 120.0), dict(ACCENT)),
    ("Part_B_Lower", 3, (128.0, 142.0), dict(PART_B, brim_type="no_brim")),
    ("Part_B_Upper", 4, (128.0, 135.0), dict(PART_B, brim_type="no_brim")),
    ("Part_B_Emblem_Cthulhu", 5, (128.0, 128.0), dict(EMBLEM_ONLAY)),
]
PLATE_NAMES = {
    1: "1 Fit tests (print first)",
    2: "2 Part A mount + accents",
    3: "3 Part B lower bezel",
    4: "4 Part B upper bezel",
    5: "5 Cthulhu emblem (optional, 0.08 mm, supports)",
}
# filament_colour: a warm light grey close to Apple "Platinum" (Snow White was never bright white); it only
# tints the preview, so load a matte warm-grey PLA to match.
PROJECT = {
    "curr_bed_type": "Textured PEI Plate",
    "enable_support": "0",
    "brim_type": "auto_brim",
    "filament_colour": ["#D3CFC6"],
    # Avoid crossing walls: the first bezel print came off strung (2026-11-19), hairs across the pocket the monitor
    # slides into. Routing travel inside the part cuts the open-air hops on the Lower from 552 to about 180.
    "reduce_crossing_wall": "1",
}
PROCESS_OVERRIDES = ("reduce_crossing_wall",)  # shown as changed from the system process in Bambu Studio
# Travel over open air (CAD/gcode_travel.py) on the two bezel plates: at most this many hops each. The v21.1.0
# project made 552 (Lower) and 512 (Upper); about half of what remains is the move to each layer's start, lifted and
# wiped, which avoid-crossing-walls does not route.
AIR_SPANS_MAX = 250
AIR_GATED = ("Part_B_Lower", "Part_B_Upper")
FILAMENT_OVERRIDES = {"additional_cooling_fan_speed": ["10"]}  # README: aux fan 10 %


def flatten(kind, name, out):
    chain, n = [], name
    while n:
        with open(os.path.join(PROFILES, kind, n + ".json")) as fh:
            d = json.load(fh)
        chain.append(d)
        n = d.get("inherits")
    flat = {}
    for d in reversed(chain):
        flat.update(d)
    flat.pop("inherits", None)
    flat.update(name=name, **{"from": "system"})
    if kind == "filament":
        flat.update(FILAMENT_OVERRIDES)
    with open(out, "w") as fh:
        json.dump(flat, fh, indent=1)
    return flat


def run(cmd, log):
    # cwd = the temp dir: the CLI drops a result.json into its working directory
    with open(log, "w") as fh:
        rc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=fh,
            stderr=subprocess.STDOUT,
            cwd=os.path.dirname(log),
            check=False,
        ).returncode  # rc judged by the caller
    return rc


def object_bbox(xml):
    v = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', xml), dtype=float)
    return v.min(0), v.max(0)


def main(layout=LAYOUT, plate_names=PLATE_NAMES, out_3mf=OUT_3MF, stl_dir=None, report=None):
    tmp = tempfile.mkdtemp(prefix="zsus3mf_")
    mach = flatten("machine", MACHINE, os.path.join(tmp, "machine.json"))
    flatten("process", PROCESS, os.path.join(tmp, "process.json"))
    flatten("filament", FILAMENT, os.path.join(tmp, "filament.json"))
    assert mach["printable_area"] == ["0x0", "256x0", "256x256", "0x256"], mach["printable_area"]
    assert mach["nozzle_diameter"] == ["0.4"], mach["nozzle_diameter"]

    # 1. let Bambu Studio import the STLs (writes a valid project_settings + object meshes)
    stls = [os.path.join(stl_dir or os.path.join(ROOT, "STLs"), n + ".stl") for n, *_ in layout]
    base = os.path.join(tmp, "base.3mf")
    rc = run(
        [
            BBS,
            "--load-settings",
            f"{tmp}/machine.json;{tmp}/process.json",
            "--load-filaments",
            f"{tmp}/filament.json",
            "--arrange",
            "0",
            "--export-3mf",
            base,
            *stls,
        ],
        os.path.join(tmp, "import.log"),
    )
    assert rc == 0, f"import failed rc={rc}, see {tmp}/import.log"
    z = zipfile.ZipFile(base)
    files = {
        n: z.read(n) for n in z.namelist() if not re.match(r"Metadata/(plate|top|pick|plate_no_light)_\d+.*\.png", n)
    }
    model = files["3D/3dmodel.model"].decode()

    # 2. map imported objects to layout (Bambu keeps input order), place them on their plates
    comps = re.findall(
        r'<object id="(\d+)"[^>]*>\s*<components>\s*<component p:path="([^"]+)" objectid="\d+"[^>]*transform="([^"]+)"',
        model,
    )
    assert len(comps) == len(layout), (len(comps), len(layout))
    cols = int(np.ceil(np.sqrt(len(plate_names))))
    placed = {}
    for (oid, path, ctf), (name, plate, (cx, cy), _) in zip(comps, layout, strict=True):
        lo, hi = object_bbox(files[path.lstrip("/")].decode())
        off = np.array(list(map(float, ctf.split()))[9:12])
        lo, hi = lo + off, hi + off
        size = hi - lo
        px = ((plate - 1) % cols) * PLATE_STRIDE
        py = -((plate - 1) // cols) * PLATE_STRIDE
        t = np.array([px + cx - (lo[0] + hi[0]) / 2, py + cy - (lo[1] + hi[1]) / 2, -lo[2]])
        x0, y0 = cx - size[0] / 2, cy - size[1] / 2
        x1, y1 = cx + size[0] / 2, cy + size[1] / 2
        assert x0 >= 0 and x1 <= BED and y0 >= 0 and y1 <= BED, (
            f"{name} off plate {plate}: {x0:.1f}..{x1:.1f} x {y0:.1f}..{y1:.1f}"
        )
        assert x0 >= EXCLUDE[0] or y0 >= EXCLUDE[1], f"{name} overlaps the bed exclusion corner"
        placed[oid] = (name, plate, t, size)
        model = re.sub(
            rf'(<item objectid="{oid}"[^>]*transform=")[^"]+(")',
            lambda m, t=t: m.group(1) + "1 0 0 0 1 0 0 0 1 " + " ".join(f"{v:.5f}" for v in t) + m.group(2),
            model,
        )
    files["3D/3dmodel.model"] = model.encode()

    # 3. model_settings: names, per-object settings, plates
    ms = files["Metadata/model_settings.config"].decode()
    for oid, (name, _plate, _t, _size) in placed.items():
        settings = dict(next(s for n, _, _, s in layout if n == name))
        settings.setdefault("enable_support", "0")  # off unless the part asks (an onlay emblem does)

        def obj_block(m, name=name, settings=settings):
            block = m.group(0)
            block = re.sub(
                r'(<object id="\d+">\s*<metadata key="name" value=")[^"]+(")',
                lambda q: q.group(1) + name + q.group(2),
                block,
                count=1,
            )
            extra = "".join(f'\n    <metadata key="{k}" value="{v}"/>' for k, v in sorted(settings.items()))
            return re.sub(
                r'(<metadata key="extruder" value="1"/>)',
                lambda q: q.group(1) + extra,
                block,
                count=1,
            )

        ms = re.sub(rf'<object id="{oid}">.*?</object>', obj_block, ms, flags=re.DOTALL)
    plates = []
    for p, pname in plate_names.items():
        inst = "".join(
            f'''
    <model_instance>
      <metadata key="object_id" value="{oid}"/>
      <metadata key="instance_id" value="0"/>
      <metadata key="identify_id" value="{100 + int(oid)}"/>
    </model_instance>'''
            for oid, (_, plate, _, _) in placed.items()
            if plate == p
        )
        plates.append(f'''  <plate>
    <metadata key="plater_id" value="{p}"/>
    <metadata key="plater_name" value="{pname}"/>
    <metadata key="locked" value="false"/>
    <metadata key="filament_map_mode" value="Auto For Flush"/>
    <metadata key="gcode_file" value=""/>{inst}
  </plate>
''')
    ms = re.sub(r"  <plate>.*</plate>\n", "".join(plates), ms, flags=re.DOTALL)
    files["Metadata/model_settings.config"] = ms.encode()
    files["Metadata/filament_sequence.json"] = json.dumps(
        {
            f"plate_{p}": {
                "nozzle_sequence": [],
                "optimal_assignment": [],
                "sequence": [],
            }
            for p in plate_names
        }
    ).encode()

    # 4. project settings
    ps = json.loads(files["Metadata/project_settings.config"])
    ps.update(PROJECT)
    for k, v in FILAMENT_OVERRIDES.items():
        ps[k] = v
    diff = ps.get("different_settings_to_system", ["", "", ""])
    diff[0] = ";".join(sorted(PROCESS_OVERRIDES))
    diff[1] = ";".join(sorted(FILAMENT_OVERRIDES))
    ps["different_settings_to_system"] = diff
    files["Metadata/project_settings.config"] = json.dumps(ps, indent=4).encode()
    rels = files["_rels/.rels"].decode()
    rels = re.sub(r'\s*<Relationship Target="/Metadata/plate_1[^"]*\.png"[^>]*/>', "", rels)
    files["_rels/.rels"] = rels.encode()

    with zipfile.ZipFile(out_3mf, "w", zipfile.ZIP_DEFLATED) as out:
        first = ("[Content_Types].xml", "_rels/.rels")
        for n in [*first, *sorted(k for k in files if k not in first)]:
            out.writestr(n, files[n])
    print("wrote", out_3mf)
    for name, plate, _t, size in sorted(placed.values(), key=lambda v: v[1]):
        print(f"  plate {plate}  {name:16s} {size[0]:6.1f} x {size[1]:6.1f} x {size[2]:5.1f} mm")

    # 5. verify: slice every plate with the CLI
    sliced = os.path.join(tmp, "sliced")
    os.makedirs(sliced)
    rc = run(
        [
            BBS,
            "--debug",
            "2",
            "--slice",
            "0",
            "--outputdir",
            sliced,
            "--export-3mf",
            "sliced.3mf",
            out_3mf,
        ],
        os.path.join(tmp, "slice.log"),
    )
    print(f"slice exit code {rc}  (log {tmp}/slice.log)")
    zs = zipfile.ZipFile(os.path.join(sliced, "sliced.3mf"))
    info = zs.read("Metadata/slice_info.config").decode()
    slice_report = {
        "bambu_studio": re.search(r'X-BBL-Client-Version" value="([^"]+)"', info).group(1),
        "exit_code": rc,
        "plates": [],
    }
    for p in re.findall(r"<plate>.*?</plate>", info, re.DOTALL):
        idx = int(re.search(r'key="index" value="(\d+)"', p).group(1))
        pred = re.search(r'key="prediction" value="(\d+)"', p)
        wt = re.search(r'key="weight" value="([\d.]+)"', p)
        warns = re.findall(r'<warning msg="([^"]+)"', p)
        objs = re.findall(r'<object identify_id="\d+" name="([^"]+)"', p)
        hours = int(pred.group(1)) / 3600 if pred else 0.0
        grams = float(wt.group(1)) if wt else 0.0
        slice_report["plates"].append(
            {
                "plate": idx,
                "name": plate_names[idx],
                "hours": round(hours, 2),
                "grams": grams,
                "objects": objs,
                "warnings": warns,
            }
        )
        print(f"  plate {idx}: {hours:5.2f} h  {grams:6.1f} g  {objs}  warnings={warns or 'none'}")
    gcodes = sorted(n for n in zs.namelist() if n.endswith(".gcode"))
    assert rc == 0 and len(gcodes) == len(plate_names), f"slice failed: rc={rc}, gcode files {gcodes}"
    assert not any(p["warnings"] for p in slice_report["plates"]), "slicer warnings, see above"
    # a part that asks for supports (an onlay emblem's flat overhang) must get them, or it prints as a droop
    for p in sorted({plate for _n, plate, _c, st in layout if st.get("enable_support") == "1"}):
        gp = zs.read(f"Metadata/plate_{p}.gcode").decode(errors="ignore")
        n_support = len(re.findall(r"^; FEATURE: Support", gp, re.MULTILINE))
        assert n_support > 0, f"plate {p} asks for supports but its slice has none"
        print(f"    plate {p} supports: {n_support} support features")
    # stringing: travel over open air, read from the G-code the printer runs (CAD/gcode_travel.py)
    for p in slice_report["plates"]:
        gp = zs.read(f"Metadata/plate_{p['plate']}.gcode").decode(errors="ignore")
        p["air_travel"] = air_travel(gp)
        gated = any(o in AIR_GATED for o in p["objects"])
        ok = not gated or p["air_travel"]["spans"] <= AIR_SPANS_MAX
        print(f"    plate {p['plate']} travel over open air: {p['air_travel']}{'' if ok else '  FAIL'}")
        assert ok, f"plate {p['plate']}: {p['air_travel']['spans']} open-air travel hops > {AIR_SPANS_MAX}"
    g1 = zs.read(gcodes[0]).decode(errors="ignore")
    for key in (
        "printer_settings_id",
        "nozzle_diameter",
        "curr_bed_type",
        "additional_cooling_fan_speed",
        "enable_support",
        "filament_colour",
        "reduce_crossing_wall",
    ):
        m = re.search(rf"^; {key} = (.*)$", g1, re.MULTILINE)
        slice_report[key] = m.group(1) if m else None
        print(f"    {key} = {slice_report[key]}")
    assert slice_report["nozzle_diameter"] == "0.4" and slice_report["curr_bed_type"] == "Textured PEI Plate", (
        slice_report
    )
    report_path = report or os.path.join(HERE, "renders", "slice_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as fh:
        json.dump(slice_report, fh, indent=1)
    print("all", len(gcodes), "plates sliced; report in", os.path.relpath(report_path, ROOT))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--emblem"]:
        stl = os.path.abspath(sys.argv[2])
        name = os.path.splitext(os.path.basename(stl))[0]
        with open(stl, "rb") as fh:  # binary STL: wider than the 18 mm cap -> an onlay, which needs supports
            fh.seek(84)
            tri = np.frombuffer(fh.read(), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])["v"]
        span = tri.reshape(-1, 3).max(0) - tri.reshape(-1, 3).min(0)
        main(
            layout=[(name, 1, (128.0, 128.0), dict(EMBLEM_ONLAY if max(span[:2]) > 18.05 else EMBLEM_FINE))],
            plate_names={1: f"1 {name} (0.08 mm)"},
            out_3mf=os.path.join(os.path.dirname(stl), name + "_P1S_PLA.3mf"),
            stl_dir=os.path.dirname(stl),
            report=os.path.join(os.path.dirname(stl), name + "_slice_report.json"),
        )
    else:
        main()
