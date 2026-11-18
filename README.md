# ZSUS 14" Portrait Mount & Apple "Snow White" Open-Back Bezel (v21)

Target printer: Bambu Lab P1S (256 x 256 x 256 mm), **0.4 mm nozzle**, Textured PEI plate.
Material: Generic PLA / PLA+ / Matte PLA. Monitor: ZSUS 14" 2K (PM14A-2K), see `Monitor_Dimensions_and_Ports.md`.

## Files
| File | What it is |
| :--- | :--- |
| `ZSUS_v21_Complete_P1S_PLA.3mf` | Bambu Studio project: 4 plates, per-object settings, slices with no warnings |
| `ZSUS_v21_Assembly_Instructions.pdf` | Print order, fit tests, assembly, disassembly, v20 to v21 changes |
| `STLs/Part_A_Test.stl` | 26.0 x 26.0 x 18.4 mm socket coupon: the mount's exact socket and collar relief, for the collar + ball test |
| `STLs/Part_A_Mount.stl` | 85.0 x 100.0 x 21.3 mm VHB glue-on ball socket |
| `STLs/Part_B_FitGauge.stl` | 55.8 x 55.0 x 18.6 mm: 15 mm of the thick-side channel plus three thin-side channels with 6.2 / 6.6 / 7.0 mm slots (1 / 2 / 3 notches) |
| `STLs/Part_B_Lower.stl` | 245.8 x 211.9 x 18.6 mm lower bezel: chin, badge + LED windows, side channels, lap tongue, snap catch |
| `STLs/Part_B_Upper.stl` | 245.8 x 157.7 x 18.6 mm upper bezel: USB-C bay, snap arm, top-right detent tab |
| `STLs/Part_B_Badge.stl`, `STLs/Part_B_LED.stl` | 15.4 x 15.4 x 3.8 / 7.4 x 3.4 x 3.8 mm press-fit chin accents |
| `CAD/` | Generators and checks (below); `CAD/renders/` holds the guide figures and the last slice report |
| `v20_archive/` | The v20 release as received, untouched |

## Plates (from the last slice, `CAD/renders/slice_report.json`)
| Plate | Contents | Settings | Time | PLA |
| :--- | :--- | :--- | :--- | :--- |
| 1 Fit tests (print first) | Part_A_Test, Part_B_FitGauge | A: 0.16 mm, 5 walls, 40% gyroid, brim; gauge: 0.20 mm, 3 walls, 15% | 0.8 h | 17 g |
| 2 Part A mount + accents | Part_A_Mount, Part_B_Badge, Part_B_LED | 0.16 mm; mount 5 walls 40% gyroid; accents 3 walls 100% | 1.2 h | 30 g |
| 3 Part B lower bezel | Part_B_Lower | 0.20 mm, 3 walls, 15% gyroid, no brim | 3.1 h | 101 g |
| 4 Part B upper bezel | Part_B_Upper | 0.20 mm, 3 walls, 15% gyroid, no brim | 2.4 h | 75 g |

Global: supports off, aux fan 10%, Generic PLA. Part B prints face-down (front on the plate). The project tints the
filament warm light grey (`#D3CFC6`, near Apple "Platinum"; Snow White products were never bright white): load a matte
warm-grey PLA for the bezel to match.

**Print plate 1 first.** Part_A_Test must take the Polbecky collar smoothly, snap the 17 mm ball in, and lock it when
the collar is hand-tight without the ball popping out, and without the collar bottoming on the coupon first. The thick
gauge piece must slide onto the monitor's thick edge with light friction. For the thin edge, the first of the three
notched pieces (1, 2, 3 notches = 6.2, 6.6, 7.0 mm slot) that slides on without rocking sets the panel thickness:
1 notch keeps `MON_THIN = 5.7`; 2 or 3 means set `MON_THIN` to 6.1 or 6.5 in `CAD/build_part_b_blender_v21.py`
and rebuild before printing plates 3 and 4. Thick edge off: adjust `MON_THICK` / `FIT_X` the same way.

## Rebuild everything
```bash
CAD/build_all.sh
```
Needs `uv`, Blender >= 4.5 (MANIFOLD boolean solver; tested on 5.3.0) and Bambu Studio (tested on 02.09.01.70).
Each step refuses to continue on failure:

| Step | Script | Gate |
| :--- | :--- | :--- |
| Part A | `CAD/build_part_a_v21.py` (manifold3d) | watertight single shell; a rigid 17 mm ball must fit at the design centre AND be captured above its equator (fails on both v20 parts); the collar keeps >= 1.5 mm travel after it meets the crown for 19.2..19.95 mm apertures (fails on v21 before the relief: 0.40 mm) |
| Part B | `CAD/build_part_b_blender_v21.py` (Blender, headless) | every boolean result manifold; each part one shell (gauge two), outward-facing; nothing written unless all pass |
| Fit | `CAD/check_part_b_fit.py` | Upper / Lower / monitor overlap 0 for a 13.6 mm (measured) and 14.0 mm (spec) hump; lips over the monitor back (fails at v20's 0.3 mm play); gauge thin slots measured as the Lower's slot + 0 / 0.4 / 0.8 mm; styling: equal visible left / right / top borders, equal groove depth both sides, only the parting-line groove reaches the front edge, the front parting line sits in a groove (all four fail on the pre-2026-11-18 bezel) |
| Project | `CAD/build_3mf_v21.py` | P1S 0.4 nozzle profile, every part inside its plate and clear of the exclusion corner; all 4 plates slice with exit 0 and no warnings |
| Guide | `CAD/render_sections.py`, `CAD/build_pdf_v21.py` | figures cut from the shipped STLs; sizes and times read from the STLs and the slice report |

## Fit allowances (v21)
Sliding channels 0.5 mm per side in X and 0.5 mm glass-to-lip in Z (v20: 0.3 mm), 0.3 mm at the Y ends. The thick channel
is 14.1 mm, so the ZSUS spec thickness (14.0 mm) still slides. The frame is 18.6 mm (v20: 18.0 mm), which keeps the thick-side
lip 1.5 mm thick.

## Bezel styling (Snow White pass, 2026-11-18)
Measured against the Snow White rules (2 mm lines on 10 mm centres set back from the front and back, zero-draft walls,
2 mm front / 3 mm rear edges, inlaid badge, Fog or Platinum colour) and the 1989 Macintosh Portrait Display:
- Visible frame 22.3 mm on the left, right and top (24.3 mm from the image edge, 2.0 mm black reveal), 36.0 mm chin.
- Lines 2.0 mm wide, 1.5 mm deep, 10 mm pitch on both long sides (35 each, from the parting line), the top (clear of the
  USB-C bay) and the bottom (clear of the control bay), from 4.0 mm behind the face to the start of the rear round.
- The Upper / Lower parting line runs through one full-depth side line and a 0.6 mm front-face groove, so it reads as a
  deliberate line.
- 1.5 mm 45-degree front chamfer (prints clean face-down where a round would droop) and a 3 mm rear round.
- Not changed (taste calls): the 36 mm chin (the Portrait Display's borders are nearly even; this chin is closer to a
  compact Mac, and it houses the control bay) and the shallow 1.65 mm bevel to the glass (the Portrait Display has a
  deep dark surround). The badge is a blank square insert, ready for an emblem.

## Known limits
- The Polbecky collar has no inner lip: its top aperture, about 19.6 mm (+/-0.4, scaled from photos against the 1-inch mat
  grid and the 33.0 mm barrel), squeezes the leaf crown (a 22-degree cone from 19.95 mm down to 17.9 mm). The socket
  stands in a 3 mm relief (r 21.5 mm) so the 9.8 mm collar meets that cone with 2.5 to 3.4 mm of travel left.
  Part_A_Test is how you check it.
- The thin panel is 5.7 mm by hand measurement, but 6.1 to 6.8 mm scaled from a side photo against the port shells.
  No caliper reading exists, so the fit gauge's stepped thin-side pieces settle it.
- Part_A_Mount's base (VHB pad, step index, scribe ring, pedestal) has no parametric source: the v20 Fusion script held
  only the boss. v21 grafts its socket onto that base, read from `CAD/assets/Part_A_Mount_base_v20.stl`.
- The 15.6 mm leaf mouth limits ball tilt at the socket to roughly +/-25 degrees. The articulated arm supplies the rest.
