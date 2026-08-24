from fastapi import APIRouter, Depends, HTTPException

from app.config import Settings, get_settings
from app.schemas.models import RegenerationRequest, SceneGenerateRequest, SceneRecord, SceneUpdate, WorkflowState
from app.services.ai.factory import get_provider
from app.services.ai.prompt_builder import build_scene_prompt
from app.services.ai.service import generate_scenes, refresh_media_prompts
from app.services.store import now, new_id, require_scene, require_script, require_state, store

router = APIRouter(tags=["scenes"])


@router.post("/scenes/generate", response_model=list[SceneRecord], status_code=201)
async def create_scenes(request: SceneGenerateRequest, settings: Settings = Depends(get_settings)) -> list[SceneRecord]:
    script = require_script(request.script_id)
    if script.project_id != request.project_id:
        raise HTTPException(status_code=404, detail="Script does not belong to project")
    require_state(script.state, WorkflowState.SCRIPT_APPROVED, "generate scenes")
    generated = await generate_scenes(get_provider(settings), build_scene_prompt(script, request.visual_style, request.user_preferences))
    timestamp = now()
    records = [SceneRecord(id=new_id("scene"), project_id=request.project_id, script_id=script.id, state=WorkflowState.SCENES_GENERATED, created_at=timestamp, updated_at=timestamp, **refresh_media_prompts(scene, script.characters, request.visual_style, request.user_preferences).model_dump()) for scene in generated]
    for record in records:
        store.add_scene(record)
    script.state = WorkflowState.SCENES_GENERATED
    script.updated_at = timestamp
    return records


@router.get("/scenes/{project_id}", response_model=list[SceneRecord])
def list_scenes(project_id: str) -> list[SceneRecord]:
    return store.scenes_for_project(project_id)


@router.put("/scenes/{scene_id}", response_model=SceneRecord)
def update_scene(scene_id: str, update: SceneUpdate) -> SceneRecord:
    scene = require_scene(scene_id)
    for key, value in update.model_dump(exclude_unset=True).items():
        setattr(scene, key, value)
    scene.updated_at = now()
    return scene


@router.post("/scenes/{scene_id}/approve", response_model=SceneRecord)
def approve_scene(scene_id: str) -> SceneRecord:
    scene = require_scene(scene_id)
    require_state(scene.state, WorkflowState.SCENES_GENERATED, "approve scene")
    scene.approved = True
    scene.state = WorkflowState.SCENES_APPROVED
    scene.updated_at = now()
    script = require_script(scene.script_id)
    project_scenes = store.scenes_for_project(scene.project_id)
    if project_scenes and all(item.approved for item in project_scenes):
        script.state = WorkflowState.SCENES_APPROVED
        script.updated_at = now()
    return scene


@router.post("/scenes/{scene_id}/regenerate", response_model=SceneRecord)
async def regenerate_scene(scene_id: str, request: RegenerationRequest, settings: Settings = Depends(get_settings)) -> SceneRecord:
    scene = require_scene(scene_id)
    script = require_script(scene.script_id)
    if request.target not in {"scene", "image_prompt", "audio_prompt", "dialogue"}:
        raise HTTPException(status_code=400, detail="Scene regeneration target is invalid")
    if request.target == "scene":
        generated = await generate_scenes(get_provider(settings), build_scene_prompt(script, request.visual_style, request.user_preferences))
        replacement = next((item for item in generated if item.scene_number == scene.scene_number), generated[0])
        for key, value in replacement.model_dump().items():
            setattr(scene, key, value)
    elif request.target == "image_prompt":
        scene.image_prompt = request.instructions or scene.image_prompt
    elif request.target == "audio_prompt":
        scene.audio_prompt = request.instructions or scene.audio_prompt
    else:
        scene.dialogue = [request.instructions or "New dialogue generated for this scene."]
    scene.approved = False
    scene.state = WorkflowState.SCENES_GENERATED
    scene.updated_at = now()
    script.state = WorkflowState.SCENES_GENERATED
    script.updated_at = now()
    return scene
