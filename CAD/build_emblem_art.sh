#!/usr/bin/env bash
# Build an emblem from a recipe (CAD/emblems/*.json) and a model the owner downloaded into CAD/third_party/:
# the relief, the gated tile, and a one-plate print project, all written next to the model (never into STLs/).
#   CAD/build_emblem_art.sh CAD/emblems/cthulhu.json
set -euo pipefail
cd "$(dirname "$0")/.."
recipe=${1:?usage: CAD/build_emblem_art.sh CAD/emblems/<name>.json}
PY=(uv run --quiet --no-project --python 3.14 --with manifold3d --with trimesh --with numpy --with scipy --with rtree
    --with embreex --with pillow --with lxml --with networkx python -I)
src=$("${PY[@]}" -c 'import json, sys; print(json.load(open(sys.argv[1]))["source"])' "$recipe")
[[ -f $src ]] || { echo "x $src is missing: download the model there first (see README, Emblem art)"; exit 1; }
name=$(basename "$recipe" .json)
dir=$(dirname "$src")
"${PY[@]}" CAD/make_relief.py "$recipe"
"${PY[@]}" CAD/build_emblem.py --relief "$dir/${name}_relief.stl"
"${PY[@]}" CAD/build_3mf_v21.py --emblem "$dir/Part_B_Emblem_${name}_relief.stl"
