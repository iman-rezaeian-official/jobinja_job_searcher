import logging
from config import JOBS_URL
from app.scraper.fetcher import fetch_page
from app.scraper.parser import parse_jobs

from app.database.engine import SessionLocal
from app.database.repository import exists, insert_job

from app.scraper.auth import create_driver, manual_login_if_needed


logger = logging.getLogger(__name__)


def sync_latest_jobs():
    driver = None

    try:
        driver = create_driver()

        manual_login_if_needed(driver)

        new_jobs = 0
        duplicate_count = 0

        with SessionLocal() as session:

            page = 1

            while True:

                url = (
                    f"{JOBS_URL}?page={page}"
                )

                html = fetch_page(
                    driver,
                    url,
                )
                jobs = parse_jobs(html)
                if not jobs:
                    logger.info("No jobs found. Stopping!")
                    break
                for job in jobs:

                    if exists(
                        session,
                        job["link"],
                    ):

                        duplicate_count += 1

                        if duplicate_count >= 20:
                            session.commit()

                            logger.info(
                                "Reached duplicate threshold. "
                                "Stopping sync."
                            )

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

            return new_jobs
    finally:
        if driver:
            driver.quit()
