"""
Backend API tests for the Mergington High School Activities app.

Tests follow the Arrange-Act-Assert (AAA) pattern throughout.
"""


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

class TestRootRedirect:
    def test_redirects_to_static_index(self, client):
        # Arrange – no setup required; hit the root path

        # Act
        response = client.get("/")

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

class TestGetActivities:
    def test_returns_200(self, client):
        # Arrange – activities are pre-populated from the app's in-memory store

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_response_is_dict(self, client):
        # Arrange
        # (no extra setup needed)

        # Act
        response = client.get("/activities")

        # Assert
        data = response.json()
        assert isinstance(data, dict)

    def test_each_activity_has_required_fields(self, client):
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}

        # Act
        response = client.get("/activities")

        # Assert
        for name, details in response.json().items():
            assert required_fields.issubset(details.keys()), (
                f"Activity '{name}' is missing one of {required_fields}"
            )

    def test_participants_is_a_list(self, client):
        # Arrange
        # (no extra setup needed)

        # Act
        response = client.get("/activities")

        # Assert
        for name, details in response.json().items():
            assert isinstance(details["participants"], list), (
                f"Activity '{name}' participants should be a list"
            )


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

class TestSignupForActivity:
    def test_signup_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_signup_adds_participant_to_activity(self, client):
        # Arrange
        activity = "Chess Club"
        email = "newstudent@mergington.edu"

        # Act
        client.post(f"/activities/{activity}/signup", params={"email": email})
        participants = client.get("/activities").json()[activity]["participants"]

        # Assert
        assert email in participants

    def test_signup_unknown_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_duplicate_signup_returns_400(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"   # already a participant in seed data

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 400

    def test_signup_full_activity_returns_400(self, client):
        # Arrange
        activity = "Chess Club"

        # Fetch current activity data to determine capacity
        activities = client.get("/activities").json()
        details = activities[activity]
        max_participants = details["max_participants"]
        current_count = len(details["participants"])
        remaining_slots = max_participants - current_count

        # Fill the activity to its max_participants limit
        for i in range(remaining_slots):
            email = f"capacity_filler_{i}@mergington.edu"
            fill_response = client.post(
                f"/activities/{activity}/signup",
                params={"email": email},
            )
            assert fill_response.status_code == 200

        # Act – attempt one more signup beyond capacity
        extra_email = "extra_student@mergington.edu"
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": extra_email},
        )

        # Assert
        assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/participants
# ---------------------------------------------------------------------------

class TestUnregisterFromActivity:
    def test_unregister_success(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"   # exists in seed data

        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 200
        assert email in response.json()["message"]

    def test_unregister_removes_participant_from_activity(self, client):
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"

        # Act
        client.delete(f"/activities/{activity}/participants", params={"email": email})
        participants = client.get("/activities").json()[activity]["participants"]

        # Assert
        assert email not in participants

    def test_unregister_unknown_activity_returns_404(self, client):
        # Arrange
        activity = "Nonexistent Club"
        email = "michael@mergington.edu"

        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404

    def test_unregister_nonexistent_participant_returns_404(self, client):
        # Arrange
        activity = "Chess Club"
        email = "ghost@mergington.edu"   # not signed up

        # Act
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email},
        )

        # Assert
        assert response.status_code == 404
