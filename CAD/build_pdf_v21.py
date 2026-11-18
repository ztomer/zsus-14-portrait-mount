"""
Build ZSUS_v21_Assembly_Instructions.pdf. Part sizes are read from STLs/, print times and weights from
CAD/renders/slice_report.json (written by build_3mf_v21.py), figures from CAD/renders/ (render_sections.py),
so the guide cannot drift from the files it describes. Needs pymupdf.
"""

import json
import os
import struct

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RENDERS = os.path.join(HERE, "renders")
OUT = os.path.join(ROOT, "ZSUS_v21_Assembly_Instructions.pdf")


def stl_size(name):
    with open(os.path.join(ROOT, "STLs", name + ".stl"), "rb") as fh:
        d = fh.read()
    n = struct.unpack("<I", d[80:84])[0]
    lo, hi = [1e9] * 3, [-1e9] * 3
    for i in range(n):
        v = struct.unpack("<9f", d[84 + 50 * i + 12 : 84 + 50 * i + 48])
        for k in range(3):
            for a in range(3):
                lo[a] = min(lo[a], v[3 * k + a])
                hi[a] = max(hi[a], v[3 * k + a])
    return " x ".join(f"{hi[a] - lo[a]:.1f}" for a in range(3)) + " mm"


with open(os.path.join(RENDERS, "slice_report.json")) as fh:
    rep = json.load(fh)
plates = {p["plate"]: p for p in rep["plates"]}
ROWS = [
    (
        1,
        "Part_A_Test",
        "0.16 mm, 5 walls, 40% gyroid, brim",
        "Collar thread + ball capture test",
    ),
    (
        1,
        "Part_B_FitGauge",
        "0.20 mm, 3 walls, 15% gyroid",
        "Thick-side channel + 3 stepped thin-side channels",
    ),
    (2, "Part_A_Mount", "0.16 mm, 5 walls, 40% gyroid", "VHB glue-on ball socket"),
    (2, "Part_B_Emblem", "0.16 mm, 3 walls, 100%", "Lower-left snap-in chin emblem (removable)"),
    (
        2,
        "Part_B_LED",
        "0.16 mm, 3 walls, 100%",
        "Lower-right slit power-light plug (press-fit)",
    ),
    (
        3,
        "Part_B_Lower",
        "0.20 mm, 3 walls, 15% gyroid, no brim",
        "Lower bezel, chin, side channels",
    ),
    (
        4,
        "Part_B_Upper",
        "0.20 mm, 3 walls, 15% gyroid, no brim",
        "Upper bezel, USB-C bay, snap arm",
    ),
]
rows = "".join(
    f"<tr><td>{p}</td><td><b>{n}</b></td><td>{stl_size(n)}</td><td>{s}</td><td>{r}</td></tr>" for p, n, s, r in ROWS
)
plate_rows = "".join(
    f"<tr><td>{p['plate']}</td><td>{p['name']}</td><td>{p['hours']:.1f} h</td><td>{p['grams']:.0f} g</td></tr>"
    for p in sorted(rep["plates"], key=lambda p: p["plate"])
)
total_h = sum(p["hours"] for p in rep["plates"])
total_g = sum(p["grams"] for p in rep["plates"])

HTML = f"""
<h1>ZSUS 14" Portrait Mount &amp; "Snow White" Bezel</h1>
<p class="sub">v21 screwless assembly guide | Bambu Lab P1S, 0.4 mm nozzle, Generic PLA, Textured PEI plate |
project file <b>ZSUS_v21_Complete_P1S_PLA.3mf</b> (4 plates, sliced clean in Bambu Studio {rep["bambu_studio"]})</p>

<h2>1. Printed parts</h2>
<table><tr><th>Plate</th><th>Part</th><th>Size</th><th>Settings</th><th>Role</th></tr>{rows}</table>
<table class="narrow"><tr><th>Plate</th><th>Contents</th><th>Time</th><th>PLA</th></tr>{plate_rows}
<tr><td></td><td><b>Total</b></td><td><b>{total_h:.1f} h</b></td><td><b>{total_g:.0f} g</b></td></tr></table>

<div class="box"><b>Supplies (no screws, no tools):</b> 3M VHB 5952 (1.1 mm, cut to 82 x 97 mm, R6.5 corners);
70%+ isopropyl alcohol and a lint-free cloth; Polbecky PO-CA-001 arm (17.0 mm ball, M22 x 2.0 winged collar).</div>

<h2>2. Print plate 1 first and test both fits</h2>
<p><b>Step 1, ball socket (Part_A_Test).</b> Back the collar off the arm's ball and thread it onto the coupon by hand:
it should run smoothly. Unscrew it, push the 17 mm ball into the socket mouth until it snaps past the leaves
(15.6 mm mouth), then screw the collar down. The collar's top edge rides the cone on the leaf tips and closes the
leaves <i>above</i> the ball's equator, so tightening pulls the ball deeper into its seat. The socket stands in a 3 mm
relief, so the collar still has 2.5 to 3.4 mm of travel when it meets the cone: it must <i>not</i> bottom out on the
coupon before the ball locks. Hand-tight, the ball must lock and must not pop out. If it does, stop and report:
Part_A_Mount uses the identical socket.</p>
<p><b>Step 2, monitor channels (Part_B_FitGauge).</b> The gauge prints as four short pieces. Slide the wide piece
onto the thick (bezel) edge of the monitor, glass against the front ledge: it should slide with light friction.
The three narrow pieces are the thin edge's channel with stepped slots, counted by the notches on their backs:
<b>1 notch = 6.2 mm</b> (what Part_B_Lower has now), <b>2 = 6.6 mm</b>, <b>3 = 7.0 mm</b>. Try them in that order and
note the first one that slides on with light friction and no rocking. 1 notch: print the bezel as is. 2 or 3:
set <code>MON_THIN</code> in <code>CAD/build_part_b_blender_v21.py</code> to 6.1 or 6.5 and run
<code>CAD/build_all.sh</code> before printing plates 3 and 4.</p>
<img src="socket_v21.png" width="300"/>
<img src="channels_v21.png" width="470"/>

<h2>3. Part A: bond the socket to the monitor</h2>
<p>Portrait, seen from the back: clean the 5.7 mm flat rear panel and the Part_A_Mount base with IPA. Apply the
VHB inside the 0.40 mm scribe ring. Butt the mount against the 3 mm step bevel (X = 76 mm), centre it vertically
(Y = 155 mm); the socket then sits on the centre of gravity (X = 104 mm). Press firmly for 30 to 60 s.
<b>Cure 24 hours unloaded before hanging.</b></p>

<h2>4. Part B: tool-free bezel</h2>
<p><b>Step 3, chin accents.</b> Lay Part_B_Lower face-down. Press Part_B_LED into the slit window lower-right from
the back until its 0.8 mm flange sits flat; it finishes flush with the chin face. Push Part_B_Emblem into the 18 mm
window lower-left from the front, face out, until both barbs click behind the plate. To change the emblem later,
reach into the control bay from behind and press the tile's back bridge forward: it pops out the front.</p>
<img src="emblem_v21.png" width="300"/>
<p><b>Step 4, monitor into the Lower.</b> Hold the monitor in portrait (bezel on the left, glass toward the bezel
face) and
slide it down (-Y) into the open top of Part_B_Lower: the thick hump runs in the left channel and the thin panel in
the right
channel, under the rear lips, until the bottom edge passes under the bottom-right lip and stops on the chin.</p>
<p><b>Step 5, close with the Upper.</b> Keep the orange 90-deg USB-C adapter in the top-left port. Slide Part_B_Upper
down
over the top of the monitor (the adapter nose runs in its relief channel) until three things click: the left 45-deg
lap
joint detent, the right snap arm (its barb drops into the catch notch), and the top-right detent tab over the monitor
edge.</p>
<p><b>Step 6, hang it.</b> After the 24 h cure: collar onto the arm, ball into the Part_A_Mount socket (it snaps in),
collar down hand-tight, as in Step 1.</p>
<img src="latch_v21.png" width="230"/>
<div class="tip"><b>Taking it apart:</b> through the rear opening at the right seam, press the snap arm's finger tab
~1 mm
toward the screen (-X) to lift the barb out of its notch, flex the top-right detent tab, and pull the Upper straight
up (+Y).</div>

<h2>5. What changed from v20</h2>
<ul>
<li><b>Ball socket.</b> v20's cup floor clipped the seat 2.8 mm high, so the ball rested with its equator level with
the rim and nothing held it; collar pressure squeezed it out. v21: full spherical seat, six leaves wrapping 3.6 mm
above the equator, and a collar cone on the leaf tips.</li>
<li><b>Collar relief.</b> The collar's top edge (about 19.6 mm across) meets the leaf cone 9.7 mm up, and the collar
is 9.8 mm tall, so on a flat pedestal it would bottom out before squeezing. The socket now stands in a 3 mm
relief.</li>
<li><b>Monitor fit.</b> Side channels 0.5 mm per side and 0.5 mm glass-to-lip (v20 0.3 mm); the thick channel also
takes
the ZSUS spec thickness of 14.0 mm; frame 18.6 mm (v20 18.0) to keep the thick-side lip 1.5 mm. The fit gauge
steps the thin-side slot (6.2 / 6.6 / 7.0 mm) because a photo suggests the thin edge may be thicker than 5.7 mm.</li>
<li><b>Snow White styling.</b> Equal 22.3 mm borders on the left, right and top (the top was 3.5 mm short); lines on
10 mm
centres, 1.5 mm deep on both sides (were 6 mm, 1.0 / 1.8 mm deep), set back from the front edge and added to the top
and
bottom; the parting line now sits in a groove across the front; a 4 mm front round (Apple IIc monitor) and a 3 mm
rear round. The chin takes the IIc's vertical slit light and a snap-in 18 mm emblem you can swap. Print the
bezel
in a matte warm light-grey PLA (Apple's Platinum), not bright white.</li>
<li><b>Bezel geometry repaired.</b> v20's Blender booleans failed silently: the thick-side lip and the lap tongue
were missing,
the thin-side lip and snap features were loose shells, and the snap arm collided with the solid Lower frame.
v21 builds every part as one manifold solid and adds a working snap channel and an LED counterbore.</li>
<li><b>Project file.</b> 0.4 mm nozzle profile (v20: 0.2 mm), all parts on four plates (v20 left Part_B_Lower
off the bed), per-object layer heights, aux fan 10%, supports off.</li>
</ul>
"""

CSS = """
* { font-family: sans-serif; }
body { font-size: 9pt; color: #222; }
h1 { font-size: 16pt; margin: 0 0 2pt 0; }
h2 { font-size: 11.5pt; margin: 9pt 0 3pt 0; border-bottom: 1px solid #999; }
p { margin: 3pt 0; }
.sub { color: #555; font-size: 8.5pt; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0; }
th { text-align: left; border-bottom: 1.5px solid #555; }
th, td { border: 1px solid #bbb; padding: 2pt 4pt; font-size: 8pt; }
.box { border: 1px solid #999; padding: 4pt; margin: 5pt 0; }
.tip { border: 1.5px solid #c08a00; padding: 4pt; margin: 5pt 0; }
code { font-family: monospace; font-size: 8pt; }
ul { margin: 2pt 0 2pt 14pt; }
li { margin: 1pt 0; }
"""

if __name__ == "__main__":
    story = pymupdf.Story(html=HTML, user_css=CSS, archive=pymupdf.Archive(RENDERS))
    page = pymupdf.paper_rect("letter")
    where = pymupdf.Rect(page.x0 + 40, page.y0 + 40, page.x1 - 40, page.y1 - 40)  # 40 pt margins
    writer = pymupdf.DocumentWriter(OUT)
    more, pages = 1, 0
    while more:
        dev = writer.begin_page(page)
        more, _ = story.place(where)
        story.draw(dev)
        writer.end_page()
        pages += 1
    writer.close()
    print(f"wrote {OUT} ({pages} pages)")
