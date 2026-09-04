import pytest
from media_api.app import create_app
import io
import os


# Allow us to run an app for testing. 
@pytest.fixture
def app():
    app = create_app()
    return app

# allow us to run client functions with just 'client'
@pytest.fixture
def client(app):
    with app.test_client() as client:
        # reset the table when calling client. 
        client.post("/api/v1/Project1/posts/populate")
        yield client


def test_populate_db_with_data(client):
    """ Test our population function. """
    response = client.post("/api/v1/Project1/posts/populate")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 6

def test_get_posts(client):
    """ Test get all posts """
    response = client.get("/api/v1/Project1/posts")
    data = response.get_json()

    assert response.status_code == 200

    assert data["count"] == 6

def test_get_post_by_id(client):
    """ test getting a single post. """
    response = client.get("/api/v1/Project1/posts/1")
    data = response.get_json()

    assert response.status_code == 200

    assert data["brand_id"] == 1

def test_get_post_by_id_not_found(client):
    """ test if input id is not found """
    response = client.get("/api/v1/Project1/posts/10")
    data = response.get_json()

    assert response.status_code == 404
    assert data["error"] == "not_found"

def test_create_new_post(client):
    """ Test our ability to make new posts. """
    payload = {
        "brand_id": 3,
        "caption_text": "This situation is a mess. We missed important steps, things broke that shouldn't have, and now everyone is dealing with the fallout. We have to fix this, because it's not acceptable.",
        "platform": "twitter",
        "scheduled_publish_time": "2026-08-28T14:30:00",
        "compliance_status": "approved"
    }

    response = client.post("/api/v1/Project1/posts", json=payload)
    data = response.get_json()

    assert response.status_code == 201

    assert data["id"] == 7

def test_create_new_post_blocked_compliance_PII(client):
    """ Test our ability to make new posts. """
    payload = {
        "brand_id": 3,
        "caption_text": "This situation is a mess. Jerry Tom missed important steps, things broke that shouldn't have, and now everyone is dealing with the fallout. We have to fix this, because it's not acceptable. Call 364-433-4893 immeidately.",
        "platform": "twitter",
        "scheduled_publish_time": "2026-08-28T14:30:00",
        "compliance_status": "approved"
    }

    response = client.post("/api/v1/Project1/posts", json=payload)
    data = response.get_json()

    assert response.status_code == 201

    assert data["id"] == 7 and data["compliance_status"] == "blocked"

def test_update_existing_post(client):
    """ Test our ability to update existing posts. """
    payload = {
        "brand_id": 1,
        "caption_text": "Our audit identified several records containing invalid personal data, including entries such asand email:  These inaccuracies compromise data integrity, and we are initiating corrective actions to prevent further issues.",
        "compliance_status": "pending",
        "image": "image1.png",
        "platform": "twitter",
        "scheduled_publish_time": "2026-08-28T14:30:00"
    }

    # Test success. 
    response = client.put("/api/v1/Project1/posts/2", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == 2 and data["compliance_status"] == "pending" and data["platform"] == "twitter"

def test_update_existing_post_compliance_blocked_PII(client):
    """ Test our ability to update existing posts. """
    payload = {
        "brand_id": 1,
        "caption_text": "Jerry Tom audit identified several records containing invalid personal data, including entries such asand email:  These inaccuracies compromise data integrity, and we are initiating corrective actions to prevent further issues.",
        "compliance_status": "approved",
        "image": "image1.png",
        "platform": "twitter",
        "scheduled_publish_time": "2026-08-28T14:30:00"
    }

    # Test success. 
    response = client.put("/api/v1/Project1/posts/2", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == 2 and data["compliance_status"] == "blocked"

def test_update_existing_post_compliance_pending_sentiment(client):
    """ Test our ability to update existing posts. """
    payload = {
        "brand_id": 1,
        "caption_text": "Everything is a compete disaster, I'm going to fire everyone!!!",
        "compliance_status": "approved",
        "image": "image1.png",
        "platform": "twitter",
        "scheduled_publish_time": "2026-08-28T14:30:00"
    }

    # Test success. 
    response = client.put("/api/v1/Project1/posts/2", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == 2 and data["compliance_status"] == "pending"

def test_update_existing_post_not_found(client):
    """ Test if input id is not found. """
    payload = {
        "brand_id": 1,
        "caption_text": "Our audit identified several records containing invalid personal data, including entries such asand email:  These inaccuracies compromise data integrity, and we are initiating corrective actions to prevent further issues.",
        "compliance_status": "pending",
        "image": "image1.png",
        "platform": "twitter",
        "scheduled_publish_time": "2026-08-28T14:30:00"
    }

    # Test success. 
    response = client.put("/api/v1/Project1/posts/10", json=payload)
    data = response.get_json()

    assert response.status_code == 404
    assert data["status"] == "Post with id of 10 not found"

def test_review_post(client):
    """ Test our ability to update reviews of posts. """
    response = client.put(
        "/api/v1/Project1/posts/review/1",
        query_string={"compliance_status": "approved"}
    )
    data = response.get_json()

    assert response.status_code == 200

    assert data["id"] == 1 and data["compliance_status"] == "approved"

def test_review_post_not_found(client):
    """ Test review if post is not found.  """
    response = client.put(
        "/api/v1/Project1/posts/review/10",
        query_string={"compliance_status": "approved"}
    )
    data = response.get_json()


    assert response.status_code == 404
    assert data["status"] == "Post with id of 10 not found"

def test_upload_image(client):
    """ test valid image input"""

    # collect our image. 
    image_path = os.path.join(os.path.dirname(__file__), "assets", "Cats.jpg")

    with open(image_path, "rb") as f:
        image = {
            "file": (io.BytesIO(f.read()), "Cats.jpg")
        }

    response = client.put(
        "/api/v1/Project1/posts/image/1",   # your route
        content_type="multipart/form-data",
        data=image
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "Successfully Inserted Image"

def test_upload_image_file_too_large(client):
    """ test too large file """
    
    # collect our image. 
    image_path = os.path.join(os.path.dirname(__file__), "assets", "large_image.png")

    with open(image_path, "rb") as f:
        image = {
            "file": (io.BytesIO(f.read()), "large_image.png")
        }

    response = client.put(
        "/api/v1/Project1/posts/image/1",   # your route
        content_type="multipart/form-data",
        data=image
    )


    data = response.get_json()

    assert response.status_code == 422
    assert data["error"] == "payload_too_large"

def test_upload_image_invalid_file_extension(client):
    """ test invalid extension"""
    
    # collect our image. 
    image_path = os.path.join(os.path.dirname(__file__), "assets", "strawberry.jpeg")

    with open(image_path, "rb") as f:
        image = {
            "file": (io.BytesIO(f.read()), "strawberry.png")
        }

    response = client.put(
        "/api/v1/Project1/posts/image/1",   # your route
        content_type="multipart/form-data",
        data=image
    )


    data = response.get_json()

    assert response.status_code == 422
    assert data["error"] == "unsupported_media_type"

def test_upload_image_invalid_file_extension(client):
    """ rekognition detecting moderation labels. """
    
    # collect our image. 
    image_path = os.path.join(os.path.dirname(__file__), "assets", "rekognition_test_image.jpg")

    with open(image_path, "rb") as f:
        image = {
            "file": (io.BytesIO(f.read()), "rekognition_test_image.jpg")
        }

    response = client.put(
        "/api/v1/Project1/posts/image/1",   # your route
        content_type="multipart/form-data",
        data=image
    )


    data = response.get_json()

    assert response.status_code == 400
    assert data["status"] == "Image was flagged for inappropriate content, update was refused."

def test_delete_post_by_id(client): 
    """ Test deleting a post with input id and postman query string. """
    response = client.delete(
        "/api/v1/Project1/posts/1",
        query_string={"delete_confirmation": "delete_1"}
    )

    assert response.status_code == 204

def test_delete_post_by_id_invalid_id(client): 
    """ Test deleting a post with an invalid input id and postman query string. """
    response = client.delete(
        "/api/v1/Project1/posts/10",
        query_string={"delete_confirmation": "delete_10"}
    )

    assert response.status_code == 404




