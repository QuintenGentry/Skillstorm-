""" Used to load in the .env file. """
import os

from dotenv import load_dotenv

# pulls in .env file into app context
load_dotenv()

# save .env variables to variables in the app that we can import in other places
AWS_PROFILE = os.environ.get("AWS_PROFILE")

AWS_REGION = os.environ.get("AWS_REGION")

BUCKET_NAME = os.environ.get("MEDIA_AI_BUCKET_NAME")
