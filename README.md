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
   consider a *money in human terms* item (see below). Also, when a story warrants it:
   update the dossier's `tldr.now` (In 30 seconds); add any new **dated** next step to `_data/upcoming.json`
   (only dates stated by the source); add a glossary term (and its match phrases) to `_data/glossary.json` if a story
   uses jargon readers may not know; add a *promised vs delivered* pair only when both values are sourced.
   Then rerun `gen.py`, `python3 _tools/chrono.py --strict` and `python3 _tools/plain.py --strict`.
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

- **Glossary / Lexique** (`/glossary/` + tap tooltips): `_data/glossary.json`. Each term: `id`, `term_en/fr`,
  `def_en/fr` (one or two plain sentences, nothing beyond what the official source says), `source_label`,
  `source_en/fr` (official page URL; `null` if none),
  `match_en`/`match_fr` (exact phrases to mark in text, longest first; avoid generic words). `assets/js/plain.js`
  wraps the first match per term and language in timelines, story summaries, Why-it-matters lines, In-30-seconds
  boxes and weekly items; tapping shows the definition (Esc / tap outside closes). `plain.py` warns about a
  phrase claimed by two terms.
- **What's next / Prochaines étapes**: `_data/upcoming.json`. Each item: `id`, `date` (`YYYY-MM-DD` or `YYYY`),
  `kind` (`on` = on that day, `by` = by that date, `year` = sometime that year), `en`/`fr`, `source_title/outlet/url`,
  `pages` (`home` and/or dossier ids). Only dates a cited source states. The page JS compares with today
  (America/Toronto) and moves passed items under a collapsed *Past / Passé*; delete items about a month after they pass.
- **Promised vs delivered / Promis vs réalisé** (`/promises/` and the dossier page): `_data/promises.json`
  `items[]`: `id`, `dossier`, `type` (`cost|date|outcome`), `item_en/fr`, `announced_en/fr` + `announced_source_*`,
  `actual_en/fr` + `actual_source_*` + `actual_date`. Both sides must come from cited sources — no estimates.
- **Printable fact sheet** (`/chronology/<id>/print/`): layout `_layouts/dossier-print.html`, one Letter/A4 page:
  In 30 seconds, key figures, timeline, main names, sources. `chrono.py` creates the stub
  `chronology/print/<id>.html` for new dossiers automatically. Check long dossiers still fit on one page (print preview).

## Weekly roundup (every Sunday)
`/weekly/` lists roundups; each lives at `/weekly/<sunday-or-end-date>/`.
1. Write `_tools/weekly/YYYY-MM-DD.json` (YYYY-MM-DD = last day covered): `start`, `end`, `intro_en/fr`,
   `picks` (exactly 5: `match` = a unique fragment of a published story URL from that week, `title_en/fr`,
   `plain_en/fr` — two plain sentences taken only from the story) and optional `also` (match strings).
2. `python3 _tools/weekly.py YYYY-MM-DD` writes `_weekly/YYYY-MM-DD.md` with links to each story in its daily digest
   (anchors `#s-<id>`). It reports an error if a `match` finds no story or more than one.
3. `python3 _tools/plain.py --strict`, build/preview, commit, push.

## SVG visuals (timeline and charts)

Inline SVG and CSS only, with no libraries. The only script is `assets/js/svg-timeline.js`, which is loaded on the home page and is about 2 KB. Animations run only when `prefers-reduced-motion` is `no-preference`, and they are switched off for print.

### Homepage timeline (`_data/svg_timelines/<id>.json`)

- Render it with `{% include svg-timeline.html data=site.data.svg_timelines.saaqclic %}` (already in `index.html`).
- Top-level fields are `id`, `title_en`/`title_fr`, `desc_en`/`desc_fr`, `legend` and `events`.
- Each event has these fields:
  - `id` and `date` (`YYYY-MM-DD`, or `YYYY` when only the year is known);
  - `kind`: `saaq` (blue circle), `vgq` (red diamond), `gov` (black square) or `commission` (ringed circle);
  - `label_en`/`label_fr`: two short lines shown on the SVG;
  - `en`/`fr`: the full sentence;
  - `source_title`, `source_outlet` and `source_url` (with optional `source_url_en`);
  - `primary`, `verified` and `checked`.
- **Rule:** every event must link to a *primary* public source (government release, report, decree, official account) that you have opened yourself. Never estimate a date. If a date can't be confirmed, set `"verified": false`. The event is then hatched and labelled "Unverified / Non vérifié". Alternatively, leave it out.
- Layout:
  - Wider than 720 px: a horizontal SVG with equal spacing. A `//` marks a gap of more than a year. Hover, focus or tap shows the details in the yellow panel. Use Left/Right/Home/End to move between steps. Enter opens the source.
  - 720 px or less, or with no JS: the same data is shown as a vertical list with sources (`details` element).

### Reusable bar chart (`_data/charts/<id>.json` and `_includes/svg-chart.html`)

```json
{
  "id": "saaqclic-cost", "render": true, "dossier": "saaqclic",
  "title_en": "...", "title_fr": "...", "desc_en": "...", "desc_fr": "...",
  "units_en": "millions of dollars", "units_fr": "millions de dollars",
  "prefix_en": "$", "suffix_en": "M", "prefix_fr": "", "suffix_fr": " M$",
  "note_en": "...", "note_fr": "...",
  "items": [
    { "label_en": "...", "label_fr": "...", "value": 638,
      "display_en": "$638M", "display_fr": "638 M$",
      "source_title": "...", "source_outlet": "...", "source_url": "https://...",
      "verified": true, "note_en": "...", "note_fr": "..." }
  ]
}
```

- **Automatic:** a chart whose `dossier` matches a chronology dossier id appears on that dossier page, after the money list.
- **Manual:** call `{% include svg-chart.html data=site.data.charts.saaqclic_cost %}` anywhere.
- `"render": false` keeps a chart out of the live site. Use it for placeholders, e.g. `example_placeholder.json`. Add `force=true` to the include only for local tests.
- `"verified": false` gives a hatched bar with a dashed red outline and the label "Unverified / Non vérifié", in both the chart and the source list.
- Labels wrap automatically. The bar length is relative to the largest value. Bars are never stacked or added together.
- Each chart includes `<title>`/`<desc>`, a visually hidden data table for screen readers, and a numbered source list. It prints in black and white without animation.

## Local preview
`bundle install && bundle exec jekyll serve` then open http://127.0.0.1:4000/news-alerts/
