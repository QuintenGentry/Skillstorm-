""" Used to verify health of identity request. """

from flask import Blueprint, jsonify

from media_api.health import service
from media_api.error_responses import error_response


health_bp = Blueprint("health", __name__)


@health_bp.get("")
def health():
    """ Verify health of identity request. """
    try:
        identity = service.whoami()
    except Exception:
        return error_response("unhealthy", 503, "Cannot Authenticate to AWS.")

    return jsonify(staus="ok", aws=identity)
