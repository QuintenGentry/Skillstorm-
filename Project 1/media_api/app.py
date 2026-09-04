"""
Handles errors, and runs the application. 
"""

from flask import Flask
from media_api.brands.routes import brand_bp
from media_api.posts.routes import post_bp
from media_api.health.routes import health_bp

from flask_migrate import Migrate
from media_api.db_files.extensions import db
import os

from media_api.error_responses import ApiError, error_response
from flask import Response
from pydantic import ValidationError
from botocore.exceptions import BotoCoreError, ClientError
from psycopg.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError

# Common AWS Errors and their codes
_CLIENT_FAULT_STATUS = {
    "AccessDeniedException": 403,
    "AccessDenied": 403,
    "UnrecognizedClientException": 403,
    "ValidationException": 422,
    "InvalidParameterException": 422,
    "InvalidParameterValueException": 422,
    "TextSizeLimitExceededException": 422,
    "InvalidRequestException": 422,
    "UnsupportedLanguagePairException": 422,
    "ThrottlingException": 429,
    "TooManyRequestsException": 429,
    "ResourceNotFoundException": 404,
}

migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.register_blueprint(brand_bp, url_prefix="/api/v1/Project1/brands")
    app.register_blueprint(post_bp, url_prefix="/api/v1/Project1/posts")
    app.register_blueprint(health_bp, url_prefix="/api/v1/Project1/health")


    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    db.init_app(app)
    migrate.init_app(app, db)

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError) -> Response:
        return error_response(error.code, error.status, error.detail)

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):

        first_error = error.errors()[0]
        detail_str = f"{first_error['loc']}: {first_error['msg']}"

        return error_response("validation_failed", 422, detail_str)

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        return error_response("integrity_error", 400, "Database constraint violated")

    @app.errorhandler(Exception)
    def handle_unhandled_exception(error: Exception):
        print(error)
        return error_response("internal", 500, "Something went wrong")

    @app.errorhandler(404)
    def handle_resource_not_found(error):
        return error_response("not_found", 404, "no route for the given path")



    # boto3 (AWS) error handling: 

    @app.errorhandler(ClientError)
    def handle_aws_client_error(error):

        # only extracting the code from aws so we don't reveal too much info to client
        aws_code = error.response.get("Error", {}).get("Code", "UnknownAwsError")
        status = _CLIENT_FAULT_STATUS.get(aws_code, 502)    # default to 502 - Bad Gateway error
        app.logger.exception("AWS call failed: %s", aws_code)
        return error_response("aws_error", status, aws_code)



    @app.errorhandler(BotoCoreError)
    def handle_botocore_error(error):
        app.logger.exception("AWS SDK/configuration error")
        return error_response("aws_configuration_error", 500, type(error).__name__)
    

    return app