import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from app.services.rag.context import RAGContextService
from app.services.memory.service import MemoryService
from app.services.vector.store import InMemoryVectorStore


def test_memory_search_is_project_scoped_and_semantic():
    async def scenario():
        service = MemoryService(InMemoryVectorStore())
        await service.store("project-a", "Mara wears a red coat", "character", {})
        await service.store("project-b", "Mara wears a blue coat", "character", {})
        results = await service.search("project-a", "Mara coat", 5)
        assert len(results) == 1
        assert "red" in results[0].content

    asyncio.run(scenario())


def test_rag_context_formats_retrieved_memory():
    async def scenario():
        memory = MemoryService(InMemoryVectorStore())
        await memory.store("project-a", "The scene takes place at dawn", "story", {})
        context = await RAGContextService(memory).build_scene_context("project-a", "dawn scene")
        assert "[story]" in context
        assert "dawn" in context

    asyncio.run(scenario())
