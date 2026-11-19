# Changelog

## v21.2.0 (2026-11-19)

- **Even screen reveal:** the opening is cut round the image as the owner's monitor shows it (photo of the printed
  Lower, 2026-11-19), not the spec sheet, which put the image 1.2..2.4 mm too far right. v21.1 left 0.8 mm of black
  glass on the left, 4.4 mm on the right and 1.7 mm at the bottom; every side now leaves 0.8 mm (`IMAGE`, `REVEAL` in
  `CAD/monitor_spec.py`). The right border and the chin move with the opening (`CAD/bezel_spec.py`), so the frame
  stays 22.3 mm left / right / top with a 36 mm chin; the bezel is 3.6 mm narrower. `CAD/check_part_b_fit.py` gates the
  reveal on all four sides.
- **Less stringing:** the first bezel print came off strung. The project turns on avoid crossing walls, and
  `CAD/gcode_travel.py` gates travel over open air in the sliced G-code: the Lower's open-air hops drop from 552 to
  about 180. Dry the PLA before printing the bezel.

## v21.1.0 (2026-11-18)

- **Thin panel 6.5 mm** (fit gauge: only the 7.0 mm slot slides on); the Lower's thin slot is 7.0 mm and the gauge
  steps 7.0 / 7.4 / 7.8. The monitor's measurements live in one module, `CAD/monitor_spec.py`.
- **STL files a slicer reads as closed:** v21.0.0 shipped pinched edges (edges shared by 4 to 10 faces) in
  Part_A_Mount (171), Part_A_Test (336) and the Cthulhu tile (1084); Bambu Studio sliced them without a warning.
  Causes removed: a redundant thread core and a lead-in that started on the mouth cylinder (Part A), a relief
  silhouette whose walls stood on the height field's grid lines and an anchor cut from the same outline (tile).
  Every manifold3d writer now goes through `CAD/stl_io.py` (float32 weld, read-back refusal), and
  `CAD/check_stl_files.py` gates every STL in the build.

## v21.0.0 (2026-11-18)

The first public release: a 14" portrait monitor mount (ball socket, Part A) and the Snow White
bezel (Part B), as one Bambu Studio project for a P1S in plain PLA.

- **Project:** `ZSUS_v21_Complete_P1S_PLA.3mf`, five plates, each sliced and checked by the
  build: socket coupon, Part A, the two bezel halves, and the optional Cthulhu emblem (plate 5,
  0.08 mm layers, tree supports from the build plate; the build fails if its G-code holds none).
- **Chin:** after the Apple IIc monitor, with a snap-in removable emblem tile and the LED slit
  plug.
- **Emblem pipeline:** `CAD/make_relief.py` turns a 3D model into a bas-relief tile, inlay
  (recessed panel) or onlay (proud of the chin). It is seated by a rigid placement (asserted
  det +1, never a mirror), with a handedness self-test and seat gates against the real bezel.
  `CAD/build_emblem_art.sh` builds one from a recipe in `CAD/emblems/`.
- **Cthulhu emblem:** after "Chtulhu Statue" by ChurchOfShrike (MakerWorld 1705652, CC BY);
  attribution in `CAD/assets/cthulhu/ATTRIBUTION.md`. 11.1 x 21.7 mm onlay, the dome inside the
  logo frame, the tentacles inside the bezel.
- **Socket leaves that survive PLA:** eight leaves with a deeper slot, gated by a cantilever
  strain model at 1.5% across layer lines (0.99% now; the first print's geometry was 3.07% and
  broke while the ball went in).
- **Pictures:** `CAD/render_views.py` renders the README images headless in Blender from the
  shipped STLs, on a light and a dark backdrop.
