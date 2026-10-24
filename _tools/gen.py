#!/usr/bin/env python3
"""Generate Jekyll posts for the Quebec Governance Monitor site from the daily digest .txt files.

Usage: python3 _tools/gen.py [YYYY-MM-DD ...]   (no args = every day listed in TAGS)
Source format per day file (SRC/YYYY-MM-DD.txt):
  *Quebec Governance Daily – ...*        (title line)
  *Section heading FR / Section heading EN*
  *Headline as published*
  🇫🇷 French summary
  🇬🇧 English summary
  https://url
  💡🇫🇷 Pourquoi c’est important (optional; else taken from _data/why.json)
  💡🇬🇧 Why it matters (optional; else taken from _data/why.json)
  — Quebec Governance Monitor           (signature)
Per story the post also shows, when present: the "Why it matters" line (_data/why.json, keyed by story URL)
and any "money in human terms" item whose story_url is that story (_data/money.json, run _tools/plain.py money).
Each language is wrapped in class="l-fr" / class="l-en" so the site's EN|FR toggle shows one at a time.
Headlines are language-neutral (shown as published in both modes).
"""
import html, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plain
SRC = os.environ.get("DIGEST_SRC", "/workspace/governance-digest")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_posts")
FR_MONTHS = ["janvier","février","mars","avril","mai","juin","juillet","août","septembre","octobre","novembre","décembre"]
EN_MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"]

# Per-day topic tags (only when clearly applicable): it-digital, crown-corporations, procurement
TAGS = {"2026-10-21": ["crown-corporations"],
        "2026-10-22": ["it-digital", "crown-corporations"],
        "2026-10-23": ["it-digital", "crown-corporations", "procurement"],
        "2026-10-24": ["it-digital", "crown-corporations"]}
# Per-day one-line summary, (FR, EN), written only from that day's stories
SUMMARY = {
 "2026-10-21": ("Lion Électrique : perquisition de la GRC et dossiers de l’AMF; nouveau Conseil des ministres; tarifs d’Hydro-Québec pour les centres de données.",
                "Lion Électrique: RCMP search and AMF cases; new cabinet; Hydro-Québec data-centre rates."),
 "2026-10-22": ("Nominations dans la haute fonction publique; faille PHP : la SAQ, la STM et la SAAQ ferment leurs sites; suivis sur Lion Électrique et les recomptages.",
                "Senior civil-service appointments; PHP flaw: SAQ, STM and SAAQ lock their sites; follow-ups on Lion Électrique and the recounts."),
 "2026-10-23": ("Contrats TI de gré à gré et firmes étrangères; Hydro-Québec et SAQ; Marie-Claude Sarrazin (ex-commission Gallant) à la Justice.",
                "Untendered IT contracts and foreign firms; Hydro-Québec and the SAQ; Marie-Claude Sarrazin (ex-Gallant commission) at Justice."),
 "2026-10-24": ("Aide d’urgence en itinérance; la SAQ et Consignaction; Hydro-Québec et la faille PHP; FNZ et La Caisse; mandats des nouveaux ministres, dont l’audit des projets informatiques; projets d’infrastructures reportés.",
                "Emergency homelessness aid; the SAQ and Consignaction; Hydro-Québec and the PHP flaw; FNZ and La Caisse; new ministers’ mandates, including an audit of IT projects; infrastructure projects delayed."),
}
# Section headings that are not in "FR / EN" form: explicit (FR, EN) pairs, trivial translations only.
HEADINGS = {
 "Fraud & investigations": ("Fraude & enquêtes", "Fraud & investigations"),
 "Government & institutions": ("Gouvernement & institutions", "Government & institutions"),
 "Energy & industry": ("Énergie & industrie", "Energy & industry"),
 "Lobbying & ethics": ("Lobbyisme & éthique", "Lobbying & ethics"),
 "Mise à jour / Update (après-midi)": ("Mise à jour (après-midi)", "Update (afternoon)"),
 "Mise à jour / Update (fin de matinée / late morning)": ("Mise à jour (fin de matinée)", "Update (late morning)"),
}
e = html.escape
def strip_star(s): return s.strip()[1:-1].strip()
def is_star(s): s = s.strip(); return len(s) > 2 and s.startswith("*") and s.endswith("*")
def bi(tag, fr, en, cls=""):
    c = f" {cls}" if cls else ""
    return (f'<{tag} class="l-fr{c}" lang="fr">{e(fr)}</{tag}>'
            f'<{tag} class="l-en{c}" lang="en">{e(en)}</{tag}>')

def money_box(it, pop):
    """'The money, in human terms' callout (same markup as _includes/money.html)."""
    src = f'<a href="{e(it["source_url"])}">{e(it["source_outlet"])}</a>'
    psrc = f'<a href="{e(pop["source_url"])}">ISQ</a>'
    return ('<div class="callout money"><p class="callout-label">' + bi("span", "L’argent, en termes concrets", "The money, in human terms") + '</p>'
            + bi("p", it["per_fr"], it["per_en"], "money-big")
            + bi("p", it["label_fr"], it["label_en"], "money-label")
            + bi("p", it["calc_fr"], it["calc_en"], "money-calc")
            + (bi("p", it["note_fr"], it["note_en"], "money-note") if it.get("note_en") else "")
            + f'<p class="l-fr money-src" lang="fr">Montant : {src}. Population : {psrc}, {e(pop["label_fr"])} (mise à jour {e(pop["source_updated"])}). Une façon de se représenter l’ordre de grandeur, pas une facture que chaque personne paie.</p>'
            + f'<p class="l-en money-src" lang="en">Amount: {src}. Population: {psrc}, {e(pop["label_en"])} (updated {e(pop["source_updated"])}). A way to picture the size, not a bill each person pays.</p>'
            + '</div>')

def split_heading(name, day, notes):
    if name in HEADINGS:
        if " / " not in name: notes.append(f"{day}: heading '{name}' was English-only; FR '{HEADINGS[name][0]}' added (trivial translation)")
        else: notes.append(f"{day}: heading '{name}' mapped to FR '{HEADINGS[name][0]}' / EN '{HEADINGS[name][1]}'")
        return HEADINGS[name]
    if name.count(" / ") == 1:
        fr, en = name.split(" / "); return fr.strip(), en.strip()
    notes.append(f"{day}: heading '{name}' exists in one language only; shown as-is in both modes")
    return name, name

def parse(day, issues):
    lines = [l.rstrip("\n") for l in open(f"{SRC}/{day}.txt", encoding="utf-8") if l.strip()]
    title_line = strip_star(lines[0]); i = 1; sections = []; cur = None
    while i < len(lines):
        l = lines[i].strip()
        if l.startswith("—"): i += 1; continue
        if is_star(l):
            nxt = lines[i+1].strip() if i+1 < len(lines) else ""
            if nxt.startswith(("🇫🇷", "🇬🇧", "http")):
                st = {"headline": strip_star(l), "fr": None, "en": None, "url": None}; i += 1
                while i < len(lines) and not is_star(lines[i]) and not lines[i].strip().startswith("—"):
                    t = lines[i].strip()
                    if t.startswith("💡🇫🇷"): st["why_fr"] = t.replace("💡🇫🇷", "", 1).strip()
                    elif t.startswith("💡🇬🇧"): st["why_en"] = t.replace("💡🇬🇧", "", 1).strip()
                    elif t.startswith("🇫🇷"): st["fr"] = t.replace("🇫🇷", "", 1).strip()
                    elif t.startswith("🇬🇧"): st["en"] = t.replace("🇬🇧", "", 1).strip()
                    elif t.startswith("http"): st["url"] = t
                    else: issues.append(f"{day}: unexpected line: {t}")
                    i += 1
                for k in ("fr", "en", "url"):
                    if not st[k]: issues.append(f"{day}: '{st['headline']}' missing {k}")
                if cur is None: cur = {"name": "", "stories": []}; sections.append(cur)
                cur["stories"].append(st); continue
            cur = {"name": strip_star(l), "stories": []}; sections.append(cur); i += 1; continue
        issues.append(f"{day}: stray line: {l}"); i += 1
    return title_line, sections

def build(day, issues, notes):
    if day not in TAGS or day not in SUMMARY:
        issues.append(f"{day}: add TAGS and SUMMARY entries first"); return None
    title_line, sections = parse(day, issues)
    y, m, d = map(int, day.split("-"))
    title_fr = f"Digest du {d}{'er' if d == 1 else ''} {FR_MONTHS[m-1]} {y}"
    title_en = f"Daily digest – {EN_MONTHS[m-1]} {d}, {y}"
    n = sum(len(s["stories"]) for s in sections)
    why = plain.load("why.json", {})
    money = plain.load("money.json", {"items": [], "population": {}})
    plain.compute(money) if money["items"] else None
    body = []
    for s in sections:
        if not s["stories"]: issues.append(f"{day}: empty section {s['name']}")
        fr, en = split_heading(s["name"], day, notes)
        body.append('<section class="digest-section">')
        body.append(f'<h2>{bi("span", fr, en)}</h2>' if fr != en else f'<h2>{e(fr)}</h2>')
        for st in s["stories"]:
            body.append('<article class="story">')
            body.append(f'<h3><a href="{e(st["url"] or "")}">{e(st["headline"])}</a></h3>')
            body.append(bi("p", st["fr"] or "", st["en"] or "", "summary"))
            w = why.get(st["url"] or "", {})
            wfr, wen = st.get("why_fr") or w.get("fr"), st.get("why_en") or w.get("en")
            if wfr and wen:
                body.append('<div class="callout why"><p class="callout-label">' + bi("span", "Pourquoi c’est important", "Why it matters") + '</p>' + bi("p", wfr, wen) + '</div>')
            else: notes.append(f"{day}: no Why-it-matters line for {st['url']} (add it to _data/why.json)")
            for it in [x for x in money["items"] if x.get("story_url") == st["url"]]:
                body.append(money_box(it, money["population"]))
            body.append('</article>')
        body.append('</section>')
    if any("{{" in t or "{%" in t for t in body): issues.append(f"{day}: Liquid-like text in content")
    sfr, sen = SUMMARY[day]
    fm = ["---", "layout: post",
          f"title: {json.dumps(title_en, ensure_ascii=False)}",
          f"title_fr: {json.dumps(title_fr, ensure_ascii=False)}",
          f"date: {day}",
          f"summary: {json.dumps(sen, ensure_ascii=False)}",
          f"summary_fr: {json.dumps(sfr, ensure_ascii=False)}",
          f"story_count: {n}",
          "tags: [" + ", ".join(TAGS[day]) + "]",
          f"source_heading: {json.dumps(title_line, ensure_ascii=False)}", "---", ""]
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/{day}-digest.md", "w", encoding="utf-8").write("\n".join(fm) + "\n".join(body) + "\n")
    return {s["name"]: len(s["stories"]) for s in sections} | {"_total": n}

if __name__ == "__main__":
    days = sys.argv[1:] or sorted(TAGS)
    issues, notes, counts = [], [], {}
    for day in days:
        r = build(day, issues, notes)
        if r: counts[day] = r
    print({d: c["_total"] for d, c in counts.items()})
    print("NOTES:"); [print("  " + x) for x in notes]
    print("ISSUES:", issues or "none")
