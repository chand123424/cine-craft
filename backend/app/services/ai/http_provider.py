import asyncio
import json
import logging
from typing import Any

import httpx

from app.exceptions import AIProviderError
from app.services.ai.base import AIProvider

logger = logging.getLogger(__name__)


class HttpJSONProvider(AIProvider):
    def __init__(self, api_key: str, endpoint: str, model: str, timeout: float = 30.0, retries: int = 2) -> None:
        self.api_key = api_key
        self.endpoint = endpoint
        self.model = model
        self.timeout = timeout
        self.retries = retries

    async def generate_structured(self, prompt: str, schema_name: str) -> dict[str, Any]:
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        last_error = "unknown provider error"
        for attempt in range(self.retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(self.endpoint, json=payload, headers=headers)
                    response.raise_for_status()
                    body = response.json()
                    content = body["choices"][0]["message"]["content"]
                    result = json.loads(content) if isinstance(content, str) else content
                    if not isinstance(result, dict):
                        raise ValueError("provider returned non-object JSON")
                    return result
            except (httpx.HTTPError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
                last_error = str(exc)
                logger.warning("AI provider attempt %d failed: %s", attempt + 1, exc)
                if attempt < self.retries:
                    await asyncio.sleep(0.25 * (2**attempt))
        raise AIProviderError(f"AI provider failed after retries: {last_error}")
