import json
import os
import random
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "contrib-heatmap.svg")

HEROBRINE = True
TORCH = True
DECOR = True
S = 3.0

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
CELL, GAP = 12, 2
PITCH = CELL + GAP
PAD = 20
LEFT = 34
SKY = 96
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

CSS = """
.lb { fill: #8b949e; font: 10px ui-monospace, Menlo, Consolas, monospace; }
.ft { fill: #c9d1d9; font: 12px ui-monospace, Menlo, Consolas, monospace; }
.c { opacity: 0; animation: pop 0.4s ease forwards; }
@keyframes pop { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }
"""

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
    delay = round((week + row) * 0.03, 2)
    blocks.append(
        f'<g class="c" style="animation-delay:{delay}s">'
        f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" fill="{color}"/>'
        f'<use href="#bv" x="{x}" y="{y}"/></g>'
    )
    col_first.setdefault(week, dt)

weeks = max(col_first) + 1
W = GX + weeks * PITCH + PAD
H = GY + 7 * PITCH + 36

def R(x, y, w, h, c, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>'


def ANIM(attr, values, dur, extra=""):
    return (f'<animate attributeName="{attr}" values="{values}" dur="{dur}s" '
            f'repeatCount="indefinite" {extra}/>')


OP55, OP35, OP45 = 'opacity="0.55"', 'opacity="0.35"', 'opacity="0.45"'
SKIN, SKIN_D = "#c68863", "#b17a57"
SHIRT, SHIRT_D = "#2fa5b5", "#278b99"
HAIR = "#4a3321"

def stone(x0, y0):
    out = [R(x0, y0, 16, 16, "#7d7d7d")]
    for dx, dy, w, h, c in [
        (1, 1, 4, 3, "#6b6b6b"), (8, 0, 5, 2, "#8c8c8c"), (12, 4, 3, 4, "#6b6b6b"),
        (2, 6, 3, 3, "#8c8c8c"), (7, 7, 4, 3, "#686868"), (1, 11, 5, 3, "#6b6b6b"),
        (9, 12, 5, 3, "#8c8c8c"), (13, 1, 2, 2, "#686868"),
        (4, 9, 2, 2, "#4de3d0"), (10, 3, 2, 2, "#4de3d0"), (11, 9, 2, 2, "#c8fff7"),
    ]:
        out.append(R(x0 + dx, y0 + dy, w, h, c))
    for dx, dy, dur in ((4, 9, 2.6), (10, 3, 3.4), (11, 9, 2.9)):
        out.append(
            f'<rect x="{x0 + dx}" y="{y0 + dy}" width="2" height="2" fill="#ffffff" opacity="0">'
            f'{ANIM("opacity", "0;0.75;0", dur)}</rect>'
        )
    out.append(R(x0, y0, 16, 1, "#ffffff", 'opacity="0.18"'))
    out.append(R(x0, y0 + 15, 16, 1, "#000000", 'opacity="0.3"'))
    out.append(R(x0 + 15, y0, 1, 16, "#000000", 'opacity="0.2"'))
    return "".join(out)


def make_head(herobrine=False):
    if herobrine:
        glow = (f'<rect x="-3.8" y="-4.8" width="3.6" height="2.6" fill="#ffffff" opacity="0.25">'
                f'{ANIM("opacity", "0.15;0.45;0.15", 3.4)}</rect>'
                f'<rect x="0.2" y="-4.8" width="3.6" height="2.6" fill="#ffffff" opacity="0.25">'
                f'{ANIM("opacity", "0.15;0.45;0.15", 3.4)}</rect>')
        eyes = glow + R(-3, -4, 2, 1, "#ffffff") + R(1, -4, 2, 1, "#ffffff")
        blink = ""
    else:
        eyes = (R(-3, -4, 2, 1, "#ffffff") + R(-2, -4, 1, 1, "#4b3a8c")
                + R(1, -4, 2, 1, "#ffffff") + R(1, -4, 1, 1, "#4b3a8c"))
        blink = (f'<rect x="-3" y="-4" width="6" height="1" fill="{SKIN}" opacity="0">'
                 '<animate attributeName="opacity" values="0;0;1;0;0" keyTimes="0;0.9;0.93;0.96;1" '
                 'dur="4s" repeatCount="indefinite"/></rect>')
    return (f'<g transform="translate(0,-12) rotate({{HR}})">'
            f'{R(-4, -8, 8, 8, SKIN)}'
            f'{R(-4, -1, 8, 1, SKIN_D, OP55)}{R(3, -6, 1, 6, SKIN_D, OP35)}'
            f'{R(-4, -8, 8, 2, HAIR)}{R(-3, -8, 2, 1, "#33231a")}{R(1, -7, 3, 1, "#5a412b")}'
            f'{R(-4, -6, 1, 2, HAIR)}{R(3, -6, 1, 2, HAIR)}'
            f'{R(-3, -6, 6, 1, SKIN_D, OP45)}'
            f'{eyes}{blink}'
            f'{R(-1, -3, 2, 1, "#a8714f")}{R(-2, -2, 4, 1, "#7a4e36")}{R(-1, -1, 2, 1, "#7a4e36")}</g>')


def sitter(hero):
    lean = 10 if hero else 14
    tilt = -4 if hero else -8
    arm = 16 if hero else 8
    breath = 3.9 if hero else 3.2
    h = make_head(hero).replace("{HR}", str(tilt))
    return f'''
  {R(-17, 0, 27, 1.3, "#000000", 'opacity="0.28"')}
  <g transform="translate(0,-4) rotate({lean})">
    <g transform="translate(6,-12) rotate(-6)">
      {R(-2, 0, 4, 14, SKIN_D)}{R(-2, 0, 4, 4, SHIRT_D)}{R(-2, 12, 4, 2, "#9a6a49")}
    </g>
  </g>
  {R(-15, -7, 15, 4, "#2b3080")}{R(-15, -7, 2, 4, "#3a3a3a")}{R(-14, -7, 14, 1, "#ffffff", 'opacity="0.1"')}
  {R(-16, -4, 16, 4, "#3c44aa")}{R(-16, -4, 2.5, 4, "#4d4d4d")}{R(-16, -4, 1, 4, "#6a6a6a")}
  {R(-16, -4, 16, 1, "#ffffff", 'opacity="0.14"')}{R(-16, -1, 16, 1, "#000000", 'opacity="0.18"')}
  {R(-13, -4, 1, 4, "#2f3688", 'opacity="0.6"')}{R(-6, -4, 1, 4, "#2f3688", 'opacity="0.6"')}
  <g transform="translate(0,-4) rotate({lean})">
    <g>
      <animateTransform attributeName="transform" type="translate" values="0 0;0 -0.35;0 0" dur="{breath}s" repeatCount="indefinite"/>
      {R(-4, -12, 8, 12, SHIRT)}{R(-4, -3, 8, 3, SHIRT_D)}
      {R(2, -12, 2, 12, "#000000", 'opacity="0.14"')}{R(-4, -12, 8, 1, "#ffffff", 'opacity="0.12"')}
      {R(-2, -12, 4, 1, SKIN)}{R(-1, -11, 2, 1, SKIN)}
      {h}
      <g transform="translate(-6,-12) rotate({arm})">
        {R(-2, 0, 4, 12, SKIN)}{R(-2, 10, 4, 2, SKIN_D)}{R(-2, 0, 4, 4, SHIRT)}{R(-2, 3, 4, 1, SHIRT_D)}
      </g>
    </g>
  </g>'''


BLOCK_X = 12
MIRROR = 2 * (BLOCK_X + 8)
CX = BLOCK_X + 8

scene = ""
if TORCH:
    scene += (f'<circle cx="{CX}" cy="-24" r="26" fill="url(#glow)" opacity="0.3">'
              f'{ANIM("opacity", "0.24;0.34;0.22;0.32;0.24", 2.4)}</circle>')
scene += R(BLOCK_X - 1, 0, 18, 1.3, "#000000", 'opacity="0.3"')
scene += stone(BLOCK_X, -16)
if TORCH:
    scene += (R(CX - 1, -22, 2, 6, "#7a5230") + R(CX - 1, -22, 1, 6, "#8a6038")
              + f'<rect x="{CX - 1}" y="-25" width="2" height="3" fill="#ff9d2e">'
                f'{ANIM("opacity", "1;0.7;1;0.85;1", 0.7)}</rect>'
              + f'<rect x="{CX - 0.5}" y="-24.5" width="1" height="1.6" fill="#fff2a8">'
                f'{ANIM("opacity", "1;0.8;1", 0.5)}</rect>')
scene += sitter(False)
if HEROBRINE:
    scene += f'<g transform="translate({MIRROR},0) scale(-1,1)">{sitter(True)}</g>'
    extent = MIRROR + 17
else:
    extent = BLOCK_X + 16

x0 = W - PAD - extent * S - 8
scene_svg = f'<g transform="translate({x0:.1f},{GROUND}) scale({S})">{scene}</g>'

decor = ""
if DECOR:
    rnd = random.Random(11)
    mx, my = PAD + 56, PAD + 14
    decor += (f'<rect x="{mx}" y="{my}" width="22" height="22" fill="#e6ebf1"/>'
              f'<rect x="{mx + 4}" y="{my + 5}" width="5" height="5" fill="#cdd5de"/>'
              f'<rect x="{mx + 13}" y="{my + 11}" width="6" height="6" fill="#cdd5de"/>'
              f'<rect x="{mx + 5}" y="{my + 14}" width="4" height="4" fill="#d8dfe7"/>'
              f'<rect x="{mx}" y="{my + 20}" width="22" height="2" fill="#000000" opacity="0.12"/>')

    limit = x0 - 70
    for _ in range(26):
        sx_ = rnd.randint(PAD + 8, int(limit))
        sy_ = rnd.randint(PAD + 6, GROUND - 22)
        if abs(sx_ - (mx + 11)) < 26 and abs(sy_ - (my + 11)) < 26:
            continue
        size = rnd.choice([2, 2, 3])
        base = rnd.choice([0.35, 0.5, 0.7])
        dur = round(rnd.uniform(2.2, 5.0), 1)
        decor += (f'<rect x="{sx_}" y="{sy_}" width="{size}" height="{size}" fill="#c9d1d9" opacity="{base}">'
                  f'{ANIM("opacity", f"{base};{min(base + 0.3, 1)};{base}", dur)}</rect>')

    for _ in range(16):
        tx = rnd.randint(PAD + 6, int(x0 - 40))
        decor += (R(tx, GROUND - 3, 2, 3, "#4a8a30") + R(tx + 2, GROUND - 5, 2, 5, "#5aa33c")
                  + R(tx + 4, GROUND - 3, 2, 3, "#6dbb4a"))

    for fx, petal in ((x0 - 120, "#d9453b"), (x0 - 215, "#f2d04a"), (x0 - 330, "#d9453b")):
        if fx > PAD + 20:
            decor += (R(fx, GROUND - 8, 1.6, 8, "#3f8f2f") + R(fx - 2, GROUND - 12, 5.6, 5, petal)
                      + R(fx - 0.2, GROUND - 10.5, 2, 2, "#f2d04a" if petal != "#f2d04a" else "#8a5a1e"))

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
  <radialGradient id="glow">
    <stop offset="0" stop-color="#ffb454" stop-opacity="0.75"/>
    <stop offset="1" stop-color="#ffb454" stop-opacity="0"/>
  </radialGradient>
</defs>
<style>{CSS}</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117"/>
<rect x="{PAD}" y="{GROUND}" width="{W - 2 * PAD}" height="4" fill="url(#grass)"/>
<rect x="{PAD}" y="{GROUND + 4}" width="{W - 2 * PAD}" height="6" fill="url(#dirt)"/>
{decor}
{scene_svg}
{month_txt}
{dow_txt}
{"".join(blocks)}
<text x="{GX}" y="{H - 12}" class="ft">{footer}</text>
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT), "-", footer)