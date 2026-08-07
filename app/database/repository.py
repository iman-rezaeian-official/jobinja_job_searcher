from sqlalchemy import select

from app.database.engine import SessionLocal
from app.models.job_model import Job


def exists(session, link):

    stmt = (
        select(Job)
        .where(Job.link == link)
    )

    return (
        session.execute(stmt)
        .scalar_one_or_none()
        is not None
    )


def insert_job(
    session,
    data,
):

    session.add(
        Job(**data)
    )
