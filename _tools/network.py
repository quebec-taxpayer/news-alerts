#!/usr/bin/env python3
"""Build _data/network.json (people/organizations named in the published stories) for the Network page.

Usage: python3 _tools/network.py [--strict]
- Reads every SRC/YYYY-MM-DD.txt that has a post in _posts/ (SRC = env DIGEST_SRC, default /workspace/governance-digest),
  using the same parser as gen.py.
- Entities per story come from _tools/network_entities.json ("stories": match = unique fragment of the story URL).
- A story with no curated entry is auto-matched on its headline + FR/EN summaries against the known names/aliases
  and reported as UNCURATED so it can be reviewed and added to the JSON (with --strict the build fails instead).
- Each curated name is checked against the cached article text (SRC/articles/*.txt, first line = URL) or the
  headline/summaries; a name not found is reported as UNVERIFIED unless the story is marked checked_by_hand.
- Two entities share an edge when they are named in the same story; weight = number of shared stories.
  An edge means co-mention only: never label edges with anything else.
"""
import glob, json, os, re, sys, unicodedata
from datetime import datetime, timezone
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gen  # noqa: E402  (parse() and SRC)
SRC = gen.SRC
ART = os.environ.get("ARTICLES_DIR", os.path.join(SRC, "articles"))
SPEC = json.load(open(os.path.join(HERE, "network_entities.json"), encoding="utf-8"))
ENT = SPEC["entities"]

def norm(s):
    s = s.replace("’", "'").replace("\u00a0", " ")
    return " ".join(s.split())
def found(name, text):
    return re.search(r"(?<![\w-])" + re.escape(norm(name)) + r"(?![\w-])", text, re.I if len(name) > 4 else 0) is not None

def article_texts():
    d = {}
    for f in glob.glob(os.path.join(ART, "*.txt")):
        u, _, body = open(f, encoding="utf-8").read().partition("\n")
        if body.strip(): d[u.strip()] = norm(body)
    return d

def main():
    strict = "--strict" in sys.argv
    days = sorted(os.path.basename(p)[:10] for p in glob.glob(os.path.join(ROOT, "_posts", "*-digest.md")))
    days = [d for d in days if os.path.exists(f"{SRC}/{d}.txt")]
    arts = article_texts(); warnings = []; stories = []; used_matches = set()
    for day in days:
        issues = []; _, sections = gen.parse(day, issues)
        y, m, dd = day.split("-"); post = f"/{y}/{m}/{dd}/digest/"
        for sec in sections:
            for st in sec["stories"]:
                url = st["url"] or ""; own = norm(" ".join([st["headline"], st["fr"] or "", st["en"] or ""]))
                cur = [s for s in SPEC["stories"] if s["match"] in url]
                if len(cur) > 1: warnings.append(f"AMBIGUOUS match for {url}")
                if cur:
                    c = cur[0]; used_matches.add(c["match"]); ids = c["entities"]
                    text = own + " " + arts.get(url, "")
                    for i in ids:
                        if i not in ENT: warnings.append(f"UNKNOWN id {i} in {url}"); continue
                        if not any(found(n, text) for n in [ENT[i]["name"]] + ENT[i]["aliases"]) and not c.get("checked_by_hand"):
                            warnings.append(f"UNVERIFIED {ENT[i]['name']} in {url}")
                else:
                    ids = [i for i, v in ENT.items() if any(found(n, own) for n in [v["name"]] + v["aliases"] if len(n) > 3)]
                    warnings.append(f"UNCURATED {day} '{st['headline']}': auto-matched {ids} - review and add to network_entities.json")
                stories.append({"date": day, "headline": st["headline"], "url": url, "post": post, "entities": sorted(set(ids))})
    for s in SPEC["stories"]:
        if s["match"] not in used_matches: warnings.append(f"UNUSED curated entry {s['match']}")
    nodes = {}; edges = {}
    for idx, s in enumerate(stories):
        ref = {"date": s["date"], "headline": s["headline"], "url": s["url"]}
        for i in s["entities"]:
            n = nodes.setdefault(i, {"id": i, **ENT[i], "mentions": 0, "stories": []})
            n["mentions"] += 1; n["stories"].append(ref)
        es = s["entities"]
        for a in range(len(es)):
            for b in range(a + 1, len(es)):
                k = (es[a], es[b]); e = edges.setdefault(k, {"source": k[0], "target": k[1], "weight": 0, "stories": []})
                e["weight"] += 1; e["stories"].append(ref)
    by_date = {}
    for idx, s in enumerate(stories):
        by_date.setdefault(s["date"], {"post": s["post"], "stories": []})["stories"].append(
            {"headline": s["headline"], "url": s["url"], "entities": s["entities"]})
    out = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "note": "An edge means two names were mentioned in the same news story. It implies no relationship, wrongdoing or involvement.",
           "story_count": len(stories), "days": by_date,
           "nodes": sorted(nodes.values(), key=lambda n: (-n["mentions"], n["name"])),
           "edges": sorted(edges.values(), key=lambda e: (-e["weight"], e["source"], e["target"]))}
    os.makedirs(os.path.join(ROOT, "_data"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "_data", "network.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"days={len(by_date)} stories={len(stories)} nodes={len(nodes)} edges={len(edges)}")
    for n in out["nodes"][:10]: print(f"  {n['mentions']:>2}  {n['name']}")
    for w in warnings: print("WARN", w)
    if strict and any(w.startswith(("UNCURATED", "UNKNOWN", "UNVERIFIED", "AMBIGUOUS")) for w in warnings): sys.exit(1)

if __name__ == "__main__":
    main()
