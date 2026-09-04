""" Handles business logic """

from media_api.posts.data import POSTS
from media_api.posts.models import Post, PostDto
from media_api.posts.responses import list_envelope
from flask import jsonify, Response

from sqlalchemy import select, ScalarResult
from sqlalchemy.sql import Select
from media_api.db_files.db_models import PostRecord
from media_api.posts.store import get_all_posts, get_post, add_record, clear_posts, commit_changes, add_and_flush_record, delete_record
from media_api.aws_ai.service import get_sentiment, get_PII_status, get_image_moderation, insert_into_bucket

def determine_compliance(input_post: dict) -> dict:
    """ Utilize Comprehend to determine compliance status. """
    # get sentiment of caption (if there is one).
    sentiment: str = get_sentiment(input_post["caption_text"])

    # if sentiment is negative, revert status to pending. 
    if sentiment == "NEGATIVE":
        input_post["compliance_status"] = 'pending'


    # Get PII status
    PII_status: bool = get_PII_status(input_post["caption_text"])

    # if PII found, set status to blocked. 
    if PII_status:
        input_post["compliance_status"] = 'blocked'

    return input_post


def list_posts() -> list[Post]:
    """ return all posts. """

    # Select all posts, and order by id. 
    stmt : Select[PostRecord] = select(PostRecord).order_by(PostRecord.id)

    # Execute query. 
    rows : ScalarResult[PostRecord] = get_all_posts(stmt)


    #Validate and return Post objects. 
    return [Post.model_validate(row) for row in rows]

def find_post_by_id(id: int) -> Post | None:
    """ return post based off of input id. """

    # Get post via primary key. 
    row: PostRecord | None = get_post(id)

    if row is None:
        return None
    else:
        return Post.model_validate(row)


def list_posts_of_brand(brand: int, compliance_status: str | None, platform: str | None) -> Response:
    """ Select all posts of a particular input brand, also filter via compliance status and platform type. """

    compliance_restriction : str = "None"
    platform_restriciton : str = "None"


    post_list: list[Post] = []  

    # Get all posts:
    all_posts: list[Post] = list_posts()

    for post in all_posts: 
        if post.brand_id == brand:
            post_list.append(post)

    compliance_list : list[Post] = []

    # filter for compliance
    if compliance_status is not None: 
        for post in post_list:
            if post.compliance_status == compliance_status:
                compliance_list.append(post)
        post_list = compliance_list
        compliance_restriction = f"compliance status = {compliance_status}"

    platform_list : list[Post] = []

    # filter for platform
    if platform is not None: 
        for post in post_list:
            if post.platform == platform:
                platform_list.append(post)
        post_list = platform_list
        platform_restriciton = f"platform = {platform}"

    if len(post_list) == 0:
        return jsonify(status=f"No posts found under brand '{brand}' with restrictions of {compliance_restriction} and {platform_restriciton}")
    else: 
        return list_envelope(post_list)


def create_post(input_post: dict) -> Post:
    """ create a new post, and validate it. """
    
    # Check for PII and sentiment. 
    input_post: dict = determine_compliance(input_post)


    #validate inputs. 
    valid_post: PostDto = PostDto.model_validate(input_post)

    # create PostRecord
    record : PostRecord = PostRecord(**valid_post.model_dump())

    add_record(record)

    return Post.model_validate(record)


def populate_posts():
    """ clear current post table, and populate it with pre-made inputs from data.py """
    
    #clear current posts. 
    clear_posts()

    post_list: list[Post] = []

    # Loop post data.py, and create Brand objects for each brand. 
    for post in POSTS:

        # Validate brand
        new_post : PostDto = PostDto.model_validate(post)

        # Create a new record. 
        record : PostRecord  = PostRecord(**new_post.model_dump())

        # add a new record. 
        add_and_flush_record(record)

        # add to list. 
        post_list.append(Post.model_validate(record))

    #commit changes. 
    commit_changes()

    return post_list


def update_post(post_id: int, input_post: dict) -> Post | None:
    """ Update a current post, and validate the inputs. """
    
    # Check for PII and sentiment. 
    input_post: dict = determine_compliance(input_post)

    # Validate inputs. 
    valid_post : PostDto = PostDto.model_validate(input_post)

    #Find record via id. 
    record : PostRecord | None = get_post(post_id)

    # Check if not found. 
    if record is None:
        return None

    # Set values to record. 
    record.platform = valid_post.platform
    record.caption_text = valid_post.caption_text
    record.image = valid_post.image
    record.scheduled_publish_time = valid_post.scheduled_publish_time
    record.compliance_status = valid_post.compliance_status
    record.brand_id = valid_post.brand_id

    # COmmit changes. 
    commit_changes()

    return Post.model_validate(record)

def update_post_image(post_id: int, attachment_bytes: bytes, file_name: str) -> bool:
    """ update current post image, and add it to S3 bucket. """
    
    # Detect moderation. 
    image_moderation = get_image_moderation(attachment_bytes)

    # Check if there is any image moderation. 
    if len(image_moderation) == 0:  #moderation will be 0 if nothing is found. 
        record : PostRecord | None = get_post(post_id)
        record.image = file_name
        commit_changes()

        # store image into s3 bucket. s
        insert_into_bucket(attachment_bytes, file_name)

        return True
    else: 
        return False

def update_compliance(post_id : int, compliance_status : str) -> Post | None:
    """ Update input post compliance status. """
    
    # Get post to update. 
    record : PostRecord | None = get_post(post_id)

    if record is None:
        return None

    # update complaince status
    record.compliance_status = compliance_status
    commit_changes()

    return Post.model_validate(record)


def delete_post(post_id: str) -> bool:
    """ delete input post, and return success. """

    record : PostRecord | None = get_post(post_id)

    # return false if none found. 
    if record is None:
        return False

    delete_record(record)
    return True
