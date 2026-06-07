import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.sync_jobs import sync_latest_jobs

logger = logging.getLogger(__name__)


def run_scheduler(minutes):

    scheduler = BlockingScheduler()

    scheduler.add_job(
        func=sync_latest_jobs,
        trigger=IntervalTrigger(minutes=minutes),
        id="jobinja_sync",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info("Starting scheduler...")

    # Optional: run immediately on startup
    try:
        added_jobs = sync_latest_jobs()

        logger.info(
            "Initial synchronization completed. Added %s jobs.",
            added_jobs,
        )

    except Exception:
        logger.exception(
            "Initial synchronization failed"
        )

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):

        logger.info(
            "Scheduler stopped"
        )

        scheduler.shutdown()
