from datetime import datetime, UTC

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.database.engine import Base

class JobAnalysis(Base):
    __tablename__ = "job_analyses"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)

    match_percent = Column(Float, nullable=False)
    strengths = Column(JSON, nullable=False)  # list of strings
    gaps = Column(JSON, nullable=False)  # list of strings
    recommendations = Column(JSON, nullable=False)  # list of strings

    raw_response = Column(Text)  # full LLM reply (for debugging)
    model_name = Column(String(100))  # e.g. "gemma2:9b"
    analyzed_at = Column(DateTime, default=lambda: datetime.now(UTC))

    job = relationship("Job", back_populates="analyses")