# Job Scraper

Scrapes job listings from [Jobinja.ir](https://jobinja.ir) and stores them in a local SQLite database.

## Architecture

```
job_searcher/
├── main.py              # Entry point – orchestrates the full pipeline
├── config.py            # Shared constants (URLs, cookie path, DB URL)
├── requirements.txt     # Python dependencies
├── database/
│   ├── db.py            # SQLAlchemy engine, session factory, base
│   ├── init_db.py       # Creates tables
│   └── repository.py    # Batch-save jobs with per-row fallback
├── models/
│   └── job_model.py     # Job ORM model (title, company, location, etc.)
├── scraper/
│   ├── auth.py          # Selenium WebDriver setup & cookie-based login
│   ├── fetcher.py       # Fetches page HTML via Selenium
│   ├── paginator.py     # Extracts last page number from paginator element
│   └── parser.py        # Parses job cards into structured dicts
└── utils/
    └── helpers.py       # Text cleaning utility
```

## Flow

1. **`main()`** initializes the database, creates a Selenium Chrome driver, and prompts for manual login (cookies are cached for subsequent runs).
2. Fetches the first page, detects the last page number via the paginator.
3. Iterates every page sequentially, fetches HTML, parses job cards.
4. Saves all parsed jobs to SQLite in batches of 100, falling back to per-row insertion on batch failure.

## Setup

```bash
pip install -r requirements.txt
```

Requires ChromeDriver (managed automatically by Selenium).

## Usage

```bash
python main.py
```

On first run, a Chrome window opens to the Jobinja login page. Log in manually, then press Enter in the terminal. Cookies are saved to `jobinja_cookies.pkl` for reuse on subsequent runs.

## Data Model

| Field       | Type   | Description               |
|-------------|--------|---------------------------|
| title       | string | Job title                 |
| company     | string | Company name              |
| location    | string | Job location              |
| job_info    | string | Contract type / info      |
| posted      | string | Relative post date        |
| link        | string | Job detail URL (unique)   |
| logo        | string | Company logo image URL    |
| created_at  | datetime | Row creation timestamp  |
| scraped_at  | datetime | Scrape timestamp         |
