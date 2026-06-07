from app.database.engine import Base, engine
from app.scraper.auth import create_driver, manual_login_if_needed

from app.scheduler.hourly_runner import run_scheduler


def main():
    Base.metadata.create_all(
        bind=engine
    )

    driver = create_driver()

    manual_login_if_needed(driver)

    run_scheduler(
        driver,
        poll_interval_seconds=120
    )


if __name__ == "__main__":
    main()
