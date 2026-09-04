""" 
Handles the conversion of post pydantic objects into json objects. 
"""
from media_api.posts.models import Post
from flask import jsonify, Response

# Converts a list of Post Objects into a json Object
def list_envelope(posts: list[Post]) -> Response:
    """ convert a post list into a json object.  """
    return jsonify(count=len(posts), items=[p.model_dump(mode="json") for p in posts])

# Converts a Post Object into a json Object
def single_envelope(post: Post) -> Response:
    """ COnvert a post object into a json object. """
    return jsonify(post.model_dump(mode="json"))

