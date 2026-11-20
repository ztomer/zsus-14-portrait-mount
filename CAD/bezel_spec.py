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

# The halves part along Y at SEAM_Y (front view) and are clamped shut by two M3 bolts lying along Y across the seam,
# one per side (CAD/build_part_b_blender_v21.py builds the joints, CAD/check_part_b_fit.py gates them). Each drops in
# from the back into an open channel: its socket head bears on a wall in the Lower, its nut sits in a hex pocket in
# the Upper (it cannot turn), and an L hex key in the slot behind the head turns it, so tightening pulls the seam
# shut. Every bolt face is a pocket open to the back. On the thin side the joint lies inside the 16.7 mm wall; the
# thick side's 4.5 mm wall has no room, so there it stands in a boss on the back, 6.6 mm proud, set in off the outer
# edge over the monitor's back, where it prints on tree supports. (v21.3: a snap arm that bent and let go; v21.4-5:
# vertical screws through a supported tab and a splice plate; v21.6: the boss flush with the outer edge, seen from the
# side.)
SEAM_Y = 177.35
FRAME_H = 18.6  # the bezel's back face, z
NUT_AF, NUT_T = 5.8, 2.7  # hex pocket for an M3 nut (5.5 across flats, 2.4 thick), its flats on +-X
CLEAR_D = 3.4  # the bolt's channel
HEAD_D, HEAD_L = 6.0, 3.2  # room for an M3 socket head (5.5 x 3.0)
WALL_L, WALL_U = (
    3.0,
    3.0,
)  # the Lower's wall under the head and the Upper's in front of the nut, either side of the seam
KEY_SLOT = 22.0  # the slot behind the head: the head and an L key's 18 mm short leg (2.5 mm hex)
TIP_END = 14.0  # the channel runs on this far past the seam for the bolt's tip: M3 x 10 to x 16
# (front-view X, axis Z, head-slot width) per side. The head's slot is as wide as the key's long leg needs to swing 60
# degrees with the bolt's axis that far under the top.
BOLTS = {"thin": (228.5, 14.8, 8.0), "thick": (5.25, 21.6, 6.0)}
KEY_SWING = 30.0  # the key's 2.6 mm leg, 30 degrees off vertical from the axis up to the top
# The thick side's back boss, front-view X: off the outer edge, from the inner face of the outer wall (4.5 mm in from
# the outer face) out over the monitor's back, floating 0.4 mm clear of it on tree supports.
BOSS_X = (-0.5, 11.0)
BOSS_Z1 = FRAME_H + 6.6  # its top
BOSS_Y = (SEAM_Y - WALL_L - KEY_SLOT - 2.0, SEAM_Y + TIP_END + 1.5)
