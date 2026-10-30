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
  — Quebec Governance Monitor           (signature; skipped: the site footer signs each page in the reader's
                                         language, site.title_fr / site.title in _config.yml)
Why it matters rule (README step 3b; enforced by plain.py --strict): the line must add one thing the summary does not
say (the public stake, what to watch next, or the gap in the record) and never repeat a number from the summary.
Every fact is checked against the cached article.
Per story the post also shows, when present: the "Why it matters" line (_data/why.json, keyed by story URL)
and any "money in human terms" item whose story_url is that story (_data/money.json, run _tools/plain.py money).
Each language is wrapped in class="l-fr" / class="l-en" so the site's FR|EN toggle shows one at a time.
Headlines are language-neutral in the post body (shown as published in both modes).

The front matter also gets a structured `stories:` list that the homepage renders (featured stories, news by
category). Per story it combines the .txt with _data/story_meta.json (keyed by story URL: category, importance 1-5,
optional title_en / title_fr translations of the headline) and _data/why.json. The 3 stories with the highest
importance (ties keep digest order) get featured: 1..3. Missing metadata never fails: the category falls back to
HEADING_CATEGORY (section heading), then 'other'; importance defaults to 2.
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
        "2026-10-24": ["it-digital", "crown-corporations"],
        "2026-10-25": ["crown-corporations", "procurement"],
        "2026-10-26": [],
        "2026-10-27": ["crown-corporations", "procurement"],
        "2026-10-28": ["crown-corporations"],
        "2026-10-29": ["crown-corporations"],
        "2026-10-30": ["crown-corporations", "procurement"]}
# Per-day one-line summary, (FR, EN), written only from that day's stories
SUMMARY = {
 "2026-10-21": ("Lion Électrique : perquisition de la GRC et dossiers de l’AMF; nouveau Conseil des ministres; tarifs d’Hydro-Québec pour les centres de données.",
                "Lion Électrique: RCMP search and AMF cases; new cabinet; Hydro-Québec data-centre rates."),
 "2026-10-22": ("Nominations dans la haute fonction publique; faille PHP : la SAQ, la STM et la SAAQ ferment leurs sites; suivis sur Lion Électrique et les recomptages.",
                "Senior civil-service appointments; PHP flaw: SAQ, STM and SAAQ lock their sites; follow-ups on Lion Électrique and the recounts."),
 "2026-10-23": ("Contrats TI de gré à gré et firmes étrangères; Hydro-Québec et SAQ; Marie-Claude Sarrazin (ex-commission Gallant) à la Justice.",
                "Untendered IT contracts and foreign firms; Hydro-Québec and the SAQ; Marie-Claude Sarrazin (ex-Gallant commission) at Justice."),
 "2026-10-24": ("Aide d’urgence en itinérance; la SAQ et Consignaction; l’Espace client d’Hydro-Québec hors ligne; FNZ et La Caisse; mandats des nouveaux ministres, dont l’audit des projets informatiques; projets d’infrastructures reportés.",
                "Emergency homelessness aid; the SAQ and Consignaction; Hydro-Québec’s customer accounts offline; FNZ and La Caisse; new ministers’ mandates, including an audit of IT projects; infrastructure projects delayed."),
 "2026-10-25": ("Contrôleurs routiers de la SAAQ de retour sur les routes; vente de vins américains à la SAQ; voie d’essais du TGV d’Alto; chirurgies reportées faute d’instruments stériles; PSPP absent de la rencontre avec les chefs autochtones; L’Ascension attend toujours Québec; sommes versées par Hydro-Québec à McKinsey et à d’autres firmes-conseils.",
                "SAAQ road controllers back on patrol; SAQ sale of American wines; Alto’s high-speed rail test track; surgeries postponed for lack of sterile instruments; PSPP absent from the meeting with Indigenous leaders; L’Ascension still waiting for Quebec; Hydro-Québec’s payments to McKinsey and other consulting firms."),
 "2026-10-26": ("L’UPAC enquête sur Rigaud (lanceur d’alerte); la RBQ retire la licence de Swimko; violence envers le personnel scolaire; attente pour les mammographies en Abitibi-Témiscamingue; BEI et déontologie pour un policier du SPVM; Montréal demande un contrôle des loyers; rencontre Premières Nations–premiers ministres; vaccination contre la grippe.",
                "UPAC investigates Rigaud (whistleblower); RBQ revokes Swimko’s licence; violence against school support staff; mammogram waits in Abitibi-Témiscamingue; BEI and ethics probes of an SPVM officer; Montreal asks for rent control; First Nations–First Ministers meeting; flu vaccination."),
 "2026-10-27": ("Tarifs des centres de données : la Cour supérieure annule les décrets de Québec; contrat d’urgence de gré à gré au Stade olympique; La Caisse achète une part des tours de Bell; PSPP privé de parole au sommet Canada-UE; soulèvement à Bordeaux; enquête du coroner sur les poids lourds; suivis : Lion Électrique, Vachon, discours d’ouverture et itinérance.",
                "Data-centre rates: Superior Court strikes down Quebec’s orders; emergency untendered contract at the Olympic Stadium; La Caisse buys into Bell’s towers; PSPP denied a speech at the Canada–EU summit; uprising at Bordeaux jail; coroner’s heavy-truck inquiry; follow-ups: Lion Électrique, Vachon, opening speech and homelessness."),
 "2026-10-28": ("Retraites anticipées et indemnités de départ pour réduire la fonction publique (selon des sources); Carney réplique à PSPP sur le sommet Canada-UE; projet de loi sur le changement d’heure; étude Cardus sur les fonds publics aux groupes militants; fautes dans des lettres de l’aide sociale; une résidence pour aînés fermera à Val-d’Or; rapport du coroner après la mort d’une fillette; branchements d’Hydro-Québec et grève; plaintes au RTC; suivi : livre blanc sur l’itinérance.",
                "Early retirement and severance to shrink the public service (according to sources); Carney hits back at PSPP over the Canada–EU summit; clock-change bill; Cardus study on public money for advocacy groups; errors in welfare letters; a Val-d’Or seniors’ residence to close; coroner’s report after a girl’s death; Hydro-Québec connections and the strike; RTC complaints; follow-up: homelessness white paper."),
 "2026-10-29": ("Deux proches de Fréchette nommés dans la haute fonction publique; la mégadéduction fédérale coûtera environ 1 milliard par année à Québec; 20 % des chirurgies au privé; deux enquêtes sur des décès d’enfants à la DPJ anglophone; Québec veut faire annuler la vente de 94 logements sociaux à Repentigny; démantèlement du poste 39 du SPVM; BAPE réclamé pour le terminal de QSL; Montréal en « mode rattrapage »; suivis : sommet Canada-UE, L’Ascension.",
                "Two Fréchette aides named to senior public-service posts; the federal mega-deduction will cost Quebec about $1 billion a year; 20% of surgeries in private clinics; two probes into child deaths at the English-language DPJ; Quebec seeks to cancel the sale of 94 social housing units in Repentigny; dismantling of SPVM station 39; BAPE sought for the QSL terminal; Montreal in “catch-up mode”; follow-ups: Canada–EU summit, L’Ascension."),
 "2026-10-30": ("L’AMP blâme la Société des traversiers pour quatre contrats de gré à gré; le TAT donne raison au syndicat en grève d’Hydro-Québec; tramway de Québec : travaux préparatoires dans les budgets, selon la Ville; Jacinthe-Eve Arel à l’Efficacité gouvernementale; la lieutenante-gouverneure défend son rôle; infrastructures d’eau et logement; un policier du poste 39 aurait effacé une preuve; Keel annule sa séance portes ouvertes à Sherbrooke; suivi : Dubé et Santé Québec.",
                "The AMP faults the ferry corporation (STQ) over four untendered contracts; the TAT sides with Hydro-Québec’s striking trades union; Quebec City tramway prep work on budget, the City says; Jacinthe-Eve Arel joins Government Efficiency; the lieutenant governor defends her role; water infrastructure and housing; a Station 39 officer allegedly erased evidence; Keel cancels its Sherbrooke open house; follow-up: Dubé and Santé Québec.")
}
# Section headings that are not in "FR / EN" form: explicit (FR, EN) pairs, trivial translations only.
HEADINGS = {
 "Fraud & investigations": ("Fraude & enquêtes", "Fraud & investigations"),
 "Government & institutions": ("Gouvernement & institutions", "Government & institutions"),
 "Energy & industry": ("Énergie & industrie", "Energy & industry"),
 "Lobbying & ethics": ("Lobbyisme & éthique", "Lobbying & ethics"),
 "Mise à jour / Update (après-midi)": ("Mise à jour (après-midi)", "Update (afternoon)"),
 "Mise à jour / Update (fin de matinée / late morning)": ("Mise à jour (fin de matinée)", "Update (late morning)"),
 "Mise à jour / Update (fin d’après-midi / late afternoon)": ("Mise à jour (fin d’après-midi)", "Update (late afternoon)"),
}
# Section heading (EN part) -> homepage category id, used when a story has no category in _data/story_meta.json.
HEADING_CATEGORY = {
 "Government & institutions": "government", "Fraud & investigations": "justice", "Energy & industry": "energy",
 "Energy & digital": "energy", "Lobbying & ethics": "justice", "Crown corporations & IT": "crown-it",
 "Contracting & Crown corporations": "crown-it", "Health": "health",
}
# Domain -> outlet name shown next to each story on the homepage (fallback: the domain).
OUTLETS = {
 "ici.radio-canada.ca": "Radio-Canada", "www.lapresse.ca": "La Presse", "www.tvanouvelles.ca": "TVA Nouvelles",
 "www.journaldemontreal.com": "Le Journal de Montréal", "www.journaldequebec.com": "Le Journal de Québec",
 "www.cbc.ca": "CBC News", "montrealgazette.com": "Montreal Gazette", "www.newswire.ca": "Newswire (communiqué)",
 "www.noovo.info": "Noovo Info", "lautorite.qc.ca": "Autorité des marchés financiers", "www.latribune.ca": "La Tribune",
 "www.ledevoir.com": "Le Devoir", "www.vgq.qc.ca": "Vérificateur général du Québec", "www.quebec.ca": "Gouvernement du Québec",
 "www.assnat.qc.ca": "Assemblée nationale", "lobbyisme.quebec": "Commissaire au lobbyisme",
 "www.hydroquebec.com": "Hydro-Québec (document)",
 "montreal.citynews.ca": "CityNews Montréal", "www.cardus.ca": "Institut Cardus (communiqué)",
}
def outlet(url):
    from urllib.parse import urlparse
    h = urlparse(url or "").netloc.lower()
    return OUTLETS.get(h) or h.removeprefix("www.")

STOP = set("""les des une est sont pour par dans avec sur que qui aux ses son leur leurs cette ces pas plus the and for are with that this from has have was were its their they will been into than about after also more who what
selon environ dont mais encore elle elles ils lui être fait avoir""".split())
def _words(t):
    import re
    return {w for w in re.findall(r"[\w’']+", (t or "").lower()) if len(w) > 3 and w not in STOP}
def _overlap(summary, why):
    w, s = {x[:5] for x in _words(why)}, {x[:5] for x in _words(summary)}
    return len(w & s) / len(w) if w else 1.0
def why_adds(st, wfr, wen):
    """Homepage only: show Why it matters when it adds to the summary (on average, under half of its words repeat it).
    The full digest post always shows it."""
    return (_overlap(st["fr"], wfr) + _overlap(st["en"], wen)) / 2 < 0.5

e = html.escape
def strip_star(s): return s.strip()[1:-1].strip()
def is_star(s): s = s.strip(); return len(s) > 2 and s.startswith("*") and s.endswith("*")
def bi(tag, fr, en, cls=""):
    c = f" {cls}" if cls else ""
    return (f'<{tag} class="l-fr{c}" lang="fr">{e(fr)}</{tag}>'
            f'<{tag} class="l-en{c}" lang="en">{e(en)}</{tag}>')

def story_id(url):
    """Stable anchor for a story (used to link straight to a story in its daily digest)."""
    import hashlib
    return "s-" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:8]

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
    meta = plain.load("story_meta.json", {"stories": {}}).get("stories", {})
    cats = {c["id"] for c in plain.load("categories.json", {"items": []})["items"]}
    body, items = [], []
    for s in sections:
        if not s["stories"]: issues.append(f"{day}: empty section {s['name']}")
        fr, en = split_heading(s["name"], day, notes)
        body.append('<section class="digest-section">')
        body.append(f'<h2>{bi("span", fr, en)}</h2>' if fr != en else f'<h2>{e(fr)}</h2>')
        for st in s["stories"]:
            body.append(f'<article class="story" id="{story_id(st["url"] or st["headline"])}">')
            body.append(f'<h3><a href="{e(st["url"] or "")}">{e(st["headline"])}</a></h3>')
            body.append(bi("p", st["fr"] or "", st["en"] or "", "summary"))
            w = why.get(st["url"] or "", {})
            wfr, wen = st.get("why_fr") or w.get("fr"), st.get("why_en") or w.get("en")
            if wfr and wen:
                body.append('<div class="callout why"><p class="callout-label">' + bi("span", "Pourquoi c’est important", "Why it matters") + '</p>' + bi("p", wfr, wen) + '</div>')
            else: notes.append(f"{day}: no Why-it-matters line for {st['url']} (add it to _data/why.json)")
            m = meta.get(st["url"] or "", {})
            cat = m.get("category") or HEADING_CATEGORY.get(en.split(" (")[0]) or "other"
            if not m.get("category"): notes.append(f"{day}: no category in _data/story_meta.json for {st['url']} (using '{cat}')")
            if cat not in cats: issues.append(f"{day}: unknown category '{cat}' for {st['url']}"); cat = "other"
            it_ = {"id": story_id(st["url"] or st["headline"]), "url": st["url"] or "", "headline": st["headline"],
                   "title_en": m.get("title_en") or st["headline"], "title_fr": m.get("title_fr") or st["headline"],
                   "outlet": outlet(st["url"]), "category": cat, "importance": int(m.get("importance", 2)),
                   "summary_fr": st["fr"] or "", "summary_en": st["en"] or ""}
            if wfr and wen and why_adds(st, wfr, wen):
                it_["why_fr"], it_["why_en"] = wfr, wen
            items.append(it_)
            for it in [x for x in money["items"] if x.get("story_url") == st["url"]]:
                body.append(money_box(it, money["population"]))
            body.append('</article>')
        body.append('</section>')
    if any("{{" in t or "{%" in t for t in body): issues.append(f"{day}: Liquid-like text in content")
    for rank, it_ in enumerate(sorted(items, key=lambda x: -x["importance"])[:3], 1): it_["featured"] = rank
    for it_ in items: it_.setdefault("featured", 0)
    sfr, sen = SUMMARY[day]
    fm = ["---", "layout: post",
          f"title: {json.dumps(title_en, ensure_ascii=False)}",
          f"title_fr: {json.dumps(title_fr, ensure_ascii=False)}",
          f"date: {day}",
          f"summary: {json.dumps(sen, ensure_ascii=False)}",
          f"summary_fr: {json.dumps(sfr, ensure_ascii=False)}",
          f"story_count: {n}",
          "tags: [" + ", ".join(TAGS[day]) + "]",
          f"source_heading: {json.dumps(title_line, ensure_ascii=False)}",
          "stories:"] + [f"  - {json.dumps(it_, ensure_ascii=False)}" for it_ in items] + ["---", ""]
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
