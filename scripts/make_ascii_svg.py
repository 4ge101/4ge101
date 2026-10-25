import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source-prepped.png")
OUT_NAME = "ascii.svg"                      # <-- must match your README
OUT = os.path.join(HERE, "..", OUT_NAME)

COLS = 110
RAMP = " .:-=+*#%@"        # black = empty, bright = dense
GAMMA = 0.8                # lower = denser face
FS = 7                     # font size
CW, CH = FS * 0.6, FS * 1.0  # character cell width / height

img = Image.open(SRC).convert("L")
rows = round(COLS * img.height / img.width * CW / CH)
img = img.resize((COLS, rows), Image.LANCZOS)
px = img.load()

lines = []
for y in range(rows):
    s = ""
    for x in range(COLS):
        v = (px[x, y] / 255.0) ** GAMMA
        s += RAMP[min(int(v * len(RAMP)), len(RAMP) - 1)]
    lines.append(s.rstrip())

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