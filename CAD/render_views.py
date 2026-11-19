"""
README pictures (docs/images/*_{light,dark}.png), rendered headless by Blender from the shipped STLs/, so the
pictures always show the parts that print. Placement comes from CAD/chin_spec.py (the same rigid matrices the fit
checks use), never from numbers typed here.

    blender -b --factory-startup --python-exit-code 1 -P CAD/render_views.py

Each view is rendered on a light and a dark backdrop; the README shows the one matching the reader's theme.
The monitor is a stand-in (black glass, grey image area, the 13.6 mm hump), only there to give the bezel context.
"""

import os
import sys

import bpy
from mathutils import Matrix, Vector

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "docs", "images")
sys.path.insert(0, HERE)
from bezel_spec import BEZEL_CX, FY0, FY1  # noqa: E402
from chin_spec import CHIN_CY, EMBLEM_CX, EMBLEM_PLACE, LED_CX  # noqa: E402
from monitor_spec import IMAGE  # noqa: E402

PLATINUM = (0.827, 0.812, 0.776, 1)
EMBLEM = os.environ.get("EMBLEM", "Part_B_Emblem_Cthulhu")
BACKDROPS = (("light", (0.93, 0.93, 0.93)), ("dark", (0.08, 0.08, 0.09)))


def reset(shadows=True):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sh = sc.display.shading
    sh.light, sh.color_type = "STUDIO", "OBJECT"
    sh.show_cavity, sh.cavity_type = True, "BOTH"
    sh.show_shadows = shadows  # off for the bezel: its shadow on the recessed screen renders as blocks
    sc.display.light_direction = (0.5, 0.6, 0.62)
    sc.display.shadow_shift = 0.5  # the default bias draws shadow acne across the flat stand-in screen
    sc.render.image_settings.color_mode = "RGB"
    sc.world = bpy.data.worlds.new("W")
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))
    sc.collection.objects.link(cam)
    sc.camera = cam
    # the scene is in mm: a 0.1 near plane spends the depth buffer before 600 mm, and the stand-in screen (0.01 mm
    # in front of the monitor body) z-fights in blocks
    cam.data.clip_start, cam.data.clip_end = 20.0, 2000.0
    return sc, cam


def stl(name, colour, matrix=None):
    bpy.ops.wm.stl_import(filepath=os.path.join(ROOT, "STLs", name + ".stl"))
    o = bpy.context.selected_objects[0]
    o.color = colour
    if matrix is not None:
        assert matrix.to_3x3().determinant() > 0.999, f"{name}: a printed part is moved, never mirrored"
        o.matrix_world = matrix
    return o


def box(x0, x1, y0, y1, z0, z1, colour):
    bpy.ops.mesh.primitive_cube_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    o = bpy.context.object
    o.scale = (x1 - x0, y1 - y0, z1 - z0)
    o.color = colour


def look(cam, at, up):
    f = (Vector(at) - cam.location).normalized()
    r = f.cross(Vector(up)).normalized()  # an explicit look-at: to_track_quat rolls the camera 180 deg here
    u = r.cross(f)
    m = Matrix((r, u, -f)).transposed().to_4x4()
    m.translation = cam.location
    cam.matrix_world = m


def render(sc, cam, views):
    os.makedirs(OUT, exist_ok=True)
    for bg_name, bg in BACKDROPS:
        sc.world.color = bg
        for name, v in views.items():
            sc.render.resolution_x, sc.render.resolution_y = v.get("res", (1000, 750))
            cam.data.type = "ORTHO" if "size" in v else "PERSP"
            if "size" in v:
                cam.data.ortho_scale = v["size"]
            else:
                cam.data.lens = v["lens"]
            cam.location = v["loc"]
            look(cam, v["at"], v.get("up", (0, 1, 0)))
            sc.render.filepath = os.path.join(OUT, f"{name}_{bg_name}.png")
            bpy.ops.render.render(write_still=True)


# ---------------------------------------------------------------- the bezel on the monitor (print frame, x = -X)
sc, cam = reset(shadows=False)
stl("Part_B_Lower", PLATINUM)
stl("Part_B_Upper", PLATINUM)
stl(EMBLEM, PLATINUM, Matrix([*EMBLEM_PLACE, [0, 0, 0, 1]]))
# the slit plug, pressed in from the back: a 180-deg turn about x puts its flange behind the 3 mm plate
stl(
    "Part_B_LED",
    (0.35, 0.72, 0.38, 1),
    Matrix.Translation((-LED_CX - 2.0, CHIN_CY + 4.7, 3.8)) @ Matrix.Rotation(3.14159265, 4, "X"),
)
box(-220, 0, 0, 310, 3.06, 8.7, (0.03, 0.03, 0.035, 1))  # monitor body; its glass sits behind the 3 mm ledge
box(-IMAGE[1], -IMAGE[0], IMAGE[2], IMAGE[3], 3.0, 3.05, (0.6, 0.62, 0.65, 1))  # the image area
box(-73, 0, 0, 310, 8.7, 16.6, (0.05, 0.05, 0.06, 1))  # the 13.6 mm hump
C = (-BEZEL_CX, (FY0 + FY1) / 2, 9.0)  # the bezel's centre, print frame
render(
    sc,
    cam,
    {
        "front": {"loc": (C[0], C[1], -600), "size": 380, "at": C, "res": (800, 1000)},
        "three_quarter": {"loc": (260, 60, -560), "lens": 55, "at": C, "res": (800, 1000)},
        "chin": {"loc": (60, -110, -150), "lens": 60, "at": (-20, -10, 5)},
        "emblem": {"loc": (-10, -70, -90), "lens": 60, "at": (-EMBLEM_CX, CHIN_CY, 0)},
        "back": {"loc": (-300, 120, 520), "lens": 55, "at": C, "res": (800, 1000)},
    },
)

# ---------------------------------------------------------------- the ball socket (Part A) on its own
sc, cam = reset()
stl("Part_A_Mount", PLATINUM)
render(sc, cam, {"socket": {"loc": (230, -90, 210), "lens": 70, "at": (28, 50, 12), "up": (0, 0, 1)}})

# ---------------------------------------------------------------- the emblem tile as printed (face up)
sc, cam = reset()
stl(EMBLEM, PLATINUM)
render(sc, cam, {"tile": {"loc": (40, 55, 75), "lens": 60, "at": (0, 0, 6), "up": (0, 0, 1)}})
print("rendered", sorted(os.listdir(OUT)))
