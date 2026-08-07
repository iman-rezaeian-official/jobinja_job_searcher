from sqlalchemy import or_, and_, not_, exists
from app.database.engine import SessionLocal
from app.models.job_model import Job
from app.models.job_analysis_model import JobAnalysis


def get_filtered_jobs(only_unanalyzed: bool = True):
    session = SessionLocal()

    try:
        # ----- Location condition -----
        location_condition = or_(
            Job.location.ilike("%مشهد%"),
            Job.location.ilike("%دورکاری%"),
            Job.title.ilike("%دورکاری%"),
            Job.location.ilike("%remote%"),
        )

        # ----- Title condition -----
        # 1. Explicitly Python
        python_condition = or_(
            Job.title.ilike("%python%"),
            Job.title.ilike("%پایتون%"),
            Job.title.ilike("%پای‌تون%"),
        )

        # 2. Generic backend / programming keywords
        backend_keywords = or_(
            Job.title.ilike("%backend%"),
            Job.title.ilike("%back-end%"),
            Job.title.ilike("%back end%"),
            Job.title.ilike("%بک‌اند%"),
            Job.title.ilike("%بک اند%"),
            Job.title.ilike("%بکند%"),
            Job.title.ilike("%برنامه نویس%"),
            Job.title.ilike("%برنامه‌نویس%"),
            Job.title.ilike("%توسعه دهنده%"),
            Job.title.ilike("%توسعه‌دهنده%"),
            Job.title.ilike("%software engineer%"),
            Job.title.ilike("%software developer%"),
        )

        # Languages / technologies that should be excluded from "generic"
        excluded_languages = or_(
            Job.title.ilike("%php%"),
            Job.title.ilike("%laravel%"),
            Job.title.ilike("%java%"),
            # Job.title.ilike("%golang%"),
            Job.title.ilike("% go %"),
            Job.title.ilike("%go/%"),
            Job.title.ilike("%c#%"),
            Job.title.ilike("%c sharp%"),
            Job.title.ilike("%.net%"),
            Job.title.ilike("%dotnet%"),
            Job.title.ilike("%asp.net%"),
            Job.title.ilike("%react%"),
            Job.title.ilike("%next.js%"),
            Job.title.ilike("%nextjs%"),
            Job.title.ilike("%vue%"),
            Job.title.ilike("%angular%"),
            Job.title.ilike("%wordpress%"),
            Job.title.ilike("%وردپرس%"),
            Job.title.ilike("%unreal%"),
            Job.title.ilike("%frontend%"),
            Job.title.ilike("%front-end%"),
            Job.title.ilike("%front end%"),
            Job.title.ilike("%full stack%"),
            Job.title.ilike("%fullstack%"),
            Job.title.ilike("%full-stack%"),
            Job.title.ilike("%qa%"),
            Job.title.ilike("%تست%"),
            Job.title.ilike("%scrum%"),
            Job.title.ilike("%ai%"),
            Job.title.ilike("%ml%"),
            Job.title.ilike("%computer vision%"),
            Job.title.ilike("%nlp%"),
            Job.title.ilike("%پردازش زبان%"),
        )

        generic_backend_condition = and_(
            backend_keywords,
            not_(excluded_languages)
        )

        title_condition = or_(
            python_condition,
            generic_backend_condition
        )

        # ----- Final query -----
        query = session.query(Job).filter(
            and_(
                location_condition,
                title_condition
            )
        )

        # Only jobs that have never been analyzed
        if only_unanalyzed:
            query = query.filter(
                ~exists().where(JobAnalysis.job_id == Job.id)
            )

        results = query.all()
        return results

    finally:
        session.close()

if __name__ == "__main__":
    valid_jobs = get_filtered_jobs()

    print(f"Found {len(valid_jobs)} matching jobs")
    for job in valid_jobs:
        print(f"- {job.title} | {job.location} | {job.url}")