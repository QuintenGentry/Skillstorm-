"""
Handles all busines operations for our brands database. 
"""

from media_api.brands.models import Brand, BrandDto

from media_api.brands.data import BRANDS
from sqlalchemy import select, ScalarResult
from sqlalchemy.sql import Select
from media_api.db_files.db_models import BrandRecord
from media_api.db_files.extensions import db
from media_api.brands.store import get_all_brands, get_brand, add_record, clear_brands, commit_changes, add_and_flush_record, delete_record
from media_api.error_responses import ApiError
from media_api.posts.services import list_posts
from media_api.posts.models import Post


def testReady() -> bool:
    """ Test if the brands database is up and running. """
    try: 
        # attempt to run an sql query:
        variable = list_brands()
        return True
    except Exception as e:
        return False


def list_brands() -> list[Brand]:
    """ select all brands. """

    # Creates an sql query
    stmt: Select[BrandRecord] = select(BrandRecord).order_by(BrandRecord.id)

    # Obtain all brands.
    rows: ScalarResult[BrandRecord] = get_all_brands(stmt)

    # Validate records
    # return list of records. 
    return [Brand.model_validate(row) for row in rows]

def list_brands_with_post_info() -> dict:
    """ select all brands, but also include post counters with their compliance statuses. """
    # obtain our database objects. 
    brands : list[Brand]= list_brands()
    posts : list[Post] = list_posts()

    format_dict: dict = {}

    # go through every 
    for brand in brands:
        # obtain brand dictionary entires. 
        brand_dict : dict = brand.model_dump()

        # create our counters for posts . 
        pending_posts: int = 0
        approved_posts: int = 0
        blocked_posts: int = 0
        total_posts : int = 0

        # find post status for each matching brand. 
        for post in posts: 
            post = post.model_dump()
            if post["brand_id"] == brand_dict["id"]:
                if post["compliance_status"] == "pending":
                    pending_posts += 1
                if post["compliance_status"] == "approved":
                    approved_posts += 1
                if post["compliance_status"] == "blocked":
                    blocked_posts += 1
                total_posts += 1

        # update post counters for our dictionary. 
        post_dict : dict = {}
        post_dict["total_posts"] = total_posts
        if pending_posts >= 1: 
            post_dict["pending_posts"] = pending_posts
        if approved_posts >= 1: 
            post_dict["approved_posts"] = approved_posts
        if blocked_posts >= 1: 
            post_dict["blocked_posts"] = blocked_posts

        # Add our post counters to our dictionary. 
        brand_dict["posts"] = post_dict

        # Generate entry for brand. 
        brand_string : str = f"Brand: {brand_dict["id"]}"
        format_dict[brand_string] = brand_dict
        
    return format_dict


def find_brand_by_id(id: int) -> Brand | None:
    """ Return a particular brand based on input id. """

    # Search via primary key (id)
    row: BrandRecord | None = get_brand(id)

    # validate selected row. 
    if row is None: 
        raise ApiError(code="brand_not_found", status=400, detail=f"Failed to find brand of id {id}")
    else: 
        return Brand.model_validate(row) 
    

def create_brand(body: dict) -> Brand:
    """ createa a new brand with input body text. """
    
    # Validate input
    new_brand: BrandDto = BrandDto.model_validate(body)

    # Create SQLAlchemy object
    record: BrandRecord = BrandRecord(**new_brand.model_dump())

    # Add record to database. 
    add_record(record)

    return Brand.model_validate(record)

def populate_brands():
    """ Populate our brands table using the data.py file with predetermined entries"""
    # Reset the table.
    clear_brands()

    brand_list: list[Brand] = []

    # Loop through data.py, and create Brand objects for each brand. 
    for brand in BRANDS:
        # Validate brand
        new_brand : BrandDto = BrandDto.model_validate(brand)

        # Create a new record. 
        record : BrandRecord = BrandRecord(**new_brand.model_dump())

        # add record, and add it to change queue. 
        add_and_flush_record(record)

        # add to list. 
        brand_list.append(Brand.model_validate(record))

    #commit changes. 
    commit_changes()

    return brand_list




def update_brand_by_id(input_id: int, body: dict) -> Brand | None:
    """ Update an existing brand via brand id with our body input. """
    # validate input. 
    valid_brand : BrandDto = BrandDto.model_validate(body)

    # find record via primary key. 
    record : BrandRecord | None = get_brand(input_id)

    # Return None if Brand is not found 
    if record is None:
        raise ApiError(code="brand_not_found", status=400, detail=(input_id))

    # Apply changes. 
    record.name = valid_brand.name
    record.industry = valid_brand.industry

    # commit changes. 
    commit_changes()

    return Brand.model_validate(record)

def delete_brand(input_id: int) -> bool:
    """ delete a particular brand via brand id. """
    
    # Find the record via primary key. 
    record : BrandRecord | None = get_brand(input_id)
    # Return False if no record is found. 
    if record is None: 
        return False

    delete_record(record)
    
    return True
