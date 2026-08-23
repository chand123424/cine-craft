from bson import ObjectId
from fastapi import APIRouter, Depends

from app.dependencies import current_user_id, owned_project
from app.schemas.common import MemorySearchRequest, MemoryStoreRequest
from app.services.memory.service import MemoryService
from app.services.vector.store import InMemoryVectorStore
from app.config import get_settings


def create_vector_store():
    settings = get_settings()
    if settings.vector_provider.lower() == "qdrant":
        if not settings.qdrant_url:
            raise RuntimeError("CINECRAFT_QDRANT_URL is required when vector provider is qdrant")
        from app.services.vector.qdrant import QdrantVectorStore

        return QdrantVectorStore(settings.qdrant_url, settings.qdrant_api_key, settings.embedding_dimension)
    return InMemoryVectorStore()

router = APIRouter(prefix="/memory", tags=["memory"])
vector_store = create_vector_store()
memory_service = MemoryService(vector_store)


@router.post("/store", status_code=201)
async def store_memory(payload: MemoryStoreRequest, user_id: ObjectId = Depends(current_user_id)):
    await owned_project(payload.project_id, user_id)
    record = await memory_service.store(payload.project_id, payload.content, payload.memory_type, payload.metadata)
    return {"project_id": record.project_id, "content": record.content, "memory_type": record.memory_type, "metadata": record.metadata}


@router.get("/search")
async def search_memory(request: MemorySearchRequest = Depends(), user_id: ObjectId = Depends(current_user_id)):
    await owned_project(request.project_id, user_id)
    records = await memory_service.search(request.project_id, request.query, request.limit)
    return [{"content": record.content, "memory_type": record.memory_type, "metadata": record.metadata} for record in records]
