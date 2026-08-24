from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Status(str, Enum):
    PENDING = "PENDING"
    GENERATING = "GENERATING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    MUSIC = "music"
    SFX = "sfx"
    DIALOGUE = "dialogue"
    NARRATION = "narration"


class ImageGenerateRequest(BaseModel):
    project_id: str
    scene_id: str
    scene_description: str
    image_prompt: str
    character_information: str = ""
    location: str = ""
    visual_style: str = "cinematic"


class AudioGenerateRequest(BaseModel):
    project_id: str
    scene_id: str
    text: str = ""
    audio_type: MediaType = MediaType.NARRATION
    voice: str = "default"
    duration_seconds: float = Field(default=3.0, gt=0, le=60)


class MediaAsset(BaseModel):
    id: str
    project_id: str
    scene_id: str
    media_type: MediaType
    url: str | None = None
    prompt: str | None = None
    provider: str
    duration_seconds: float | None = None
    status: Status
    approved: bool = False
    created_at: datetime
    error: str | None = None


class RegenerateRequest(BaseModel):
    media_type: MediaType
    image_prompt: str | None = None
    text: str | None = None
    voice: str | None = None


class VideoCreateRequest(BaseModel):
    project_id: str
    scene_ids: list[str] = Field(min_length=1)
    aspect_ratio: str = "9:16"
    scene_durations: dict[str, float] = {}
    transition_seconds: float = Field(default=0, ge=0, le=2)
    music_asset_id: str | None = None


class Video(BaseModel):
    id: str
    project_id: str
    url: str | None = None
    aspect_ratio: str
    status: Status
    duration_seconds: float | None = None
    created_at: datetime
    error: str | None = None