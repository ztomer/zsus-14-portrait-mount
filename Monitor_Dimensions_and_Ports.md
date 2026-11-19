# ZSUS 14" Portable Monitor & Polbecky Arm — Measured Reference

All coordinates are in **Portrait Mode (chin bezel on the left)**, viewed from the **front**:
- **X:** `0.0 mm` (left outer edge) -> `220.0 mm` (right outer edge)
- **Y:** `0.0 mm` (bottom outer edge) -> `310.0 mm` (top outer edge)
- **Z:** `0.0 mm` (front glass plane) -> `+Z` toward the rear

## 1. Monitor Chassis & Active LCD
| Feature | Dimensions / Coordinates | Notes |
| :--- | :--- | :--- |
| **Outer Chassis Footprint** | `220.0 mm (W) x 310.0 mm (H)`, `R = 6.0 mm` corners | v21 cradle pocket is `221.0 x 310.6 mm` (`0.50 mm`/side along the sliding channels, `0.30 mm` at the ends) |
| **Active LCD Area** | `197.2 x 295.9 mm`; spec sheet `X = 19.3..216.5`, `Y = 8.5..304.4`; as photographed in the bezel (2026-11-19) `X = 18.1..214.1`, `Y = 8.2..304.4` (top not photographed) | Part B's opening meets the glass `0.8 mm` outside the photographed image on every side (`IMAGE`, `REVEAL` in `CAD/monitor_spec.py`) |
| **Front Monitor Bezels** | Left `19.3 mm` \| Right `3.5-5.5 mm` \| Top `8.9 mm` \| Bottom `8.5 mm` (hand-measured; the photo puts the image `1.2..2.4 mm` further left) | Part B equalizes Left/Right/Top to a `22.3 mm` visible frame + `0.8 mm` black reveal, and a `36.0 mm` chin |
| **Rear Thick Hump (Left)** | `X = 0.0..73.0 mm`, `13.6 mm` thick | Houses 14W driver board; v21 Part B left lip wraps at `Z_b = 17.1..18.6 mm` (`0.5 mm` play; a `14.0 mm` hump still slides) |
| **Rear Step Bevel** | `X = 73.0..76.0 mm`, `3.0 mm` run x `7.9 mm` drop (`45 deg`) | `Part_A_Mount` indexes flush against `X = 76.0 mm` |
| **Rear Flat Panel (Right)** | `X = 76.0..220.0 mm`, `6.5 mm` thick (fit gauge 2026-11-18; a hand measurement read `5.7 mm`) | `Part_A_Mount` bonds here; v21 Part B right lip wraps at `Z_b = 10.0..12.0 mm` (`7.0 mm` slot, `0.5 mm` play); `Part_B_FitGauge` also has `7.4` / `7.8 mm` slots |

## 2. Top-Edge Ports (`Y = 310.0 mm`, Left-to-Right)
| Port / Feature | Center (`X`) | Span (`X`) | Clearance Notes |
| :--- | :--- | :--- | :--- |
| **Mini HDMI (`HD`)** | `21.9 mm` | `16.5..27.3 mm` | Inside top-left open rear bay (`X = 14.0..65.0 mm`) |
| **USB-C #1 (Orange 90 deg Adapter)** | `40.0 mm` | `35.8..44.2 mm` | Stands `11.5 mm` above `Y = 310.0`; front nose/lanyard protrudes `~1.0 mm` forward (`X = 34..46`); cleared by `14.0 x 20.6 x 1.5 mm` relief channel (`X = 33..47`) |
| **USB-C #2 (Lightning/Video)** | `57.2 mm` | `53.0..61.4 mm` | Inside top-left open rear bay (`X = 14.0..65.0 mm`) |
| **Slot #4** | `70.0 mm` | `67.5..72.5 mm` | Clears `Part_B_Upper` top-left bay & `6.5 mm` step |

## 3. Bottom-Left Controls (`X = 0.0..73.0 mm`, `Y = 0.0 mm`)
- **Power button, OSD dial/rocker wheel, 3.5 mm audio jack, and status LED** all sit along the bottom-left edge (`X = 0..73 mm`) and remain unobstructed via `Part_B_Lower`'s open control bay (`X = 12.0..73.0 mm`, `Y = -28.6..0.0 mm`, `Z_b = 3.0..18.6 mm`).

## 4. Polbecky PO-CA-001 Articulated Arm
- **Ball Stud:** `17.0 mm` diameter (`~9.5 mm` neck) | **Max Load:** `1,200 g` (`1.2 kg`)
- **Factory Winged Collar:** `M22 x 2.0` internal thread (`~22.3 mm` major ID), `33.0 mm` barrel OD, `41.3 mm` wing span, `9.8 mm` height, top aperture `~19.6 mm` (`+/-0.4`, from photos; no inner lip, the top edge squeezes the leaves).
- **Socket Placement:** `Part_A_Mount` centers the socket at `X = 104.0 mm` (`28.0 mm` from the `X = 76.0 mm` step edge, aligned with portrait CoG), boss base at `Z = 9.5 mm`. A `3.0 mm` deep, `r = 21.5 mm` collar relief (floor `Z = 6.5 mm`) clears the `41.3 mm` wings and lets the collar reach the leaf cone with `2.5..3.4 mm` of travel to spare.

## 5. Cross-check against the ZSUS published spec (2026-11-18)
The ZSUS 14" 2K portable monitor (PM14A-2K / PM14T-2K, 2160 x 1440, 15:10) user manual lists the product as
**310 mm (W) x 220 mm (H) x 14 mm (thickness), approx. 500 g (PM14A-2K) / 750 g (PM14T-2K)**, with the note that the
figures are hand-measured and approximate (manuals.plus/ae/1005006111326351). That matches the `220.0 x 310.0 mm`
footprint above; it publishes no thin-edge thickness and no per-zone figures.

| Quantity | Measured (above) | ZSUS spec | v21 bezel sized for |
| :--- | :--- | :--- | :--- |
| Footprint | `220.0 x 310.0 mm` | `220 x 310 mm` (approx.) | `221.0 x 310.6 mm` pocket |
| Thick hump | `13.6 mm` | `14 mm` max thickness | `14.1 mm` channel (front ledge to lip) |
| Thin panel | `6.5 mm` (fit gauge; hand `5.7 mm`) | not published | `7.0 mm` slot; gauge also `7.4` / `7.8 mm` |

The monitor's measurements (`MON_*`, `LEDGE`, `FIT_Z`) live in `CAD/monitor_spec.py`, the other fit allowances
(`FIT_X`, `FIT_Y`) at the top of `CAD/build_part_b_blender_v21.py`;
print `Part_B_FitGauge` (plate 1) to check them on the real monitor before printing the bezel.
