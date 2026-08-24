from fastapi.testclient import TestClient

from app.main import app
from app.services.store import store

client = TestClient(app)


def setup_function() -> None:
    store.scripts.clear()
    store.scenes.clear()


def test_generate_script_returns_structured_json() -> None:
    response = client.post("/api/scripts/generate", json={"project_id": "p1", "idea": "A baker finds a hidden map."})
    assert response.status_code == 201
    body = response.json()
    assert body["state"] == "SCRIPT_GENERATED"
    assert body["characters"][0]["name"] == "Alex"
    assert isinstance(body["estimated_duration"], (int, float))


def test_scenes_require_script_approval() -> None:
    generated = client.post("/api/scripts/generate", json={"project_id": "p2", "idea": "A quiet discovery."}).json()
    response = client.post("/api/scenes/generate", json={"project_id": "p2", "script_id": generated["id"]})
    assert response.status_code == 409
    assert "required SCRIPT_APPROVED" in response.json()["detail"]


def test_approval_workflow_reaches_scenes_approved() -> None:
    generated = client.post("/api/scripts/generate", json={"project_id": "p3", "idea": "A new beginning."}).json()
    assert client.post(f"/api/scripts/{generated['id']}/approve").status_code == 200
    scenes = client.post("/api/scenes/generate", json={"project_id": "p3", "script_id": generated["id"]}).json()
    approved = client.post(f"/api/scenes/{scenes[0]['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["state"] == "SCENES_APPROVED"
    assert store.get_script(generated["id"]).state == "SCENES_APPROVED"
