#!/usr/bin/env python3
"""Generate the weekly roundup (Bilan de la semaine) from a small spec file.

Usage: python3 _tools/weekly.py 2026-10-24      (reads _tools/weekly/2026-10-24.json, writes _weekly/2026-10-24.md)
Spec: {"start", "end", "intro_en", "intro_fr",
       "picks": [{"match": "<unique fragment of a published story URL>", "title_en", "title_fr", "plain_en", "plain_fr"}]  (exactly 5),
       "also": ["<url fragment>", ...]  (optional short list)}
Everything else (headline, source, daily digest link and anchor, Why it matters) is pulled from _posts and
_data/why.json, so the roundup only links to stories already published in the dailies.
"""
import html, json, os, re, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen, plain
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
e = html.escape
FRM, ENM = gen.FR_MONTHS, gen.EN_MONTHS

def stories():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "_posts", "*-digest.md"))):
        day = os.path.basename(f)[:10]
        for sid, url, head in re.findall(r'<article class="story" id="([^"]+)">\s*<h3><a href="([^"]+)">([^<]*)</a>', open(f, encoding="utf-8").read()):
            out.append({"day": day, "id": sid, "url": html.unescape(url), "headline": html.unescape(head)})
    return out

def find(all_, frag, start, end, issues):
    m = [s for s in all_ if frag in s["url"] and start <= s["day"] <= end]
    if len(m) != 1: issues.append(f"'{frag}' matches {len(m)} published stories in {start}..{end}"); return None
    return m[0]

def range_label(a, b):
    ya, ma, da = map(int, a.split("-")); yb, mb, db = map(int, b.split("-"))
    en = f"{ENM[ma-1]} {da}–{db}, {yb}" if ma == mb else f"{ENM[ma-1]} {da} – {ENM[mb-1]} {db}, {yb}"
    fr = f"{da}{'er' if da == 1 else ''} au {db} {FRM[mb-1]} {yb}" if ma == mb else f"{da} {FRM[ma-1]} au {db} {FRM[mb-1]} {yb}"
    return en, fr

def build(key):
    spec = json.load(open(os.path.join(ROOT, "_tools", "weekly", key + ".json"), encoding="utf-8"))
    issues, all_, why = [], stories(), plain.load("why.json", {})
    if len(spec["picks"]) != 5: issues.append(f"{len(spec['picks'])} picks (expected 5)")
    en_r, fr_r = range_label(spec["start"], spec["end"])
    body = ['<p class="l-en wk-intro" lang="en">' + e(spec["intro_en"]) + '</p><p class="l-fr wk-intro" lang="fr">' + e(spec["intro_fr"]) + '</p>', '<ol class="wk-list">']
    for i, p in enumerate(spec["picks"], 1):
        s = find(all_, p["match"], spec["start"], spec["end"], issues)
        if not s: continue
        y, m, d = s["day"].split("-")
        link = "{{ '/" + f"{y}/{m}/{d}/digest/" + "' | relative_url }}#" + s["id"]
        w = why.get(s["url"])
        if not w: issues.append(f"no Why-it-matters line for {s['url']}")
        dd = int(d)
        body.append('<li class="wk-item">')
        body.append(f'<h2 class="wk-h"><span class="wk-n">{i}</span> {gen.bi("span", p["title_fr"], p["title_en"])}</h2>')
        body.append(gen.bi("p", p["plain_fr"], p["plain_en"], "wk-text"))
        if w: body.append('<div class="callout why"><p class="callout-label">' + gen.bi("span", "Pourquoi c’est important", "Why it matters") + '</p>' + gen.bi("p", w["fr"], w["en"]) + '</div>')
        body.append(f'<p class="wk-links"><a href="{link}">' + gen.bi("span", f"Dans le bulletin du {dd}{'er' if dd == 1 else ''} {FRM[int(m)-1]}", f"In the {ENM[int(m)-1]} {dd} digest") + f'</a> · <a href="{e(s["url"])}" rel="noopener" target="_blank">' + gen.bi("span", "Source", "Source") + f'</a>: <span class="wk-head">{e(s["headline"])}</span></p>')
        body.append('</li>')
    body.append('</ol>')
    if spec.get("also"):
        body.append('<h2>' + gen.bi("span", "Aussi cette semaine", "Also this week") + '</h2><ul class="wk-also">')
        for frag in spec["also"]:
            s = find(all_, frag, spec["start"], spec["end"], issues)
            if not s: continue
            y, m, d = s["day"].split("-")
            body.append(f'<li><a href="' + "{{ '/" + f"{y}/{m}/{d}/digest/" + "' | relative_url }}#" + s["id"] + f'">{e(s["headline"])}</a></li>')
        body.append('</ul>')
    fm = ["---", "layout: weekly",
          f"title: {json.dumps('Weekly roundup – ' + en_r, ensure_ascii=False)}",
          f"title_fr: {json.dumps('Bilan de la semaine – ' + fr_r, ensure_ascii=False)}",
          f"date: {spec['end']}", f"start: {spec['start']}", f"end: {spec['end']}",
          f"summary: {json.dumps(spec['intro_en'], ensure_ascii=False)}",
          f"summary_fr: {json.dumps(spec['intro_fr'], ensure_ascii=False)}", "---", ""]
    os.makedirs(os.path.join(ROOT, "_weekly"), exist_ok=True)
    open(os.path.join(ROOT, "_weekly", key + ".md"), "w", encoding="utf-8").write("\n".join(fm) + "\n".join(body) + "\n")
    return issues

if __name__ == "__main__":
    keys = sys.argv[1:] or sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, "_tools", "weekly", "*.json")))
    allis = []
    for k in keys:
        iss = build(k); allis += [f"{k}: {x}" for x in iss]; print(f"wrote _weekly/{k}.md")
    print("ISSUES:", allis or "none")
