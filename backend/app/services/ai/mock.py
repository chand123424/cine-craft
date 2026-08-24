from typing import Any

from app.services.ai.base import AIProvider


class MockProvider(AIProvider):
    async def generate_structured(self, prompt: str, schema_name: str) -> dict[str, Any]:
        if schema_name == "script":
            return {"title": "Untitled Story", "logline": "A small idea becomes an unforgettable journey.", "characters": [{"name": "Alex", "role": "protagonist", "appearance": "expressive face", "personality": "curious and determined", "age_range": "20s", "clothing": "practical jacket", "important_characteristics": ["resourceful"]}], "locations": ["A changing city"], "story": prompt, "narration": "Every journey starts with a question.", "dialogue": ["Alex: We have to try."], "scenes": [], "estimated_duration": 60}
        if schema_name == "scenes":
            return {"scenes": [{"scene_number": 1, "duration": 60, "description": "Alex takes the first step.", "characters": ["Alex"], "location": "A changing city", "action": "Alex looks toward the horizon and walks forward.", "dialogue": ["We have to try."], "narration": "Every journey starts with a question.", "mood": "hopeful", "image_prompt": "", "audio_prompt": ""}]}
        if schema_name == "regeneration":
            return {"value": prompt}
        return {}
