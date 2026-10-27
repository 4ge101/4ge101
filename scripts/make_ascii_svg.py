import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source-cutout.png")
OUT_NAME = "sami-ascii.svg"
OUT = os.path.join(HERE, "..", OUT_NAME)

COLS = 110
RAMP = " .:-=+*#%@" 
GAMMA = 0.8 
FS = 7
CW, CH = FS * 0.6, FS * 1.0
MARGIN = 20

arr = np.array(Image.open(SRC).convert("RGBA"))
alpha = arr[:, :, 3]
gray = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2GRAY)
gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)

mask = (alpha > 128).astype(np.uint8)
mask = cv2.erode(mask, np.ones((5, 5), np.uint8))

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

rows = round(COLS * CW / CH)
small = cv2.resize(g, (COLS, rows), interpolation=cv2.INTER_AREA).astype(np.float32)
ms = cv2.resize(m.astype(np.float32), (COLS, rows), interpolation=cv2.INTER_AREA) > 0.5

if ms.sum() > 50:
    lo, hi = np.percentile(small[ms], [3, 99])
    small = np.clip((small - lo) / (hi - lo + 1e-6), 0, 1)
else:
    small = small / 255.0

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

USER = "4ge101"
NAME = "Ali Sami"

PAD = 14
TITLE_H = 28
FOOT_H = 30
W = round(COLS * CW + PAD * 2)
H = round(TITLE_H + PAD + rows * CH + PAD + FOOT_H)

body = []
for i, s in enumerate(lines):
    if not s:
        continue
    y = TITLE_H + PAD + (i + 1) * CH - 2
    body.append(
        f'<text class="r" x="{PAD}" y="{y:.1f}" textLength="{len(s) * CW:.1f}" '
        f'lengthAdjust="spacing" xml:space="preserve" '
        f'style="animation-delay:{i * 0.04:.2f}s">{s}</text>'
    )

prompt = f"{USER}@github:~$ whoami "
FF = 9
foot_y = H - 12
foot_delay = rows * 0.04 + 0.4
cursor_x = PAD + (len(prompt) + len(NAME)) * FF * 0.6 + 2

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
  .r {{ font-size: {FS}px; fill: #c9d1d9; opacity: 0; animation: in 0.3s ease forwards; }}
  .ttl {{ font-size: 9px; fill: #6e7681; }}
  .ft {{ font-size: {FF}px; fill: #8b949e; opacity: 0; animation: in 0.3s ease forwards; animation-delay: {foot_delay:.2f}s; }}
  .ft tspan {{ fill: #f0f6fc; }}
  .cur {{ fill: #f0f6fc; opacity: 0; animation: blink 1s steps(1) infinite; animation-delay: {foot_delay:.2f}s; }}
  @keyframes in {{ to {{ opacity: 1; }} }}
  @keyframes blink {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0; }} 100% {{ opacity: 1; }} }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<rect width="{W}" height="{TITLE_H}" rx="10" fill="#161b22"/>
<rect y="{TITLE_H - 10}" width="{W}" height="10" fill="#161b22"/>
<circle cx="16" cy="14" r="4.5" fill="#ff5f56"/>
<circle cx="32" cy="14" r="4.5" fill="#ffbd2e"/>
<circle cx="48" cy="14" r="4.5" fill="#27c93f"/>
<text x="{W / 2}" y="17" class="ttl" text-anchor="middle">{USER}@github: ~$ ./portrait.sh</text>
{chr(10).join(body)}
<line x1="0" y1="{H - FOOT_H}" x2="{W}" y2="{H - FOOT_H}" stroke="#21262d"/>
<text x="{PAD}" y="{foot_y}" class="ft" xml:space="preserve">{prompt}<tspan>{NAME}</tspan></text>
<rect class="cur" x="{cursor_x:.1f}" y="{foot_y - 9}" width="5" height="10"/>
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT), f"({COLS}x{rows})")