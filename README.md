# Job Radar

A personal job tracking pipeline that scrapes listings from Indeed and LinkedIn, scores them for relevance using Claude AI, surfaces the best matches in a password-protected dashboard, and sends a nightly email digest.

Built in Python with a fully automated cloud infrastructure: jobs are scraped and enriched twice daily via GitHub Actions, stored in Postgres on Supabase, and served via a Streamlit dashboard.

---

## What it does

1. **Scrapes** job postings from Indeed and LinkedIn using [JobSpy](https://github.com/speedyapply/JobSpy)
2. **Classifies** each posting by apply type (ATS, company site, aggregator) for informational purposes in the dashboard
3. **Enriches** each job using the Claude API (Haiku), scoring relevance 1-10 against a custom candidate profile including resume, experience level, location preferences, and domain interests
4. **Auto-rejects** low-scoring jobs so the dashboard stays clean
5. **Serves** a filterable dashboard showing unreviewed jobs sorted by relevance score, with links to job posts and status tracking
6. **Emails** a nightly HTML digest of all unreviewed jobs scoring above a customizable threshold

---

## Stack

| Layer | Tool                                  |
|---|---------------------------------------|
| Scraping | JobSpy (Indeed + LinkedIn)            |
| Classification | Python + regex (ATS domain whitelist) |
| AI enrichment | Anthropic Claude API (Haiku 4.5)      |
| Database | PostgreSQL via Supabase               |
| ORM + migrations | SQLAlchemy + Alembic                  |
| Dashboard | Streamlit                             |
| Scheduling | GitHub Actions (cron)                 |
| Email | Gmail SMTP                            |

---

## Architecture

```
GitHub Actions (cron: 7am + 7pm CT)
    → scraper.py       — scrapes jobs, classifies apply URLs
    → ai_enricher.py   — scores unscored jobs via Claude API

GitHub Actions (cron: 9pm CT)
    → emailer.py       — sends HTML digest of unreviewed jobs scoring 6+

All data → Supabase (Postgres)

Streamlit Cloud (24/7)
    → dashboard.py     — password-protected, reads from Supabase
```

---

## Setup

### 1. Clone and install

```bash
git clone https://github.com/choutz/job-radar.git
cd job-radar
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure your profile

Edit `config.py` to personalize the tool for your background. The key things to change:

**`USER_PROFILE`** — paste in your resume summary, experience level, location preferences, and interests.

**`SEARCH_TERMS`** — Search queries to run. Keep this list short — the AI handles relevance filtering so a few broad terms are enough, and too many rapid requests can trigger temporary IP blocks.

**`EMAIL_ALERT_THRESHOLD`** — minimum relevance score (1-10) to include in the nightly digest. Default is 6.

**`RELEVANCE_SCORE_INSTRUCTIONS`** — customize how Claude scores jobs. Add or remove criteria based on what matters to you (seniority, domain, location, etc).

### 3. Set up environment variables

Create a `.env` file:

```
DATABASE_URL=postgresql://...        # Supabase connection string (port 6543 pooler)
ANTHROPIC_API_KEY=sk-ant-...
EMAIL_SENDER=your.sender@gmail.com
EMAIL_RECIPIENT=your.main@gmail.com
EMAIL_APP_PASSWORD=xxxxxxxxxxxxxxxx  # Gmail App Password (no spaces)
```

### 4. Run migrations

```bash
alembic upgrade head
```

### 5. Run locally

```bash
python main.py          # scrape, store, and enrich jobs
python emailer.py       # send digest (optional)
streamlit run dashboard.py
```

---

## Deployment

### Supabase
- Create a free project at [supabase.com](https://supabase.com)
- Use the **Transaction mode** connection string (port 6543) for cloud compatibility
- Run `alembic upgrade head` to create tables

### GitHub Actions
- Add `DATABASE_URL`, `ANTHROPIC_API_KEY`, `EMAIL_SENDER`, `EMAIL_RECIPIENT`, `EMAIL_APP_PASSWORD` as repository secrets
- The workflow in `.github/workflows/scrape.yml` runs automatically on schedule
- Trigger manually anytime via **Actions → Run workflow**

### Streamlit Cloud
- Connect your GitHub repo at [share.streamlit.io](https://share.streamlit.io)
- Add `DATABASE_URL` and `password` to Streamlit secrets
- Dashboard redeploys automatically on every push


---

## Cost

- **Supabase** — free tier (500MB)
- **GitHub Actions** — free tier (2,000 min/month; this uses ~300)
- **Streamlit Cloud** — free
- **Claude API** — ~$0.005 per job enriched on Haiku 4.5; $5 lasts ~1,000 enrichments
- **Gmail SMTP** — free

---

## Project structure

```
job-radar/
├── main.py              # entry point — runs scraper
├── scraper.py           # Indeed scraping via JobSpy
├── classifier.py        # ATS/company site URL classifier
├── ai_enricher.py       # Claude API enrichment + scoring
├── emailer.py           # nightly HTML digest
├── dashboard.py         # Streamlit dashboard
├── models.py            # SQLAlchemy models + DB connection
├── config.py            # user profile, search terms, thresholds
├── alembic/             # DB migrations
└── .github/workflows/   # GitHub Actions cron jobs
```
