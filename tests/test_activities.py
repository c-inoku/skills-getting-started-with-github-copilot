import sys
import uuid
from pathlib import Path
from urllib.parse import quote

from fastapi.testclient import TestClient

# Ensure we can import the application module from the src/ directory
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app import app


client = TestClient(app)


def unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # basic sanity: at least one known activity exists
    assert "Chess Club" in data


def test_signup_and_reflect():
    email = unique_email()
    activity = "Chess Club"
    activity_path = quote(activity, safe="")

    # Sign up
    resp = client.post(f"/activities/{activity_path}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Confirm the participant shows up in the activity list
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    participants = resp2.json()[activity]["participants"]
    assert email in participants


def test_unregister_participant():
    email = unique_email()
    activity = "Chess Club"
    activity_path = quote(activity, safe="")

    # Ensure the user is signed up first
    resp = client.post(f"/activities/{activity_path}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 200

    # Now unregister
    resp = client.delete(f"/activities/{activity_path}/participants?email={quote(email, safe='')}")
    assert resp.status_code == 200
    body = resp.json()
    assert "Unregistered" in body.get("message", "")

    # Confirm removal
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    participants = resp2.json()[activity]["participants"]
    assert email not in participants
