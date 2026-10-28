import os

import cv2
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source-cutout.png")
OUT_NAME = "sami-ascii.svg"                 # <-- must match your README
OUT = os.path.join(HERE, "..", OUT_NAME)

COLS = 110
RAMP = " .:-=+*#%@"        # empty -> dense
GAMMA = 0.8                # lower = denser face
FS = 7                     # font size
CW, CH = FS * 0.6, FS * 1.0
MARGIN = 20

# ---------- animation settings ----------
TOTAL_TIME = 2.5       # seconds the whole portrait takes to draw (smaller = faster)
ROW_GAP = 0.012        # seconds the cursor takes to glide to the next row
ROW_START = 0.3        # seconds before drawing starts
CURSOR = "#ffffff"     # pointer fill colour
CURSOR_EDGE = "#0d1117"  # pointer outline colour
CURSOR_SIZE = 0.4      # pointer size (1.0 = normal, 1.5 = bigger)

USER = "sami"                 # <-- your username (shows as sami@github)
NAME = "Sami"                 # <-- your name (shows after whoami)

STATIC = os.environ.get("STATIC") == "1"   # STATIC=1 -> finished picture, no animation (preview)

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
TITLE_H = 28
FOOT_H = 30
W = round(COLS * CW + PAD * 2)
H = round(TITLE_H + PAD + rows * CH + PAD + FOOT_H)
FF = 9                                   # footer font size
FW = FF * 0.6                            # footer character width

# how many characters will be drawn in total (blank space at the start of a row is skipped)
vis_total = sum(len(s.lstrip()) for s in lines if s.strip()) or 1
per_char = TOTAL_TIME / vis_total

clips, body, path = [], [], []
t = ROW_START
for i, s in enumerate(lines):
    if not s.strip():
        continue
    lead = len(s) - len(s.lstrip())              # blank characters before the art starts
    n = len(s) - lead                            # characters that get drawn
    xs_ = PAD + lead * CW                        # where drawing starts on this row
    width = n * CW
    y = TITLE_H + PAD + (i + 1) * CH - 2
    begin = t
    dur = max(0.015, n * per_char)
    t = begin + dur + ROW_GAP

    if STATIC:
        body.append(
            f'<text class="r" x="{PAD}" y="{y:.1f}" textLength="{len(s) * CW:.1f}" '
            f'lengthAdjust="spacing" xml:space="preserve">{s}</text>'
        )
        continue

    clips.append(
        f'<clipPath id="c{i}"><rect x="{xs_:.1f}" y="{y - CH:.1f}" width="0" height="{CH + 2:.1f}">'
        f'<animate attributeName="width" from="0" to="{width:.1f}" begin="{begin:.4f}s" '
        f'dur="{dur:.4f}s" fill="freeze"/></rect></clipPath>'
    )
    body.append(
        f'<text class="r" x="{PAD}" y="{y:.1f}" textLength="{len(s) * CW:.1f}" '
        f'lengthAdjust="spacing" xml:space="preserve" clip-path="url(#c{i})">{s}</text>'
    )
    # the cursor path: start of this row -> end of this row
    path.append((begin, xs_, y - CH * 0.5))
    path.append((begin + dur, xs_ + width, y - CH * 0.5))

last_end = path[-1][0] if path else ROW_START

cursor_svg = ""
if not STATIC and path:
    D = last_end - ROW_START
    key_times = ";".join(f"{(tt - ROW_START) / D:.6f}" for tt, _, _ in path)
    values = ";".join(f"{xx:.1f} {yy:.1f}" for _, xx, yy in path)
    arrow = "M0,0 L0,16 L4,12.4 L6.8,18.6 L9.4,17.5 L6.7,11.4 L11.6,11.4 Z"
    cursor_svg = (
        f'<g opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{ROW_START:.3f}s"/>'
        f'<set attributeName="opacity" to="0" begin="{last_end + 0.12:.3f}s"/>'
        f'<animateTransform attributeName="transform" type="translate" calcMode="linear" '
        f'values="{values}" keyTimes="{key_times}" begin="{ROW_START:.3f}s" dur="{D:.4f}s" fill="freeze"/>'
        f'<g transform="scale({CURSOR_SIZE})">'
        f'<path d="{arrow}" transform="translate(1,1.2)" fill="#000000" opacity="0.35"/>'
        f'<path d="{arrow}" fill="{CURSOR}" stroke="{CURSOR_EDGE}" stroke-width="1.1" stroke-linejoin="round"/>'
        f'</g></g>'
    )

# ---------- bottom prompt line: types "whoami Name" after the portrait ----------
prompt = f"{USER}@github:~$ whoami "
full = prompt + NAME
fwidth = len(full) * FW
foot_y = H - 12
foot_begin = last_end + 0.35
foot_dur = len(full) * 0.05
foot_end = foot_begin + foot_dur

if STATIC:
    foot_clip = ""
    foot_clip_attr = ""
    foot_cursor = f'<rect x="{PAD + fwidth + 1:.1f}" y="{foot_y - 9}" width="5" height="10" fill="#e6edf3"/>'
else:
    foot_clip = (
        f'<clipPath id="cf"><rect x="{PAD}" y="{foot_y - 12}" width="0" height="16">'
        f'<animate attributeName="width" from="0" to="{fwidth:.1f}" begin="{foot_begin:.2f}s" '
        f'dur="{foot_dur:.2f}s" fill="freeze"/></rect></clipPath>'
    )
    foot_clip_attr = ' clip-path="url(#cf)"'
    foot_cursor = (
        f'<rect x="{PAD}" y="{foot_y - 9}" width="5" height="10" fill="#e6edf3" opacity="0">'
        f'<set attributeName="opacity" to="1" begin="{foot_begin:.2f}s"/>'
        f'<animate attributeName="x" from="{PAD}" to="{PAD + fwidth + 1:.1f}" begin="{foot_begin:.2f}s" '
        f'dur="{foot_dur:.2f}s" fill="freeze"/>'
        f'<animate attributeName="opacity" values="1;0;1" keyTimes="0;0.5;1" calcMode="discrete" '
        f'dur="1s" begin="{foot_end:.2f}s" repeatCount="indefinite"/></rect>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  {"".join(clips)}{foot_clip}
</defs>
<style>
  text {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
  .r {{ font-size: {FS}px; fill: #c9d1d9; }}
  .ttl {{ font-size: 9px; fill: #6e7681; }}
  .ft {{ font-size: {FF}px; fill: #8b949e; }}
  .ft tspan {{ fill: #f0f6fc; }}
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
<text x="{PAD}" y="{foot_y}" class="ft" textLength="{fwidth:.1f}" lengthAdjust="spacing" xml:space="preserve"{foot_clip_attr}>{prompt}<tspan>{NAME}</tspan></text>
{cursor_svg}
{foot_cursor}
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT), f"({COLS}x{rows}) - draws in about {last_end:.1f}s")