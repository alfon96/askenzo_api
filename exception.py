from starlette import status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import logging
from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound

logger = logging.getLogger(__name__)


class CustomExceptionsClass(Exception):
    def __init__(self, db, error):
        self.db = db
        self.error = error

    def handle(self):
        self.db.rollback()
        if isinstance(self.error, IntegrityError):
            if "duplicate key value violates unique constraint" in str(self.error):
                logger.error(
                    "Value already registered.(Value can be an email a title or a popup message text)."
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Value already registered. (Value can be an email a title or a popup message text).",
                )
            else:
                logger.error(self.error)
                raise self.error
        elif isinstance(self.error, NoResultFound):
            logger.error("Experience id not existing.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Experience id not existing.",
            )
        elif isinstance(self.error, SQLAlchemyError):
            logger.error(self.error)
            raise self.error
