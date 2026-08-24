from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_validator


class APIModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class ProjectCreate(APIModel):
    title: str = Field(min_length=1, max_length=200)
    original_idea: str = Field(min_length=1)


class ProjectUpdate(APIModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    original_idea: str | None = Field(default=None, min_length=1)
    status: str | None = None
    script_status: str | None = None
    scene_status: str | None = None
    media_status: str | None = None
    video_status: str | None = None


class CharacterCreate(APIModel):
    project_id: str
    name: str = Field(min_length=1, max_length=120)
    appearance: str
    personality: str
    clothing: str
    role: str
    reference_information: dict = Field(default_factory=dict)

    @field_validator("project_id")
    @classmethod
    def valid_project_id(cls, value: str) -> str:
        if not ObjectId.is_valid(value):
            raise ValueError("project_id must be a valid ObjectId")
        return value


class CharacterUpdate(APIModel):
    name: str | None = None
    appearance: str | None = None
    personality: str | None = None
    clothing: str | None = None
    role: str | None = None
    reference_information: dict | None = None


class MemoryStoreRequest(APIModel):
    project_id: str
    content: str = Field(min_length=1)
    memory_type: str
    metadata: dict = Field(default_factory=dict)

    @field_validator("project_id")
    @classmethod
    def valid_project_id(cls, value: str) -> str:
        if not ObjectId.is_valid(value):
            raise ValueError("project_id must be a valid ObjectId")
        return value


class MemorySearchRequest(APIModel):
    project_id: str
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)

    @field_validator("project_id")
    @classmethod
    def valid_project_id(cls, value: str) -> str:
        if not ObjectId.is_valid(value):
            raise ValueError("project_id must be a valid ObjectId")
        return value
