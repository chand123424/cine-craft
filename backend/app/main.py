from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database.mongodb import mongodb_lifespan
from app.exceptions import AIProviderError, WorkflowError, provider_error_handler, workflow_error_handler
from app.routes.characters import router as characters_router
from app.routes.memory import router as memory_router
from app.routes.projects import router as projects_router
from app.routes import scenes, scripts
from app.routes.media import router as media_router
from app.routes.videos import router as videos_router
from app.services.media_store import media_store

@asynccontextmanager
async def lifespan(_: FastAPI):
    async with mongodb_lifespan():
        yield


settings = get_settings()
app = FastAPI(title="CineCraft", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(projects_router, prefix="/api")
app.include_router(characters_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(scripts.router, prefix="/api")
app.include_router(scenes.router, prefix="/api")
app.add_exception_handler(WorkflowError, workflow_error_handler)
app.add_exception_handler(AIProviderError, provider_error_handler)
app.include_router(media_router, prefix="/api/media", tags=["media"])
app.include_router(videos_router, prefix="/api/videos", tags=["videos"])
app.mount("/media-files", StaticFiles(directory=media_store.root), name="media-files")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
