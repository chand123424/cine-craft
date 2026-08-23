from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.asynchronous.database import AsyncDatabase
from pymongo import AsyncMongoClient

from app.config import get_settings

_client: AsyncMongoClient | None = None
_database: AsyncDatabase | None = None


async def connect_to_mongodb() -> None:
    global _client, _database
    settings = get_settings()
    _client = AsyncMongoClient(settings.mongodb_uri)
    await _client.admin.command("ping")
    _database = _client[settings.mongodb_database]
    await ensure_indexes(_database)


async def close_mongodb() -> None:
    global _client, _database
    if _client is not None:
        await _client.close()
    _client = None
    _database = None


def get_database() -> AsyncDatabase:
    if _database is None:
        raise RuntimeError("MongoDB is not connected")
    return _database


async def ensure_indexes(database: AsyncDatabase) -> None:
    await database.users.create_indexes([IndexModel([("email", ASCENDING)], unique=True)])
    await database.projects.create_indexes([
        IndexModel([("owner_id", ASCENDING), ("updated_at", DESCENDING)]),
        IndexModel([("status", ASCENDING)]),
    ])
    await database.scripts.create_indexes([IndexModel([("project_id", ASCENDING), ("version", DESCENDING)])])
    await database.scenes.create_indexes([IndexModel([("project_id", ASCENDING), ("order", ASCENDING)])])
    await database.characters.create_indexes([IndexModel([("project_id", ASCENDING), ("name", ASCENDING)])])
    await database.media.create_indexes([IndexModel([("project_id", ASCENDING), ("scene_id", ASCENDING)])])
    await database.videos.create_indexes([IndexModel([("project_id", ASCENDING), ("created_at", DESCENDING)])])
    await database.approvals.create_indexes([IndexModel([("project_id", ASCENDING), ("created_at", DESCENDING)])])


@asynccontextmanager
async def mongodb_lifespan() -> AsyncIterator[None]:
    await connect_to_mongodb()
    try:
        yield
    finally:
        await close_mongodb()
