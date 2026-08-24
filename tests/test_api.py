from fastapi.testclient import TestClient

from app.main import app
from app.services.media_store import media_store


client = TestClient(app)


def test_health_and_image_generation():
    assert client.get("/health").json() == {"status": "ok"}
    response = client.post("/api/media/image/generate", json={"project_id": "p1", "scene_id": "s1", "scene_description": "desc", "image_prompt": "a blue room"})
    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"


def test_video_rejects_missing_approved_assets():
    media_store.set_project_approval("missing", script_approved=True, scenes_approved=True)
    response = client.post("/api/videos/create", json={"project_id": "missing", "scene_ids": ["s1"]})
    assert response.status_code == 400
    assert "approved image" in response.json()["detail"]