from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,

)
from sqlalchemy.orm import relationship

from app.database.engine import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)

    title = Column(String, nullable=False)

    company = Column(String)

    location = Column(String)

    job_info = Column(String)

    posted = Column(String)

    link = Column(String, unique=True, nullable=False)

    logo = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    scraped_at = Column(
        DateTime,
        default=datetime.now(UTC),
        nullable=False
    )

    analyses = relationship("JobAnalysis", back_populates="job", cascade="all, delete-orphan")
