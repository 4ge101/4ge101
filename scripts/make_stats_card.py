import json
import os
from datetime import date
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "data", "contributions.json")
OUT = os.path.join(HERE, "..", "stats.svg")

data = json.load(open(SRC))
USER = data.get("username", "you")
days = data["days"]
counts = [d["count"] for d in days]
dates = [d["date"] for d in days]


def fmt(iso):
    d = date.fromisoformat(iso)
    return f"{d:%b} {d.day}"


# ---------- numbers ----------
total = sum(counts)
active = sum(1 for c in counts if c > 0)
pct = round(100 * active / len(days))
avg = total / active if active else 0
best_i = max(range(len(counts)), key=lambda i: counts[i])

# current streak (if today has nothing yet, start from yesterday)
e = len(days) - 1
if counts[e] == 0 and e > 0:
    e -= 1
s = e
while s >= 0 and counts[s] > 0:
    s -= 1
cur_len = e - s
cur_range = f"{fmt(dates[s + 1])} – {fmt(dates[e])}" if cur_len else "no streak"

# longest streak
best_len, best_s, run, run_s = 0, 0, 0, 0
for i, c in enumerate(counts):
    if c > 0:
        if run == 0:
            run_s = i
        run += 1
        if run > best_len:
            best_len, best_s = run, run_s
    else:
        run = 0
long_range = (f"{fmt(dates[best_s])} – {fmt(dates[best_s + best_len - 1])}"
              if best_len else "no streak")

# monthly totals
months = {}
for d in days:
    months[d["date"][:7]] = months.get(d["date"][:7], 0) + d["count"]
month_keys = list(months)
month_vals = [months[k] for k in month_keys]
month_lbl = [date(int(k[:4]), int(k[5:]), 1).strftime("%b")[0] for k in month_keys]

# ---------- layout ----------
W, PAD, TITLE_H = 490, 14, 30
TW, TH, GAP = (W - 2 * PAD - 10) // 2, 88, 10
TOP = TITLE_H + 14

tiles = [
    ("$ current streak", str(cur_len), "days", cur_range, True),
    ("$ longest streak", str(best_len), "days", long_range, False),
    ("$ contributions", f"{total:,}", "", "in the last year", False),
    ("$ active days", str(active), f"/ {len(days)}", f"{pct}% of the year", False),
    ("$ best day", str(counts[best_i]), "", fmt(dates[best_i]), False),
    ("$ avg / active day", f"{avg:.1f}", "", "contributions", False),
]

out = []
for i, (label, value, unit, sub, green) in enumerate(tiles):
    x = PAD + (i % 2) * (TW + GAP)
    y = TOP + (i // 2) * (TH + GAP)
    delay = round(0.2 + i * 0.12, 2)
    ux = x + 14 + len(value) * 17 + 8
    out.append(f'<g class="f" style="animation-delay:{delay}s">')
    out.append(f'<rect x="{x}" y="{y}" width="{TW}" height="{TH}" rx="8" class="tile"/>')
    out.append(f'<text x="{x+14}" y="{y+24}" class="lab">{escape(label)}</text>')
    out.append(f'<text x="{x+14}" y="{y+58}" class="val{" g" if green else ""}">{escape(value)}</text>')
    if unit:
        out.append(f'<text x="{ux}" y="{y+58}" class="unit">{escape(unit)}</text>')
    out.append(f'<text x="{x+14}" y="{y+77}" class="sub">{escape(sub)}</text>')
    out.append('</g>')

# bar chart tile
CY = TOP + 3 * (TH + GAP)
CH = 160
CW = W - 2 * PAD
out.append(f'<g class="f" style="animation-delay:1s">')
out.append(f'<rect x="{PAD}" y="{CY}" width="{CW}" height="{CH}" rx="8" class="tile"/>')
out.append(f'<text x="{PAD+14}" y="{CY+24}" class="lab">$ contributions / month</text>')

base = CY + CH - 26
max_h = 84
vmax = max(month_vals) or 1
slot = (CW - 28) / len(month_vals)
bw = 20
for i, v in enumerate(month_vals):
    h = max(2, v / vmax * max_h)
    bx = PAD + 14 + i * slot + (slot - bw) / 2
    top = v == vmax
    out.append(
        f'<rect class="bar{" top" if top else ""}" x="{bx:.1f}" y="{base-h:.1f}" '
        f'width="{bw}" height="{h:.1f}" rx="2" style="animation-delay:{1.1+i*0.06:.2f}s"/>'
    )
    if top:
        out.append(f'<text x="{bx+bw/2:.1f}" y="{base-h-6:.1f}" class="peak" text-anchor="middle">{v:,}</text>')
    out.append(f'<text x="{bx+bw/2:.1f}" y="{base+16}" class="mon" text-anchor="middle">{month_lbl[i]}</text>')
out.append('</g>')

H = CY + CH + PAD

css = """
text { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
.tile { fill: #11161d; stroke: #21262d; }
.lab { fill: #8b949e; font-size: 12px; }
.val { fill: #f0f6fc; font-size: 28px; font-weight: bold; }
.val.g { fill: #39d353; }
.unit { fill: #8b949e; font-size: 14px; }
.sub { fill: #6e7681; font-size: 11px; }
.mon { fill: #8b949e; font-size: 11px; }
.peak { fill: #c9d1d9; font-size: 11px; }
.ttl { fill: #6e7681; font-size: 10px; }
.f { opacity: 0; animation: fade 0.5s ease forwards; }
.bar { fill: #26a641; transform-box: fill-box; transform-origin: 50% 100%;
       transform: scaleY(0); animation: grow 0.6s ease forwards; }
.bar.top { fill: #39d353; }
@keyframes fade { from { opacity: 0; } to { opacity: 1; } }
@keyframes grow { from { transform: scaleY(0); } to { transform: scaleY(1); } }
"""

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>{css}</style>
<rect width="{W}" height="{H}" rx="10" fill="#0d1117" stroke="#30363d"/>
<rect width="{W}" height="{TITLE_H}" rx="10" fill="#161b22"/>
<rect y="{TITLE_H-10}" width="{W}" height="10" fill="#161b22"/>
<circle cx="18" cy="15" r="5" fill="#ff5f56"/>
<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>
<circle cx="54" cy="15" r="5" fill="#27c93f"/>
<text x="{W/2}" y="19" class="ttl" text-anchor="middle">{escape(USER)}@github: ~$ ./stats.sh</text>
{chr(10).join(out)}
</svg>'''

with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", os.path.abspath(OUT))