import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

# Helper: get a valid activity name and a test email
def get_sample_activity():
    resp = client.get("/activities")
    data = resp.json()
    for name in data:
        return name, data[name]["participants"]
    return None, []

def test_get_activities():
    # Arrange
    # (No setup needed)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert len(response.json()) > 0

def test_signup_success():
    # Arrange
    activity, _ = get_sample_activity()
    test_email = "testuser1@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert response.status_code == 200
    assert f"Signed up {test_email}" in response.json()["message"]

def test_signup_duplicate():
    # Arrange
    activity, participants = get_sample_activity()
    if not participants:
        # Register a user first
        test_email = "testuser2@mergington.edu"
        client.post(f"/activities/{activity}/signup?email={test_email}")
    else:
        test_email = participants[0]
    # Act
    response = client.post(f"/activities/{activity}/signup?email={test_email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    # Arrange
    test_email = "testuser3@mergington.edu"
    # Act
    response = client.post(f"/activities/NonexistentActivity/signup?email={test_email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_remove_participant_success():
    # Arrange
    activity, _ = get_sample_activity()
    test_email = "testuser4@mergington.edu"
    # Ensure user is signed up
    client.post(f"/activities/{activity}/signup?email={test_email}")
    # Act
    response = client.delete(f"/activities/{activity}/participants/{test_email}")
    # Assert
    assert response.status_code == 200
    assert f"Removed {test_email}" in response.json()["message"]

def test_remove_participant_not_found():
    # Arrange
    activity, _ = get_sample_activity()
    test_email = "notfound@mergington.edu"
    # Act
    response = client.delete(f"/activities/{activity}/participants/{test_email}")
    # Assert
    assert response.status_code == 404
    assert "Participant not found" in response.json()["detail"]
