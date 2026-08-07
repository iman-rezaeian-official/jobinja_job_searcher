# app/analyzer/persistence.py

from datetime import datetime, timezone
import json
from sqlalchemy.orm import Session

from app.database.engine import SessionLocal
from app.models.job_analysis_model import JobAnalysis


def save_analysis(
    job_id: int,
    llm_result: dict,
    model_name: str = "gemma2:9b",
    session: Session | None = None,
) -> JobAnalysis:
    """
    Save LLM match result for a job.
    Creates a new JobAnalysis row.
    """
    close_session = False
    if session is None:
        session = SessionLocal()
        close_session = True

    try:
        print(llm_result)
        print(llm_result["match_percent"])
        analysis = JobAnalysis(
            job_id=job_id,
            match_percent=llm_result["match_percent"],
            strengths=llm_result["strengths"],
            gaps=llm_result["gaps"],
            recommendations=llm_result["recommendations"],
            raw_response=json.dumps(llm_result, ensure_ascii=False),
            model_name=model_name,
            analyzed_at=datetime.now(timezone.utc),
        )
        session.add(analysis)
        session.commit()
        session.refresh(analysis)
        return analysis
    except Exception:
        session.rollback()
        raise
    finally:
        if close_session:
            session.close()