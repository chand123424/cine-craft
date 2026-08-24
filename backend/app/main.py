from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.exceptions import AIProviderError, WorkflowError, provider_error_handler, workflow_error_handler
from app.routes import scenes, scripts
from app.routes.media import router as media_router
from app.routes.videos import router as videos_router
from app.services.media_store import media_store

app = FastAPI(title="CineCraft AI Engine", version="0.1.0")
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
