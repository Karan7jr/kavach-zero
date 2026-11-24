
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app

from app.extensions import db


def check_database_connection():

    try:
        db.session.execute(text("SELECT 1"))
        return True

    except SQLAlchemyError as error:
        db.session.rollback()

        current_app.logger.error(
            "Database connection failed: %s",
            type(error).__name__
        )

        return False

    finally:
        db.session.remove()
