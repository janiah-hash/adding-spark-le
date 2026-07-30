# Adding Spark-le ✨ — Automated Daily Newsletter (Webpage Edition)

An automated Mon–Fri morning newsletter that pulls the latest energy-industry
news, sorts it by client vertical, and publishes it as a **webpage** you
bookmark — no email account gets connected to anything.

## How it works

```
fetch_content.py  →  pulls stories from RSS feeds + NewsAPI.org
enrich.py         →  calls Claude to add "why it matters," Follow of the
                      Day, Pitch Angle, Event Spotlight, Reporter Radar
render.py         →  fills template.html with the day's content
publish_web.py    →  writes it to docs/index.html (+ a dated archive copy)
main.py           →  runs all four steps in order; skips weekends
```

It runs automatically **Monday–Friday** via **GitHub Actions**, then commits
the generated page to the `docs/` folder, which **GitHub Pages** serves as a
live website.

## Does this require downloading a bunch of platforms?

No. The only account you need is **GitHub**, which you already need for the
automation to run at all, whether or not you email yourself. GitHub Pages
isn't a separate product to sign up for — it's a free, built-in setting on
the same repo. There's nothing to install locally and nothing else to sign
up for.

## One-time setup

### 1. Create a GitHub repo
Create a new repo (public or private — private repos get free GitHub Pages
too, on a paid GitHub plan; public repos always get it free) and push these
files to it.

### 2. Turn on GitHub Pages
In your repo: **Settings → Pages → Build and deployment → Source: "Deploy
from a branch"** → Branch: `main`, folder: `/docs` → **Save**.

GitHub will give you a URL like:
```
https://YOUR-USERNAME.github.io/YOUR-REPO-NAME/
```
That's the link you bookmark and check each morning. The archive of past
editions lives at `.../archive/index.html`.

### 3. (Optional) Get a free NewsAPI.org key
Sign up at https://newsapi.org (free tier: 100 requests/day). This broadens
discovery beyond your curated RSS feeds. Skip this and it'll just rely on
RSS feeds alone.

### 4. (Optional) Get an Anthropic API key
From https://console.anthropic.com — powers "why it matters" blurbs, Follow
of the Day, Pitch Angle, Event Spotlight, and Reporter Radar. Without it,
you'll still get categorized headlines, just without the editorial layer.

### 5. Add secrets to GitHub (only if you did steps 3–4)
In your repo: **Settings → Secrets and variables → Actions → New repository
secret**.

| Secret name | Value |
|---|---|
| `NEWSAPI_KEY` | your NewsAPI.org key |
| `ANTHROPIC_API_KEY` | your Anthropic API key |

If you skip both, the workflow still runs fine — it just uses RSS only and
skips the editorial sections.

### 6. Test it
Go to your repo's **Actions** tab → "Publish Adding Spark-le Newsletter" →
**Run workflow** to trigger a manual test run. Then visit your GitHub Pages
URL from step 2 — it may take a minute to update the first time.

### 7. Let it run
Once set up, it fires automatically at 11:00 UTC (7am ET) Monday–Friday.
Edit the `cron:` line in `.github/workflows/send-newsletter.yml` to change
the time — [crontab.guru](https://crontab.guru) is handy for this.

## Customizing

Almost everything editorial lives in **`config.py`**:
- Add/remove client verticals, RSS feeds, and keywords
- Add reporters to `TRACKED_REPORTERS`
- Adjust `MAX_STORIES_PER_VERTICAL` and the lookback window

The visual design lives in **`template.html`** — the fall/cozy styling from
the sample edition, templated with Jinja2 placeholders.

## Important honesty note on Reporter Radar

Journalist moves, beat changes, and open-records requests aren't reliably
detectable from RSS/News API content alone. The AI enrichment step does a
best-effort scan of the day's pulled articles for anything suggestive, but
this section will often be empty, and anything it does surface should be
treated as a lead to verify (Twitter/X, LinkedIn, Muck Rack), not a
confirmed fact.

## Local testing (before relying on GitHub Actions)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in your real values (optional)
python fetch_content.py   # test just the fetching step
python render.py          # renders preview.html you can open in a browser
python main.py             # full run: fetch → enrich → render → publish to docs/
```
After a local `python main.py` run, open `docs/index.html` directly in your
browser to see the result before it's ever pushed anywhere.

## Files

| File | Purpose |
|---|---|
| `config.py` | Verticals, feeds, keywords, reporters — your main editing surface |
| `fetch_content.py` | Pulls & scores stories from RSS + NewsAPI |
| `enrich.py` | Calls Claude for the editorial sections |
| `render.py` | Fills `template.html` with the day's content |
| `template.html` | The page's HTML/CSS design |
| `publish_web.py` | Writes the result to `docs/` for GitHub Pages |
| `main.py` | Orchestrates the whole run; skips weekends |
| `.github/workflows/send-newsletter.yml` | GitHub Actions schedule (Mon–Fri) + auto-publish |
| `.env.example` | Template for local testing values |
