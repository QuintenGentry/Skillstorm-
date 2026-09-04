"""
Handles all database operations for our brands database. 
"""

from sqlalchemy import ScalarResult, text
from sqlalchemy.sql import Select
from media_api.db_files.db_models import BrandRecord
from media_api.db_files.extensions import db

def get_all_brands(stmt: Select[BrandRecord] ) -> ScalarResult[BrandRecord]:
    """ return all brands frmo the brands database """
    return db.session.execute(stmt).scalars()

def get_brand(id: int) -> BrandRecord | None:
    """ return a specific brand via id from the brands database"""
    return db.session.get(BrandRecord, id)

def add_record(record: BrandRecord) -> None:
    """ add a particular recor to the brands database. """

    # add record to database. 
    db.session.add(record)
    db.session.commit()

def add_and_flush_record(record: BrandRecord) -> None:
    """ Record a database entry without committing changes. """
    db.session.add(record)
    db.session.flush()

def commit_changes() -> None:
    """ Commit all flushed changes. """
    db.session.commit()

def clear_brands() -> None:
    """ clear current brands database entries. """
    db.session.execute(text("TRUNCATE TABLE brands RESTART IDENTITY CASCADE"))
    db.session.commit()

def delete_record(record: BrandRecord) -> None:
    """ delete a particular brand entry. """
    db.session.delete(record)
    db.session.commit()