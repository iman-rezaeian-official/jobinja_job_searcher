from time import sleep

from app.services.sync_jobs import (
    sync_latest_jobs,
)


def run_scheduler(
    poll_interval_seconds=3600,
):

    while True:

        try:

            count = sync_latest_jobs()

            print(
                f"Added {count} jobs"
            )

        except Exception as e:

            print(
                f"Sync failed: {e}"
            )

        sleep(
            poll_interval_seconds
        )
