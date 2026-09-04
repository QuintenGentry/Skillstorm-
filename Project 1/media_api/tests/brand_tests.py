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
        client.post("/api/v1/Project1/brands/populate")
        client.post("/api/v1/Project1/posts/populate")
        yield client


def test_populate_db_with_data(client):
    """ Test our population function. """
    response = client.post("/api/v1/Project1/brands/populate")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 5

def test_live_status(client):
    """ Test our live function, testing if our application is operational.  """
    response = client.get("/api/v1/Project1/brands/live")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "ok"

def test_ready_status(client):
    """ Test our ready function, testing if our database is operational.   """
    response = client.get("/api/v1/Project1/brands/ready")
    data = response.get_json()

    assert response.status_code == 200
    assert data["status"] == "ok"

def test_get_brands(client):
    """ Test our live function, testing if our function is operational.  """
    response = client.get("/api/v1/Project1/brands")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 5

def test_view_brands(client):
    """ Test our live function, testing if our function is operational.  """
    response = client.get("/api/v1/Project1/brands/posts_total")
    data = response.get_json()

    assert response.status_code == 200


    brand = data["Brand: 1"]

    assert brand["id"] == 1
    assert brand["industry"] == "Construction"
    assert brand["name"] == "Mitten Alloy Industries"

    posts = brand["posts"]

    assert posts["blocked_posts"] == 2
    assert posts["pending_posts"] == 1
    assert posts["total_posts"] == 3

def test_brand_by_id(client):
    """ test if we can get a particular brand via id """
    response = client.get("/api/v1/Project1/brands/1")
    data = response.get_json()

    assert response.status_code == 200

    assert data["id"] == 1
    assert data["industry"] == "Construction"

def test_get_posts_of_brand_complaince_platform(client):
    """ test if we can get particular post sof a brand with compliance and platform filters """
    response = client.get(
        "/api/v1/Project1/brands/posts",
        query_string={
            "id": 1,
            "compliance_status": "blocked",
            "platform": "twitter"
        }
    )
    data = response.get_json()

    assert response.status_code == 200

    assert data["count"] == 1

def test_get_posts_of_brand_complaince(client):
    """ test if we can get particular post sof a brand with compliance filters """
    response = client.get(
        "/api/v1/Project1/brands/posts",
        query_string={
            "id": 1,
            "compliance_status": "blocked"
        }
    )
    data = response.get_json()

    assert response.status_code == 200

    assert data["count"] == 2

def test_get_posts_of_brand_complaince_platform(client):
    """ test if we can get particular post sof a brand with platform filters """
    response = client.get(
        "/api/v1/Project1/brands/posts",
        query_string={
            "id": 1,
            "platform": "twitter"
        }
    )
    data = response.get_json()

    assert response.status_code == 200

    assert data["count"] == 1

def test_create_new_brand(client):
    """ Test our ability to make new brands. """
    payload = {
        "industry": "Construction",
        "name": "Unobstructed Table Edges Factory"
    }

    response = client.post("/api/v1/Project1/brands", json=payload)
    data = response.get_json()

    assert response.status_code == 201

    assert data["id"] == 6

def test_update_existing_brand(client):
    """ Test our ability to update existing brands. """
    payload = {
        "industry": "Technology",
        "name": "Unobstructed Table Edges Factory"
    }

    # Test success. 
    response = client.put("/api/v1/Project1/brands/3", json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert data["id"] == 3 and data["industry"] == "Technology"

def test_delete_brand_by_id(client): 
    """ Test deleting a brand with input id and postman query string. """
    response = client.delete(
        "/api/v1/Project1/brands/1",
        query_string={"delete_confirmation": "delete_1"}
    )

    assert response.status_code == 204

def test_delete_brand_by_id_invalid_id(client): 
    """ Test deleting a brand with an invalid input id and postman query string. """
    response = client.delete(
        "/api/v1/Project1/brands/10",
        query_string={"delete_confirmation": "delete_10"}
    )

    assert response.status_code == 404