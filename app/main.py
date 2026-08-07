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
        hours=12
    )


if __name__ == "__main__":
    main()
