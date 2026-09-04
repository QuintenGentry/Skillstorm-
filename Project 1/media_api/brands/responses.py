""" Convert brand objects into json objects. """

from media_api.brands.models import Brand
from flask import jsonify, Response

# Converts a list of Post Objects into a json Object
def list_envelope(brands: list[Brand]) -> Response:
    """ Convert a brand list into a json object. """
    return jsonify(count=len(brands), items=[b.model_dump(mode="json") for b in brands])

# Converts a Post Object into a json Object
def single_envelope(brands: Brand) -> Response:
    """ convert a brand object into a json object. """
    return jsonify(brands.model_dump(mode="json"))
