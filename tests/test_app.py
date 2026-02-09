import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)

@pytest.fixture(autouse=True)
def reset_activities():
    # Backup and restore the in-memory activities to keep tests isolated
    orig = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = orig


import copy
import pytest
from fastapi.testclient import TestClient

from src import app as app_module

client = TestClient(app_module.app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Backup and restore the in-memory activities to keep tests isolated
    orig = copy.deepcopy(app_module.activities)
    yield
    app_module.activities = orig


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # sample check
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]


def test_signup_and_unregister():
    activity = "Tennis Club"
    email = "testuser@example.com"

    # ensure not present
    resp = client.get("/activities")
    assert resp.status_code == 200
    assert email not in resp.json()[activity]["participants"]

    # sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"]

    # confirm present
    resp = client.get("/activities")
    assert email in resp.json()[activity]["participants"]

    # unregister
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # confirm removed
    resp = client.get("/activities")
    assert email not in resp.json()[activity]["participants"]


def test_duplicate_signup_rejected():
    activity = "Drama Club"
    email = "duplicate@example.com"

    # first signup ok
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200

    # duplicate should be rejected
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "").lower()


def test_unregister_nonexistent():
    activity = "Chess Club"
    email = "nonexistent@example.com"

    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 404