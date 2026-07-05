import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture(autouse=True)
def reset_activity_state():
    original_state = {
        name: list(details["participants"])
        for name, details in app_module.activities.items()
    }
    yield
    for name, participants in original_state.items():
        app_module.activities[name]["participants"] = participants


def test_unregister_participant_removes_them_from_activity():
    client = TestClient(app_module.app)
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    assert email in activities_response.json()[activity_name]["participants"]

    delete_response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )
    assert delete_response.status_code == 200

    updated_response = client.get("/activities")
    assert updated_response.status_code == 200
    assert email not in updated_response.json()[activity_name]["participants"]
