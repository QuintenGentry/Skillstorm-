""" Used to handle our postman queries. """

from flask import Blueprint, jsonify, request, Response
from media_api.brands.services import list_brands, find_brand_by_id, create_brand, update_brand_by_id, delete_brand, populate_brands, list_brands_with_post_info, testReady
from media_api.brands.responses import single_envelope, list_envelope
from media_api.posts.services import list_posts_of_brand


brand_bp = Blueprint("brands", __name__)

@brand_bp.get("/live")
def live() -> Response:
    """ test if the app is up and running. """
    return jsonify(status = "ok"), 200

@brand_bp.get("/ready")
def ready() -> Response:
    """ test if the database is up and running. """
    test : bool = testReady()
    if test: 
        return jsonify(status = "ok"), 200
    else: 
        return jsonify(Status = "error"), 500

@brand_bp.get("")
def get_brands() -> Response:
    """ return all brands as a json object. """
    return list_envelope(list_brands())

@brand_bp.get("/posts_total")
def view_brands() -> Response:
    """ return all all brands with post information counters as a json object. """
    return jsonify(list_brands_with_post_info())

@brand_bp.get("/<id>")
def get_brand_by_id(id: str) -> Response:
    """ return a particular brand as a json object based on input id. """
    brand = find_brand_by_id(id)

    if brand is None:
        return jsonify(error="not_found", detail = id), 404
    return single_envelope(brand)


@brand_bp.get("/posts")
def get_posts_of_brand() -> Response:
    """ return all post of a particular input brand, with compliance status and platform filters. """
    
    id : str = request.args.get("id")
    id : int = int(id) # Cast input into an int, as for some reason it is a str. 
    compliance_status : str = request.args.get("compliance_status")
    platform : str = request.args.get("platform")

    return list_posts_of_brand(id, compliance_status, platform)

@brand_bp.post("")
def create_new_brand() -> Response:
    """ create a new brand with postman input body. """
    body = request.get_json(silent = True) or {}
    return single_envelope(create_brand(body)), 201

@brand_bp.post("/populate")
def populate_db_with_data() -> Response:
    """ populate the brands table with predetermined inputs. """
    return list_envelope(populate_brands())

@brand_bp.put("/<id>")
def update_brand(id: str) -> Response:
    """ Update a particular brand using input id and postman request body """
    body = request.get_json(silent = True) or {}
    return single_envelope(update_brand_by_id(id, body))

@brand_bp.delete("/<id>")
def delete_brand_by_id (id: str) -> Response: 
    """ delete aparticular brand via input id, and delete confirmation. """
    # Get conformation input:

    confirmation_str = request.args.get("delete_confirmation")

    generate_str = f"delete_{id}"

    if confirmation_str != generate_str:
        return jsonify(status=f"Please enter confirmation string of 'delete_{id}'"), 400

    success = delete_brand(id)

    if success: 
        return jsonify(status=""), 204
    return jsonify(status=f"Brand with id of {id} not found."), 404
