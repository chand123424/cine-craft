from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database.repositories.projects import ProjectRepository
from app.dependencies import current_user_id
from app.database.mongodb import get_database
from app.schemas.common import ProjectCreate, ProjectUpdate

router = APIRouter(prefix="/projects", tags=["projects"])


def project_response(project) -> dict:
    data = project.model_dump()
    data["id"] = str(data.pop("id"))
    data["owner_id"] = str(data["owner_id"])
    return data


def repository() -> ProjectRepository:
    return ProjectRepository(get_database())


@router.post("", status_code=201)
async def create_project(payload: ProjectCreate, user_id: ObjectId = Depends(current_user_id)):
    return project_response(await repository().create(user_id, payload.title, payload.original_idea))


@router.get("")
async def list_projects(user_id: ObjectId = Depends(current_user_id)):
    return [project_response(project) for project in await repository().list_for_owner(user_id)]


@router.get("/{project_id}")
async def get_project(project_id: str, user_id: ObjectId = Depends(current_user_id)):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project id")
    project = await repository().get_for_owner(ObjectId(project_id), user_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_response(project)


@router.put("/{project_id}")
async def update_project(project_id: str, payload: ProjectUpdate, user_id: ObjectId = Depends(current_user_id)):
    if not ObjectId.is_valid(project_id):
        raise HTTPException(status_code=400, detail="Invalid project id")
    changes = payload.model_dump(exclude_none=True)
    project = await repository().update_for_owner(ObjectId(project_id), user_id, changes)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_response(project)


@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str, user_id: ObjectId = Depends(current_user_id)):
    if not ObjectId.is_valid(project_id) or not await repository().delete_for_owner(ObjectId(project_id), user_id):
        raise HTTPException(status_code=404, detail="Project not found")
