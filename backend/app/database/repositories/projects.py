from datetime import datetime, timezone

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase

from app.database.models import Project


class ProjectRepository:
    def __init__(self, database: AsyncDatabase):
        self.collection = database.projects

    async def create(self, owner_id: ObjectId, title: str, original_idea: str) -> Project:
        project = Project(owner_id=owner_id, title=title, original_idea=original_idea)
        await self.collection.insert_one(project.model_dump(by_alias=True))
        return project

    async def list_for_owner(self, owner_id: ObjectId) -> list[Project]:
        return [Project.model_validate(document) async for document in self.collection.find({"owner_id": owner_id}).sort("updated_at", -1)]

    async def get_for_owner(self, project_id: ObjectId, owner_id: ObjectId) -> Project | None:
        document = await self.collection.find_one({"_id": project_id, "owner_id": owner_id})
        return Project.model_validate(document) if document else None

    async def update_for_owner(self, project_id: ObjectId, owner_id: ObjectId, changes: dict) -> Project | None:
        changes["updated_at"] = datetime.now(timezone.utc)
        document = await self.collection.find_one_and_update(
            {"_id": project_id, "owner_id": owner_id}, {"$set": changes}, return_document=ReturnDocument.AFTER
        )
        return Project.model_validate(document) if document else None

    async def delete_for_owner(self, project_id: ObjectId, owner_id: ObjectId) -> bool:
        result = await self.collection.delete_one({"_id": project_id, "owner_id": owner_id})
        return result.deleted_count == 1
