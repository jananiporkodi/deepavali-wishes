#!/usr/bin/env python3
"""Who opened their personalised Deepavali link?

Put one name per line in names.txt (exactly as typed after ?to= in the link you sent),
then run:  python3 names.py
The site only ever sends a scrambled code of each name; this script scrambles your
names the same way and checks which codes were counted. names.txt and the output
(stats/names-*.md) stay on this laptop: both are excluded from the public repo.
"""
import hashlib, json, os, re, datetime, urllib.request, urllib.error

BASE = "https://abacus.jasoncameron.dev/get/jananip-deepavali-live/"
HERE = os.path.dirname(os.path.abspath(__file__))


def code(name):
    # must match the site: strip < >, trim, first 24 chars, lower-case, collapse spaces
    n = name.replace("<", "").replace(">", "").strip()[:24]
    n = re.sub(r"\s+", " ", n.lower()).strip()
    return hashlib.sha256(n.encode("utf-8")).hexdigest()[:16]


def get(key):
    try:
        with urllib.request.urlopen(BASE + key, timeout=10) as r:
            return int(json.load(r).get("value", 0))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return 0
        raise


def main():
    path = os.path.join(HERE, "names.txt")
    names = [l.strip() for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")]
    seen, rows = set(), []
    for n in names:
        c = code(n)
        if c in seen:
            continue
        seen.add(c)
        rows.append({"name": n, "opened": get("n_" + c), "finished": get("f_" + c)})
    rows.sort(key=lambda r: (-r["opened"], -r["finished"], r["name"].lower()))
    now = datetime.datetime.now()
    opened = [r for r in rows if r["opened"]]
    out = [f"# Who opened their link", f"_As of {now:%d %b %Y, %I:%M %p}_", "",
           f"**{len(opened)} of {len(rows)}** people have opened their personalised link.", "",
           "| Name | Opened | Reached the finale |", "|---|---|---|"]
    for r in rows:
        out.append(f"| {r['name']} | {'✓ ' + str(r['opened']) + 'x' if r['opened'] else 'not yet'} | {'✓' if r['finished'] else ''} |")
    report = "\n".join(out) + "\n"
    os.makedirs(os.path.join(HERE, "stats"), exist_ok=True)
    with open(os.path.join(HERE, "stats", f"names-{now:%Y-%m-%d}.md"), "w", encoding="utf-8") as f:
        f.write(report)
    with open(os.path.join(HERE, "stats", "names-latest.json"), "w", encoding="utf-8") as f:
        json.dump({"as_of": now.isoformat(timespec="minutes"), "people": rows}, f, indent=1, ensure_ascii=False)
    print(report)


if __name__ == "__main__":
    main()
