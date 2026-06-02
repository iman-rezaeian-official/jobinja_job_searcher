from config import JOBS_URL

from database.init_db import init_db
from database.repository import save_jobs

from scraper.auth import (
    create_driver,
    manual_login_if_needed,
)

from scraper.fetcher import fetch_page

from scraper.paginator import (
    get_last_page,
)

from scraper.parser import parse_jobs


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



# from config import JOBS_URL
#
# from database.init_db import init_db
# from database.repository import save_jobs
#
# from scraper.auth import (
#     create_authenticated_session,
# )
#
# from scraper.fetcher import (
#     fetch_pages_threaded,
# )
#
# from scraper.paginator import (
#     get_last_page,
# )
#
# from scraper.parser import parse_jobs
#
#
# def main():
#     # create tables
#     init_db()
#
#     # authenticated session
#     session = create_authenticated_session()
#
#     # fetch first page
#     first_page_response = session.get(
#         JOBS_URL
#     )
#
#     first_page_html = (
#         first_page_response.text
#     )
#
#     driver = create_driver()
#
#     manual_login_if_needed(driver)
#
#     html = fetch_page(driver, JOBS_URL)
#
#     # detect last page dynamically
#     last_page = get_last_page(
#         first_page_html
#     )
#
#     print(
#         f"Detected last page: {last_page}"
#     )
#
#     # build all page urls
#     urls = [
#         f"{JOBS_URL}?page={page}"
#         for page in range(
#             1,
#             last_page + 1
#         )
#     ]
#
#     # threaded fetch
#     fetched_pages = fetch_pages_threaded(
#         session,
#         urls
#     )
#
#     all_jobs = []
#
#     for url, html in fetched_pages:
#         jobs = parse_jobs(html)
#
#         all_jobs.extend(jobs)
#
#         print(
#             f"Parsed {len(jobs)} jobs from {url}"
#         )
#
#     # save to database
#     save_jobs(all_jobs)
#
#     print(
#         f"Saved {len(all_jobs)} jobs"
#     )
#
#
# if __name__ == "__main__":
#     main()
