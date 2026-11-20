# Roadmap

Open work only. What shipped is in git history.

## Phase 1: prove the fits on the real parts

- **FIT.EMBLEM** Print the blank Part_B_Emblem and snap it into the Lower's chin window: it clicks in from the front,
  sits flush without rattling, and pops out when the bridge is pressed forward from behind. Then print the Cthulhu tile
  (plate 5 of `ZSUS_v21_Complete_P1S_PLA.3mf`): the tentacles print separate, the supports
  break cleanly off the onlay's back, and the onlay sits flat on the chin face.
  Done when: it does, or `CAD/build_emblem.py`'s barb (`BARB`, `CATCH_DEG`) or clearances are adjusted and rebuilt.

- **FIT.SEAM** Print plate 1's seam test (`Part_B_SeamTest_Upper` + `_Lower`) with an M3 nut and an M3 socket-head
  bolt (10 to 16 mm): the nut stands in its pocket and does not turn, the bolt drops into its channel, a 2.5 mm L key
  turns it, and it pulls the pieces shut so they do not move when pulled. Then print the v21.7 Upper and Lower (plates
  3 and 4): the tree supports under the thick-side back boss snap off clean and leave no hairs on the screen opening's
  edge at the seam, and on the monitor both seam bolts pull the halves shut. Done when: they do, or the joint
  (`BOLTS`, `WALL_*`, `NUT_*`, `KEY_SLOT` in `CAD/bezel_spec.py`), `MON_H` (`CAD/monitor_spec.py`, tape 311.0) or the
  shrink compensation (`filament_shrink` 99.4 %, `CAD/layout.json`, from one tape reading of the closed bezel: about
  354 of 356.1 mm) is corrected and rebuilt. The closed v21.7 bezel should measure 355.8 mm (the model's length).

- **FIT.REVEAL** With the v21.3 bezel on, check the black gap between the image and the bezel's edge: 0.8 mm on every
  side (`REVEAL`). The top edge is now the image's bottom plus its active height (304.1), not a photographed edge,
  and the screen-on photo of 2026-11-19 put the image's left edge 16.8..17.0 mm from the monitor's, against the
  18.1 the opening was cut for. The image's X edges were read against the v21.1 Lower's opening, which shrank 0.6 %
  (about 0.5 mm at each side edge), so they may move by that much. A straight-on photo of the assembled bezel with a light image settles both.
  Done when: all four gaps match, or `IMAGE` in `CAD/monitor_spec.py` takes the photographed edges and is rebuilt.

## Phase 2: styling decisions left open

- **STYLE.SURROUND** Decide the screen surround: keep the 1.65 mm bevel to the glass, or widen it (about 5 mm) or deepen
  the ledge for a CRT-like recess.
  Done when: the owner has chosen and the bezel is rebuilt to it.
