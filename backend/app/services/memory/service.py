from app.services.vector.store import MemoryRecord, VectorStore


class MemoryService:
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store

    async def store(self, project_id: str, content: str, memory_type: str, metadata: dict) -> MemoryRecord:
        return await self.vector_store.store(MemoryRecord(project_id, content, memory_type, metadata))

    async def search(self, project_id: str, query: str, limit: int) -> list[MemoryRecord]:
        return await self.vector_store.search(project_id, query, limit)
