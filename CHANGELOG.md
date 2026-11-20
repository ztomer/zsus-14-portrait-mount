# Changelog

## v21.7.0 (2026-11-20)

- **The thick side's back boss moves in off the outer edge** (owner: flush with the edge it was the first thing seen
  from the side): it now starts at the outer wall's inner face, 4.5 mm in from the outer face, and stands out over the
  monitor's back to 11 mm, floating 0.4 mm clear of it, with the bolt 5.25 mm in. Its flat underside prints on tree
  supports in both halves (new support regions, `STLs/Part_B_supports.json`), which stand on the plate in the screen
  opening at the seam: the slice puts support under each region and none more than 11 mm from one. With the key's
  room now inward, the slot no longer opens out through the boss's side. The trips out to those trees add about 80
  short open-air hops to each bezel plate (plate 3: 231 to 315, plate 4: 197 to 274, median 5 mm, all at the seam),
  so the hop cap goes from 250 to 330. A screwdriver cannot drive the seam bolts: the bolt lies 3 mm under the back,
  and a driver in line with it would put its handle through the bezel; the 2.5 mm L key stays. An 8-shaped peg was
  ruled out: the 4.5 mm wall has its inner 2 mm taken by the lap tongue at the seam. Reprint both halves.

## v21.6.0 (2026-11-20)

- **Two seam bolts lying across the gap replace the tab, the splice plate and the third screw** (owner's idea): on
  each side an M3 socket-head bolt (10 to 16 mm) lies along the monitor across the seam, dropped in from the back,
  its head bearing on a wall in the Lower and its nut in a hex pocket in the Upper, and a 2.5 mm L key in the slot
  behind the head turns it: tightening pulls the seam shut, where v21.4-5's vertical screws only pinned it with
  0.2-0.25 mm of play. The thin side's lies inside the 16.7 mm frame, no tab and no supports (plate 3 has none
  now); the thick side's sits in a back boss 6.6 mm proud (v21.5: 8 mm plus a 3 mm plate and the screw heads), whose
  key slot opens out through the boss's outer side above the bolt so the key can swing 60 degrees.
  `CAD/check_part_b_fit.py` models each bolt in place: it clears both halves, pulled apart the halves meet head and
  nut within 0.1 mm, the nut cannot turn, bolt and nut lift straight out the back, an L key turns 30 degrees each
  way without touching the Lower (the thick side's first, narrower slot allowed about 22: red), and hinged open about
  the thin-side corner the thick side opens 0.13 mm. v21.5.0's parts are red on all of them. Hardware: two M3
  socket-head bolts, two M3 nuts, a 2.5 mm L key; `Part_B_Splice` is gone.

## v21.5.0 (2026-11-20)

- **The thick side is screwed too:** v21.4.0 pinned only the thin side, and the thick side had nothing but the lap
  tongue's 0.35 mm detent, a click and not a stop: pulled, the Upper hinged about the seam's thin-side corner and the
  thick side opened 1.0 mm (5.1 mm without the monitor), stopped only by the monitor in its side channels. Its 4.5 mm
  wall has no room for a nut, so each half now carries an 8 mm boss on its back at the seam with an M3 nut in a hex
  pocket, and a flat 9 x 22 x 3 mm splice plate (`Part_B_Splice`, plate 2) lies across both with an M3 screw (6 to
  10 mm) into each nut. The bosses' edge over the monitor rises at 45 degrees, so nothing needs support.
  `CAD/check_part_b_fit.py` models the plate, screws and nuts: they clear both halves, pulled apart the Upper meets its
  nut after 0.2 mm, no nut can turn, and hinged open about the thin-side corner the thick side opens 0.25 mm (gate
  0.5; 1.00 mm and red with the splice left out). Reprint both halves and print the splice; hardware is three M3
  screws and three M3 nuts.

## v21.4.0 (2026-11-20)

- **The thin side is held by an M3 screw and nut, not a snap latch:** v21.3's square-hook latch let go when pulled
  (owner's seam test, 2026-11-20). Its arm, a 1.8 x 17 mm cantilever, has to bend to snap in, so it bends away under
  any pull, and a stiffer one would not snap in at all. Now a 9 x 10 x 6 mm tab on the Lower's back laps over a recess
  in the Upper's, and one M3 screw (6 to 12 mm) drops through the tab into an M3 nut held in a hex pocket in the
  recess floor: pulling the halves apart is shear on the screw. No heat-set insert. The tab is the Lower's because
  its tree supports string: on the Upper they added 49 open-air hops and put plate 4 over its 250. `CAD/check_part_b_fit.py` models
  the screw and nut in place: they clear both halves shut, pulled apart the Lower's tab meets the screw after 0.25 mm
  and the Upper meets the nut after 0.2 mm, the nut cannot turn (1.9 mm3 in the way at 30 degrees), and the front face is
  solid under the hole (v21.3.0's parts: red). The Upper's supports under the snap arm's tip are gone; the Lower
  takes one under the tab. The seam test on plate 1 is cut from the new parts; the guide's figure is a section through the
  screw. Reprint both halves and the seam test.

## v21.3.0 (2026-11-19)

- **The bezel prints to size:** the two halves stood about 2 mm apart on the monitor (flush without it) because PLA
  shrinks as it cools and nothing compensated: the closed bezel measured about 354 mm against the model's 356.1
  (0.6 %), so the 310.6 mm pocket printed near 308.8. The slicer now scales every part by 1 / 0.994
  (`filament_shrink` 99.4 % in `CAD/layout.json`), and the slice check fails if the G-code did not use a filament
  override (gates_of_heck GOH.CADOVERRIDE). The shrink also left the Upper riding high, which is the wide black band
  along the top edge.
- **The monitor's length is the tape's, 311.0 mm** (310.5..311, was the spec sheet's 310): `MON_H`
  (`CAD/monitor_spec.py`); the pocket, the top rear lips, the top detent tab and its flex slot and the USB-C bay
  follow it, and the image's top is its bottom plus the active height (304.1, was the sheet's 304.4). The extra length
  is all in the Upper.
- **The thin-side latch holds:** its barb was a 40-degree ramp, a detent that cammed out at about 2 kg, and it caught
  only with the seam within 0.7 mm of shut. The barb is now a square hook, and the Lower's ledge stands 1.5 mm above
  it (`LATCH_CATCH`, `CAD/bezel_spec.py`), so it holds with the seam anywhere from shut to 1.5 mm open. Nothing gated
  the latch before: `CAD/check_part_b_fit.py` now lifts the Upper off its seat and requires the barb to meet the ledge
  after 1.5 (+/- 0.2) mm and bear on it across >= 0.6 mm (v21.2.1: 0.75 mm and 0.26 mm, red). Reprint both halves:
  the hook is on the Upper, the ledge in the Lower.
- **Seam test on plate 1:** `Part_B_SeamTest_Upper` and `Part_B_SeamTest_Lower`, the thin-side corner of each half
  round the parting line, cut from the real parts: snap them together before printing the bezel.

## v21.2.2 (2026-11-19)

- **One copy of the print checks, in gates_of_heck:** the mesh, leaf-strain, slicer and stringing checks this repo
  carried (`CAD/check_stl_files.py`, the strain model in `CAD/build_part_a_v21.py`, the slice gates in
  `CAD/build_3mf_v21.py`, `CAD/bambu_supports.py`, `CAD/gcode_travel.py`) are gates_of_heck's CAD layer now, and the
  push gate runs it (`gates/cad_gate.sh`, `GOH_CAD_LAYOUT=CAD/layout.json`). The plates, per-object settings, support
  regions and limits are data in `CAD/layout.json`; the generator writes the socket's spec to
  `STLs/Part_A_socket.strain.json`. The printed parts and the project are unchanged (same STLs; the rebuilt 3MF differs
  only in UUIDs and dates). The mesh check also fails a zero stored normal, which Bambu Studio refuses to load.

## v21.2.1 (2026-11-19)

- **Upper prints without a floating cantilever:** face-down, the right snap arm is a 17 mm beam that starts 4.5 mm
  above the plate with nothing under it; Bambu Studio warned "floating cantilever" and the tip would have printed as
  spaghetti. The Upper now carries two support enforcer volumes (tree supports from the plate): under the arm's tip past
  the seam, and under the 4.2 mm lip over the left lap pocket, where the Lower's tongue seats. Nothing else on the
  Upper takes support (`tree(auto)` also filled the 1.6 mm USB-C nose slot). The Upper's arm channel floor drops to
  3.0 mm so the arm, now a bridge from its root to the supported tip, has 1.5 mm of air under it (0.5 before) and
  cannot sag onto the floor. Snap the two supports off before assembly.
- **Every slicing warning fails the build:** the CLI writes the warnings Bambu Studio shows over the plate to
  `result.json` and its log, not to `slice_info.config`, which was all the gate read, so v21.2.0 passed with this one.
  Turning supports on in the GUI did not clear it either: the project set `enable_support` off per object, which
  overrides the global switch.

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
  Part_A_Mount (169), Part_A_Test (244) and the Cthulhu tile (1084; counted as admesh joins vertices,
  without the degenerate self-edges an earlier count of 171 / 336 included); Bambu Studio sliced them without a warning.
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

Changes from v20:

- **Ball socket:** v20's cup floor clipped the seat 2.8 mm high, so the ball rested with its equator level with the
  rim and collar pressure squeezed it out. v21 has a full spherical seat, leaves wrapping 2.6 mm above the equator and
  a collar cone on the leaf tips. The first v21 print (six leaves, 15.6 mm mouth) snapped its leaves in PLA as the
  ball went in, which gave the eight-leaf socket above.
- **Collar relief:** the collar's top edge (about 19.6 mm) meets the leaf cone 9.7 mm up and the collar is 9.8 mm tall,
  so on v20's flat pedestal it bottomed out before squeezing (0.40 mm of travel past the crown); the socket now
  stands in a 3 mm relief.
- **Monitor fit:** side channels 0.5 mm per side and 0.5 mm glass-to-lip (v20: 0.3 mm); frame 18.6 mm (v20: 18.0) to
  keep the thick-side lip 1.5 mm.
- **Snow White styling:** equal 22.3 mm borders left, right and top (the top was 3.5 mm short); lines on 10 mm centres,
  1.5 mm deep on both sides (were 6 mm, 1.0 / 1.8 mm deep), set back from the front edge and added to the top and
  bottom; the parting line in a front groove; 4 mm front and 3 mm rear rounds.
- **Bezel geometry repaired:** v20's Blender booleans failed silently: the thick-side lip and the lap tongue were
  missing, the thin-side lip and snap features were loose shells, and the snap arm collided with the Lower's frame.
  Every part is now one manifold solid, with a working snap channel and an LED counterbore.
- **Project file:** 0.4 mm nozzle profile (v20: 0.2 mm), every part on a plate (v20 left Part_B_Lower off the bed),
  per-object layer heights, aux fan 10 %.
