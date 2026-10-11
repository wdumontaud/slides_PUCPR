#!/usr/bin/env python3
"""Straighten band 1 of the street-canyon frame: assets/04-introduction/band1.jpg

Slide 4 turns band 1 of the façade into a block of wall (a 3D block in CSS). Its front face is this picture: the band as a
flat rectangle, cut out of the frame of the video with a perspective correction. Run it again if the frame changes:

    python config/make_band.py        (needs Pillow:  pip install pillow)

The numbers are the ones of the video overlay in parts/04-introduction.html (band polygon, shadow edge), taken a few pixels
inside the polygon so that neither the red frame nor the pedestrian shows on the edges.
"""
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/04-introduction/canyon_street_poster.jpg"
OUT = ROOT / "assets/04-introduction/band1.jpg"

W, H = 240, 900                                                    # same proportions as the front face of the block (110 x 340)
QUAD = [(440, 150), (564, 168), (568, 690), (464, 722)]            # band 1 in the frame: top left, top right, bottom right, bottom left
SHADOW_EDGE = [(440, 324), (569, 372)]                             # the line drawn on the video at step 1 (sunlit above, shadow below)
EDGE_COLOR, EDGE_WIDTH = (254, 234, 109), 9                        # --yellowCNRS


def homography(pairs):
    """(a..h) of the projective map (x, y) -> ((a x + b y + c) / (g x + h y + 1), (d x + e y + f) / (g x + h y + 1)) from 4 point pairs"""
    rows = []
    for (x, y), (u, v) in pairs:
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y, u])
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y, v])
    for i in range(8):                                             # Gauss-Jordan elimination
        p = max(range(i, 8), key=lambda r: abs(rows[r][i]))
        rows[i], rows[p] = rows[p], rows[i]
        rows[i] = [c / rows[i][i] for c in rows[i]]
        for r in range(8):
            if r != i:
                f = rows[r][i]
                rows[r] = [a - f * b for a, b in zip(rows[r], rows[i])]
    return [rows[i][8] for i in range(8)]


def apply(h, p):
    a, b, c, d, e, f, g, hh = h
    w = g * p[0] + hh * p[1] + 1
    return (a * p[0] + b * p[1] + c) / w, (d * p[0] + e * p[1] + f) / w


def main():
    rect = [(0, 0), (W, 0), (W, H), (0, H)]
    back = homography(list(zip(rect, QUAD)))                       # strip -> frame: what Pillow wants
    forward = homography(list(zip(QUAD, rect)))                    # frame -> strip: to draw the shadow edge
    strip = Image.open(SRC).convert("RGB").transform((W, H), Image.PERSPECTIVE, back, Image.BICUBIC)
    ImageDraw.Draw(strip).line([apply(forward, p) for p in SHADOW_EDGE], fill=EDGE_COLOR, width=EDGE_WIDTH)
    strip.save(OUT, quality=92)
    print(f"written: {OUT.relative_to(ROOT)} ({W}x{H}, {OUT.stat().st_size // 1024} kB)")


if __name__ == "__main__":
    main()
