from app.database.db import engine
from app.models.job_model import Base


def init_db():
    Base.metadata.create_all(bind=engine)
    