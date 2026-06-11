# Job Scraper

Scrapes job listings from [Jobinja.ir](https://jobinja.ir) using Selenium and stores them in a local SQLite database. Runs periodically via APScheduler.

## Architecture

```
jobinja_job_searcher/
├── app/
│   ├── __init__.py          # Logging setup
│   ├── main.py              # Entry point – creates tables, starts scheduler
│   ├── database/
│   │   ├── engine.py        # SQLAlchemy engine, session factory, declarative base
│   │   ├── init_db.py       # Table creation utility
│   │   └── repository.py    # Per-row existence check & insert
│   ├── models/
│   │   └── job_model.py     # Job ORM model (title, company, location, etc.)
│   ├── scraper/
│   │   ├── auth.py          # Selenium WebDriver setup & cookie-based login
│   │   ├── fetcher.py       # Fetches page HTML via Selenium
│   │   ├── paginator.py     # Extracts last page number (currently unused)
│   │   └── parser.py        # Parses job cards into structured dicts
│   ├── scheduler/
│   │   └── scheduler.py     # APScheduler periodic sync (every N minutes)
│   ├── services/
│   │   └── sync_jobs.py     # Orchestrates scraping & persistence per page
│   └── utils/
│       └── helpers.py       # Text cleaning utility
├── config.py                # Shared constants (URLs, cookie path, DB URL)
├── requirements.txt         # Python dependencies
└── README.md
```

## Flow

1. **`main()`** initializes the database and starts the APScheduler.
2. On each sync cycle, Selenium opens Jobinja (with cached cookies), fetches pages one by one, and parses job cards.
3. Each job is checked against the database by link; duplicates are skipped. After 20 consecutive duplicates the sync stops (assumes all pages are caught up).
4. New jobs are committed per page.

## Setup

```bash
pip install -r requirements.txt
```

Requires Chrome and ChromeDriver (managed by Selenium).

## Usage

```bash
python -m app.main
```

On first run, a Chrome window opens to the Jobinja login page. Log in manually, then press Enter in the terminal. Cookies are saved to `jobinja_cookies.pkl` for reuse on subsequent runs. Thereafter the scraper runs automatically every 10 minutes.

## Data Model

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
