import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source-cutout.png")
OUT_NAME = "sami-ascii.svg"                      # <-- must match your README
OUT = os.path.join(HERE, "..", OUT_NAME)

COLS = 110
RAMP = " .:-=+*#%@"        # empty -> dense
GAMMA = 0.8                # lower = denser face
FS = 7                     # font size
CW, CH = FS * 0.6, FS * 1.0
MARGIN = 20

# ---------- load cut-out: alpha is the mask ----------
arr = np.array(Image.open(SRC).convert("RGBA"))
alpha = arr[:, :, 3]
gray = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2GRAY)
gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

mask = (alpha > 128).astype(np.uint8)
mask = cv2.erode(mask, np.ones((5, 5), np.uint8))      # trim the edge halo

# ---------- square crop around the subject ----------
ys, xs = np.where(mask > 0)
side = max(xs.max() - xs.min(), ys.max() - ys.min()) + MARGIN * 2
cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
x0, y0 = cx - side // 2, cy - side // 2
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, gray.shape[1]), min(y0 + side, gray.shape[0])

g = np.zeros((side, side), np.uint8)
m = np.zeros((side, side), np.uint8)
g[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = gray[sy0:sy1, sx0:sx1]
m[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = mask[sy0:sy1, sx0:sx1]

# ---------- shrink to the character grid ----------
rows = round(COLS * CW / CH)
small = cv2.resize(g, (COLS, rows), interpolation=cv2.INTER_AREA).astype(np.float32)
ms = cv2.resize(m.astype(np.float32), (COLS, rows), interpolation=cv2.INTER_AREA) > 0.5

if ms.sum() > 50:
    lo, hi = np.percentile(small[ms], [3, 99])
    small = np.clip((small - lo) / (hi - lo + 1e-6), 0, 1)
else:
    small = small / 255.0

# ---------- characters ----------
n_r = len(RAMP)
lines = []
for y in range(rows):
    s = ""
    for x in range(COLS):
        if not ms[y, x]:
            s += " "
        else:
            v = small[y, x] ** GAMMA
            s += RAMP[min(int(v * n_r), n_r - 1)]
    lines.append(s.rstrip())

# ---------- svg ----------
PAD = 14
W = round(COLS * CW + PAD * 2)
H = round(rows * CH + PAD * 2)
body = []
for i, s in enumerate(lines):
    if not s:
        continue
    y = PAD + (i + 1) * CH - 2
    body.append(
        f'<text class="r" x="{PAD}" y="{y:.1f}" textLength="{len(s) * CW:.1f}" '
        f'lengthAdjust="spacing" xml:space="preserve" '
        f'style="animation-delay:{i * 0.04:.2f}s">{s}</text>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .r {{ font-family: ui-monospace, Menlo, Consolas, monospace; font-size: {FS}px;
        fill: #c9d1d9; opacity: 0; animation: in 0.3s ease forwards; }}
  @keyframes in {{ to {{ opacity: 1; }} }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
{chr(10).join(body)}
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT), f"({COLS}x{rows})")