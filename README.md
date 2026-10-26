# Quebec Governance Monitor – news-alerts

Daily digest on Quebec governance, published with Jekyll on GitHub Pages:
https://quebec-taxpayer.github.io/news-alerts/

The site has a **FR | EN** toggle at the top right. **French is the default** for first-time visitors (also when
JavaScript is off); there is no automatic switch based on the browser's language. The choice is remembered in the
browser (localStorage key `qgm-lang`), and switching keeps the reader's place on the page (the first visible element is
measured before/after and the page is scrolled to compensate).
- `?lang=en` / `?lang=fr` in any URL overrides the saved choice and is saved. The toggle writes the current language to
  the URL with `history.replaceState` (no reload), so a copied link opens in the same language.
- `document.title` swaps with the toggle on every page (`data-en` / `data-fr` on `<title>`, `_layouts/default.html`).
- `<meta name="description">` stays French (`page.summary_fr`, else `site.description`); `og:title` and
  `og:description` are English (`page.summary`, else `site.description_en`).
- **RSS:** `feed.xml` (hand-written RSS 2.0, bilingual item titles "FR / EN"; jekyll-feed is not used because it would
  give English-only titles). Linked with `<link rel="alternate">` in the head and a small *RSS* link next to the toggle.

Design rules (see `assets/css/style.css`): one system sans-serif stack (`--font`, no web-font service), white
background, dark text, deep blue for links/navigation/accents, red only as a sparing accent (the top story, *Delayed*
status). Yellow (`#ffd400`) marks the current menu item; plain-language boxes are `#fff8d6` with black text.
Mobile: title 28 px, section headings 22 px, headlines 18 px, summaries 16 px, metadata 14 px, line height 1.5,
16–20 px side padding, touch targets ≥ 44 px, no horizontal scroll from 320 px. No animations, banners or images.

## Homepage (`index.html`, data-driven)
Built from the front-matter `stories:` list of the latest post (`site.posts.first.stories`, written by `gen.py`):
1. Title, the subtitle (what the site covers), then the meta line: date · *Updated daily around 10:00 ET / Mis à jour
   chaque jour vers 10 h (HE)* (the daily routine runs at about 10:00 Toronto time) · story count · number of promises
   tracked (computed from `_data/promises.json`). The header tagline is `tagline_en` / `tagline_fr` in `_config.yml`.
2. **À la une / Top stories** – the 3 stories with `featured: 1..3` (highest `importance`; ties keep digest order).
   Each card: category badge, headline, byline = the source only (no category or date on the homepage; digest and
   archive pages keep dates), summary, *Why it matters*, *Read the source* and *Permalink / Lien permanent* (the story
   in the day's digest). *Headline as published (FR) / Titre tel que publié (EN)* appears only in the language whose
   displayed title differs from the original, with the original's language code.
3. **Promis vs réalisé** tracker (`_includes/tracker-home.html`, data `_data/promises.json` + `_data/promise_status.json`).
4. **The other N stories / Les N autres nouvelles** (badge = number of rows) – the non-featured stories as compact
   headlines grouped by category (`_data/categories.json` order), each a `<details>` with summary, *Why it matters*
   (only when it adds to the summary), source link and *Permalink*. Then *Today's digest on one page (permanent link)*
   (it holds the same stories; if a hand-made post ever differs, its own count is shown). Markup: `_includes/news-item.html`.
5. **What's next**, then the previous 6 days and a link to the Archive.
Posts without `stories:` fall back to a plain link to the digest.

## How the language toggle works
- Every piece of language-specific text exists twice: `<span class="l-en" lang="en">…</span>`
  and `<span class="l-fr" lang="fr">…</span>` (or `<p>`, `<section>` with the same classes).
- The `<html>` element carries `lang-en` or `lang-fr`; `assets/css/style.css` hides the other language.
- Headlines link to the original article. On the homepage a translated display title (`title_fr` / `title_en` in
  `_data/story_meta.json`) may be shown; the original title is then shown as *Titre tel que publié (EN) / Headline as
  published (FR)*, only in the language where the display title differs.
  Inside the daily digest posts the headline stays exactly as published.
- Post front matter has both languages: `title` (EN), `title_fr`, `summary` (EN), `summary_fr`.
  Pages use `title` (EN) and `title_fr`.

## Menu and URLs
Menu order (EN / FR), defined in `_includes/nav.html`. Labels were renamed in October 2026; **URLs did not change**.

| # | EN | FR | URL |
|---|---|---|---|
| 1 | Home | Accueil | `/` |
| 2 | Dossiers | Dossiers | `/chronology/` (ongoing subjects with timelines; formerly *Chronology*) |
| 3 | Topics | Thèmes | `/topics/` (the team's three priority topics, by day) |
| 4 | Who's named | Qui est nommé | `/network/` (formerly *Network*; the disclaimer stays first on the page) |
| 5 | Special Reports | Rapports spéciaux | `/special-reports/` (long-form report series; see below) |
| 6 | Archive | Archives | `/past-news/` (all daily digests by month; `past-news.md`; formerly *Past News*) |
| 7 | About | À propos | `/about/` (includes *Sources and method / Sources et méthode* at `/about/#sources`) |

The current section is highlighted in yellow. Daily digest posts count as *Archive*, dossier pages as
*Dossiers*; other pages use the first URL segment or a `section:` front-matter value.
Homepage category badges are plain labels (not links): homepage categories (`_data/categories.json`) and the Topics
page (`topics:` in `_config.yml`) are two different lists.
Old URLs are kept as plain redirect pages (meta refresh + link, no plugin, not in the menu):
`/archive/` → `/past-news/` (`archive-redirect.html`, the Archive), `/sources/` → `/about/#sources` (`sources-redirect.html`) and
`/glossary/` → `/` (`glossary-redirect.html`; the glossary page was replaced by pop-up definitions, see below).
There is no weekly roundup section.

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
3a. **Homepage metadata (daily):** for every new story add an entry to `_data/story_meta.json` →
   `"stories": {"<story url>": {"category": "<id>", "importance": 1-5, "title_en": "…", "title_fr": "…"}}`.
   `category` is an id from `_data/categories.json`: `government` (*Governments and assemblies / Gouvernements et
   assemblées*: any level of government, the National Assembly, Parliament, municipal councils), `finances`, `crown-it`,
   `justice`, `health`, `energy`, `other`. `importance` is editorial: 5 = major public-money/accountability impact, 4 = significant,
   3 = notable, 2 = routine, 1 = minor/local; the top 3 become *À la une*. Add `title_en` for French headlines and
   `title_fr` for English ones: a faithful translation of the original title, nothing added. If an entry is missing,
   `gen.py` falls back to the section heading's category and importance 2 (`plain.py` prints a NOTE).
3b. **Plain-language upkeep (daily):** for every new story add a *Why it matters* line to `_data/why.json`
   (`"<story url>": {"en": "…", "fr": "…"}`) — one or two plain sentences taken only from that story's source.
   **Rule: it must add one thing the summary did not say** — the public stake, what to watch next, or the gap in the
   record (what is not known or not public) — **and never repeat a number already in the summary.** `plain.py --strict`
   fails when a figure in the latest day's line also appears in its summary (older days: NOTE only). Verify every fact
   against the cached article; if nothing new can be sourced, write a short neutral line that still repeats no figure. (Alternatively put
   `💡🇫🇷 …` / `💡🇬🇧 …` lines under the story's URL in the .txt.) If a story gives a large public-money figure,
   consider a *money in human terms* item (see below). Also, when a story warrants it:
   update the dossier's `tldr.now` (In 30 seconds); add any new **dated** next step to `_data/upcoming.json`
   (only dates stated by the source); add a pop-up definition term (and its EN/FR match phrases) to `_data/glossary.json` if a story
   uses jargon readers may not know; add a *promised vs delivered* pair only when both values are sourced.
   Then rerun `gen.py`, `python3 _tools/chrono.py --strict` and `python3 _tools/plain.py --strict`.
4. Commit and push to `main`. Home, Archive, Topics and the RSS feed update automatically (about 1 minute).

**Option B – by hand.** Copy an existing `_posts/…-digest.md`, update the front matter
(`title`, `title_fr`, `date`, `summary`, `summary_fr`, `story_count`, `tags`) and the stories,
keeping the `l-en` / `l-fr` markup for summaries and section headings.

## Who's named page (`/network/`, formerly Network)

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

## Dossiers (`/chronology/`, formerly Chronology)

`/chronology/` lists ongoing subjects ("dossiers"); each dossier has a vertical timeline at `/chronology/<id>/`.
Data: `_data/dossiers.json` — per dossier `id`, `name_en/fr`, `desc_en/fr`, `entities` (network entity ids, used for
"Appears in these dossiers" on the Who's named page) and `events`. Each event: `date` (`YYYY`, `YYYY-MM` or `YYYY-MM-DD`
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

## Special Reports (`/special-reports/`)

Long-form, bilingual report series. The first series is *Investigated, Reported, Ignored: Seventy Years of Quebec
Governance Failures, from Duplessis to SAAQclic* / *Enquêté, rapporté, ignoré*. It has four reports:
`special-reports/lobbying.html`, `auditor-general.html`, `charbonneau.html` and `saaqclic.html`.
`special-reports/index.html` lists them under the series title. Each page uses `layout: page`, `section: special-reports`
(the menu highlight) and a `permalink` under `/special-reports/`.

Each report has the same structure:
- an "In 30 seconds" box;
- "Why it matters" callouts;
- money boxes (`_data/money.json`, per person via `plain.py`) where a sourced figure supports one;
- a "What's against this view" section;
- inline source links, with `#page=N` for PDFs.

Allegations are attributed, never stated as fact. The series' master chronology is the `decades` dossier at
`/chronology/decades/`, and every report links to it. Internal links in dossier `desc_en/fr` may be written root-relative
(`href="/special-reports/"`); `chronology.html` and `_layouts/dossier.html` prefix them via `relative_url`.

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

- **Pop-up definitions / Définitions en contexte** (there is no glossary page any more): `_data/glossary.json` is the
  single source. Each term: `id`, `term_en/fr`, `def_en/fr` (one or two plain sentences, nothing beyond what the official
  source says), `source_label`, `source_en/fr` (official page URL; `null` if none), and `match_en` / `match_fr`.
  **A new term added to the file automatically appears as a pop-up definition on every page** after the next build.
  How matching works (`assets/js/plain.js`, data emitted by `_layouts/default.html` as `#gl-data`):
  - `match_en` lists the English forms/aliases, `match_fr` the French ones (e.g. `["Auditor General"]` /
    `["Vérificateur général", "vérificatrice générale"]`). English text (`lang="en"`) is matched only against `match_en`,
    French text only against `match_fr`; the pop-up shows the definition in the language of the text.
  - Case-insensitive, whole words only; `'`/`’`, spaces and hyphens are interchangeable. Longer phrases win
    (list the full name and the acronym separately). Avoid generic words.
  - Only the **first** mention of each term per page (per language) is marked, with a dotted blue underline.
  - Marked anywhere in the page body (homepage, posts, topics, chronology/dossiers, About, Archive), but never in
    links (so not in headlines as published), buttons, headings, the nav/header/footer, code, SVG, labels or
    callout labels. A page can opt out with `no_popups: true` in its front matter (used by `/network/`).
  - Hover (mouse) or keyboard focus shows the pop-up; click/tap or Enter pins it; Esc, tap outside or × closes it.
    With JavaScript off the text reads normally, with no marks.
  `plain.py --strict` validates the file and warns about a phrase claimed by two terms.
- **What's next / Prochaines étapes**: `_data/upcoming.json`. Each item: `id`, `date` (`YYYY-MM-DD` or `YYYY`),
  `kind` (`on` = on that day, `by` = by that date, `year` = sometime that year), `en`/`fr`, `source_title/outlet/url`,
  `pages` (`home` and/or dossier ids), optional `story_url`. Only dates a cited source states. The box lists items
  strictly by date, year-only items last, with the note *Only dates stated in a cited source* at the top. Today
  (America/Toronto) shows as *Today / Aujourd'hui* (page JS; without JS the date is shown). On the homepage, passed
  items are left out at build time and hidden by the page JS; on dossier pages they move under a collapsed
  *Past / Passé*. If `story_url` (or `source_url`) is one of today's stories, the homepage item links to its card.
  Delete items about a month after they pass.
- **Promised vs delivered / Promis vs réalisé** (`/promises/` and the dossier page): `_data/promises.json`
  `items[]`: `id`, `dossier`, `type` (`cost|date|outcome`), `item_en/fr`, `announced_en/fr` + `announced_source_*`,
  `actual_en/fr` + `actual_source_*` + `actual_date`. Both sides must come from cited sources — no estimates.
  `type` is `cost|deadline|outcome`. Every item has a `status`: `promised` (Promis), `in_progress` (En cours),
  `completed` (Réalisé), `delayed` (En retard), `unfulfilled` (Non réalisé); labels/marks in `_data/promise_status.json`,
  always shown as text + symbol, never colour alone. Optional `status_note_en/fr`. **`delayed` and `unfulfilled`
  require cited evidence:** `status_evidence_en/fr`, `status_source_url`, `status_source_outlet`, `status_source_date`
  (`plain.py --strict` fails otherwise). **Every item, whatever its status, now needs this sourced *Why this status*.**
  Status definitions (shown under the legend; check each status against them, and report a doubtful one rather than
  silently changing it): *Promised* = announced, no concrete step yet; *In progress* = a bill, mandate letter, budget
  line or contract exists; *Completed* = in force; *Delayed* = past a date the government itself gave; *Unfulfilled* =
  dropped or contradicted. Also: `updated` (YYYY-MM-DD of the latest sourced change; cards show *Last update* and sort
  newest first), optional `party_en/fr` for an election promise (e.g. *PQ election promise*), optional
  `announced_lines` / `actual_lines` (`[{en, fr, source_title, source_outlet, source_url, date}]`) when one card
  compares several sourced figures (e.g. *SAAQclic: what it was supposed to cost vs the latest estimate*). The homepage
  tracker and `/promises/` link each entry to its sources and to the dossier (related coverage).
- **Printable fact sheet** (`/chronology/<id>/print/`): layout `_layouts/dossier-print.html`, one Letter/A4 page:
  In 30 seconds, key figures, timeline, main names, sources. `chrono.py` creates the stub
  `chronology/print/<id>.html` for new dossiers automatically. Check long dossiers still fit on one page (print preview).

## SVG visuals (timeline and charts)

Inline SVG and CSS only, with no libraries. The only script is `assets/js/svg-timeline.js`, which is about 2 KB and is loaded only on dossier pages that have a `svg_timeline` (see `_layouts/default.html`). The homepage is reserved for the latest news and has no timeline. Animations run only when `prefers-reduced-motion` is `no-preference`, and they are switched off for print.

### Dossier timeline (`_data/svg_timelines/<id>.json`)

- To give a dossier a visual timeline, create `_data/svg_timelines/<id>.json` and add `"svg_timeline": "<id>"` to that dossier in `_data/dossiers.json`. The dossier page then shows it just after the "In 30 seconds" box, followed by the dossier's charts and then the detailed event list. The script loads automatically, and the Dossiers index shows a "Visual timeline" badge. Example: `saaqclic`. On such dossiers, the detailed event list is wrapped in a `<details>` element ("Detailed timeline with all sources / Chronologie détaillée et sources"). It is closed on phones (720 px or less) so the steps aren't repeated, and always open on desktop, without JS and in print.
- Manual use: `{% include svg-timeline.html data=site.data.svg_timelines.saaqclic %}` (also add the script tag on that page).
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

- **Automatic:** a chart whose `dossier` matches a chronology dossier id appears on that dossier page, after the visual timeline (if any) and before the detailed event list.
- **Manual:** call `{% include svg-chart.html data=site.data.charts.saaqclic_cost %}` anywhere.
- `"render": false` keeps a chart out of the live site. Use it for placeholders, e.g. `example_placeholder.json`. Add `force=true` to the include only for local tests.
- `"verified": false` gives a hatched bar with a dashed red outline and the label "Unverified / Non vérifié", in both the chart and the source list.
- Labels wrap automatically. The bar length is relative to the largest value. Bars are never stacked or added together.
- Each chart includes `<title>`/`<desc>`, a visually hidden data table for screen readers, and a numbered source list. It prints in black and white without animation.

## Local preview
`bundle install && bundle exec jekyll serve` then open http://127.0.0.1:4000/news-alerts/
