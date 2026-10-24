# Quebec Governance Monitor – news-alerts

Daily digest on Quebec governance, published with Jekyll on GitHub Pages:
https://quebec-taxpayer.github.io/news-alerts/

The site has an **EN | FR** toggle at the top right. English is the default (also when
JavaScript is off). The choice is remembered in the browser (localStorage key `qgm-lang`).

## How the language toggle works
- Every piece of language-specific text exists twice: `<span class="l-en" lang="en">…</span>`
  and `<span class="l-fr" lang="fr">…</span>` (or `<p>`, `<section>` with the same classes).
- The `<html>` element carries `lang-en` or `lang-fr`; `assets/css/style.css` hides the other language.
- Headlines are not wrapped: they link to the original article and stay as published in both modes.
- Post front matter has both languages: `title` (EN), `title_fr`, `summary` (EN), `summary_fr`.
  Pages use `title` (EN) and `title_fr`.

## Add a day
**Option A – generator (recommended).**
1. Save the day's digest as `/workspace/governance-digest/YYYY-MM-DD.txt` in the usual format
   (`*Section FR / Section EN*`, `*Headline*`, `🇫🇷 French summary`, `🇬🇧 English summary`, URL,
   signature). Use another folder with `DIGEST_SRC=/path`.
2. In `_tools/gen.py`, add the day to `TAGS` (only clearly applicable: `it-digital`,
   `crown-corporations`, `procurement`) and to `SUMMARY` as `("French one-liner", "English one-liner")`.
   If a section heading isn't in `FR / EN` form, add it to `HEADINGS` as `("FR", "EN")`.
3. Run `python3 _tools/gen.py YYYY-MM-DD`. It writes `_posts/YYYY-MM-DD-digest.md` and reports
   any story missing a field and any one-language heading.
3b. **Plain-language upkeep (daily):** for every new story add a *Why it matters* line to `_data/why.json`
   (`"<story url>": {"en": "…", "fr": "…"}`) — one factual sentence on the concrete effect on ordinary people,
   taken only from that story; if the effect is unclear, write a neutral factual line instead. (Alternatively put
   `💡🇫🇷 …` / `💡🇬🇧 …` lines under the story's URL in the .txt.) If a story gives a large public-money figure,
   consider a *money in human terms* item (see below). Then rerun `gen.py` and `python3 _tools/plain.py --strict`.
4. Commit and push to `main`. Home, archive and topics update automatically (about 1 minute).

**Option B – by hand.** Copy an existing `_posts/…-digest.md`, update the front matter
(`title`, `title_fr`, `date`, `summary`, `summary_fr`, `story_count`, `tags`) and the stories,
keeping the `l-en` / `l-fr` markup for summaries and section headings.

## Network page (`/network/`)

A bubble map of the people and organizations named in the published stories.
Bubble size = number of stories naming the entity; blue = organization, red = person.
**A link only means two names were mentioned in the same news story** — it does not
imply any relationship, wrongdoing or involvement. Edges are never labelled with allegations.

Files:

- `_tools/network_entities.json` — the curated list. `entities` maps an id to
  `{name, type: person|organization, aliases}`; `stories` maps a unique URL fragment
  (`match`) to the entity ids actually named in that article.
- `_tools/network.py` — builds `_data/network.json` (served as `/assets/data/network.json`).
- `assets/js/network.js` + vendored `assets/js/d3.v7.min.js` (D3 v7.9.0, ISC licence in `d3.LICENSE.txt`).

Daily routine, after `gen.py` has written the day's digest post:

1. Cache each new article's text in `$DIGEST_SRC/articles/<md5(url)[:10]>.txt`
   (first line = URL, then the article text). Sites that block scripts can be pasted in by hand;
   set `"checked_by_hand": true` on that story.
2. Add the new stories to `_tools/network_entities.json`: only names that actually appear in the
   article, normalized to the full official name (put short forms in `aliases`). Skip generic
   places, non-specific groups, journalists and media used as sources, and private individuals
   unless they are central to the story and publicly named.
3. Run `python3 _tools/network.py --strict`. It warns (and with `--strict`, fails) on
   UNCURATED stories (no curation entry), UNVERIFIED names (not found in the cached article
   text), UNKNOWN or UNUSED ids and AMBIGUOUS matches. Fix them, rerun, then `bundle exec jekyll build`.
4. Commit `_data/network.json` and `_tools/network_entities.json` with the day's digest.

`DIGEST_SRC` defaults to `/workspace/governance-digest`.

## Chronology

`/chronology/` lists ongoing subjects ("dossiers"); each dossier has a vertical timeline at `/chronology/<id>/`.
Data: `_data/dossiers.json` — per dossier `id`, `name_en/fr`, `desc_en/fr`, `entities` (network entity ids, used for
"Appears in these dossiers" on the Network page) and `events`. Each event: `date` (`YYYY`, `YYYY-MM` or `YYYY-MM-DD`
— the date it **happened**, not the publication date), `en`, `fr`, `source_title`, `source_outlet`, `source_url`,
`source_type` (`primary` or `media`), `post` (digest date if the source is a published story, else `null`) and
`background` (set by the tool). Pages are built by Jekyll from the data (`chronology.html`, `_layouts/dossier.html`,
one stub per dossier in `chronology/`, created by the tool).

Daily routine, after the digest and the network update:
1. In `_tools/network_entities.json`, give each new story `"dossiers": [ids]` (or `[]` if it fits none). A new
   subject gets a dossier only once it has 2+ stories (add it to `_data/dossiers.json` by hand).
2. For each tag, add the event: `python3 _tools/chrono.py add --dossier ID --date YYYY-MM-DD --en "..." --fr "..."
   --source-title "headline" --outlet "Outlet" --source-url URL --type media --post YYYY-MM-DD`.
   Use the date of the event as stated in the article (month or year precision if that is all it gives).
   Phrase allegations as reported ("X reports…", "alleged"); do not add future dates.
3. Background events: only from primary sources or credible outlets actually opened, cited with their URL
   (`--type primary` for government, VGQ, court, company releases). If unsure, leave it out.
4. `python3 _tools/chrono.py --strict` must exit 0 (validates fields, dates, entity ids, digest dates, sorts events,
   creates stubs, and fails if a tagged story has no event or a story has no `dossiers` field).

## Plain-language features
Validate everything with `python3 _tools/plain.py --strict` (exit 1 on any warning) before pushing.

- **In 30 seconds / En 30 secondes** (top of every dossier page): `tldr` in `_data/dossiers.json`,
  `{"what": {en, fr}, "why": {en, fr}, "now": {en, fr}}` — three plain sentences (grade-8 level), written only
  from that dossier's sourced events. Update `now` when a dossier gets a new event. `chrono.py --strict` checks it.
- **Why it matters / Pourquoi c'est important** (under each story): `_data/why.json`, keyed by story URL.
  `plain.py` warns about any published story without one.
- **The money, in human terms / L'argent, en termes concrets**: `_data/money.json`. Each item: `id`, `dossier`,
  `story_url` (or null), `amount` (as stated by the source), `qualifier` (`exact|about|at_least|more_than|target`),
  `per_year`, `label_en/fr`, `source_title`, `source_outlet`, `source_date`, `source_url`, optional `note_en/fr`.
  Run `python3 _tools/plain.py money` to compute `per_person_*`, `calc_*` (shown as "$X ÷ N people = $Y each").
  "at least"/"more than" are rounded down. Rules: only amounts quoted by a cited source; never add figures with
  different scopes (e.g. the $44.8B all-infrastructure and the $22.5B road deficits); leave out private, federal,
  litigation or multi-year cumulative totals that are not comparable with one year's population.
  When ISQ publishes a new population estimate, update the `population` block (value, as_of, source_updated) and rerun.
  Items show on their dossier page and under their story (rerun `gen.py` for posts).

## Local preview
`bundle install && bundle exec jekyll serve` then open http://127.0.0.1:4000/news-alerts/
