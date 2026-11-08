#!/usr/bin/env python3
"""Deepavali site stats: read the anonymous counters and save a report.

Usage:  python3 report.py          -> prints the report, writes stats/<date>.md and stats/latest.json
The counters only hold numbers (no names, no personal data).
"""
import json, os, datetime, urllib.request, urllib.error

BASE = "https://abacus.jasoncameron.dev/get/jananip-deepavali-live/"
KEYS = [
    "visit", "visit_named", "music",
    "reach_hall", "reach_pooja", "reach_kitchen", "reach_terrace", "reach_finale",
    "wick", "lamp_complete", "diya", "kolam_complete",
    "sweet_laddu", "sweet_pak", "sweet_jalebi", "sweet_murukku", "sweet_athi",
    "flowerpot", "chakkaram", "rocket", "more_fireworks", "share",
]


def get(key):
    try:
        with urllib.request.urlopen(BASE + key, timeout=10) as r:
            return int(json.load(r).get("value", 0))
    except urllib.error.HTTPError as e:
        if e.code == 404:          # nobody has done this yet
            return 0
        raise


def main():
    c = {k: get(k) for k in KEYS}
    sweets = {k: c["sweet_" + k] for k in ("laddu", "pak", "jalebi", "murukku", "athi")}
    names = {"laddu": "Laddu", "pak": "Mysore pak", "jalebi": "Jalebi", "murukku": "Murukku", "athi": "Athirasam"}
    now = datetime.datetime.now()
    lines = [
        f"# Deepavali wishes: stats",
        f"_As of {now:%d %b %Y, %I:%M %p}_",
        "",
        "## Visitors",
        f"- Opened the site: **{c['visit']}**",
        f"- Opened a personalised link: **{c['visit_named']}**",
        f"- Turned the music on: **{c['music']}**",
        "",
        "## How far people got",
        f"- Hall: {c['reach_hall']}",
        f"- Pooja room: {c['reach_pooja']}",
        f"- Kitchen: {c['reach_kitchen']}",
        f"- Terrace: {c['reach_terrace']}",
        f"- Finale: {c['reach_finale']}",
        "",
        "## Lamps",
        f"- Kuthu vilakku wicks lit: **{c['wick']}** (fully lit {c['lamp_complete']} times)",
        f"- Diyas lit around the kolam: **{c['diya']}** (all 9 lit {c['kolam_complete']} times)",
        "",
        f"## Sweets eaten: **{sum(sweets.values())}**",
        *[f"- {names[k]}: {v}" for k, v in sorted(sweets.items(), key=lambda kv: -kv[1])],
        "",
        f"## Crackers burst: **{c['flowerpot'] + c['chakkaram'] + c['rocket']}**",
        f"- Flower pots: {c['flowerpot']}",
        f"- Chakkaram: {c['chakkaram']}",
        f"- Big rockets: {c['rocket']}",
        f"- 'More fireworks' taps: {c['more_fireworks']}",
        "",
        f"## Shared onward: **{c['share']}**",
    ]
    report = "\n".join(lines) + "\n"
    here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(here, "stats"), exist_ok=True)
    with open(os.path.join(here, "stats", f"{now:%Y-%m-%d}.md"), "w") as f:
        f.write(report)
    with open(os.path.join(here, "stats", "latest.json"), "w") as f:
        json.dump({"as_of": now.isoformat(timespec="minutes"), **c}, f, indent=2)
    print(report)


if __name__ == "__main__":
    main()
