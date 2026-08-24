from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database.mongodb import get_database
from app.database.repositories.characters import CharacterRepository
from app.dependencies import current_user_id, owned_project
from app.schemas.common import CharacterCreate, CharacterUpdate

router = APIRouter(prefix="/characters", tags=["characters"])


def character_response(character) -> dict:
    data = character.model_dump()
    data["id"] = str(data.pop("id"))
    data["project_id"] = str(data["project_id"])
    return data


def repository() -> CharacterRepository:
    return CharacterRepository(get_database())


@router.get("/{project_id}")
async def list_characters(project_id: str, user_id: ObjectId = Depends(current_user_id)):
    project_object_id, _ = await owned_project(project_id, user_id)
    return [character_response(character) for character in await repository().list_for_project(project_object_id)]


@router.post("", status_code=201)
async def create_character(payload: CharacterCreate, user_id: ObjectId = Depends(current_user_id)):
    await owned_project(payload.project_id, user_id)
    values = payload.model_dump()
    values["project_id"] = ObjectId(values["project_id"])
    return character_response(await repository().create(values))


@router.put("/{character_id}")
async def update_character(character_id: str, payload: CharacterUpdate, user_id: ObjectId = Depends(current_user_id)):
    if not ObjectId.is_valid(character_id):
        raise HTTPException(status_code=400, detail="Invalid character id")
    existing = await repository().get_by_id(ObjectId(character_id))
    if existing is None:
        raise HTTPException(status_code=404, detail="Character not found")
    project_object_id, _ = await owned_project(str(existing.project_id), user_id)
    character = await repository().update(ObjectId(character_id), project_object_id, payload.model_dump(exclude_none=True))
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character_response(character)
