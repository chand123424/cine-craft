from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkflowState(StrEnum):
    IDEA = "IDEA"
    SCRIPT_GENERATED = "SCRIPT_GENERATED"
    SCRIPT_APPROVED = "SCRIPT_APPROVED"
    SCENES_GENERATED = "SCENES_GENERATED"
    SCENES_APPROVED = "SCENES_APPROVED"
    MEDIA_GENERATED = "MEDIA_GENERATED"
    MEDIA_APPROVED = "MEDIA_APPROVED"
    VIDEO_GENERATING = "VIDEO_GENERATING"
    COMPLETED = "COMPLETED"


class Character(BaseModel):
    name: str
    role: str
    appearance: str
    personality: str
    age_range: str
    clothing: str
    important_characteristics: list[str] = Field(default_factory=list)


class Scene(BaseModel):
    scene_number: int = Field(ge=1)
    duration: float = Field(gt=0)
    description: str
    characters: list[str] = Field(default_factory=list)
    location: str
    action: str
    dialogue: list[str] = Field(default_factory=list)
    narration: str = ""
    mood: str
    image_prompt: str
    audio_prompt: str
    approved: bool = False


class Script(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    project_id: str
    title: str
    logline: str
    characters: list[Character] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    story: str
    narration: str
    dialogue: list[str] = Field(default_factory=list)
    scenes: list[Scene] = Field(default_factory=list)
    estimated_duration: float = Field(gt=0)
    state: WorkflowState
    created_at: datetime
    updated_at: datetime


class SceneRecord(Scene):
    id: str
    project_id: str
    script_id: str
    state: WorkflowState
    created_at: datetime
    updated_at: datetime


class IdeaRequest(BaseModel):
    project_id: str = Field(min_length=1)
    idea: str = Field(min_length=1, max_length=10000)
    genre: str = "drama"
    tone: str = "cinematic"
    target_platform: str = "short video"


class ScriptUpdate(BaseModel):
    title: str | None = None
    logline: str | None = None
    story: str | None = None
    narration: str | None = None
    dialogue: list[str] | None = None
    characters: list[Character] | None = None
    locations: list[str] | None = None
    estimated_duration: float | None = Field(default=None, gt=0)


class SceneGenerateRequest(BaseModel):
    project_id: str = Field(min_length=1)
    script_id: str = Field(min_length=1)
    visual_style: str = "cinematic"
    user_preferences: str = ""


class SceneUpdate(BaseModel):
    duration: float | None = Field(default=None, gt=0)
    description: str | None = None
    characters: list[str] | None = None
    location: str | None = None
    action: str | None = None
    dialogue: list[str] | None = None
    narration: str | None = None
    mood: str | None = None
    image_prompt: str | None = None
    audio_prompt: str | None = None


class RegenerationRequest(BaseModel):
    target: str = Field(pattern="^(script|scene|image_prompt|audio_prompt|dialogue)$")
    instructions: str = ""
    visual_style: str = "cinematic"
    user_preferences: str = ""


class ProviderPayload(BaseModel):
    data: dict[str, Any]
