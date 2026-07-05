import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activity_state():
    # Arrange: capture the original participant state before each test.
    original_state = {
        name: list(details["participants"])
        for name, details in app_module.activities.items()
    }

    yield

    # Teardown: restore the original state after each test.
    for name, participants in original_state.items():
        app_module.activities[name]["participants"] = participants


def test_unregister_participant_removes_them_from_activity():
    # Arrange
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act: sign the student up for the activity.
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert: signup succeeded.
    assert signup_response.status_code == 200

    # Act: fetch the activity list and then unregister the student.
    activities_response = client.get("/activities")
    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert: the participant was removed from the activity.
    assert activities_response.status_code == 200
    assert email in activities_response.json()[activity_name]["participants"]
    assert delete_response.status_code == 200

    updated_response = client.get("/activities")
    assert updated_response.status_code == 200
    assert email not in updated_response.json()[activity_name]["participants"]
