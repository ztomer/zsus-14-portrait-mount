#!/usr/bin/env bash
# Rebuild every deliverable from source, gating each step:
#   STLs/*.stl, ZSUS_v21_Complete_P1S_PLA.3mf (sliced to verify), CAD/renders/*, ZSUS_v21_Assembly_Instructions.pdf,
#   docs/images/* (README pictures)
# Needs: uv (Python deps are fetched per run), Blender >= 4.5 (MANIFOLD boolean solver), Bambu Studio.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=(uv run --quiet --no-project --python 3.14 --with manifold3d --with trimesh --with numpy --with scipy
    --with rtree --with shapely --with networkx --with matplotlib --with pymupdf --with embreex --with pillow --with scikit-image python -I)
BLENDER=${BLENDER:-blender}

echo "-> Part A (ball socket): CAD/build_part_a_v21.py"
"${PY[@]}" CAD/build_part_a_v21.py

echo "-> Part B (bezel): CAD/build_part_b_blender_v21.py"
log=$(mktemp)
"$BLENDER" -b --factory-startup --python-exit-code 1 -P CAD/build_part_b_blender_v21.py >"$log" 2>&1 || { cat "$log"; exit 1; }
grep '^GATE' "$log"
grep -q '^GATE all Part B meshes' "$log" || { echo "x Part B gate did not pass"; exit 1; }

echo "-> Emblem relief handedness: CAD/make_relief.py --self-test"
"${PY[@]}" CAD/make_relief.py --self-test

echo "-> Chin emblem (snap-in tile): CAD/build_emblem.py"
"${PY[@]}" CAD/build_emblem.py

echo "-> Cthulhu emblem (CC BY, CAD/assets/cthulhu/ATTRIBUTION.md): relief + tile"
"${PY[@]}" CAD/make_relief.py CAD/emblems/cthulhu.json
"${PY[@]}" CAD/build_emblem.py --relief CAD/build/cthulhu_relief.stl --out STLs/Part_B_Emblem_Cthulhu.stl

echo "-> Part B assembly fit: CAD/check_part_b_fit.py"
"${PY[@]}" CAD/check_part_b_fit.py

echo "-> Every STL as a slicer reads it: CAD/check_stl_files.py"
"${PY[@]}" CAD/check_stl_files.py

echo "-> Bambu project + slice check: CAD/build_3mf_v21.py"
"${PY[@]}" CAD/build_3mf_v21.py

echo "-> Guide figures + PDF"
"${PY[@]}" CAD/render_sections.py
"${PY[@]}" CAD/build_pdf_v21.py
echo "-> README pictures: CAD/render_views.py (Blender), CAD/pack_images.py"
"$BLENDER" -b --factory-startup --python-exit-code 1 -P CAD/render_views.py >"$log" 2>&1 || { cat "$log"; exit 1; }
"${PY[@]}" CAD/pack_images.py
echo "ok all deliverables rebuilt and verified"
