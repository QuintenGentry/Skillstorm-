""" 
Handle database functions. 
"""

from sqlalchemy import ScalarResult, text
from sqlalchemy.sql import Select
from media_api.db_files.db_models import PostRecord
from media_api.db_files.extensions import db


def get_all_posts(stmt: Select[PostRecord] ) -> ScalarResult[PostRecord]:
    """ Return all posts. """
    return db.session.execute(stmt).scalars()

def get_post(id: int) -> PostRecord | None:
    """ return specific post with input id.  """
    return db.session.get(PostRecord, id)

def add_record(record: PostRecord) -> None:
    """ add a particular record to the database """
    db.session.add(record)
    db.session.commit()

def add_and_flush_record(record: PostRecord) -> None:
    """ add a record without commiting (flush)"""
    db.session.add(record)
    db.session.flush()

def commit_changes() -> None:
    """ commit changes """
    db.session.commit()

# Clear the table, and reset the id counter. 
def clear_posts() -> None:
    """ clear current post table (truncate) """
    db.session.execute(text("TRUNCATE TABLE posts RESTART IDENTITY CASCADE"))
    db.session.commit()

def delete_record(record: PostRecord) -> None:
    """ delete inputted PostRecord """
    db.session.delete(record)
    db.session.commit()