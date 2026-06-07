from app.database.engine import Base, engine

from app.scheduler.hourly_runner import run_scheduler


def main():
    Base.metadata.create_all(
        bind=engine
    )

    run_scheduler(
        poll_interval_seconds=120
    )


if __name__ == "__main__":
    main()
