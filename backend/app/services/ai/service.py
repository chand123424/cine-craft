from pydantic import ValidationError

from app.exceptions import AIProviderError
from app.schemas.models import Character, Scene
from app.services.ai.base import AIProvider
from app.services.ai.prompt_builder import build_audio_prompt, build_image_prompt


async def generate_script(provider: AIProvider, prompt: str) -> dict:
    result = await provider.generate_structured(prompt, "script")
    try:
        result["characters"] = [Character.model_validate(item).model_dump() for item in result.get("characters", [])]
        result["scenes"] = [Scene.model_validate(item).model_dump() for item in result.get("scenes", [])]
        return result
    except (ValidationError, TypeError) as exc:
        raise AIProviderError(f"AI returned invalid script JSON: {exc}") from exc


async def generate_scenes(provider: AIProvider, prompt: str) -> list[Scene]:
    result = await provider.generate_structured(prompt, "scenes")
    try:
        return [Scene.model_validate(item) for item in result["scenes"]]
    except (ValidationError, KeyError, TypeError) as exc:
        raise AIProviderError(f"AI returned invalid scenes JSON: {exc}") from exc


def refresh_media_prompts(scene: Scene, characters: list[Character], style: str, preferences: str) -> Scene:
    scene.image_prompt = build_image_prompt(scene, characters, style, preferences)
    scene.audio_prompt = build_audio_prompt(scene, style)
    return scene
