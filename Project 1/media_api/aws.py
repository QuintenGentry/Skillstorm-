"""
Handles aws connection. 
"""

import boto3
from functools import lru_cache
from media_api.config import AWS_PROFILE, AWS_REGION


@lru_cache(maxsize=1) # cache our aws session
def get_session() -> boto3.Session:
    """ Obtained shared aws session for the application. """
    return boto3.Session(profile_name=AWS_PROFILE, region_name=AWS_REGION)

@lru_cache(maxsize=None)
def get_client(service_name: str):
    """ Obtain boto3 client for our aws service. """
    return get_session().client(service_name)