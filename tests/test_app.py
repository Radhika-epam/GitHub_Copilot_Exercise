"""
FastAPI backend tests for src/app.py using the AAA pattern.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset in-memory activity state before each test."""
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_all_activities(self, client):
        # Arrange
        expected_names = set(INITIAL_ACTIVITIES.keys())

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert set(data.keys()) == expected_names
        assert isinstance(data["Chess Club"]["participants"], list)

    def test_get_activities_returns_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity in data.values():
            assert required_fields.issubset(set(activity.keys()))


class TestSignupEndpoint:
    def test_signup_for_activity_success(self, client):
        # Arrange
        activity_name = "Swimming Club"
        email = "newstudent@mergington.edu"
        assert email not in activities[activity_name]["participants"]

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    def test_signup_duplicate_email_returns_400(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
        assert activities[activity_name]["participants"].count(email) == 1


class TestUnregisterEndpoint:
    def test_unregister_from_activity_success(self, client):
        # Arrange
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"
        assert email in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email not in activities[activity_name]["participants"]
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    def test_unregister_non_registered_participant_returns_400(self, client):
        # Arrange
        activity_name = "Swimming Club"
        email = "notregistered@mergington.edu"
        assert email not in activities[activity_name]["participants"]

        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400
        assert response.json()["detail"] == "Student not registered for this activity"
