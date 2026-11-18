# ZSUS 14" Portable Monitor & Polbecky Arm — Measured Reference (v20)

All coordinates are in **Portrait Mode (chin bezel on the left)**, viewed from the **front**:
- **X:** `0.0 mm` (left outer edge) -> `220.0 mm` (right outer edge)
- **Y:** `0.0 mm` (bottom outer edge) -> `310.0 mm` (top outer edge)
- **Z:** `0.0 mm` (front glass plane) -> `+Z` toward the rear

## 1. Monitor Chassis & Active LCD
| Feature | Dimensions / Coordinates | Notes |
| :--- | :--- | :--- |
| **Outer Chassis Footprint** | `220.0 mm (W) x 310.0 mm (H)`, `R = 6.0 mm` corners | Cradle pocket is `220.6 x 310.6 mm` (`0.30 mm`/side clearance) |
| **Active LCD Area** | `197.2 x 295.9 mm` (`X = 19.3..216.5`, `Y = 8.5..304.4`) | Part B inner aperture (`197.6 x 296.3 mm`) leaves `0.20 mm` margin/side |
| **Front Monitor Bezels** | Left `19.3 mm` \| Right `3.5-5.5 mm` \| Top `8.9 mm` \| Bottom `8.5 mm` | Part B equalizes Left/Right/Top to `24.1 mm` + `38.0 mm` chin |
| **Rear Thick Hump (Left)** | `X = 0.0..73.0 mm`, `13.6 mm` thick | Houses 14W driver board; Part B left lip wraps at `Z_b = 16.9..18.0 mm` |
| **Rear Step Bevel** | `X = 73.0..76.0 mm`, `3.0 mm` run x `7.9 mm` drop (`45 deg`) | `Part_A_Mount` indexes flush against `X = 76.0 mm` |
| **Rear Flat Panel (Right)** | `X = 76.0..220.0 mm`, `5.7 mm` thick | `Part_A_Mount` bonds here; Part B right lip wraps at `Z_b = 9.0..11.0 mm` |

## 2. Top-Edge Ports (`Y = 310.0 mm`, Left-to-Right)
| Port / Feature | Center (`X`) | Span (`X`) | Clearance Notes |
| :--- | :--- | :--- | :--- |
| **Mini HDMI (`HD`)** | `21.9 mm` | `16.5..27.3 mm` | Inside top-left open rear bay (`X = 14.0..65.0 mm`) |
| **USB-C #1 (Orange 90 deg Adapter)** | `40.0 mm` | `35.8..44.2 mm` | Stands `11.5 mm` above `Y = 310.0`; front nose/lanyard protrudes `~1.0 mm` forward (`X = 34..46`); cleared by `14.0 x 20.6 x 1.5 mm` relief channel (`X = 33..47`) |
| **USB-C #2 (Lightning/Video)** | `57.2 mm` | `53.0..61.4 mm` | Inside top-left open rear bay (`X = 14.0..65.0 mm`) |
| **Slot #4** | `70.0 mm` | `67.5..72.5 mm` | Clears `Part_B_Upper` top-left bay & `5.7 mm` step |

## 3. Bottom-Left Controls (`X = 0.0..73.0 mm`, `Y = 0.0 mm`)
- **Power button, OSD dial/rocker wheel, 3.5 mm audio jack, and status LED** all sit along the bottom-left edge (`X = 0..73 mm`) and remain unobstructed via `Part_B_Lower`'s open control bay (`X = 12.0..73.0 mm`, `Y = -29.5..0.0 mm`, `Z_b = 3.0..18.0 mm`).

## 4. Polbecky PO-CA-001 Articulated Arm
- **Ball Stud:** `17.0 mm` diameter (`~9.5 mm` neck) | **Max Load:** `1,200 g` (`1.2 kg`)
- **Factory Winged Collar:** `M22 x 2.0` internal thread (`~22.3 mm` major ID), `33.0 mm` barrel OD, `41.3 mm` wing span, `9.8 mm` height.
- **Socket Placement:** `Part_A_Mount` centers the socket at `X = 104.0 mm` (`28.0 mm` from the `X = 76.0 mm` step edge, aligned with portrait CoG) and `Z = 9.5 mm` pedestal height (`1.6 mm` proud of the `7.9 mm` electronics hump so the `41.3 mm` collar spins freely).
