from app.schemas.models import Character, Scene, Script


def build_script_prompt(idea: str, genre: str, tone: str, target_platform: str) -> str:
    return (f"Create a structured screenplay JSON for {target_platform}. Idea: {idea}. "
            f"Genre: {genre}. Tone: {tone}. Include title, logline, characters, locations, "
            "story, narration, dialogue, scenes, and estimated_duration.")


def build_scene_prompt(script: Script, visual_style: str, user_preferences: str = "") -> str:
    return f"Convert this approved script into scene JSON. Script={script.model_dump_json()}; style={visual_style}; preferences={user_preferences}"


def build_image_prompt(scene: Scene, characters: list[Character], visual_style: str, preferences: str) -> str:
    cast = ", ".join(f"{c.name}: {c.appearance}, {c.clothing}" for c in characters)
    return f"{scene.description}. Cast: {cast}. Location: {scene.location}. Style: {visual_style}. {preferences}".strip()


def build_audio_prompt(scene: Scene, visual_style: str = "cinematic") -> str:
    return f"{visual_style} audio for {scene.mood} scene at {scene.location}: {scene.action}"
