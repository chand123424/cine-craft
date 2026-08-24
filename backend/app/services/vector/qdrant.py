import hashlib
import uuid
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models

from app.services.vector.store import DeterministicEmbedder, MemoryRecord


class QdrantVectorStore:
    collection_name = "cinecraft_memory"

    def __init__(self, url: str, api_key: str | None, dimension: int = 128):
        self.client = AsyncQdrantClient(url=url, api_key=api_key)
        self.embedder = DeterministicEmbedder(dimension)
        self.dimension = dimension
        self._ready = False

    async def _ensure_collection(self) -> None:
        if self._ready:
            return
        collections = await self.client.get_collections()
        names = {collection.name for collection in collections.collections}
        if self.collection_name not in names:
            await self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(size=self.dimension, distance=models.Distance.COSINE),
            )
        self._ready = True

    async def store(self, record: MemoryRecord) -> MemoryRecord:
        await self._ensure_collection()
        record.embedding = self.embedder.embed(record.content)
        point_id = str(uuid.uuid5(uuid.NAMESPACE_URL, hashlib.sha256(
            f"{record.project_id}:{record.memory_type}:{record.content}".encode()
        ).hexdigest()))
        await self.client.upsert(
            collection_name=self.collection_name,
            points=[models.PointStruct(
                id=point_id,
                vector=record.embedding,
                payload={"project_id": record.project_id, "content": record.content,
                         "memory_type": record.memory_type, "metadata": record.metadata},
            )],
        )
        return record

    async def search(self, project_id: str, query: str, limit: int) -> list[MemoryRecord]:
        await self._ensure_collection()
        response = await self.client.query_points(
            collection_name=self.collection_name,
            query=self.embedder.embed(query),
            query_filter=models.Filter(must=[models.FieldCondition(
                key="project_id", match=models.MatchValue(value=project_id)
            )]),
            limit=limit,
            with_payload=True,
        )
        return [
            MemoryRecord(
                project_id=str(point.payload.get("project_id", project_id)),
                content=str(point.payload.get("content", "")),
                memory_type=str(point.payload.get("memory_type", "unknown")),
                metadata=point.payload.get("metadata", {}),
                embedding=[],
            )
            for point in response.points
            if point.payload
        ]

    async def close(self) -> None:
        await self.client.close()
