# ZSUS 14" Portrait Mount & Apple "Snow White" Open-Back Bezel (v20)

Target Printer: Bambu Lab P1S (256 x 256 x 256 mm, 0.4 mm nozzle, Textured PEI Plate)
Material: Generic PLA / PLA+ / Matte PLA

## Included Files
- `ZSUS_v20_Complete_P1S_PLA.3mf` — Ready-to-print Bambu Studio project (0.4 mm nozzle, Generic PLA, auto-arranged, supports disabled on Part B, verified slice exit code 0)
- `ZSUS_v20_Assembly_Instructions.pdf` — 2-page dual-latch screwless assembly guide with diagrams
- `STLs/Part_A_Test.stl` — 26.0 x 26.0 x 12.8 mm M22x2.0 thread & 17.0 mm ball calibration coupon
- `STLs/Part_A_Mount.stl` — 85.0 x 100.0 x 20.3 mm CoG-aligned step-indexed VHB glue-on ball socket
- `STLs/Part_B_Upper.stl` — 245.8 x 154.20 x 18.0 mm upper Snow White bezel with 90-deg USB-C bay, 1.80 mm compliant snap arm, and top-right detent tab
- `STLs/Part_B_Lower.stl` — 245.8 x 208.55 x 18.0 mm lower Snow White bezel with 38.0 mm chin, 14 x 14 mm badge window, 6 x 2 mm LED window, and left 45-deg lap joint with 0.35 mm detent
- `STLs/Part_B_Badge.stl` — 15.4 x 15.4 x 3.8 mm press-fit lower-left rainbow badge insert
- `STLs/Part_B_LED.stl` — 7.4 x 3.4 x 3.8 mm press-fit lower-right green LED plug

## Key Slicing & DFM Settings
- **Part A (`Part_A_Test`, `Part_A_Mount`):** 0.16 mm layer height, 5 walls, 40% gyroid infill, outer brim on `Part_A_Test`.
- **Part B (`Part_B_Upper`, `Part_B_Lower`):** 0.20 mm layer height, 3 walls, 15% gyroid infill, Aux fan 10%, **supports disabled** (`enable_support = 0`).
- **Accents (`Part_B_Badge`, `Part_B_LED`):** 0.16 mm layer height, 3 walls, 100% infill, supports disabled.
- **Waist Latching:** 100% tool-free dual-sided locking (1.80 mm right compliant snap arm + 0.35 mm left 45-deg lap-joint micro-detent, 0.20 mm sliding clearances).
- **Bonding Hardware:** 3M VHB 5952 (1.1 mm foam tape, trimmed to 82 x 97 mm with R6.5 mm corners), 70%+ IPA surface prep, 24-hour unweighted cure before hanging.
