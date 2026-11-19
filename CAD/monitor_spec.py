"""
The monitor the bezel is built around, in ONE place: the bezel generator (Blender, CAD/build_part_b_blender_v21.py),
the fit check (CAD/check_part_b_fit.py), the section figures (CAD/render_sections.py) and the assembly guide
(CAD/build_pdf_v21.py) all read these, so a measurement changed here reaches every part, gate, figure and page.

Front-view monitor coordinates (Monitor_Dimensions_and_Ports.md): X right, Y up, Z from the bezel face toward the
back. Portrait, the chin bezel on the left: a 13.6 mm hump over X 0..73, a step, and a flat panel over X 76..220.
"""

MON_W, MON_H = 220.0, 310.0
MON_THICK = 13.6  # measured hump (X 0..73); ZSUS spec max is 14.0; the thick gauge piece slides on (2026-11-18)
# The flat panel (X 76..220) is 5.7 mm by hand measurement and 6.1..6.8 mm scaled from a side photo. The fit gauge
# settled it (2026-11-18): only the 3-notch piece (7.0 mm slot) slides on, with light friction and no rocking, and the
# 6.2 / 6.6 mm pieces do not, so the panel is 7.0 - FIT_Z = 6.5 mm.
MON_THIN = 6.5
HUMP_X1, STEP_X1 = 73.0, 76.0  # the hump ends, and the step down to the flat panel ends
LEDGE = 3.0  # the bezel's front ledge the glass rests on
FIT_Z = 0.5  # glass-to-lip channel play (CAD/build_part_b_blender_v21.py lets PARTB_FIT_Z override it)

# The lit image (X0, X1, Y0, Y1), the monitor centred in the bezel's pocket. The spec sheet put it at X 19.3..216.5,
# Y 8.5..304.4, and the v21.1 bezel left 2.0 mm of black glass round it on that basis. The owner's photo of that
# printed Lower on the monitor (2026-11-19, monitor resting on the chin, 0.3 mm below centre) read the black between
# the image and the bezel's edge as 0.8 mm left, 4.4 mm right (4.2..4.6 along the side) and 1.4 mm at the bottom,
# measured in each row against the image's own 197.2 mm width: the image sits 1.2 mm left of the sheet on its left
# edge, 2.4 mm left on its right edge, and 0.3 mm low. The top was not in the photo; it keeps the sheet's 304.4.
IMAGE = (18.1, 214.1, 8.2, 304.4)
REVEAL = 0.8  # black glass left showing round the image: every side as the photo's left side (owner, 2026-11-19)
