from bson import ObjectId
from fastapi import Header, HTTPException

from app.database.mongodb import get_database
from app.database.repositories.projects import ProjectRepository


def current_user_id(x_user_id: str = Header(..., alias="X-User-Id")) -> ObjectId:
    if not ObjectId.is_valid(x_user_id):
        raise HTTPException(status_code=400, detail="X-User-Id must be a valid ObjectId")
    return ObjectId(x_user_id)


async def owned_project(project_id: str, user_id: ObjectId) -> tuple[ObjectId, ProjectRepository]:
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project id")
    repository = ProjectRepository(get_database())
    project_object_id = ObjectId(project_id)
    if await repository.get_for_owner(project_object_id, user_id) is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_object_id, repository
