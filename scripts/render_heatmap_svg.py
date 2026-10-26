import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "contrib-heatmap.svg")

# ---------- settings ----------
S = 3.0               # Steve size (3 = about 70px tall)
SIDE = "right"        # "right" or "left" end of the grass strip

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP = 12, 2
PITCH = CELL + GAP
PAD = 20
LEFT = 34
SKY = 92              # room above the grass for Steve
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CSS = """
.lb { fill: #8b949e; font: 10px ui-monospace, Menlo, Consolas, monospace; }
.ft { fill: #c9d1d9; font: 12px ui-monospace, Menlo, Consolas, monospace; }
"""

# ---------- load data ----------
data = json.load(open(SRC))
days = data["days"]
first = date.fromisoformat(days[0]["date"])
first_sunday = first.toordinal() - ((first.weekday() + 1) % 7)

GROUND = PAD + SKY
GX = PAD + LEFT
GY = GROUND + 10 + 24

blocks, col_first = [], {}
total = 0
for d in days:
    dt = date.fromisoformat(d["date"])
    week = (dt.toordinal() - first_sunday) // 7
    row = (dt.weekday() + 1) % 7
    total += d["count"]
    color = PALETTE[min(d["level"], len(PALETTE) - 1)]
    x, y = GX + week * PITCH, GY + row * PITCH
    blocks.append(
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{color}"/>'
        f'<use href="#bv" x="{x}" y="{y}"/>'
    )
    col_first.setdefault(week, dt)

weeks = max(col_first) + 1
W = GX + weeks * PITCH + PAD
H = GY + 7 * PITCH + 36

# ---------- Steve, sitting (ground is y = 0, he faces left) ----------
SKIN, SKIN_D = "#c68863", "#b17a57"
SHIRT, SHIRT_D = "#2fa5b5", "#278b99"
HAIR = "#4a3321"

steve = f'''<g transform="scale({S})">
  <!-- far arm, behind the body, propping him up -->
  <g transform="translate(0,-4) rotate(14)">
    <g transform="translate(6,-12) rotate(-6)">
      <rect x="-2" y="0" width="4" height="14" fill="{SKIN_D}"/>
      <rect x="-2" y="0" width="4" height="4" fill="{SHIRT_D}"/>
    </g>
  </g>
  <!-- legs stretched out to the left -->
  <rect x="-15" y="-7" width="15" height="4" fill="#2b3080"/>
  <rect x="-15" y="-7" width="2" height="4" fill="#3a3a3a"/>
  <rect x="-16" y="-4" width="16" height="4" fill="#3c44aa"/>
  <rect x="-16" y="-4" width="2.5" height="4" fill="#4d4d4d"/>
  <rect x="-16" y="-4" width="16" height="1" fill="#ffffff" opacity="0.12"/>
  <!-- upper body leans back a little -->
  <g transform="translate(0,-4) rotate(14)">
    <rect x="-4" y="-12" width="8" height="12" fill="{SHIRT}"/>
    <rect x="-4" y="-3" width="8" height="3" fill="{SHIRT_D}"/>
    <rect x="-2" y="-12" width="4" height="1" fill="{SKIN}"/>
    <!-- head -->
    <g transform="translate(0,-12) rotate(-8)">
      <rect x="-4" y="-8" width="8" height="8" fill="{SKIN}"/>
      <rect x="-4" y="-8" width="8" height="2" fill="{HAIR}"/>
      <rect x="-4" y="-6" width="1" height="2" fill="{HAIR}"/>
      <rect x="3" y="-6" width="1" height="2" fill="{HAIR}"/>
      <rect x="-3" y="-4" width="2" height="1" fill="#ffffff"/>
      <rect x="-2" y="-4" width="1" height="1" fill="#4b3a8c"/>
      <rect x="1" y="-4" width="2" height="1" fill="#ffffff"/>
      <rect x="1" y="-4" width="1" height="1" fill="#4b3a8c"/>
      <rect x="-3" y="-4" width="6" height="1" fill="{SKIN}" opacity="0">
        <animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.9;0.93;0.96;1" dur="4s" repeatCount="indefinite"/>
      </rect>
      <rect x="-1" y="-3" width="2" height="1" fill="#a8714f"/>
      <rect x="-2" y="-2" width="4" height="1" fill="#7a4e36"/>
      <rect x="-1" y="-1" width="2" height="1" fill="#7a4e36"/>
    </g>
    <!-- near arm, resting on the leg -->
    <g transform="translate(-6,-12) rotate(8)">
      <rect x="-2" y="0" width="4" height="12" fill="{SKIN}"/>
      <rect x="-2" y="10" width="4" height="2" fill="{SKIN_D}"/>
      <rect x="-2" y="0" width="4" height="4" fill="{SHIRT}"/>
    </g>
  </g>
</g>'''

sx = W - PAD - 52 if SIDE == "right" else PAD + 60
steve_svg = f'<g transform="translate({sx},{GROUND})">{steve}</g>'

# ---------- labels ----------
changes, prev = [], None
for w in range(weeks):
    m = col_first[w].month
    if m != prev:
        changes.append((w, m))
        prev = m
if len(changes) > 1 and changes[1][0] - changes[0][0] < 3:
    changes.pop(0)

month_txt = "".join(
    f'<text x="{GX + w * PITCH}" y="{GY - 8}" class="lb">{MONTHS[m - 1]}</text>'
    for w, m in changes
)
dow_txt = "".join(
    f'<text x="{PAD}" y="{GY + r * PITCH + 10}" class="lb">{n}</text>'
    for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
)
footer = f"{total:,} contributions in the last year"

# ---------- write the svg ----------
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs>
  <g id="bv">
    <rect width="{CELL}" height="1.5" fill="#ffffff" opacity="0.2"/>
    <rect width="1.5" height="{CELL}" fill="#ffffff" opacity="0.1"/>
    <rect y="{CELL - 1.5}" width="{CELL}" height="1.5" fill="#000000" opacity="0.3"/>
  </g>
  <pattern id="grass" width="12" height="4" patternUnits="userSpaceOnUse">
    <rect width="12" height="4" fill="#5aa33c"/>
    <rect x="2" width="3" height="2" fill="#6dbb4a"/>
    <rect x="8" y="2" width="3" height="2" fill="#4a8a30"/>
  </pattern>
  <pattern id="dirt" width="12" height="6" patternUnits="userSpaceOnUse">
    <rect width="12" height="6" fill="#7a5230"/>
    <rect x="1" y="1" width="3" height="2" fill="#6a4526"/>
    <rect x="7" y="3" width="3" height="2" fill="#8a6038"/>
  </pattern>
</defs>
<style>{CSS}</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
<rect x="{PAD}" y="{GROUND}" width="{W - 2 * PAD}" height="4" fill="url(#grass)"/>
<rect x="{PAD}" y="{GROUND + 4}" width="{W - 2 * PAD}" height="6" fill="url(#dirt)"/>
{month_txt}
{dow_txt}
{"".join(blocks)}
{steve_svg}
<text x="{GX}" y="{H - 12}" class="ft">{footer}</text>
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT), "-", footer)