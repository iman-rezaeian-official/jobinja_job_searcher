from app.scraper.fetcher import fetch_page
from app.scraper.parser import parse_jobs

from app.database.engine import SessionLocal
from app.database.repository import (
    exists,
    insert_job,
)


def sync_latest_jobs(driver):

    new_jobs = 0

    with SessionLocal() as session:

        page = 1

        while True:

            url = (
                f"https://jobinja.ir/jobs?page={page}"
            )

            html = fetch_page(
                driver,
                url,
            )

            duplicate_count = 0

            for job in parse_jobs(html):

                if exists(
                    session,
                    job["link"],
                ):

                    duplicate_count += 1

                    if duplicate_count >= 20:
                        session.commit()

                        return new_jobs

                    continue

                duplicate_count = 0

                insert_job(
                    session,
                    job,
                )

                new_jobs += 1

            session.commit()

            page += 1