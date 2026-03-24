import os
import json
import datetime
import glob

HISTORY_PATH = "docs/digest/history"
OUTPUT_PATH = "docs/digest/weekly.md"

# Get last 7 days of snapshots
files = sorted(glob.glob(f"{HISTORY_PATH}/*.json"))[-7:]

all_tools = []
all_hacks = []
all_use_cases = []
all_big_moves = []
all_deprecated = []

for f in files:
    with open(f) as fp:
        d = json.load(fp)
        all_tools.extend(d.get("tools", []))
        all_hacks.extend(d.get("hacks", []))
        all_use_cases.extend(d.get("use_cases", []))
        all_big_moves.extend(d.get("big_moves", []))
        all_deprecated.extend(d.get("deprecated", []))

today = datetime.date.today().isoformat()

def format_tools(items):
    if not items: return "_Nothing notable this week._\n"
    out = ""
    for i in items[:6]:
        out += f"- **{i['name']}** — {i['summary']} *(relevance: {i.get('relevance','?')})*\n"
        if i.get('url'): out += f"  → {i['url']}\n"
    return out

def format_hacks(items):
    if not items: return "_Nothing notable this week._\n"
    out = ""
    for i in items[:5]:
        out += f"- **{i['title']}** — {i['description']} *(via {i.get('source','?')})*\n"
    return out

def format_use_cases(items):
    if not items: return "_Nothing notable this week._\n"
    out = ""
    for i in items[:6]:
        out += f"- **{i['title']}** — {i['description']} `[{i.get('applicable_to','?')}]`\n"
    return out

def format_big_moves(items):
    if not items: return "_Nothing notable this week._\n"
    out = ""
    for i in items[:5]:
        out += f"- **{i['who']}** — {i['what']} → _{i.get('why_it_matters','')}_\n"
    return out

def format_deprecated(items):
    if not items: return "_Nothing died this week._\n"
    out = ""
    for i in items[:3]:
        out += f"- ~~{i['what']}~~ — {i.get('note','')}\n"
    return out

md = f"""# 🤖 AI Weekly Digest — {today}
> Auto-generated. Paste sections marked [CLODI] at session start with Clodi or Codi.

---

## 🔧 New Tools `[CLODI]`
{format_tools(all_tools)}
---

## ⚡ Hacks & Prompting Tricks `[CLODI]`
{format_hacks(all_hacks)}
---

## 💡 Use Cases Relevant to Your Projects
{format_use_cases(all_use_cases)}
---

## 🚀 Big Moves
{format_big_moves(all_big_moves)}
---

## ❌ Deprecated / Dead
{format_deprecated(all_deprecated)}

---
_Generated from {len(files)} daily snapshots. Source: docs/digest/history/_
"""

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(md)

print(f"✅ Weekly digest written: {OUTPUT_PATH}")
