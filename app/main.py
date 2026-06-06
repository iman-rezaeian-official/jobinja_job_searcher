from config import JOBS_URL

from database.init_db import init_db
from database.repository import save_jobs

from app.scraper.auth import (
    create_driver,
    manual_login_if_needed,
)

from app.scraper.fetcher import fetch_page

from app.scraper.paginator import (
    get_last_page,
)

from app.scraper.parser import parse_jobs


def main():
    # initialize database
    init_db()

    # create selenium driver
    driver = create_driver()

    try:
        # login once manually
        manual_login_if_needed(driver)

        # fetch first page
        first_page_html = fetch_page(
            driver,
            JOBS_URL
        )

        # detect last page dynamically
        last_page = get_last_page(
            first_page_html
        )

        print(
            f"Detected last page: {last_page}"
        )

        all_jobs = []

        # sequential scraping
        for page in range(1, last_page + 1):

            url = (
                f"{JOBS_URL}?page={page}"
            )

            print(
                f"Fetching page {page}"
            )
            try:
                html = fetch_page(
                    driver,
                    url
                )

                jobs = parse_jobs(html)

                all_jobs.extend(jobs)

                print(
                    f"Parsed {len(jobs)} jobs"
                )
            except Exception as e:
                print(f"Could not load and parse the page {page}")

        # save to sqlite
        save_jobs(all_jobs)

        print(
            f"Saved {len(all_jobs)} jobs"
        )

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
