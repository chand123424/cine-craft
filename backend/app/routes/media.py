from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.models import AudioGenerateRequest, ImageGenerateRequest, MediaAsset, RegenerateRequest, Status
from app.services.audio.generator import generate_audio
from app.services.image.generator import generate_image
from app.services.media_store import media_store

router = APIRouter()


@router.post("/image/generate", response_model=MediaAsset)
def generate_scene_image(request: ImageGenerateRequest) -> MediaAsset:
    prompt = f"{request.image_prompt}. {request.character_information}. {request.location}. {request.visual_style}"
    try:
        path, provider = generate_image(prompt, media_store.root)
        asset = MediaAsset(id=str(uuid4()), project_id=request.project_id, scene_id=request.scene_id, media_type="image", url=f"/media-files/{path}", prompt=prompt, provider=provider, status=Status.COMPLETED, created_at=datetime.now(timezone.utc))
        media_store.save_asset(asset.model_dump())
        media_store.write_metadata()
        return asset
    except Exception as error:
        raise HTTPException(500, f"Image generation failed: {error}") from error


@router.post("/audio/generate", response_model=MediaAsset)
def generate_scene_audio(request: AudioGenerateRequest) -> MediaAsset:
    try:
        path, provider = generate_audio(request.text, request.duration_seconds, media_store.root)
        asset = MediaAsset(id=str(uuid4()), project_id=request.project_id, scene_id=request.scene_id, media_type=request.audio_type, url=f"/media-files/{path}", provider=provider, duration_seconds=request.duration_seconds, status=Status.COMPLETED, created_at=datetime.now(timezone.utc))
        media_store.save_asset(asset.model_dump())
        media_store.write_metadata()
        return asset
    except Exception as error:
        raise HTTPException(500, f"Audio generation failed: {error}") from error


@router.post("/{id}/regenerate", response_model=MediaAsset)
def regenerate_media(id: str, request: RegenerateRequest) -> MediaAsset:
    original = media_store.assets.get(id)
    if not original:
        raise HTTPException(404, "Media asset not found")
    if request.media_type == "image":
        path, provider = generate_image(request.image_prompt or original.get("prompt") or "cinematic scene", media_store.root)
        original.update(url=f"/media-files/{path}", provider=provider)
    else:
        path, provider = generate_audio(request.text or "", original.get("duration_seconds") or 3, media_store.root)
        original.update(url=f"/media-files/{path}", provider=provider)
    original.update(status=Status.COMPLETED, approved=False, created_at=datetime.now(timezone.utc))
    media_store.write_metadata()
    return MediaAsset.model_validate(original)