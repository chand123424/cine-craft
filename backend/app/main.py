from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.mongodb import mongodb_lifespan
from app.routes.characters import router as characters_router
from app.routes.memory import router as memory_router
from app.routes.projects import router as projects_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with mongodb_lifespan():
        yield


settings = get_settings()
app = FastAPI(title="CineCraft Data and Memory API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins, allow_methods=["*"], allow_headers=["*"])
app.include_router(projects_router, prefix="/api")
app.include_router(characters_router, prefix="/api")
app.include_router(memory_router, prefix="/api")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
