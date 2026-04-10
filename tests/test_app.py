from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)
original_activities = deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(deepcopy(original_activities))
    yield
    activities.clear()
    activities.update(deepcopy(original_activities))


def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"].endswith("/static/index.html")


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert isinstance(response.json()["Chess Club"], dict)


def test_signup_for_activity():
    email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity():
    response = client.post("/activities/Nonexistent/signup", params={"email": "a@b.com"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_student():
    existing_email = "michael@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": existing_email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity():
    email = "daniel@mergington.edu"
    response = client.delete("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_registered_student():
    email = "unknown@mergington.edu"
    response = client.delete("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 400
    assert response.json()["detail"] == "Student not registered for this activity"
