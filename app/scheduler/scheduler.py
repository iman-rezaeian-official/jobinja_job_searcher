import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.services.sync_jobs import sync_latest_jobs
from app.services.evaluate_jobs import evaluate_new_jobs

logger = logging.getLogger(__name__)

def run_full_pipeline():
    try:
        added = sync_latest_jobs()
        logger.info("Synchronization completed. Added %s jobs.", added)
    except Exception:
        logger.exception("Synchronization failed")

    try:
        analyzed = evaluate_new_jobs()
        logger.info("Evaluation Finished. Analyzed %s jobs.", analyzed)
    except Exception:
        logger.exception("Evaluation failed")

def run_scheduler(hours):

    scheduler = BlockingScheduler()

    scheduler.add_job(
        func=run_full_pipeline,
        trigger=IntervalTrigger(hours=hours),
        id="jobinja_full_pipeline",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    logger.info("Starting scheduler (every %s hours)...", hours)

    run_full_pipeline()

    try:
        scheduler.start()

    except (KeyboardInterrupt, SystemExit):

        logger.info(
            "Scheduler stopped"
        )

        scheduler.shutdown()
