"""
The chin's emblem window and the snap-in emblem tile that fills it, in ONE place: the bezel generator
(Blender, CAD/build_part_b_blender_v21.py) cuts the window from these numbers and the emblem generator
(manifold3d, CAD/build_emblem.py) sizes the tile from them, so the two cannot drift apart.

Front-view monitor coordinates (Monitor_Dimensions_and_Ports.md): X right, Y up, Z from the bezel face
toward the back. The window sits in the 3 mm chin plate over the open control bay (X 12..73, Y -30..0),
so the tile's back is reachable from behind without taking the bezel off.
"""

# Placement (Apple IIc monitor: emblem lower-left, light lower-right, both on the chin's centre line). The visible
# chin runs Y -29.5..6.5 (36 mm), so its centre line is Y -11.5; the emblem's visible edge (the pocket plus the
# 0.225 mm its front chamfer is wide at the face) lines up with the screen opening's left edge at X 17.3,
# and the light mirrors it about the bezel centre.
CHIN_CY = -11.5
OPENING_X0, BEZEL_CX = 17.3, 117.9
EMBLEM_CX, EMBLEM_CY = OPENING_X0 + 18.4 / 2 + 0.225, CHIN_CY  # window centre (26.725, -11.5)
# The window is stepped so the tile seats from the front with its face flush: an 18.4 mm pocket 0.8 mm deep,
# a 45-deg seat narrowing it to a 16.4 mm hole (z 0.8..1.8), and the hole through the rest of the plate.
# The seat is 45 deg so it prints as a roof with the bezel face-down and as an overhang with the tile face-up.
EMBLEM_WIN = 18.4  # pocket, square
EMBLEM_POCKET = 0.8  # pocket depth before the seat
EMBLEM_HOLE = 16.4  # hole behind the seat, square
CHIN_PLATE = 3.0  # plate thickness the tile's barbs catch behind (the bezel's LEDGE)
TILE_DEPTH = 11.1  # emblem tile, face to the back of its bridge (in the bay, which is open to Z = 18.6)

# Vertical slit power-light window, lower-right (the IIc monitor's slit), and its plug's rear counterbore
LED_CX = 2 * BEZEL_CX - EMBLEM_CX  # 209.0
LED_SLIT = (LED_CX - 0.8, LED_CX + 0.8, CHIN_CY - 3.5, CHIN_CY + 3.5)  # X0, X1, Y0, Y1: 1.6 x 7 mm
LED_BORE = (LED_CX - 3.0, LED_CX + 3.0, CHIN_CY - 5.5, CHIN_CY + 5.5)

assert abs(EMBLEM_CX - (OPENING_X0 + EMBLEM_WIN / 2 + 0.225)) < 1e-9

# Seating the PRINTED tile (STLs/Part_B_Emblem.stl, face up) in the Lower's print frame. A printed part can only be
# moved, never mirrored, so this must be a rotation plus a shift (determinant +1; every user asserts it). The tile
# frame (u, v, w) is right-handed with w running from the face into the part, so a viewer of the face sees v up and
# u to their LEFT, the same mirror as the bezel's print frame (front-view X = -x): front-view X = EMBLEM_CX - u.
EMBLEM_PLACE = [  # printed (p, q, r) = (u, -v, TILE_DEPTH - w)  ->  (x, y, z) = (u - EMBLEM_CX, EMBLEM_CY + v, w)
    [1.0, 0.0, 0.0, -EMBLEM_CX],
    [0.0, -1.0, 0.0, EMBLEM_CY],
    [0.0, 0.0, -1.0, TILE_DEPTH],
]
