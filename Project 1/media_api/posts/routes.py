""" Handle postman queries. """

from flask import Blueprint, jsonify, request, Response
from media_api.posts.services import list_posts, find_post_by_id, create_post, update_post, delete_post, populate_posts, update_post_image, update_compliance
from media_api.posts.responses import list_envelope, single_envelope
from media_api.upload import read_upload
from media_api.aws_ai.service import ALLOWED_EXTENSIONS, MAX_IMAGE_BYTES

UPLOAD_FILE = "file"

post_bp = Blueprint("posts", __name__)

@post_bp.get("")
def get_posts() -> Response:
    """ Recieve all posts """
    return list_envelope(list_posts())

@post_bp.get("/<id>")
def get_post_by_id(id: int) -> Response:
    """ return particular post via id. """
    post = find_post_by_id(id)

    if post is None:
        return jsonify(error="not_found", detail = f"failed to find post of id {id}"), 404

    return single_envelope(post)

@post_bp.post("")
def create_new_post() -> Response:
    """ Create a new post with input body from postman. """
    body = request.get_json(silent = True) or {}
    return single_envelope(create_post(body)), 201

@post_bp.post("/populate")
def populate_db_with_data() -> Response:
    """ populate Post table with data.py information. """
    return list_envelope(populate_posts())

@post_bp.put("/<id>")
def update_existing_post(id: str) -> Response:
    """ update an exitsing post with postman body input. """
    body = request.get_json(silent = True) or {}

    update_status = update_post(id, body) # Return None, or the updated Post Object

    if update_status is None: 
        return jsonify(status=f"Post with id of {id} not found"), 404
    else:
        return single_envelope(update_status), 200

@post_bp.put("/review/<id>")
def review_post(id: str) -> Response:
    """ update complaince status of an input post. """
    compliance_status : str = request.args.get("compliance_status")

    update_status = update_compliance(id, compliance_status)

    if update_status is None: 
        return jsonify(status=f"Post with id of {id} not found"), 404
    else:
        return single_envelope(update_status), 200

@post_bp.put("/image/<id>")
def insert_image(id: str) -> Response:
    """ insert an image via pydanic file input, and assign it to input post. """
    id = int(id)    
    post = find_post_by_id(id)

    if post is None:
        return jsonify(error="not_found", detail = f"failed to find post of id {id}"), 404


    attachment_bytes: bytes
    file_name: str
    attachment_bytes, file_name = read_upload(
        request.files.get(UPLOAD_FILE),
        allowed_extensions=ALLOWED_EXTENSIONS,
        max_bytes=MAX_IMAGE_BYTES
    )
    

    update_status: bool =  update_post_image(id, attachment_bytes, file_name) # Return None, or the updated Post Object

    if update_status: 
        return jsonify(status=f"Successfully Inserted Image"), 200
    else: 
        return jsonify(status=f"Image was flagged for inappropriate content, update was refused."), 400

@post_bp.delete("/<id>")
def delete_post_by_id(id: str) -> Response:
    """ delete post via input id. """
    # Get confirmation input: 
    confirmation_str = request.args.get("delete_confirmation")
    generate_str = f"delete_{id}"

    # Check if input is correct. 
    if confirmation_str != generate_str:
        return jsonify(status=f"Please enter confirmation string of 'delete_{id}'"), 400

    delete_status = delete_post(id)

    if delete_status == True:
        return jsonify(status=""), 204
    return jsonify(status=f"Post with id of {id} not found."), 404