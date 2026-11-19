# ZSUS 14" Portrait Mount & Apple "Snow White" Open-Back Bezel (v21)

A 3D-printed, tool-free bezel that turns the ZSUS 14" 2K portable monitor into a portrait display in the spirit of
Apple's 1980s "Snow White" design language and the Apple IIc monitor, plus a glue-on ball socket that hangs it on an
articulated arm. Every part is generated from source and gated (fits, strains, styling), then sliced to verify.

<p align="center">
<picture><source media="(prefers-color-scheme: dark)" srcset="docs/images/three_quarter_dark.png"><img src="docs/images/three_quarter_light.png" alt="The bezel on the monitor, three-quarter view" width="360"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="docs/images/front_dark.png"><img src="docs/images/front_light.png" alt="The bezel from the front" width="360"></picture>
</p>

<p align="center">
<picture><source media="(prefers-color-scheme: dark)" srcset="docs/images/chin_dark.png"><img src="docs/images/chin_light.png" alt="The chin: soft 4 mm rim, Snow White side lines, the snap-in Cthulhu emblem" width="360"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="docs/images/emblem_dark.png"><img src="docs/images/emblem_light.png" alt="The snap-in emblem tile with the Cthulhu head breaking out of its frame" width="360"></picture>
</p>

<p align="center">
<picture><source media="(prefers-color-scheme: dark)" srcset="docs/images/socket_dark.png"><img src="docs/images/socket_light.png" alt="Part A: the glue-on ball socket with eight leaves and the M22 collar thread" width="300"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="docs/images/tile_dark.png"><img src="docs/images/tile_light.png" alt="The Cthulhu emblem tile as printed, face up, with its two snap arms" width="240"></picture>
<picture><source media="(prefers-color-scheme: dark)" srcset="docs/images/back_dark.png"><img src="docs/images/back_light.png" alt="The open back: channels, rear lips and the latch" width="220"></picture>
</p>

Target printer: Bambu Lab P1S (256 x 256 x 256 mm), **0.4 mm nozzle**, Textured PEI plate.
Material: Generic PLA / PLA+ / Matte PLA. Monitor: ZSUS 14" 2K (PM14A-2K), see `Monitor_Dimensions_and_Ports.md`.

## Files
| File | What it is |
| :--- | :--- |
| `ZSUS_v21_Complete_P1S_PLA.3mf` | Bambu Studio project: 5 plates, per-object settings, slices with no warnings |
| `ZSUS_v21_Assembly_Instructions.pdf` | Print order, fit tests, assembly, disassembly, v20 to v21 changes |
| `STLs/Part_A_Test.stl` | 26.0 x 26.0 x 18.4 mm socket coupon: the mount's exact socket and collar relief, for the collar + ball test |
| `STLs/Part_A_Mount.stl` | 85.0 x 100.0 x 21.3 mm VHB glue-on ball socket |
| `STLs/Part_B_FitGauge.stl` | 55.8 x 55.0 x 18.6 mm: 15 mm of the thick-side channel plus three thin-side channels with 6.2 / 6.6 / 7.0 mm slots (1 / 2 / 3 notches) |
| `STLs/Part_B_Lower.stl` | 245.8 x 211.9 x 18.6 mm lower bezel: chin, emblem window + slit light, side channels, lap tongue, snap catch |
| `STLs/Part_B_Upper.stl` | 245.8 x 157.7 x 18.6 mm upper bezel: USB-C bay, snap arm, top-right detent tab |
| `STLs/Part_B_Emblem.stl` | 18.0 x 18.0 x 11.1 mm snap-in chin emblem tile (blank face), removable from behind |
| `STLs/Part_B_Emblem_Cthulhu.stl` | 18.0 x 22.4 x 12.3 mm emblem tile with the Cthulhu head as an onlay (CC BY, see below) |
| `STLs/Part_B_LED.stl` | 4.0 x 9.4 x 3.8 mm press-fit plug for the vertical slit power light |
| `CAD/` | Generators and checks (below); `CAD/renders/` holds the guide figures and the last slice report |
| `CAD/assets/cthulhu/` | The Cthulhu statue mesh by ChurchOfShrike (CC BY) and its `ATTRIBUTION.md` |
| `docs/images/` | The pictures above, rendered from `STLs/` by `CAD/render_views.py` |
| `v20_archive/` | The v20 release as received, untouched |

## Plates (from the last slice, `CAD/renders/slice_report.json`)
| Plate | Contents | Settings | Time | PLA |
| :--- | :--- | :--- | :--- | :--- |
| 1 Fit tests (print first) | Part_A_Test, Part_B_FitGauge | A: 0.16 mm, 5 walls, 40% gyroid, brim; gauge: 0.20 mm, 3 walls, 15% | 0.8 h | 17 g |
| 2 Part A mount + accents | Part_A_Mount, Part_B_Emblem, Part_B_LED | 0.16 mm; mount 5 walls 40% gyroid; accents 3 walls 100% | 1.2 h | 33 g |
| 3 Part B lower bezel | Part_B_Lower | 0.20 mm, 3 walls, 15% gyroid, no brim | 3.1 h | 100 g |
| 4 Part B upper bezel | Part_B_Upper | 0.20 mm, 3 walls, 15% gyroid, no brim | 2.4 h | 75 g |
| 5 Cthulhu emblem (optional) | Part_B_Emblem_Cthulhu | 0.08 mm, 3 walls, 100%, tree supports from the plate | 0.4 h | 4 g |

Global: supports off (plate 5's tile turns them on for itself), aux fan 10%, Generic PLA. Part B prints face-down (front on the plate). The project tints the
filament warm light grey (`#D3CFC6`, near Apple "Platinum"; Snow White products were never bright white): load a matte
warm-grey PLA for the bezel to match.

**Print plate 1 first.** Part_A_Test must take the Polbecky collar smoothly, snap the 17 mm ball in, and lock it when
the collar is hand-tight without the ball popping out, and without the collar bottoming on the coupon first. The thick
gauge piece must slide onto the monitor's thick edge with light friction. For the thin edge, the first of the three
notched pieces (1, 2, 3 notches = 7.0, 7.4, 7.8 mm slot) that slides on without rocking sets the panel thickness:
1 notch keeps `MON_THIN = 6.5`; 2 or 3 means raise `MON_THIN` in `CAD/monitor_spec.py` by 0.4 or 0.8 mm and rebuild
before printing plates 3 and 4. Thick edge off: adjust `MON_THICK` (same file) / `FIT_X` the same way.
On the owner's monitor (2026-11-18) the socket coupon, the thick piece and the first gauge's 7.0 mm thin piece all fit.

## Rebuild everything
```bash
CAD/build_all.sh
```
Needs `uv`, Blender >= 4.5 (MANIFOLD boolean solver; tested on 5.3.0) and Bambu Studio (tested on 02.09.01.70).
Each step refuses to continue on failure:

| Step | Script | Gate |
| :--- | :--- | :--- |
| Part A | `CAD/build_part_a_v21.py` (manifold3d) | watertight single shell; a rigid 17 mm ball must fit at the design centre AND be captured above its equator (fails on both v20 parts); the collar keeps >= 1.5 mm travel after it meets the crown for 19.2..19.95 mm apertures (fails on v21 before the relief: 0.40 mm); leaf bending strain snapping the ball in <= 1.5 % (fails on the first v21 print's leaves: 3.07 %) |
| Relief | `CAD/make_relief.py --self-test` | handedness end to end: a feature on the source's right seats on the viewer's right (red with the mirrored mapping the first cut had) |
| Emblem | `CAD/build_emblem.py` (manifold3d) | arm strain <= 2 % at the deflection that passes the hole; barb grip >= 0.3 mm; arm tips >= 0.3 mm clear of the shoulder as printed and clear of body and spine when deflected (each fails when its margin is broken) |
| Part B | `CAD/build_part_b_blender_v21.py` (Blender, headless) | every boolean result manifold; each part one shell (gauge two), outward-facing; nothing written unless all pass |
| Fit | `CAD/check_part_b_fit.py` | Upper / Lower / monitor overlap 0 for a 13.6 mm (measured) and 14.0 mm (spec) hump; lips over the monitor back (fails at v20's 0.3 mm play); gauge thin slots measured as the Lower's slot + 0 / 0.4 / 0.8 mm; styling: equal visible left / right / top borders, equal groove depth both sides, only the parting-line groove reaches the front edge, the front parting line sits in a groove (all four fail on the pre-2026-11-18 bezel; borders are measured on the screen opening's own run, since the rim round's flanks also lie behind the glass plane); emblem (seated by `chin_spec.EMBLEM_PLACE`, asserted a rotation, never a mirror): no overlap seated, face flush, pushed back 0.15 mm it lands on the seat, pulled forward 0.25 mm the barbs catch |
| Emblem art | `CAD/make_relief.py`, `CAD/build_emblem.py --relief` | the Cthulhu head's top inside the tile, the onlay seated in the real Lower with no overlap and on flat chin face all round |
| STL files | `CAD/stl_io.py` (every manifold3d writer), `CAD/check_stl_files.py` | every shipped STL read back as a slicer reads it (vertices joined by exact float32 equality): each edge shared by exactly two faces, positive volume, one body (the gauge four); fails on v21.0.0's 171 / 336 / 1084 pinched edges |
| Project | `CAD/build_3mf_v21.py` | P1S 0.4 nozzle profile, every part inside its plate and clear of the exclusion corner; all 5 plates slice with exit 0 and no warnings; a plate whose part asks for supports has them in its G-code |
| Guide | `CAD/render_sections.py`, `CAD/build_pdf_v21.py` | figures cut from the shipped STLs; sizes and times read from the STLs and the slice report |
| Pictures | `CAD/render_views.py` (Blender), `CAD/pack_images.py` | the README pictures, light and dark, placed by the same rigid matrices as the fit checks |

## Fit allowances (v21)
Sliding channels 0.5 mm per side in X and 0.5 mm glass-to-lip in Z (v20: 0.3 mm), 0.3 mm at the Y ends. The thick channel
is 14.1 mm, so the ZSUS spec thickness (14.0 mm) still slides. The frame is 18.6 mm (v20: 18.0 mm), which keeps the thick-side
lip 1.5 mm thick.

## Bezel styling (Snow White pass, 2026-11-18)
Measured against the Snow White rules (2 mm lines on 10 mm centres set back from the front and back, zero-draft walls,
2 mm front / 3 mm rear edges, inlaid badge, Fog or Platinum colour) and the 1989 Macintosh Portrait Display:
- Visible frame 22.3 mm on the left, right and top (24.3 mm from the image edge, 2.0 mm black reveal), 36.0 mm chin.
- Lines 2.0 mm wide, 1.5 mm deep, 10 mm pitch on both long sides (35 each, from the parting line), the top (clear of the
  USB-C bay) and the bottom (clear of the control bay), from 5.0 mm behind the face (past the front round) to the start of the rear round.
- The Upper / Lower parting line runs through one full-depth side line and a 0.6 mm front-face groove, so it reads as a
  deliberate line.
- 4 mm front round, after the Apple IIc monitor's soft rim (Snow White's own rule is 2 mm). Face-down, the part of a
  round flatter than 45 degrees would droop, so below its 45-degree point it continues as a 45-degree chamfer (a
  teardrop round). 3 mm rear round.
- Not changed (taste calls): the 36 mm chin (the Portrait Display's borders are nearly even; this chin is closer to a
  compact Mac, and it houses the control bay) and the shallow 1.65 mm bevel to the glass (the Portrait Display has a
  deep dark surround).

## Chin (Apple IIc monitor details, 2026-11-18)
The 36 mm chin stays (it houses the control bay) and takes the IIc monitor's details: the soft front rim above, a
vertical slit power light lower-right (1.6 x 7 mm, `Part_B_LED` pressed in from the back; it is a styling plug, the
monitor's own status LED is in the control bay), and an 18 mm emblem lower-left. The window numbers live in
`CAD/chin_spec.py`, which both the bezel and the emblem generator read.

The emblem is a snap-in tile, so it can be changed without taking the bezel off. The window is stepped: an 18.4 mm
pocket 0.8 mm deep, a 45-degree seat, then a 16.4 mm hole through the 3 mm plate. The tile's cap fills the pocket flush
with the face, its shoulder lands on the seat, and two 0.8 mm cantilever arms from a rear bridge carry barbs that catch
0.35 mm behind the plate. **Fit:** push it in from the front until it clicks. **Remove:** reach into the control bay
from behind and press the bridge forward; the catch faces lean 35 degrees, so the plate cams the arms in and the tile
comes out the front. It prints face-up (the bridge on the bed), so a relief on the face prints as top surfaces.

### Emblem art: the Cthulhu head
The first emblem is the head of **"Chtulhu Statue" by ChurchOfShrike** (MakerWorld model 1705652,
https://makerworld.com/en/models/1705652-chtulhu-statue), used under **Creative Commons Attribution (CC BY)**. The
statue mesh is in `CAD/assets/cthulhu/` with its `ATTRIBUTION.md`; the changes are ours: `CAD/make_relief.py`
(recipe `CAD/emblems/cthulhu.json`) depth-casts the statue from the front, cuts the head and its tentacle beard out of
the shoulders, hands and wings behind it, and compresses it into a 1.2 mm relief on the tile.

It is an **onlay**, 11.1 x 21.7 mm: its dome stays inside the tile's frame and its tentacle beard spills out of the
frame onto the chin face, where it rests, ending on flat face above the bezel's rounded rim. The tile then stops on
the chin face rather than its seat, and still pops out from behind. `CAD/build_emblem.py` gates it seated in the real
Lower: no overlap, a stop when pushed back, and flat chin face under the whole onlay plus 0.5 mm (red at 71.7 % when
the head is moved 6 mm up over the screen edge). It prints on plate 5 at 0.08 mm with tree supports under the
overhang; break them off the onlay's back, which sits against the chin unseen, and swap the tile in from the front.

Other emblems: put a model in `CAD/emblems/<name>.json` (`"mode": "onlay"` or `"inlay"`, the art inside the tile's
recessed panel with no supports). Art under a personal-use licence goes in the gitignored `CAD/third_party/`, and
`CAD/build_emblem_art.sh CAD/emblems/<name>.json` builds its relief, tile and one-plate project next to it, out of git.

## Known limits
- The Polbecky collar has no inner lip: its top aperture, about 19.6 mm (+/-0.4, scaled from photos against the 1-inch mat
  grid and the 33.0 mm barrel), squeezes the leaf crown (a 22-degree cone from 19.95 mm down to 17.9 mm). The socket
  stands in a 3 mm relief (r 21.5 mm) so the 9.8 mm collar meets that cone with 2.5 to 3.4 mm of travel left.
  Part_A_Test is how you check it.
- The thin panel was 5.7 mm by hand measurement, 6.1 to 6.8 mm scaled from a side photo. The first fit gauge settled
  it at 6.5 mm (only its 7.0 mm slot slides on); the monitor's measurements live in `CAD/monitor_spec.py`.
- Part_A_Mount's base (VHB pad, step index, scribe ring, pedestal) has no parametric source: the v20 Fusion script held
  only the boss. v21 grafts its socket onto that base, read from `CAD/assets/Part_A_Mount_base_v20.stl`.
- The 16.4 mm leaf mouth limits ball tilt at the socket (a little more than the first print's 15.6 mm mouth, about
  +/-25 degrees). The articulated arm supplies the rest.
- Plain PLA only: the first PLA socket snapped its leaves as the ball went in. They stand vertical in the print, so
  the bend pulls across the layer lines, PLA's weakest direction. Eight leaves, a 0.3 mm snap per leaf and slots cut
  2.3 mm deeper bring the modelled peak strain from 3.1 % to 1.0 % (gate: <= 1.5 %). Push the ball in straight and
  firmly; the collar, not the snap, is what locks it. PETG would add a large margin if it is ever on hand.

## Licence
[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE): print, remix and share it, commercially too, as
long as you credit this project. The Cthulhu emblem is a derivative of "Chtulhu Statue" by ChurchOfShrike (CC BY);
keep that credit too (`CAD/assets/cthulhu/ATTRIBUTION.md`).
