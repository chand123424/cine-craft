import logging

from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas.models import IdeaRequest, RegenerationRequest, Script, ScriptUpdate, WorkflowState
from app.services.ai.factory import get_provider
from app.services.ai.prompt_builder import build_script_prompt
from app.services.ai.service import generate_script
from app.services.store import now, new_id, require_script, require_state, store

logger = logging.getLogger(__name__)
router = APIRouter(tags=["scripts"])


@router.post("/scripts/generate", response_model=Script, status_code=201)
async def create_script(request: IdeaRequest, settings: Settings = Depends(get_settings)) -> Script:
    data = await generate_script(get_provider(settings), build_script_prompt(request.idea, request.genre, request.tone, request.target_platform))
    timestamp = now()
    script = Script(id=new_id("script"), project_id=request.project_id, state=WorkflowState.SCRIPT_GENERATED, created_at=timestamp, updated_at=timestamp, **data)
    return store.add_script(script)


@router.get("/scripts/{project_id}", response_model=list[Script])
def list_scripts(project_id: str) -> list[Script]:
    return store.scripts_for_project(project_id)


@router.put("/scripts/{script_id}", response_model=Script)
def update_script(script_id: str, update: ScriptUpdate) -> Script:
    script = require_script(script_id)
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(script, key, value)
    script.updated_at = now()
    return script


@router.post("/scripts/{script_id}/approve", response_model=Script)
def approve_script(script_id: str) -> Script:
    script = require_script(script_id)
    require_state(script.state, WorkflowState.SCRIPT_GENERATED, "approve script")
    script.state = WorkflowState.SCRIPT_APPROVED
    script.updated_at = now()
    return script


@router.post("/scripts/{script_id}/regenerate", response_model=Script)
async def regenerate_script(script_id: str, request: RegenerationRequest, settings: Settings = Depends(get_settings)) -> Script:
    script = require_script(script_id)
    if request.target not in {"script", "dialogue"}:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Script regeneration supports target 'script' or 'dialogue'")
    if request.target == "script":
        data = await generate_script(get_provider(settings), build_script_prompt(script.story + " " + request.instructions, "", "", ""))
        for key, value in data.items():
            setattr(script, key, value)
    else:
        script.dialogue = [request.instructions or "New dialogue generated for this scene."]
    script.state = WorkflowState.SCRIPT_GENERATED
    script.updated_at = now()
    return script
