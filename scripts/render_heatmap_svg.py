import json
import os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "contrib-heatmap.svg")

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP, PAD = 12, 4, 20
PITCH = CELL + GAP

data = json.load(open(SRC))
days = data["days"]
first = date.fromisoformat(days[0]["date"])
first_sunday = first.toordinal() - ((first.weekday() + 1) % 7)

cells = []
weeks = 0
total = 0
for d in days:
    dt = date.fromisoformat(d["date"])
    week = (dt.toordinal() - first_sunday) // 7
    row = (dt.weekday() + 1) % 7
    weeks = max(weeks, week + 1)
    total += d["count"]
    x = PAD + week * PITCH
    y = PAD + row * PITCH
    delay = round((week + row) * 0.03, 2)
    color = PALETTE[min(d["level"], len(PALETTE) - 1)]
    cells.append(
        f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
        f'rx="3" fill="{color}" style="animation-delay:{delay}s"/>'
    )

W = PAD * 2 + weeks * PITCH
H = PAD + 7 * PITCH + 40
footer = f"{total:,} contributions in the last year"

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  .c {{ opacity: 0; animation: pop 0.4s ease forwards; }}
  @keyframes pop {{ from {{ opacity: 0; transform: translateY(-6px); }} to {{ opacity: 1; transform: none; }} }}
  text {{ font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; fill: #8b949e; }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
{chr(10).join(cells)}
<text x="{PAD}" y="{H - 14}">{footer}</text>
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT), "-", footer)