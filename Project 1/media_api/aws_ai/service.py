"""
aws comprehend and rekognition features to help aid our application. 
"""

from media_api.aws import get_client
from media_api.config import BUCKET_NAME

# Restrict to 5 MBs
MAX_IMAGE_BYTES = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"jpg", "png"}

def get_image_moderation(image_bytes: bytes) -> list[str]: 
    """ Return a list of image moderation entires, if there exist any. """
    try: 
        # Obtain rekognition moderation labels. 
        response = get_client("rekognition").detect_moderation_labels(
            Image={"Bytes": image_bytes}
        )

        # THis extracts the obtained labels, it will extract an empty list otherwise. 
        labels = response.get("ModerationLabels", [])

        return [label["Name"] for label in labels]
    except Exception as e:
        print(e)
        return []

def insert_into_bucket(image_bytes: bytes, image_name: str) -> None: 
    """ insert input image into a S3 aws bucket. """
    
    image_key = f"images/{image_name}"
    get_client("s3").put_object(Bucket=BUCKET_NAME, Key=image_key, Body=image_bytes)



def get_sentiment(text: str) -> str:
    """ determine the sentiment of an input text string. """
    
    # Detect sentiment of text. 

    try: # check status of comprehend. 
        response = get_client("comprehend").detect_sentiment(
            Text=text,
            LanguageCode="en"
        )
        # Return resulting sentiment. 
        return response["Sentiment"]
    except Exception as e:
        # return negative sentiment by default, forcing the compliance status to become pending.  
        print(e)
        return "NEGATIVE"


def get_PII_status(text: str) -> bool:
    # Detect presence of PII. 

    try: # check status of comprehend. 
        response = get_client("comprehend").detect_pii_entities(
            Text=text,
            LanguageCode="en"
        )
        # If any entities are found, the length will not be 0
        if len(response["Entities"]) == 0:
            return False
        else: 
            return True
        
    except Exception as e:
        # REturn positive PII status if comprehend is down, to ensure failure. 
        print(e)
        return True