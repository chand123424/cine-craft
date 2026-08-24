import hashlib
import math
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class MemoryRecord:
    project_id: str
    content: str
    memory_type: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)


class VectorStore(Protocol):
    async def store(self, record: MemoryRecord) -> MemoryRecord: ...
    async def search(self, project_id: str, query: str, limit: int) -> list[MemoryRecord]: ...


class DeterministicEmbedder:
    def __init__(self, dimension: int = 128):
        self.dimension = dimension

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in text.lower().split():
            index = int(hashlib.sha256(token.encode()).hexdigest(), 16) % self.dimension
            vector[index] += 1.0
        magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / magnitude for value in vector]


class InMemoryVectorStore:
    def __init__(self, embedder: DeterministicEmbedder | None = None):
        self.embedder = embedder or DeterministicEmbedder()
        self.records: list[MemoryRecord] = []

    async def store(self, record: MemoryRecord) -> MemoryRecord:
        record.embedding = self.embedder.embed(record.content)
        self.records.append(record)
        return record

    async def search(self, project_id: str, query: str, limit: int) -> list[MemoryRecord]:
        query_embedding = self.embedder.embed(query)
        candidates = [record for record in self.records if record.project_id == project_id]
        candidates.sort(key=lambda record: sum(a * b for a, b in zip(record.embedding, query_embedding)), reverse=True)
        return candidates[:limit]
