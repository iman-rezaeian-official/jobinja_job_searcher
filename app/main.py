from app.database.engine import Base, engine

from app.scheduler.scheduler import run_scheduler

from app.analyzer.filter import get_filtered_jobs
from app.analyzer.normalizer import job_data, scrape_multiple_jobs
from app.analyzer.matcher import resume_matcher
from app.analyzer.persistence import save_analysis
import ast

def main():
    Base.metadata.create_all(
        bind=engine
    )

    run_scheduler(
        minutes=10
    )


if __name__ == "__main__":
    # main()
    Base.metadata.create_all(
        bind=engine
    )
    valid_jobs = get_filtered_jobs()
    print(f"Found {len(valid_jobs)} matching jobs")

    scraped_data = scrape_multiple_jobs(valid_jobs)

    for job in valid_jobs:
        print(f"- {job.title} | {job.location} | {job.link}")
        job_details = scraped_data.get(job.id)
        if not job_details:
            print(f"Skipping job {job.id} (no data)")
            continue
        try:
            llm_result = resume_matcher(job_details)
            print(f"Match for {job.title}: {llm_result}")

            # Handle both str and already-parsed dict
            if isinstance(llm_result, str):
                llm_result = ast.literal_eval(llm_result)

            save_analysis(job.id, llm_result)

        except Exception as e:
            print(f"LLM/save failed for job {job.id}: {e}")
            continue
