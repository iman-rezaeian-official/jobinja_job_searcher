# Jobinja Job Searcher

Scrapes job listings from [Jobinja.ir](https://jobinja.ir) using Selenium and stores them in a local SQLite database. Filters relevant roles, analyzes them against your resume with a local LLM, and stores both raw jobs and match results in SQLite. Runs periodically via APScheduler.

## Architecture

```
jobinja_job_searcher/
├── app/
│   ├── init.py                 # Logging setup
│   ├── main.py                     # Entry point – creates tables, starts scheduler
│   ├── database/
│   │   ├── engine.py               # SQLAlchemy engine, session factory, Base
│   │   ├── init_db.py              # Table creation utility
│   │   └── repository.py           # Per-row existence check & insert
│   ├── models/
│   │   ├── job_model.py            # Job ORM model
│   │   └── job_analysis_model.py   # LLM match results (match_percent, strengths, …)
│   ├── scraper/
│   │   ├── auth.py                 # Selenium WebDriver & cookie-based login
│   │   ├── fetcher.py              # Fetches page HTML via Selenium
│   │   ├── paginator.py            # Extracts last page number
│   │   └── parser.py               # Parses job cards into structured dicts
│   ├── analyzer/
│   │   ├── filter.py               # Mashhad / remote + Python / generic backend filter
│   │   ├── extractor.py            # Detailed job-page extraction (responsibilities, skills)
│   │   ├── scraper.py              # Multi-job scrape with one browser session
│   │   ├── matcher.py              # LLM resume ↔ job comparison
│   │   ├── persistence.py          # Save analysis results to DB
│   │   └── top_matches.py          # Print top N jobs by match_percent
│   ├── scheduler/
│   │   └── scheduler.py            # APScheduler – full pipeline every N minutes
│   ├── services/
│   │   ├── sync_jobs.py            # Scrape listing pages & persist new jobs
│   │   └── evaluate_jobs.py        # Filter → detail scrape → LLM → save analysis
│   └── utils/
│       └── helpers.py              # Text cleaning utility
├── config.py                       # URLs, cookie path, DB URL, model name, …
├── requirements.txt
└── README.md
```

## Flow

1. **`main()`** creates/verifies tables and starts the scheduler.
2. On each cycle (`run_full_pipeline`):
   - **Sync** – Selenium opens Jobinja (cached cookies), fetches listing pages, parses job cards. New jobs are inserted; after many consecutive duplicates the sync stops.
   - **Evaluate** – Loads jobs that pass the filter **and** have no analysis yet:
     - Location: مشهد **or** remote (دورکاری)
     - Title: Python / پایتون **or** generic backend/programming **without** a specific other language (PHP, Java, React, …)
   - Opens the browser **once**, visits each filtered job detail page, extracts responsibilities / must-have / nice-to-have.
   - Sends compact JSON to a local LLM (Ollama) for resume matching.
   - Saves `match_percent`, strengths, gaps, recommendations into `job_analyses`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

## Setup

```bash
pip install -r requirements.txt
```

Requirements:

Chrome + ChromeDriver (managed by Selenium)
Ollama running locally with a model (e.g. gemma4:latest) for the matcher

## Usage

```bash
python -m app.main
```

On first run, a Chrome window opens to the Jobinja login page. Log in manually, then press Enter in the terminal. Cookies are saved to `jobinja_cookies.pkl` for reuse on subsequent runs. Thereafter the scraper runs automatically every 10 minutes.

## Data Model

### `jobs`

| Field       | Type     | Description               |
|-------------|----------|---------------------------|
| title       | string   | Job title                 |
| company     | string   | Company name              |
| location    | string   | Job location              |
| job_info    | string   | Contract type / info      |
| posted      | string   | Relative post date        |
| link        | string   | Job detail URL (unique)   |
| logo        | string   | Company logo image URL    |
| created_at  | datetime | Row creation timestamp    |
| scraped_at  | datetime | Scrape timestamp          |

### `job_analyses`

| Field           | Type     | Description                                      |
|-----------------|----------|--------------------------------------------------|
| id              | integer  | Primary key                                      |
| job_id          | integer  | Foreign key → jobs.id                            |
| match_percent   | float    | 0–100 match score from the LLM                   |
| strengths       | JSON     | List of candidate strengths for this job         |
| gaps            | JSON     | List of skill/experience gaps                    |
| recommendations | JSON     | List of practical recommendations                |
| raw_response    | text     | Full LLM JSON response (for debugging)           |
| model_name      | string   | Model used for the analysis (e.g. gemma2:9b)     |
| analyzed_at     | datetime | When the analysis was stored                     |
