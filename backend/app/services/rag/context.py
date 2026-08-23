from app.services.memory.service import MemoryService


class RAGContextService:
    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service

    async def build_scene_context(self, project_id: str, scene_request: str, limit: int = 8) -> str:
        memories = await self.memory_service.search(project_id, scene_request, limit)
        if not memories:
            return "No prior project memory was found."
        return "\n\n".join(
            f"[{memory.memory_type}] {memory.content}" for memory in memories
        )
