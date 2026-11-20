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

# The halves part along Y at SEAM_Y (front view). On the thin side they are held by ONE M3 screw used as a pin
# (CAD/build_part_b_blender_v21.py builds it, CAD/check_part_b_fit.py gates it): a tab on the Lower's back laps over a
# recess in the Upper's, and the screw drops through the tab into an M3 nut held in a hex pocket in the recess floor, so
# pulling the halves apart is shear on the screw, not a bend. (v21.3's snap arm, a 1.8 mm cantilever, bent and let go.)
# Face-down, the tab past the seam takes tree supports, and their travel strings: on the Upper its 49 open-air hops put
# plate 4 over its 250 (256), so the tab is the Lower's, whose plate had the room (183 before).
SEAM_Y = 177.35
TAB_X = (224.0, 233.0)  # front-view X: the pocket wall is at 220.5, the outer face's back round starts at 234.2
TAB_LEN = 10.0  # how far the tab reaches past the seam over the Upper
TAB_Z0 = 12.6  # the tab's underside: 6.0 mm of tab under the 18.6 mm back face
SCREW = ((TAB_X[0] + TAB_X[1]) / 2, SEAM_Y + TAB_LEN / 2)  # the screw's axis, front view (X, Y)
CLEAR_D = 3.4  # M3 clearance, through the tab and below the nut
HEAD_D, HEAD_K = 6.5, 3.2  # counterbore in the tab's back: an M3 socket, button or pan head sits below the face
NUT_AF, NUT_T = 5.8, 2.7  # hex pocket for an M3 nut (5.5 across flats, 2.4 thick), a flat facing the pull
HOLE_Z0 = 3.0  # the hole's bottom, 3 mm behind the front face: an M3 x 6 to x 12 screw fits

# The thick side's 4.5 mm wall has no room for a nut, so its joint stands on the back: a boss on each half's back at
# the seam, an M3 nut in a hex pocket in each, and a flat splice plate (Part_B_Splice, printed on its own) laid across
# both with an M3 screw into each nut. Every face prints without supports: the bosses grow up from the back, their
# inner edge over the monitor is a 45-degree chamfer. With both sides pinned the halves cannot part; the lap tongue
# and its detent only align them. (v21.4.0: the thick side had the detent alone, and opened 1.0 mm when pulled.)
FRAME_H = 18.6  # the bezel's back face, z
BOSS_X = (-5.0, 4.0)  # front-view X: flush with the outer face; over the monitor from the lip's edge at 1.7
BOSS_LEN = 11.5  # along Y on each side of the seam
BOSS_Z1 = FRAME_H + 8.0  # the bosses' top, where the splice plate lies
SPLICE_T = 3.0
THICK_SCREWS = [(-0.5, SEAM_Y - 6.0), (-0.5, SEAM_Y + 6.0)]  # front view (X, Y): the Lower's, the Upper's
THICK_HOLE_Z0 = 17.6  # the holes' bottom, 0.5 mm into the rear lip over the monitor: M3 x 6 to x 10
