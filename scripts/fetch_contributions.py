import json
import os
import re

import requests
from bs4 import BeautifulSoup

USERNAME = "4ge101"

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "data", "contributions.json")

url = f"https://github.com/users/{USERNAME}/contributions"
resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.text, "html.parser")

counts = {}
for tip in soup.find_all("tool-tip"):
    m = re.match(r"(\d+) contribution", tip.get_text(strip=True))
    counts[tip.get("for")] = int(m.group(1)) if m else 0

days = []
for cell in soup.find_all("td", attrs={"data-date": True}):
    days.append({
        "date": cell["data-date"],
        "level": int(cell.get("data-level", 0)),
        "count": counts.get(cell.get("id"), 0),
    })
days.sort(key=lambda d: d["date"])

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    json.dump({"username": USERNAME, "days": days}, f)
print("saved", len(days), "days")