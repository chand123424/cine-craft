import os
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.models import Status, Video, VideoCreateRequest
from app.services.media_store import media_store
from app.utils.ffmpeg import ASPECTS, create_video

router = APIRouter()


def validate_assets(request: VideoCreateRequest) -> tuple[list[dict], list[dict]]:
    project = media_store.approvals.get(request.project_id)
    if not project:
        raise HTTPException(400, "Project approval state is unavailable")
    if not project.get("script_approved"):
        raise HTTPException(400, "Script is not approved")
    if not project.get("scenes_approved"):
        raise HTTPException(400, "Scenes are not approved")
    all_media = media_store.project_media(request.project_id)
    images, audio = [], []
    for scene_id in request.scene_ids:
        scene_media = [asset for asset in all_media if asset["scene_id"] == scene_id]
        image = next((asset for asset in scene_media if asset["media_type"] == "image" and asset["status"] == Status.COMPLETED and asset["approved"]), None)
        sound = next((asset for asset in scene_media if asset["media_type"] in {"audio", "music", "dialogue", "narration", "sfx"} and asset["status"] == Status.COMPLETED and asset["approved"]), None)
        if not image:
            raise HTTPException(400, f"Scene '{scene_id}' is missing an approved image")
        if not sound:
            raise HTTPException(400, f"Scene '{scene_id}' is missing approved audio")
        images.append(image)
        audio.append(sound)
    return images, audio


@router.post("/create", response_model=Video)
def create_project_video(request: VideoCreateRequest) -> Video:
    if request.aspect_ratio not in ASPECTS:
        raise HTTPException(422, "aspect_ratio must be one of: 9:16, 16:9, 1:1")
    images, audio = validate_assets(request)
    music_path = None
    if request.music_asset_id:
        music = media_store.assets.get(request.music_asset_id)
        if not music or music["project_id"] != request.project_id or music["media_type"] != "music" or not music["approved"] or music["status"] != Status.COMPLETED:
            raise HTTPException(400, "Requested music asset is missing or not approved")
        music_path = music["url"].removeprefix("/media-files/")
    video_id = str(uuid4())
    durations = [request.scene_durations.get(scene_id, 3.0) for scene_id in request.scene_ids]
    output = os.path.join(media_store.root, f"{video_id}.mp4")
    try:
        total = create_video([asset["url"].removeprefix("/media-files/") for asset in images], [asset["url"].removeprefix("/media-files/") for asset in audio], durations, output, request.aspect_ratio, request.transition_seconds, music_path)
        video = Video(id=video_id, project_id=request.project_id, url=f"/media-files/{video_id}.mp4", aspect_ratio=request.aspect_ratio, status=Status.COMPLETED, duration_seconds=total, created_at=datetime.now(timezone.utc))
    except Exception as error:
        video = Video(id=video_id, project_id=request.project_id, aspect_ratio=request.aspect_ratio, status=Status.FAILED, created_at=datetime.now(timezone.utc), error=str(error))
        media_store.save_video(video.model_dump())
        raise HTTPException(500, video.error) from error
    media_store.save_video(video.model_dump())
    media_store.write_metadata()
    return video


@router.get("/project/{project_id}", response_model=list[Video])
def list_project_videos(project_id: str) -> list[Video]:
    return [Video.model_validate(video) for video in media_store.videos.values() if video["project_id"] == project_id]


@router.get("/{id}", response_model=Video)
def get_video(id: str) -> Video:
    video = media_store.videos.get(id)
    if not video:
        raise HTTPException(404, "Video not found")
    return Video.model_validate(video)