from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    async def generate_structured(self, prompt: str, schema_name: str) -> dict[str, Any]:
        raise NotImplementedError
