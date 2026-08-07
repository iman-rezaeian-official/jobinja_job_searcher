from app.database.engine import SessionLocal
from app.models.job_model import Job
from app.models.job_analysis_model import JobAnalysis
from sqlalchemy import desc


def get_top_matches(limit: int = 100):
    session = SessionLocal()
    try:
        results = (
            session.query(
                JobAnalysis.match_percent,
                Job.title,
                Job.company,
                Job.location,
                Job.link,
                JobAnalysis.analyzed_at,
                JobAnalysis.id.label("analysis_id"),
                JobAnalysis.gaps,
                JobAnalysis.strengths,
                JobAnalysis.recommendations
            )
            .join(Job, JobAnalysis.job_id == Job.id)
            .order_by(desc(JobAnalysis.match_percent), desc(JobAnalysis.analyzed_at))
            .limit(limit)
            .all()
        )
        return results
    finally:
        session.close()


if __name__ == "__main__":
    top_jobs = get_top_matches(70)

    if not top_jobs:
        print("No analysis results found in the database.")
    else:
        print(f"{'#':<4} {'Match':<8} {'Title':<55} {'Company':<30} {'Location'}")
        print("-" * 120)

        for i, row in enumerate(top_jobs, 1):
            match = f"{row.match_percent:.0f}%"
            title = (row.title or "")[:53]
            company = (row.company or "")[:28]
            location = (row.location or "")[:25]

            print(f"{i:<4} {match:<8} {title:<55} {company:<30} {location}")
            print(f"Strength: {row.strengths}")
            print()
            print(f"gaps: {row.gaps}")
            print()
            print(f"recommendations: {row.recommendations}")
            print()
            print(f"     → {row.link}")
            print("-" * 120)
            print()