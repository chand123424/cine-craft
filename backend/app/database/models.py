from datetime import datetime, timezone
from enum import StrEnum
from typing import Any

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ApprovalState(StrEnum):
    IDEA = "IDEA"
    SCRIPT_GENERATED = "SCRIPT_GENERATED"
    SCRIPT_APPROVED = "SCRIPT_APPROVED"
    SCENES_GENERATED = "SCENES_GENERATED"
    SCENES_APPROVED = "SCENES_APPROVED"
    MEDIA_GENERATED = "MEDIA_GENERATED"
    MEDIA_APPROVED = "MEDIA_APPROVED"
    VIDEO_GENERATING = "VIDEO_GENERATING"
    COMPLETED = "COMPLETED"


class MongoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class User(MongoModel):
    email: str
    display_name: str


class Project(MongoModel):
    owner_id: ObjectId
    title: str
    original_idea: str
    status: ApprovalState = ApprovalState.IDEA
    script_status: str = "pending"
    scene_status: str = "pending"
    media_status: str = "pending"
    video_status: str = "pending"


class Script(MongoModel):
    project_id: ObjectId
    version: int = 1
    content: str
    generated_by: str = "ai"


class Scene(MongoModel):
    project_id: ObjectId
    order: int
    title: str
    description: str
    dialogue: list[dict[str, Any]] = Field(default_factory=list)
    character_ids: list[ObjectId] = Field(default_factory=list)
    location: str | None = None


class Character(MongoModel):
    project_id: ObjectId
    name: str
    appearance: str
    personality: str
    clothing: str
    role: str
    reference_information: dict[str, Any] = Field(default_factory=dict)


class Media(MongoModel):
    project_id: ObjectId
    scene_id: ObjectId | None = None
    media_type: str
    url: str
    prompt: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Video(MongoModel):
    project_id: ObjectId
    url: str | None = None
    status: str = "pending"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Approval(MongoModel):
    project_id: ObjectId
    state: ApprovalState
    approved: bool
    approved_by: ObjectId | None = None
    notes: str | None = None
