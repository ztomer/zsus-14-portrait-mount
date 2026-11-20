"""
Turn part of a 3D model into a bas-relief for the chin emblem's face (CAD/build_emblem.py --relief).

    python3 CAD/make_relief.py CAD/emblems/cthulhu.json

The recipe (numbers only) names the source model, the side it is viewed from, a window around the feature, and
how to cut the feature out of what is behind it. The model is depth-cast from that side, the feature is the
connected region in front of `depth_min` that holds `seed` (`depth_min_below` applies under `deep_below_z`, to
part it from whatever it touches there), and its depth is compressed into the emblem's recessed panel: the
silhouette stands `h_edge` proud of the panel floor, the nearest point is flush with the tile face, and a
high-pass of the depth (`detail_sigma`, `detail_gain`) is added back so small forms survive the compression.

Two modes (`mode` in the recipe):
  inlay (default)  the feature fits inside the tile's flush border, in the recessed panel.
  onlay            the feature stands proud of the face (0..RELIEF_D in front of it) and may spill past the tile
                   and the window onto the chin face, where it rests: it breaks the frame. `top_v` and
                   `bottom_v` are its top and bottom edges on the chin, measured up from the tile's centre (mm);
                   `top_inside_tile` gates that its top stays 0.3 mm inside the tile. CAD/build_emblem.py gates
                   that it rests on flat chin face all round; the print needs supports under the overhang.

Writes into the recipe's `out_dir` (default: next to the source model, so art under a personal-use licence stays in
its gitignored CAD/third_party/ folder):
  <stem>_relief.stl   a closed solid in the tile frame (CAD/build_emblem.py), for --relief
  <stem>_relief.png   the height map as an image, for a quick look
"""

import json
import os
import sys

import manifold3d as m3
import numpy as np
import trimesh
from PIL import Image
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from build_emblem import CAP, RELIEF_D, RIM  # noqa: E402
from stl_io import write_stl  # noqa: E402

GRID = 0.06  # tile-side sample pitch (mm): finer than the 0.4 mm nozzle can draw, coarse enough to stay small
SIL_GROW = 0.013  # mm the silhouette grows by: off the grid lines (see onlay_solid)
EDGE_SOFT = 0.06  # mm: smooths the silhouette step (below what a 0.4 mm nozzle resolves)
H_BG = 0.03  # panel floor stands this proud of the cut floor, so the union never meets a coplanar face
# viewer side -> (axis looked along, right-hand axis in the picture, its sign); picture up is always +z
VIEWS = {"+x": (0, 1, 1.0), "-x": (0, 1, -1.0), "+y": (1, 0, -1.0), "-y": (1, 0, 1.0)}


def depth_map(mesh, r, step):
    axis, right, sign = VIEWS[r["view"]]
    toward = 1.0 if r["view"][0] == "+" else -1.0  # depth grows toward the viewer
    hs = np.arange(*r["window_h"], step)
    zs = np.arange(*r["window_z"], step)
    hh, zz = np.meshgrid(hs, zs)
    o = np.zeros((hh.size, 3))
    o[:, axis] = toward * (abs(mesh.bounds[:, axis]).max() + 10)
    o[:, right] = sign * hh.ravel()
    o[:, 2] = zz.ravel()
    d = np.zeros((hh.size, 3))
    d[:, axis] = -toward
    loc, idx, _ = mesh.ray.intersects_location(o, d, multiple_hits=False)
    dep = np.full(hh.size, np.nan)
    dep[idx] = toward * loc[:, axis]
    return hs, zs, dep.reshape(hh.shape)


def feature_mask(hs, zs, dep, r):
    _, zz = np.meshgrid(hs, zs)
    d = np.nan_to_num(dep, nan=-np.inf)
    cand = np.where(zz < r["deep_below_z"], d > r["depth_min_below"], d > r["depth_min"])
    seed = (int(np.argmin(abs(zs - r["seed_hz"][1]))), int(np.argmin(abs(hs - r["seed_hz"][0]))))

    def holding_seed(m):
        lab, _ = ndi.label(m)
        assert lab[seed], f"the seed {r['seed_hz']} is not on the feature"
        return lab == lab[seed]

    m = ndi.binary_fill_holes(holding_seed(cand))
    return holding_seed(ndi.binary_opening(m, iterations=3))


def heights(dep, mask, r, step):
    d = np.where(mask, dep, 0.0)
    lo, hi = r["depth_min"], float(np.percentile(dep[mask], 99.5))
    f = np.clip((d - lo) / (hi - lo), 0.0, 1.0) ** r["gamma"]
    sig = r["detail_sigma"] / step
    w = ndi.gaussian_filter(mask.astype(float), sig)
    local = ndi.gaussian_filter(d, sig) / np.maximum(w, 1e-6)  # blur of the feature alone (normalised)
    h = r["h_edge"] + (RELIEF_D - r["h_edge"]) * f + r["detail_gain"] * (d - local)
    return np.where(mask, np.clip(h, r["h_edge"], RELIEF_D), H_BG)


def heightfield(us, vs, top, bottom):
    """Closed solid between the surface w = top[j, i] (at u = us[i], v = vs[j]) and the plane w = bottom."""
    nj, ni = top.shape
    uu, vv = np.meshgrid(us, vs)
    verts = np.vstack(
        [np.c_[uu.ravel(), vv.ravel(), top.ravel()], np.c_[uu.ravel(), vv.ravel(), np.full(top.size, bottom)]]
    )
    idx = np.arange(top.size).reshape(nj, ni)
    a, b, c, d = idx[:-1, :-1].ravel(), idx[:-1, 1:].ravel(), idx[1:, 1:].ravel(), idx[1:, :-1].ravel()
    n = top.size
    tris = [np.c_[a, c, b], np.c_[a, d, c], np.c_[a + n, b + n, c + n], np.c_[a + n, c + n, d + n]]
    for e in (idx[0, :], idx[:, -1], idx[-1, ::-1], idx[::-1, 0]):  # the four walls, walked around the rim
        p, q = e[:-1], e[1:]
        tris += [np.c_[p, q, p + n], np.c_[q, q + n, p + n]]
    tris = np.vstack(tris)
    man = m3.Manifold(m3.Mesh(vert_properties=verts.astype(np.float32), tri_verts=tris.astype(np.uint32)))
    if man.status() != m3.Error.NoError or man.volume() <= 0:
        tris = tris[:, ::-1]
        man = m3.Manifold(m3.Mesh(vert_properties=verts.astype(np.float32), tri_verts=tris.astype(np.uint32)))
    assert man.status() == m3.Error.NoError and man.volume() > 0, man.status()
    return man


def onlay_solid(us, vs, ht):
    """The proud relief: the height field (w = -ht, back on the face plane w = 0) cut to the feature's
    silhouette, plus an anchor 0.3 mm into the tile's cap wherever the two overlap (and 0.1 mm past the cap's
    edge), so the union with the tile never meets a coplanar face or edge."""
    from skimage import measure

    polys = [
        [(us[0] + c * GRID, vs[0] + rr * GRID) for rr, c in cont]
        for cont in measure.find_contours(ht, (H_BG + 0.15) / 2)
        if len(cont) > 8
    ]
    # The silhouette grows by SIL_GROW: marching squares puts every contour vertex ON a grid edge, where the
    # height field's own triangle edges run, so walls cut exactly there met the slab at coincident edges, and
    # contours touching at a saddle point made a prism edge shared by four faces; the STL pinched at both
    # (goh checks/cad_mesh.py). Grown by a fraction of GRID that is no simple ratio of it, the walls sit between
    # grid lines and touching contours merge.
    sil = m3.CrossSection(polys, m3.FillRule.EvenOdd).offset(SIL_GROW, m3.JoinType.Round)
    slab = heightfield(us, vs, -ht, 0.0)
    prism = m3.Manifold.extrude(sil, RELIEF_D + 0.2).translate((0.0, 0.0, -(RELIEF_D + 0.2)))
    # the anchor reaches 0.1 mm PAST the cap's edge (into its 0.2 mm pocket clearance), so the cap's front edge is
    # buried in it; inset, the relief's back lay on the cap face up to that edge and the STL pinched along it
    cap = m3.CrossSection.square((2 * CAP + 0.2, 2 * CAP + 0.2)).translate((-(CAP + 0.1), -(CAP + 0.1)))
    # inset 0.03 mm from the silhouette: cut from the same outline, the anchor's walls lay ON the relief's walls
    anchor = m3.Manifold.extrude(sil.offset(-0.03, m3.JoinType.Round) ^ cap, 0.32).translate((0.0, 0.0, -0.02))
    return (slab ^ prism) + anchor


def relief_grid(mesh, r):
    """The tile-side height map: (us, vs, ht) with ht[j, i] the relief height at u = us[i], v = vs[j], plus the
    scale and the feature's size on the tile. The viewer of the face sees u to their LEFT (CAD/chin_spec.py), so
    the source picture's right maps to -u: the emblem reads as the model does, not mirrored."""
    step = r["step"]
    hs, zs, dep = depth_map(mesh, r, step)
    mask = feature_mask(hs, zs, dep, r)
    rows, cols = np.where(mask)
    h_lo, h_hi, z_lo, z_hi = hs[cols.min()], hs[cols.max()], zs[rows.min()], zs[rows.max()]
    if "top_v" in r:  # an onlay placed by its edges on the chin
        r = dict(r, fit_height=r["top_v"] - r["bottom_v"], centre_v=(r["top_v"] + r["bottom_v"]) / 2)
    s = r["fit_height"] / (z_hi - z_lo)
    hc, zc = (h_lo + h_hi) / 2, (z_lo + z_hi) / 2
    h = heights(dep, mask, r, step)
    if r.get("mode", "inlay") == "onlay":  # a grid around the feature, wherever it reaches
        pu = (h_hi - h_lo) * s / 2 + 1.0
        v0 = r.get("centre_v", 0.0)
        us = np.arange(-pu, pu + 1e-9, GRID)
        vs = np.arange(v0 - r["fit_height"] / 2 - 1.0, v0 + r["fit_height"] / 2 + 1.0 + 1e-9, GRID)
    else:
        p = CAP - RIM
        v0 = 0.0
        us = np.arange(-p, p + 1e-9, GRID)
        vs = np.arange(-p, p + 1e-9, GRID)
    uu, vv = np.meshgrid(us, vs)
    ci = (hc - uu / s - hs[0]) / step  # tile (u, v) -> source picture (column, row); picture right = -u
    ri = (zc + (vv - v0) / s - zs[0]) / step
    ht = ndi.map_coordinates(h, [ri, ci], order=1, cval=H_BG)
    ht = ndi.gaussian_filter(ht, EDGE_SOFT / GRID)  # the mask's pixel stairs would print as a jagged outline
    return us, vs, ht, s, ((h_hi - h_lo) * s, (z_hi - z_lo) * s)


def front_view_x_of_relief(us, vs, ht):
    """Front-view X (relative to the emblem centre) of the relief's height-weighted centre, seated in the chin."""
    from chin_spec import EMBLEM_CX, EMBLEM_PLACE

    place = np.array(EMBLEM_PLACE, float)
    assert np.linalg.det(place[:, :3]) > 0.999
    uu, _ = np.meshgrid(us, vs)
    wgt = np.clip(ht - H_BG, 0.0, None)  # height-weighted: where the relief stands tallest
    u = float((uu * wgt).sum() / wgt.sum())
    # tile (u, v, w) -> printed (u, -v, D - w) -> placed x = place @ printed; front-view X = -x
    x = place[0, 0] * u + place[0, 3]
    return -x - EMBLEM_CX


def self_test():
    """Handedness, end to end: a symmetric slab with a tall bump on its picture-RIGHT must seat with the bump on
    the viewer's right. Runs with no third-party model, so the build can always ask it."""
    back = trimesh.creation.box((2.0, 30.0, 30.0))
    slab = trimesh.creation.box((1.0, 20.0, 20.0)).apply_translation((1.4, 0.0, 0.0))  # the feature, centred
    bump = trimesh.creation.box((3.0, 6.0, 6.0)).apply_translation((2.0, 6.0, 0.0))  # +y: right, seen from +x
    mesh = trimesh.util.concatenate([back, slab, bump])
    r = {"view": "+x", "window_h": [-16.0, 16.0], "window_z": [-16.0, 16.0], "step": 0.1, "seed_hz": [0.0, 0.0],
         "depth_min": 1.2, "deep_below_z": -100.0, "depth_min_below": 1.2, "fit_height": 12.0, "h_edge": 0.35,
         "gamma": 1.0, "detail_sigma": 1.0, "detail_gain": 0.0}  # fmt: skip
    dx = front_view_x_of_relief(*relief_grid(mesh, r)[:3])
    ok = dx > 0.1  # +0.30 when right, -0.30 when mirrored
    print(f"{'OK  ' if ok else 'FAIL'} relief handedness: a picture-right feature seats {dx:+.2f} mm right of centre")
    return ok


def main(argv):
    if argv[:1] == ["--self-test"]:
        sys.exit(0 if self_test() else "relief handedness self-test failed")
    recipe_path = argv[0]
    with open(recipe_path) as fh:
        r = json.load(fh)
    src = os.path.join(ROOT, r["source"])
    scene = trimesh.load(src)
    mesh = scene.to_geometry() if hasattr(scene, "to_geometry") else scene
    if not self_test():
        sys.exit("relief handedness self-test failed")
    us, vs, ht, s, (size_u, size_v) = relief_grid(mesh, r)
    onlay = r.get("mode", "inlay") == "onlay"
    p = CAP - RIM
    fits = onlay or (size_u <= 2 * p - 0.6 and size_v <= 2 * p - 0.6)
    edge = max(ht[0].max(), ht[-1].max(), ht[:, 0].max(), ht[:, -1].max())
    vv = np.meshgrid(us, vs)[1]
    top = float(vv[ht > H_BG + 0.02].max())
    fails = []
    if r.get("top_inside_tile"):
        ok = top <= CAP - 0.3
        msg = f"top of the feature inside the tile: v {top:.2f} <= {CAP - 0.3:.2f}"
        print(f"{'OK  ' if ok else 'FAIL'} {msg}")
        fails += [] if ok else [msg]
    for ok, msg in (
        (
            fits,
            f"feature {size_u:.1f} x {size_v:.1f} mm "
            + ("(onlay: seated fit gated by build_emblem)" if onlay else "fits the panel"),
        ),
        (
            ht.max() >= RELIEF_D - 0.01,
            f"nearest point at the relief's full height (h max {ht.max():.2f} of {RELIEF_D})",
        ),
        (edge <= H_BG + 1e-6, "grid border clear (the whole feature is inside the sampled area)"),
    ):
        print(f"{'OK  ' if ok else 'FAIL'} {msg}")
        if not ok:
            fails.append(msg)
    if fails:
        sys.exit(f"relief gate failed: {fails}")
    solid = onlay_solid(us, vs, ht) if onlay else heightfield(us, vs, RELIEF_D - ht, RELIEF_D + 0.5)
    out_dir = os.path.join(ROOT, r["out_dir"]) if "out_dir" in r else os.path.dirname(src)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, os.path.splitext(os.path.basename(recipe_path))[0] + "_relief")
    write_stl(solid, stem + ".stl", header="ZSUS relief", shells=None)  # an onlay may be several islands
    # the preview is drawn as the viewer sees the face: picture right = -u, so flip the u axis
    img = (ht[::-1, ::-1] / RELIEF_D * 255).astype(np.uint8)
    Image.fromarray(img).resize((ht.shape[1] * 2, ht.shape[0] * 2)).save(stem + ".png")
    print(f"wrote {os.path.relpath(stem, ROOT)}.stl/.png  scale {s:.3f}, feature {size_u:.1f} x {size_v:.1f} mm")


if __name__ == "__main__":
    main(sys.argv[1:])
