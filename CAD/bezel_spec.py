"""
The bezel's front, in ONE place: the screen opening, the outer frame placed round it, and the chin. The bezel
generator (Blender, CAD/build_part_b_blender_v21.py), the chin layout (CAD/chin_spec.py), the fit check
(CAD/check_part_b_fit.py) and the README pictures (CAD/render_views.py) read these, so moving the opening moves
the frame, the chin's centre line, the emblem and the light with it.

Front-view monitor coordinates (Monitor_Dimensions_and_Ports.md): X right, Y up, Z from the bezel face toward the
back; the glass rests on the ledge at Z = LEDGE.
"""

from monitor_spec import IMAGE, REVEAL


def grow(rect, d):
    """(x0, x1, y0, y1) grown by d on every side (shrunk when d < 0)."""
    x0, x1, y0, y1 = rect
    return (x0 - d, x1 + d, y0 - d, y1 + d)


# The screen opening where the bezel meets the glass: the image plus the reveal on every side.
OPENING = grow(IMAGE, REVEAL)
# The bevel down to the glass: 1.65 mm outside the opening at the face (z 0.25), 1.81 mm inside it at z 6.02 (inside
# the pocket, so it only sets the slope), with a 0.3 mm micro-chamfer at the face edge.
BEVEL_FACE, BEVEL_IN, MICRO = 1.65, 1.81, 0.30

# Outer frame. The left wall is 4.5 mm outside the pocket wall (the lap pocket sits at -2.5 and the side lines are
# 1.5 mm deep), so FX0 is fixed; the visible frame (face plus bevel, measured to the opening) is the same width on the
# right and the top, and the chin is 36 mm under the opening.
FX0 = -5.0
BORDER = OPENING[0] - FX0  # 22.3
CHIN = 36.0
FX1 = OPENING[1] + BORDER
FY0 = OPENING[2] - CHIN
FY1 = OPENING[3] + BORDER
BEZEL_CX = (FX0 + FX1) / 2
CHIN_CY = (FY0 + OPENING[2]) / 2  # the visible chin's centre line
