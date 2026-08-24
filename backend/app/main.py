from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes.media import router as media_router
from app.routes.videos import router as videos_router
from app.services.media_store import media_store

app = FastAPI(title="CineCraft Media API", version="1.0.0")
app.include_router(media_router, prefix="/api/media", tags=["media"])
app.include_router(videos_router, prefix="/api/videos", tags=["videos"])
app.mount("/media-files", StaticFiles(directory=media_store.root), name="media-files")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}