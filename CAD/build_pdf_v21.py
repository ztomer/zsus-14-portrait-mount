"""
Build ZSUS_v21_Assembly_Instructions.pdf. Part sizes are read from STLs/, print times and weights from
CAD/renders/slice_report.json (written by build_3mf_v21.py), figures from CAD/renders/ (render_sections.py),
so the guide cannot drift from the files it describes. Needs pymupdf.
"""

import json
import os
import struct
import sys

import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RENDERS = os.path.join(HERE, "renders")
sys.path.insert(0, HERE)
from monitor_spec import FIT_Z, MON_H, MON_THIN  # noqa: E402

SLOT = MON_THIN + FIT_Z  # the Lower's thin-side slot; the gauge's other two pieces are 0.4 / 0.8 mm taller
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
    (1, "Part_B_SeamTest_Upper", "0.20 mm, 3 walls, 15% gyroid", "Seam test: the Upper's nut-pocket corner"),
    (1, "Part_B_SeamTest_Lower", "0.20 mm, 3 walls, 15% gyroid", "Seam test: the Lower's bolt-head corner"),
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
        "Lower bezel, chin, side channels, bolt-head slots",
    ),
    (
        4,
        "Part_B_Upper",
        "0.20 mm, 3 walls, 15% gyroid, no brim",
        "Upper bezel, USB-C bay, M3 nut pockets",
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
project file <b>ZSUS_v21_Complete_P1S_PLA.3mf</b> ({len(rep["plates"])} plates, sliced clean in Bambu Studio
{rep["bambu_studio"]})</p>

<h2>1. Printed parts</h2>
<table><tr><th>Plate</th><th>Part</th><th>Size</th><th>Settings</th><th>Role</th></tr>{rows}</table>
<table class="narrow"><tr><th>Plate</th><th>Contents</th><th>Time</th><th>PLA</th></tr>{plate_rows}
<tr><td></td><td><b>Total</b></td><td><b>{total_h:.1f} h</b></td><td><b>{total_g:.0f} g</b></td></tr></table>

<div class="box"><b>Supplies (no screws, no tools):</b> 3M VHB 5952 (1.1 mm, cut to 82 x 97 mm, R6.5 corners);
70%+ isopropyl alcohol and a lint-free cloth; Polbecky PO-CA-001 arm (17.0 mm ball, M22 x 2.0 winged collar).</div>

<h2>2. Print plate 1 first and test both fits</h2>
<p><b>Step 1, ball socket (Part_A_Test).</b> Back the collar off the arm's ball and thread it onto the coupon by hand:
it should run smoothly. Unscrew it, push the 17 mm ball straight into the socket mouth until it clicks past the
leaves (16.4 mm mouth, a light 0.3 mm snap: in PLA, do not lever it in at an angle), then screw the collar
down. The collar's top edge rides the cone on the leaf tips and closes the
leaves <i>above</i> the ball's equator, so tightening pulls the ball deeper into its seat. The socket stands in a 3 mm
relief, so the collar still has 2.5 to 3.4 mm of travel when it meets the cone: it must <i>not</i> bottom out on the
coupon before the ball locks. Hand-tight, the ball must lock and must not pop out. If it does, stop and report:
Part_A_Mount uses the identical socket.</p>
<p><b>Step 2, monitor channels (Part_B_FitGauge).</b> The gauge prints as four short pieces. Slide the wide piece
onto the thick (bezel) edge of the monitor, glass against the front ledge: it should slide with light friction.
The three narrow pieces are the thin edge's channel with stepped slots, counted by the notches on their backs:
<b>1 notch = {SLOT:.1f} mm</b> (what Part_B_Lower has now), <b>2 = {SLOT + 0.4:.1f} mm</b>,
<b>3 = {SLOT + 0.8:.1f} mm</b>. Try them in that order and note the first one that slides on with light friction
and no rocking. 1 notch: print the bezel
as is. 2 or 3: raise <code>MON_THIN</code> in <code>CAD/monitor_spec.py</code> by 0.4 or 0.8 mm and run
<code>CAD/build_all.sh</code> before printing plates 3 and 4.</p>
<p><b>Step 3, seam bolt (Part_B_SeamTest_Upper + Part_B_SeamTest_Lower, one M3 nut, one M3 socket-head bolt 10 to
16 mm long, a 2.5 mm L hex key).</b> The two small pieces are the bezel's thin-side corner round the parting line,
cut from both halves. Lay them back-up and push them together along the seam. Drop the nut into the hex pocket on the
Upper piece's back (it stands on edge), lay the bolt in the channel with its head in the Lower piece's slot, and turn
it with the key's short leg in the head until it pulls the pieces shut. Pulled apart, they must not move. If the nut
turns, the key cannot turn the bolt, or the bolt does not reach the nut, stop and report before printing plates 3
and 4.</p>
<img src="socket_v21.png" width="300"/>
<img src="channels_v21.png" width="470"/>

<h2>3. Part A: bond the socket to the monitor</h2>
<p>Portrait, seen from the back: clean the {MON_THIN} mm flat rear panel and the Part_A_Mount base with IPA. Apply the
VHB inside the 0.40 mm scribe ring. Butt the mount against the 3 mm step bevel (X = 76 mm), centre it vertically
(Y = {MON_H / 2:.1f} mm); the socket then sits on the centre of gravity (X = 104 mm). Press firmly for 30 to 60 s.
<b>Cure 24 hours unloaded before hanging.</b></p>

<h2>4. Part B: the bezel (two M3 bolts and nuts)</h2>
<p><b>Step 4, chin accents.</b> Lay Part_B_Lower face-down. Press Part_B_LED into the slit window lower-right from
the back until its 0.8 mm flange sits flat; it finishes flush with the chin face. Push Part_B_Emblem into the 18 mm
window lower-left from the front, face out, until both barbs click behind the plate. To change the emblem later,
reach into the control bay from behind and press the tile's back bridge forward: it pops out the front.</p>
<img src="emblem_v21.png" width="300"/>
<p><b>Step 5, monitor into the Lower.</b> Hold the monitor in portrait (bezel on the left, glass toward the bezel
face) and
slide it down (-Y) into the open top of Part_B_Lower: the thick hump runs in the left channel and the thin panel in
the right
channel, under the rear lips, until the bottom edge passes under the bottom-right lip and stops on the chin.</p>
<p><b>Step 6, close with the Upper.</b> First snap the small tree support out of Part_B_Upper's left lap-joint pocket
at the seam. Keep the orange 90-deg USB-C adapter in the top-left port. Slide Part_B_Upper down over the top of the
monitor (the adapter nose runs in its relief channel) until the left 45-deg lap joint detent and the top-right
detent tab click. Lay the bezel face-down on a soft cloth. On each side of the seam (the thin side inside the frame,
the thick side in the boss on the back): drop an M3 nut on edge into the hex pocket in the Upper, lay an M3
socket-head bolt (10 to 16 mm) in the channel with its head in the Lower's slot, and turn it with a 2.5 mm L key
(short leg in the head, long leg up; on the thick side the key swings out over the edge) until the seam is shut and
snug. The bolts pull the halves together.</p>
<p><b>Step 7, hang it.</b> After the 24 h cure: collar onto the arm, ball into the Part_A_Mount socket (it snaps in),
collar down hand-tight, as in Step 1.</p>
<img src="joint_v21.png" width="400"/>
<div class="tip"><b>Taking it apart:</b> face-down, unscrew both seam bolts and lift them and their nuts out of the
back, flex the top-right detent tab, and pull the Upper straight up (+Y).</div>

<h2>5. Printing notes</h2>
<ul>
<li><b>Colour.</b> Print the bezel in a matte warm light-grey PLA (Apple's Platinum, about #D3CFC6), not bright white:
Snow White products were never white.</li>
<li><b>Stringing.</b> The project keeps travel over the part (avoid crossing walls) rather than across the screen
opening and the pocket. Strings that remain are usually wet filament: dry the PLA (about 55 C for 8 h) before
printing the bezel, and pull any hairs out of the channels before sliding the monitor in.</li>
<li><b>Supports.</b> Only the Upper (the left lap corner) and the Cthulhu tile take supports; snap them off before
assembly.</li>
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
