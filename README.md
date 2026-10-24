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
4. Commit and push to `main`. Home, archive and topics update automatically (about 1 minute).

**Option B – by hand.** Copy an existing `_posts/…-digest.md`, update the front matter
(`title`, `title_fr`, `date`, `summary`, `summary_fr`, `story_count`, `tags`) and the stories,
keeping the `l-en` / `l-fr` markup for summaries and section headings.

## Local preview
`bundle install && bundle exec jekyll serve` then open http://127.0.0.1:4000/news-alerts/
