from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.models import SceneRecord, Script, WorkflowState


class InMemoryStore:
    def __init__(self) -> None:
        self.scripts: dict[str, Script] = {}
        self.scenes: dict[str, SceneRecord] = {}

    def add_script(self, script: Script) -> Script:
        self.scripts[script.id] = script
        return script

    def get_script(self, script_id: str) -> Script | None:
        return self.scripts.get(script_id)

    def scripts_for_project(self, project_id: str) -> list[Script]:
        return [item for item in self.scripts.values() if item.project_id == project_id]

    def add_scene(self, scene: SceneRecord) -> SceneRecord:
        self.scenes[scene.id] = scene
        return scene

    def scenes_for_project(self, project_id: str) -> list[SceneRecord]:
        return [item for item in self.scenes.values() if item.project_id == project_id]

    def get_scene(self, scene_id: str) -> SceneRecord | None:
        return self.scenes.get(scene_id)


store = InMemoryStore()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def now() -> datetime:
    return datetime.now(timezone.utc)


def require_script(script_id: str) -> Script:
    script = store.get_script(script_id)
    if script is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Script not found")
    return script


def require_scene(scene_id: str) -> SceneRecord:
    scene = store.get_scene(scene_id)
    if scene is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Scene not found")
    return scene


def require_state(actual: WorkflowState, expected: WorkflowState, action: str) -> None:
    from app.exceptions import WorkflowError
    if actual != expected:
        raise WorkflowError(f"Cannot {action} while workflow is {actual}; required {expected}.")
