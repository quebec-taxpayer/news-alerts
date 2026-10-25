#!/usr/bin/env python3
"""Plain-language data tools for the Quebec Governance Monitor.

Usage:
  python3 _tools/plain.py money     compute per-person fields in _data/money.json and validate it
  python3 _tools/plain.py check     validate every plain-language data file (money, why, and the batch-2 files when present)
  python3 _tools/plain.py --strict  same as check, exit 1 on any warning (use before every push)

Data files:
  _data/money.json   "The money, in human terms": sourced amounts ÷ the latest ISQ population.
  _data/why.json     "Why it matters": {story_url: {en, fr}}, one plain factual sentence per published story.
  _data/glossary.json  Glossary terms (definitions, official source, phrases auto-marked on pages).
  _data/upcoming.json  "What's next" dates (only dates stated in a cited source).
  _data/promises.json  "Promised vs delivered" pairs (both values sourced).
"""
import json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda f: os.path.join(ROOT, "_data", f)
QUAL = {"exact": ("", ""), "about": ("about ", "environ "), "at_least": ("at least ", "au moins "),
        "more_than": ("more than ", "plus de "), "target": ("", "")}

def load(f, default=None):
    p = D(f)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default
def save(f, d):
    with open(D(f), "w", encoding="utf-8") as fh: json.dump(d, fh, ensure_ascii=False, indent=1); fh.write("\n")

def _grp(n, sep): return f"{n:,}".replace(",", sep)
def amount_en(a):
    for v, w in ((1e9, "billion"), (1e6, "million")):
        if a >= v: x = a / v; return f"${x:.1f}".rstrip("0").rstrip(".") + f" {w}"
    return "$" + _grp(int(a), ",")
def amount_fr(a):
    for v, s, p in ((1e9, "milliard", "milliards"), (1e6, "million", "millions")):
        if a >= v:
            x = a / v; t = f"{x:.1f}".rstrip("0").rstrip(".").replace(".", ",")
            return f"{t} {s if x < 2 else p} $"
    return _grp(int(a), "\u00a0") + " $"
def money_str(v, lang):
    if v >= 100:
        n = _grp(int(v), "," if lang == "en" else "\u00a0")
        return f"${n}" if lang == "en" else f"{n} $"
    s = f"{v:.2f}"
    return f"${s}" if lang == "en" else s.replace(".", ",") + " $"

def per_person(item, pop):
    raw = item["amount"] / pop
    q = item.get("qualifier", "exact")
    # never overstate: "at least"/"more than" round DOWN so the wording stays true
    if q in ("at_least", "more_than"): v = math.floor(raw) if raw >= 100 else math.floor(raw * 100) / 100
    else:  # round half-up from the cent value shown in the calculation
        from decimal import Decimal, ROUND_HALF_UP
        c = Decimal(f"{raw:.2f}")
        v = int(c.quantize(Decimal(1), ROUND_HALF_UP)) if raw >= 100 else float(c)
    return raw, v

def compute(d):
    pop = d["population"]["value"]; warns = []
    d["population"]["value_en"], d["population"]["value_fr"] = _grp(pop, ","), _grp(pop, "\u00a0")
    for it in d["items"]:
        for k in ("id", "dossier", "amount", "qualifier", "label_en", "label_fr", "source_title", "source_outlet", "source_url"):
            if it.get(k) in (None, ""): warns.append(f"money {it.get('id')}: missing {k}")
        if it.get("qualifier") not in QUAL: warns.append(f"money {it.get('id')}: qualifier must be one of {list(QUAL)}")
        if not str(it.get("source_url", "")).startswith("http"): warns.append(f"money {it.get('id')}: bad source_url")
        raw, v = per_person(it, pop)
        qen, qfr = QUAL.get(it.get("qualifier"), ("", ""))
        yen, yfr = (" per year", " par année") if it.get("per_year") else ("", "")
        it["per_person_value"] = round(raw, 4)
        it["amount_en"], it["amount_fr"] = amount_en(it["amount"]), amount_fr(it["amount"])
        it["per_en"] = f"{qen}{money_str(v, 'en')} per person in Quebec{yen}".strip()
        it["per_fr"] = f"{qfr}{money_str(v, 'fr')} par personne au Québec{yfr}".strip()
        it["per_en"], it["per_fr"] = (x[:1].upper() + x[1:] for x in (it["per_en"], it["per_fr"]))
        r2 = f"{raw:,.2f}"  # the exact division, shown to the cent
        it["calc_en"] = f"{it['amount_en']} ÷ {_grp(pop, ',')} people = ${r2} each{yen}"
        it["calc_fr"] = f"{it['amount_fr']} ÷ {_grp(pop, chr(160))} personnes = {r2.replace(',', chr(160)).replace('.', ',')} $ chacun{yfr}"
    return warns

def check_money(save_it=True):
    d = load("money.json")
    if d is None: return ["_data/money.json missing"]
    w = compute(d)
    p = d["population"]
    for k in ("value", "as_of", "source_url", "source_updated"):
        if not p.get(k): w.append(f"population: missing {k}")
    ids = [i["id"] for i in d["items"]]
    if len(ids) != len(set(ids)): w.append("money: duplicate ids")
    dossiers = {x["id"] for x in load("dossiers.json")["dossiers"]}
    stories = published()
    for it in d["items"]:
        if it["dossier"] not in dossiers: w.append(f"money {it['id']}: unknown dossier {it['dossier']}")
        if it.get("story_url") and it["story_url"] not in stories: w.append(f"money {it['id']}: story_url is not a published story")
    if save_it: save("money.json", d)
    return w

def published():
    """{url: post date} for every story in _posts (parsed from the generated HTML)."""
    import re, glob
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, "_posts", "*-digest.md"))):
        day = os.path.basename(f)[:10]
        for u in re.findall(r'<article class="story"[^>]*>\s*<h3><a href="([^"]+)"', open(f, encoding="utf-8").read()):
            out[__import__("html").unescape(u)] = day
    return out

def check_why():
    why, w = load("why.json", {}), []
    pub = published()
    for u in pub:
        e = why.get(u)
        if not e or not e.get("en") or not e.get("fr"): w.append(f"why: no Why-it-matters line for {u}")
    for u in why:
        if u not in pub: w.append(f"why: entry for an unpublished story {u}")
    for u, e in why.items():
        for lg in ("en", "fr"):
            if len(e.get(lg, "")) > 260: w.append(f"why: {lg} line over 260 characters for {u}")
    return w

def valid_date(x):
    import re as _re
    return bool(_re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", str(x or "")))

def check_glossary():
    g, w = load("glossary.json"), []
    if g is None: return w
    ids = set()
    for t in g["terms"]:
        i = t.get("id")
        if i in ids: w.append(f"glossary: duplicate id {i}")
        ids.add(i)
        for k in ("term_en", "term_fr", "def_en", "def_fr", "match_en", "match_fr"):
            if not t.get(k): w.append(f"glossary {i}: missing {k}")
        for k in ("source_en", "source_fr"):
            if t.get(k) and not str(t[k]).startswith("http"): w.append(f"glossary {i}: bad {k}")
        if len(t.get("def_en", "")) > 300: w.append(f"glossary {i}: definition over 300 characters (keep it short)")
    seen = {}
    for t in g["terms"]:
        for lg in ("en", "fr"):
            for m in t.get("match_" + lg, []):
                if seen.get((lg, m.lower()), t["id"]) != t["id"]: w.append(f"glossary: phrase '{m}' used by {seen[(lg, m.lower())]} and {t['id']}")
                seen[(lg, m.lower())] = t["id"]
    return w

def check_upcoming():
    u, w = load("upcoming.json"), []
    if u is None: return w
    dossiers = {x["id"] for x in load("dossiers.json")["dossiers"]}
    for it in u["items"]:
        i = it.get("id")
        for k in ("id", "date", "kind", "en", "fr", "source_title", "source_outlet", "source_url", "pages"):
            if not it.get(k): w.append(f"upcoming {i}: missing {k}")
        if not valid_date(it.get("date")) or len(str(it.get("date"))) == 7: w.append(f"upcoming {i}: date must be YYYY-MM-DD or YYYY")
        if it.get("kind") not in ("on", "by", "year"): w.append(f"upcoming {i}: kind must be on|by|year")
        if it.get("kind") == "year" and len(str(it.get("date"))) != 4: w.append(f"upcoming {i}: kind=year needs a YYYY date")
        for pg in it.get("pages", []):
            if pg != "home" and pg not in dossiers: w.append(f"upcoming {i}: unknown page {pg}")
    return w

def check_promises():
    pr, w = load("promises.json"), []
    if pr is None: return w
    dossiers = {x["id"] for x in load("dossiers.json")["dossiers"]}
    for it in pr["items"]:
        i = it.get("id")
        for k in ("id", "dossier", "type", "item_en", "item_fr", "announced_en", "announced_fr", "announced_source_url",
                  "announced_source_outlet", "actual_en", "actual_fr", "actual_source_url", "actual_source_outlet", "actual_date"):
            if not it.get(k): w.append(f"promises {i}: missing {k} (both values must be sourced)")
        if it.get("type") not in ("cost", "deadline", "outcome"): w.append(f"promises {i}: type must be cost|deadline|outcome")
        if it.get("dossier") not in dossiers: w.append(f"promises {i}: unknown dossier")
        for k in ("announced_source_url", "actual_source_url"):
            if it.get(k) and not str(it[k]).startswith("http"): w.append(f"promises {i}: bad {k}")
    return w

def main():
    a = sys.argv[1:] or ["check"]
    strict = "--strict" in a
    if "money" in a:
        w = check_money()
        for it in load("money.json")["items"]: print(f"  {it['id']:<22} {it['calc_en']}")
    else:
        w = check_money() + check_why() + check_glossary() + check_upcoming() + check_promises()
    pub = published(); why = load("why.json", {}); m = load("money.json", {"items": []})
    g = load("glossary.json", {"terms": []}); u = load("upcoming.json", {"items": []}); pr = load("promises.json", {"items": []})
    print(f"stories={len(pub)} why={sum(1 for u_ in pub if u_ in why)} money_items={len(m['items'])} "
          f"glossary_terms={len(g['terms'])} upcoming={len(u['items'])} promise_pairs={len(pr['items'])}")
    for x in w: print("WARN", x)
    if strict and w: sys.exit(1)

if __name__ == "__main__": main()
