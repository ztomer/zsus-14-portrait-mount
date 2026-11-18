#!/usr/bin/env bash
# Rebuild every deliverable from source, gating each step:
#   STLs/*.stl, ZSUS_v21_Complete_P1S_PLA.3mf (sliced to verify), CAD/renders/*, ZSUS_v21_Assembly_Instructions.pdf
# Needs: uv (Python deps are fetched per run), Blender >= 4.5 (MANIFOLD boolean solver), Bambu Studio.
set -euo pipefail
cd "$(dirname "$0")/.."

PY=(uv run --quiet --no-project --python 3.14 --with manifold3d --with trimesh --with numpy --with scipy
    --with rtree --with shapely --with networkx --with matplotlib --with pymupdf python -I)
BLENDER=${BLENDER:-blender}

echo "-> Part A (ball socket): CAD/build_part_a_v21.py"
"${PY[@]}" CAD/build_part_a_v21.py

echo "-> Part B (bezel): CAD/build_part_b_blender_v21.py"
log=$(mktemp)
"$BLENDER" -b --factory-startup --python-exit-code 1 -P CAD/build_part_b_blender_v21.py >"$log" 2>&1 || { cat "$log"; exit 1; }
grep '^GATE' "$log"
grep -q '^GATE all Part B meshes' "$log" || { echo "x Part B gate did not pass"; exit 1; }

echo "-> Chin emblem (snap-in tile): CAD/build_emblem.py"
"${PY[@]}" CAD/build_emblem.py

echo "-> Part B assembly fit: CAD/check_part_b_fit.py"
"${PY[@]}" CAD/check_part_b_fit.py

echo "-> Bambu project + slice check: CAD/build_3mf_v21.py"
"${PY[@]}" CAD/build_3mf_v21.py

echo "-> Guide figures + PDF"
"${PY[@]}" CAD/render_sections.py
"${PY[@]}" CAD/build_pdf_v21.py
echo "ok all deliverables rebuilt and verified"
