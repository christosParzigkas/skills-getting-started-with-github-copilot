"""Tests for the Mergington High School Activities API using AAA pattern"""

from fastapi import status


class TestHealthCheck:
    """Tests for health check / root endpoint"""

    def test_root_redirect(self, client):
        # Arrange: client fixture provided
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_success(self, client):
        # Arrange
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert required_fields.issubset(activity_data.keys()), \
                f"Activity '{activity_name}' missing required fields"


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, valid_activity):
        # Arrange
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert email in data["message"]

        activities = client.get("/activities").json()
        assert email in activities[valid_activity]["participants"]

    def test_signup_duplicate_email(self, client, valid_activity, existing_email):
        # Arrange
        # Act
        response = client.post(
            f"/activities/{valid_activity}/signup",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity(self, client, sample_email, invalid_activity):
        # Arrange
        # Act
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_unregister_success(self, client, valid_activity, existing_email):
        # Arrange

        # Act
        response = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": existing_email}
        )

        # Assert
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

        activities = client.get("/activities").json()
        assert existing_email not in activities[valid_activity]["participants"]

    def test_unregister_nonexistent_activity(self, client, sample_email, invalid_activity):
        # Arrange
        # Act
        response = client.delete(
            f"/activities/{invalid_activity}/participants",
            params={"email": sample_email}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_participant_not_signed_up(self, client, valid_activity):
        # Arrange
        email = "notsignedupstudent@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{valid_activity}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Participant not found" in response.json()["detail"]
