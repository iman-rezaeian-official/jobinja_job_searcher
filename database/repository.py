from sqlalchemy.exc import IntegrityError

from database.db import SessionLocal
from models.job_model import Job


BATCH_SIZE = 100


def save_jobs(jobs_data):

    with SessionLocal() as session:

        for i in range(
            0,
            len(jobs_data),
            BATCH_SIZE
        ):

            batch = jobs_data[
                i:i + BATCH_SIZE
            ]

            try:
                session.add_all(
                    [Job(**item) for item in batch]
                )

                session.commit()

                print(
                    f"Saved batch {i}"
                )

            except Exception as batch_error:

                print(
                    f"Batch failed: {batch_error}"
                )

                session.rollback()

                # fallback to per-row save
                for item in batch:

                    try:
                        session.add(
                            Job(**item)
                        )

                        session.commit()

                    except IntegrityError:
                        session.rollback()

                    except Exception as row_error:
                        session.rollback()

                        print(
                            f"Row failed: "
                            f"{row_error}"
                        )