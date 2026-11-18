# Roadmap

Open work only. What shipped is in git history.

## Phase 1: prove the fits on the real parts

- **FIT.A** Print plate 1 and test Part_A_Test with the Polbecky collar and ball: the collar threads on, the ball snaps
  in, and hand-tight it locks the ball without the collar bottoming on the coupon first.
  Done when: the ball holds hand-tight on the coupon, or the failure is reported with what moved.
- **FIT.THIN** Slide the three notched thin-side gauge pieces (6.2 / 6.6 / 7.0 mm) onto the monitor's thin edge and set
  `MON_THIN` from the first that slides without rocking (1 notch: 5.7, 2: 6.1, 3: 6.5), then rebuild.
  Done when: `MON_THIN` in `CAD/build_part_b_blender_v21.py` matches the gauge result and `CAD/build_all.sh` is green.
- **FIT.THICK** Slide the thick-side gauge piece onto the 13.6 mm hump.
  Done when: it slides with light friction, or `MON_THICK` / `FIT_X` are adjusted and rebuilt.

## Phase 2: styling decisions left open

- **STYLE.CHIN** Decide the chin: keep 36.0 mm (compact-Mac proportion, houses the control bay) or bring it toward the
  Portrait Display's near-even borders.
  Done when: the owner has chosen and the bezel is rebuilt to it.
- **STYLE.SURROUND** Decide the screen surround: keep the 1.65 mm bevel to the glass, or widen it (about 5 mm) or deepen
  the ledge for a CRT-like recess.
  Done when: the owner has chosen and the bezel is rebuilt to it.
- **STYLE.BADGE** Give the 14 mm chin badge an emblem (relief or multi-colour), or keep it blank.
  Done when: Part_B_Badge carries the chosen artwork, or the owner keeps it blank.
