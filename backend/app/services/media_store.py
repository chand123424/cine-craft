import json
import os
from pathlib import Path
from typing import Any

from app.services.approval import InMemoryApprovalProvider


class MediaStore:
    def __init__(self) -> None:
        self.root = os.getenv("MEDIA_ROOT", "media")
        Path(self.root).mkdir(parents=True, exist_ok=True)
        self.assets: dict[str, dict[str, Any]] = {}
        self.videos: dict[str, dict[str, Any]] = {}
        self.approvals = InMemoryApprovalProvider()

    def set_project_approval(self, project_id: str, script_approved: bool, scenes_approved: bool) -> None:
        """Integration seam for the project service that owns script and scene approval."""
        self.approvals.set(project_id, script_approved, scenes_approved)

    def save_asset(self, asset: dict[str, Any]) -> dict[str, Any]:
        self.assets[asset["id"]] = asset
        return asset

    def save_video(self, video: dict[str, Any]) -> dict[str, Any]:
        self.videos[video["id"]] = video
        return video

    def project_media(self, project_id: str, scene_id: str | None = None) -> list[dict[str, Any]]:
        return [a for a in self.assets.values() if a["project_id"] == project_id and (scene_id is None or a["scene_id"] == scene_id)]

    def write_metadata(self) -> None:
        Path(self.root, "metadata.json").write_text(json.dumps({"assets": self.assets, "videos": self.videos}, default=str, indent=2), encoding="utf-8")


media_store = MediaStore()