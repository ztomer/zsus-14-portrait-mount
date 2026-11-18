"""Shrink docs/images/*.png for the README: 128-colour palettes, no dithering (the renders are flat-shaded greys,
so this keeps them sharp at about a third of the size). Run after CAD/render_views.py."""

import glob
import os

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
total = 0
for path in sorted(glob.glob(os.path.join(ROOT, "docs", "images", "*.png"))):
    im = Image.open(path)
    if im.mode != "P":
        im.convert("RGB").quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(
            path, optimize=True
        )
    total += os.path.getsize(path)
print(f"docs/images: {total / 1e6:.1f} MB")
