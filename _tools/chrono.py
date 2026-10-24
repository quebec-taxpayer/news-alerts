#!/usr/bin/env python3
"""Chronology tool: validate, sort and extend _data/dossiers.json; keep one stub page per dossier.

Usage:
  python3 _tools/chrono.py [--strict]          validate, sort events by the date they happened, create missing
                                               chronology/<id>.html stubs, check story tags
  python3 _tools/chrono.py add --dossier ID --date YYYY[-MM[-DD]] --en "..." --fr "..." \
          --source-title "..." --source-url URL [--outlet "..."] [--type media|primary] [--post YYYY-MM-DD]
                                               append one event (then validates)
  python3 _tools/chrono.py tag                 copy dossier ids onto stories in _tools/network_entities.json
                                               from the events that cite them

Story tagging: each story in _tools/network_entities.json may carry "dossiers": [ids]. A tagged story must be
cited (source_url contains the story's "match" fragment) by at least one event of each tagged dossier.
"""
import argparse, datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "_data", "dossiers.json")
ENT = os.path.join(ROOT, "_tools", "network_entities.json")
NET = os.path.join(ROOT, "_data", "network.json")
PAGES = os.path.join(ROOT, "chronology")
DATE_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
REQ_D = ["id", "name_en", "name_fr", "desc_en", "desc_fr", "entities", "events"]
REQ_E = ["date", "en", "fr", "source_title", "source_url", "source_type"]
STUB = """---
layout: dossier
dossier: {id}
title: "{en}"
title_fr: "{fr}"
permalink: /chronology/{id}/
---
"""

def load(p): return json.load(open(p, encoding="utf-8"))
def save(p, d):
    with open(p, "w", encoding="utf-8") as f: json.dump(d, f, ensure_ascii=False, indent=1); f.write("\n")

def valid_date(s):
    if not DATE_RE.match(s): return False
    parts = [int(x) for x in s.split("-")]
    try: datetime.date(parts[0], parts[1] if len(parts) > 1 else 1, parts[2] if len(parts) > 2 else 1)
    except ValueError: return False
    return True

def posts():
    out = set()
    for f in os.listdir(os.path.join(ROOT, "_posts")):
        m = re.match(r"(\d{4}-\d{2}-\d{2})-", f)
        if m: out.add(m.group(1))
    return out

def check(strict):
    data, ents = load(DATA), load(ENT)
    eids, stories = set(ents["entities"]), ents["stories"]
    net = load(NET) if os.path.exists(NET) else {"days": {}}
    published = {s["url"] for d in net["days"].values() for s in d["stories"]}
    P, warns, seen = posts(), [], set()
    today = datetime.date.today().isoformat()
    for d in data["dossiers"]:
        for k in REQ_D:
            if k not in d: warns.append(f"{d.get('id')}: missing {k}")
        if d["id"] in seen: warns.append(f"duplicate dossier id {d['id']}")
        seen.add(d["id"])
        for e in d.get("entities", []):
            if e not in eids: warns.append(f"{d['id']}: UNKNOWN entity {e}")
        tl = d.get("tldr") or {}  # "In 30 seconds" box: what / why / now, each {en, fr}, from this dossier's sourced events only
        for k in ("what", "why", "now"):
            for lg in ("en", "fr"):
                if not (tl.get(k) or {}).get(lg): warns.append(f"{d['id']}: tldr.{k}.{lg} missing (In 30 seconds box)")
        for ev in d["events"]:
            tag = f"{d['id']} {ev.get('date')}"
            for k in REQ_E:
                if not ev.get(k): warns.append(f"{tag}: missing {k}")
            if not valid_date(ev.get("date", "")): warns.append(f"{tag}: bad date")
            elif ev["date"] > today: warns.append(f"{tag}: FUTURE date (chronology lists events that happened)")
            if ev.get("source_type") not in ("primary", "media"): warns.append(f"{tag}: source_type must be primary|media")
            if not str(ev.get("source_url", "")).startswith("http"): warns.append(f"{tag}: bad source_url")
            if ev.get("post"):
                if ev["post"] not in P: warns.append(f"{tag}: post {ev['post']} has no digest")
                if ev["source_url"] not in published: warns.append(f"{tag}: post set but source_url is not a published story")
        for ev in d["events"]:  # background = before the first digest, or not from a digest story
            if "background" not in ev: ev["background"] = (not ev.get("post")) or ev.get("date", "") < min(P, default="")
        d["events"].sort(key=lambda ev: ev["date"])  # stable: same-date events keep their order
        stub = os.path.join(PAGES, d["id"] + ".html")
        if not os.path.exists(stub):
            os.makedirs(PAGES, exist_ok=True)
            open(stub, "w", encoding="utf-8").write(STUB.format(id=d["id"], en=d["name_en"].replace('"', "'"), fr=d["name_fr"].replace('"', "'")))
            print(f"created {os.path.relpath(stub, ROOT)}")
    for f in os.listdir(PAGES) if os.path.isdir(PAGES) else []:
        if f.endswith(".html") and f != "index.html" and f[:-5] not in seen: warns.append(f"ORPHAN stub chronology/{f}")
    by = {d["id"]: d for d in data["dossiers"]}
    untagged = 0
    for s in stories:
        tags = s.get("dossiers")
        if tags is None: untagged += 1; continue
        for t in tags:
            if t not in by: warns.append(f"story {s['match']}: UNKNOWN dossier {t}")
            elif not any(s["match"] in ev["source_url"] for ev in by[t]["events"]):
                warns.append(f"story {s['match']}: tagged {t} but no event cites it")
    save(DATA, data)
    n = sum(len(d["events"]) for d in data["dossiers"])
    print(f"dossiers={len(data['dossiers'])} events={n} untagged_stories={untagged}")
    for d in data["dossiers"]:
        print(f"  {d['id']:<20} {len(d['events']):>3} events  {d['events'][0]['date'] if d['events'] else '-'} … {d['events'][-1]['date'] if d['events'] else '-'}")
    for w in warns: print("WARN", w)
    if untagged: print(f"NOTE {untagged} stories have no 'dossiers' field (use [] for stories that fit no dossier)")
    if strict and (warns or untagged): sys.exit(1)

def tag():
    data, ents = load(DATA), load(ENT)
    for s in ents["stories"]:
        s["dossiers"] = [d["id"] for d in data["dossiers"] if any(s["match"] in ev["source_url"] for ev in d["events"])]
    save(ENT, ents); print("tagged", sum(1 for s in ents["stories"] if s["dossiers"]), "of", len(ents["stories"]), "stories")

def add(a):
    data = load(DATA)
    d = next((x for x in data["dossiers"] if x["id"] == a.dossier), None)
    if not d: sys.exit(f"unknown dossier {a.dossier}")
    if not valid_date(a.date): sys.exit("bad date")
    d["events"].append({"date": a.date, "en": a.en, "fr": a.fr, "source_title": a.source_title,
                        "source_outlet": a.outlet or "", "source_url": a.source_url, "source_type": a.type, "post": a.post,
                        "background": (not a.post) or a.date < min(posts(), default="")})
    save(DATA, data); print("added to", a.dossier)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "add":
        p = argparse.ArgumentParser(prog="chrono.py add")
        for k in ["--dossier", "--date", "--en", "--fr", "--source-title", "--source-url"]: p.add_argument(k, required=True)
        p.add_argument("--outlet"); p.add_argument("--type", default="media", choices=["media", "primary"]); p.add_argument("--post")
        add(p.parse_args(sys.argv[2:])); check(False)
    elif len(sys.argv) > 1 and sys.argv[1] == "tag": tag(); check(False)
    else: check("--strict" in sys.argv)
