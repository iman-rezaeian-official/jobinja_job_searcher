from app.database.engine import Base, engine

from app.scheduler.scheduler import run_scheduler


def main():
    Base.metadata.create_all(
        bind=engine
    )

    run_scheduler(
        minutes=10
    )


if __name__ == "__main__":
    main()
