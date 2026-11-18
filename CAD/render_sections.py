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
        "leaves close to a 15.6 mm mouth\n3.6 mm ABOVE the ball's equator",
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
    ax.set_title("v21 ball socket (6 leaves, unclipped seat, collar relief)", fontsize=9)
    fig.savefig(os.path.join(OUT, "socket_v21.png"), bbox_inches="tight")
    plt.close(fig)


def channels():
    lo = stl("Part_B_Lower")
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.4), dpi=150, gridspec_kw={"width_ratios": [1, 1]})
    X = np.array([0, 0, 73, 76, 220, 220, 0])
    Z = 3 + np.array([0, 13.6, 13.6, 5.7, 5.7, 0, 0])
    for ax, (x0, x1), title in (
        (axs[0], (-6, 24), "thick side (bezel left, 13.6 mm hump)"),
        (axs[1], (196, 242), "thin side (5.7 mm panel)"),
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
        "lip at Z 17.1: 0.5 mm play\n(ZSUS spec 14.0 still slides)",
        xy=(1, 17.1),
        xytext=(6, 11),
        fontsize=7,
        arrowprops={"arrowstyle": "->", "lw": 0.7},
    )
    axs[1].annotate(
        "lip at Z 9.2: 6.2 mm slot\nfor the 5.7 mm panel",
        xy=(219, 9.2),
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


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    socket()
    channels()
    latch()
    print("wrote", sorted(os.listdir(OUT)))
