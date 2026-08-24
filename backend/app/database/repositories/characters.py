from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.database.models import Character


class CharacterRepository:
    def __init__(self, database: AsyncDatabase):
        self.collection = database.characters

    async def create(self, values: dict) -> Character:
        character = Character(**values)
        await self.collection.insert_one(character.model_dump(by_alias=True))
        return character

    async def list_for_project(self, project_id: ObjectId) -> list[Character]:
        return [Character.model_validate(document) async for document in self.collection.find({"project_id": project_id}).sort("name", 1)]

    async def get(self, character_id: ObjectId, project_id: ObjectId) -> Character | None:
        document = await self.collection.find_one({"_id": character_id, "project_id": project_id})
        return Character.model_validate(document) if document else None

    async def get_by_id(self, character_id: ObjectId) -> Character | None:
        document = await self.collection.find_one({"_id": character_id})
        return Character.model_validate(document) if document else None

    async def update(self, character_id: ObjectId, project_id: ObjectId, changes: dict) -> Character | None:
        document = await self.collection.find_one_and_update(
            {"_id": character_id, "project_id": project_id}, {"$set": changes}, return_document=ReturnDocument.AFTER
        )
        return Character.model_validate(document) if document else None
