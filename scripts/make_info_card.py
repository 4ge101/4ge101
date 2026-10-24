import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")

# ---- EDIT THESE ----
TITLE = "yourname@github ~ $ neofetch"
ROWS = [
    ("Name", "Your Name"),
    ("Now", "What you do or study now"),
    ("Prev", "Past work or projects"),
    ("Stack", "Python, JavaScript, Git"),
    ("Goal", "What you want to build"),
]
# --------------------

W = 490
TOP = 70
STEP = 34
H = TOP + STEP * len(ROWS) + 30

lines = []
for i, (key, val) in enumerate(ROWS):
    y = TOP + i * STEP
    delay = 0.4 + i * 0.35
    lines.append(
        f'<g class="l" style="animation-delay:{delay}s">'
        f'<text x="24" y="{y}" class="k">{escape(key)}</text>'
        f'<text x="110" y="{y}" class="v">{escape(val)}</text>'
        f'</g>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
  text {{ font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 15px; }}
  .k {{ fill: #39d353; font-weight: bold; }}
  .v {{ fill: #c9d1d9; }}
  .t {{ fill: #8b949e; font-size: 13px; }}
  .l {{ opacity: 0; animation: in 0.5s ease forwards; }}
  @keyframes in {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<rect width="{W}" height="36" rx="10" fill="#161b22"/>
<circle cx="20" cy="18" r="6" fill="#ff5f56"/>
<circle cx="40" cy="18" r="6" fill="#ffbd2e"/>
<circle cx="60" cy="18" r="6" fill="#27c93f"/>
<text x="80" y="23" class="t">{escape(TITLE)}</text>
{chr(10).join(lines)}
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT))