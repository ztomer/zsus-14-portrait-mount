"""
Render the cross-section figures used by the assembly guide (CAD/renders/*.png) straight from STLs/,
so the guide always shows the geometry that ships. Needs trimesh, numpy, matplotlib.
"""

import os

import matplotlib
import numpy as np
import trimesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "CAD", "renders")
INK, BALL, MON, UP, LO = "#222222", "#c0392b", "#2e86c1", "#c0392b", "#2e86c1"


def stl(name):
    return trimesh.load(os.path.join(ROOT, "STLs", name + ".stl"))


def draw_section(ax, m, origin, normal, hx, hy, color=INK, label=None, xf=lambda a: a):
    s = m.section(plane_origin=origin, plane_normal=normal)
    if s is None:
        return
    for e in s.entities:
        p = s.vertices[e.points]
        ax.plot(xf(p[:, hx]), p[:, hy], "-", color=color, lw=1.1)
    if label:
        ax.plot([], [], "-", color=color, label=label)


def socket():
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import build_part_a_v21 as pa  # labels come from the generator, so they cannot go stale

    wrap = np.sqrt(pa.CUP_R**2 - pa.MOUTH_R**2)
    m = stl("Part_A_Mount")
    cx, cy, bz = 28.0, 50.0, 9.5
    fig, ax = plt.subplots(figsize=(6.2, 4.4), dpi=150)
    draw_section(
        ax,
        m,
        [cx, cy, 0],
        [0, 1, 0],
        0,
        2,
        label="Part_A_Mount (section through axis)",
        xf=lambda a: a - cx,
    )
    t = np.linspace(0, 2 * np.pi, 200)
    c = bz + 6.2
    ax.plot(
        8.5 * np.cos(t),
        c + 8.5 * np.sin(t),
        "--",
        color=BALL,
        lw=1,
        label="17.0 mm ball, seated",
    )
    ax.axhline(c, color=BALL, lw=0.5, ls=":")
    ax.annotate(
        f"leaves close to a {2 * pa.MOUTH_R:.1f} mm mouth\n{wrap:.1f} mm ABOVE the ball's equator",
        xy=(7.8, c + 3.6),
        xytext=(9.6, c + 7.4),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    ax.annotate(
        "M22 x 2.0 thread",
        xy=(-10.8, bz + 4),
        xytext=(-21, bz + 9),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    ax.annotate(
        "collar cone",
        xy=(-9.4, bz + 10.6),
        xytext=(-21, bz + 14),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    ax.annotate(
        "collar relief: 3 mm below the\nboss base, so the collar reaches\nthe cone with 2.5+ mm to spare",
        xy=(15, bz - 3.0),
        xytext=(10.5, bz + 0.8),
        fontsize=6.5,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    ax.set_xlim(-22, 22)
    ax.set_ylim(bz - 5, bz + 16)
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3)
    ax.set_xlabel("mm from socket axis")
    ax.set_ylabel("Z (mm)")
    ax.legend(loc="lower center", fontsize=7)
    ax.set_title(f"v21 ball socket ({pa.N_SLOTS} leaves, unclipped seat, collar relief)", fontsize=9)
    fig.savefig(os.path.join(OUT, "socket_v21.png"), bbox_inches="tight")
    plt.close(fig)


def channels():
    lo = stl("Part_B_Lower")
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.4), dpi=150, gridspec_kw={"width_ratios": [1, 1]})
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from monitor_spec import FIT_Z, HUMP_X1, LEDGE, MON_THICK, MON_THIN, MON_W, STEP_X1

    X = np.array([0, 0, HUMP_X1, STEP_X1, MON_W, MON_W, 0])
    Z = LEDGE + np.array([0, MON_THICK, MON_THICK, MON_THIN, MON_THIN, 0, 0])
    z_thick, z_thin = LEDGE + MON_THICK + FIT_Z, LEDGE + MON_THIN + FIT_Z
    for ax, (x0, x1), title in (
        (axs[0], (-6, 24), f"thick side (bezel left, {MON_THICK} mm hump)"),
        (axs[1], (196, 242), f"thin side ({MON_THIN} mm panel)"),
    ):
        draw_section(
            ax,
            lo,
            [0, 100, 0],
            [0, 1, 0],
            0,
            2,
            label="Part_B_Lower at Y = 100",
            xf=lambda a: -a,
        )
        ax.fill(X, Z, color=MON, alpha=0.25, label="monitor (measured)")
        ax.set_xlim(x0, x1)
        ax.set_ylim(-1, 20)
        ax.set_aspect("equal")
        ax.grid(True, lw=0.3)
        ax.set_title(title, fontsize=8)
        ax.set_xlabel("X, front view (mm)")
    axs[0].set_ylabel("Z from front face (mm)")
    axs[0].annotate(
        f"lip at Z {z_thick:.1f}: {FIT_Z} mm play\n(ZSUS spec 14.0 still slides)",
        xy=(1, z_thick),
        xytext=(6, 11),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    axs[1].annotate(
        f"lip at Z {z_thin:.1f}: {MON_THIN + FIT_Z:.1f} mm slot\nfor the {MON_THIN} mm panel",
        xy=(219, z_thin),
        xytext=(197, 13.5),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    axs[1].legend(loc="lower left", fontsize=6)
    fig.savefig(os.path.join(OUT, "channels_v21.png"), bbox_inches="tight")
    plt.close(fig)


def latch():
    up, lo = stl("Part_B_Upper"), stl("Part_B_Lower")
    fig, ax = plt.subplots(figsize=(3.6, 4.4), dpi=150)
    for m, col, lab in ((lo, LO, "Part_B_Lower"), (up, UP, "Part_B_Upper")):
        draw_section(ax, m, [0, 0, 9.0], [0, 0, 1], 0, 1, color=col, label=lab, xf=lambda a: -a)
    ax.set_xlim(218, 242)
    ax.set_ylim(165, 192)
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3)
    ax.annotate(
        "snap arm",
        xy=(229.1, 182),
        xytext=(233, 186),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    ax.annotate(
        "barb in\nnotch",
        xy=(230.6, 172.5),
        xytext=(234, 167),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    ax.annotate(
        "press -X\nto release",
        xy=(227.5, 172),
        xytext=(219, 167),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    ax.set_title("right latch, section at Z = 9 (assembled)", fontsize=8)
    ax.set_xlabel("X, front view (mm)")
    ax.set_ylabel("Y (mm)")
    ax.legend(loc="upper left", fontsize=6)
    fig.savefig(os.path.join(OUT, "latch_v21.png"), bbox_inches="tight")
    plt.close(fig)


def emblem():
    """Snap-in emblem seated in the chin window: section through the arms at the window centre."""
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from chin_spec import EMBLEM_CX, EMBLEM_CY, EMBLEM_PLACE, TILE_DEPTH

    lo, em = stl("Part_B_Lower"), stl("Part_B_Emblem")
    xf = np.vstack([np.array(EMBLEM_PLACE, float), [0, 0, 0, 1]])
    assert np.linalg.det(xf[:3, :3]) > 0.999, "a printed part is moved, never mirrored"
    em.apply_transform(xf)  # printed face-up -> seated (as CAD/check_part_b_fit.py places it)
    fig, ax = plt.subplots(figsize=(4.6, 3.4), dpi=150)
    for m, col, lab in ((lo, LO, "Part_B_Lower (chin plate)"), (em, UP, "Part_B_Emblem")):
        draw_section(ax, m, [0, EMBLEM_CY, 0], [0, 1, 0], 0, 2, color=col, label=lab, xf=lambda a: -a)
    ax.set_xlim(EMBLEM_CX - 13, EMBLEM_CX + 13)
    ax.set_ylim(13, -2)  # the face at the top
    ax.set_aspect("equal")
    ax.grid(True, lw=0.3)
    ax.annotate("face, flush", xy=(EMBLEM_CX, 0), xytext=(EMBLEM_CX - 4, -1.2), fontsize=7)
    ax.annotate("barb catches\nbehind the plate", xy=(EMBLEM_CX + 8.4, 3.3), xytext=(EMBLEM_CX + 9.5, 7.5),
                fontsize=7, arrowprops={"arrowstyle": "->", "lw": 0.7})  # fmt: skip
    ax.annotate("press the bridge\nforward to remove", xy=(EMBLEM_CX - 3, TILE_DEPTH), xytext=(EMBLEM_CX - 12.5, 12.4),
                fontsize=7, arrowprops={"arrowstyle": "->", "lw": 0.7})  # fmt: skip
    ax.set_title(f"chin emblem, section at Y = {EMBLEM_CY} (seated)", fontsize=8)
    ax.set_xlabel("X, front view (mm)")
    ax.set_ylabel("Z from the face (mm)")
    ax.legend(loc="lower right", fontsize=6)
    fig.savefig(os.path.join(OUT, "emblem_v21.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    socket()
    channels()
    latch()
    emblem()
    print("wrote", sorted(os.listdir(OUT)))
