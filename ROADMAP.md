# Roadmap

Open work only. What shipped is in git history.

## Phase 1: prove the fits on the real parts

- **FIT.EMBLEM** Print the blank Part_B_Emblem and snap it into the Lower's chin window: it clicks in from the front,
  sits flush without rattling, and pops out when the bridge is pressed forward from behind. Then print the Cthulhu tile
  (plate 5 of `ZSUS_v21_Complete_P1S_PLA.3mf`): the tentacles print separate, the supports
  break cleanly off the onlay's back, and the onlay sits flat on the chin face.
  Done when: it does, or `CAD/build_emblem.py`'s barb (`BARB`, `CATCH_DEG`) or clearances are adjusted and rebuilt.

- **FIT.REVEAL** Print the v21.2 Upper and Lower (plates 3 and 4) and check the black gap between the image and the
  bezel's edge: 0.8 mm on every side (`REVEAL`). The top was not in the 2026-11-19 photo, so its edge still follows
  the spec sheet's image top (304.4). A straight-on photo of the assembled bezel with a light image settles it.
  Done when: all four gaps match, or `IMAGE` in `CAD/monitor_spec.py` takes the photographed edges and is rebuilt.

## Phase 2: styling decisions left open

- **STYLE.SURROUND** Decide the screen surround: keep the 1.65 mm bevel to the glass, or widen it (about 5 mm) or deepen
  the ledge for a CRT-like recess.
  Done when: the owner has chosen and the bezel is rebuilt to it.
