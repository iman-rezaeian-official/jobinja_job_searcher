# app/services/evaluate_jobs.py

import logging
import ast
from app.analyzer.filter import get_filtered_jobs
from app.analyzer.normalizer import scrape_multiple_jobs   # the one-browser version
from app.analyzer.matcher import resume_matcher
from app.analyzer.persistence import save_analysis

logger = logging.getLogger(__name__)


def evaluate_new_jobs():
    """
    Filter → scrape details → LLM match → save analysis
    Only processes jobs that passed the filter and have no analysis yet.
    """
    jobs = get_filtered_jobs(only_unanalyzed=True)

    if not jobs:
        logger.info("No new jobs to evaluate.")
        return 0

    logger.info("Found %s jobs to evaluate.", len(jobs))

    # Scrape all of them with one browser session
    scraped = scrape_multiple_jobs(jobs)

    analyzed_count = 0
    for job in jobs:
        details = scraped.get(job.id)
        if not details:
            logger.warning("No details for job %s – skipping", job.id)
            continue

        try:
            llm_result = resume_matcher(details)

            if isinstance(llm_result, str):
                llm_result = ast.literal_eval(llm_result)

            save_analysis(job.id, llm_result)
            analyzed_count += 1
            logger.info(
                "Analyzed job %s (%s) → %s%%",
                job.id, job.title, llm_result.get("match_percent"),
            )
        except Exception:
            logger.exception("Failed to analyze job %s", job.id)

    return analyzed_count