from app.database.engine import engine, Base
import app.models.job_model
import app.models.job_analysis_model


def init_db():
    Base.metadata.create_all(bind=engine)
    