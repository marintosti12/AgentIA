import logging
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: AsyncIOMotorClient | None = None
_db = None


def init_mongodb() -> None:
    global _client, _db
    uri = f"mongodb://{settings.mongodb_host}:{settings.mongodb_port}"
    _client = AsyncIOMotorClient(uri)
    _db = _client[settings.mongodb_database]
    logger.info("MongoDB connected to %s, database: %s", uri, settings.mongodb_database)


async def close_mongodb() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
    logger.info("MongoDB connection closed")


async def save_analysis(fen: str, agent_response: str, tools_used: list[str], opening_name: str = "") -> str:
    if _db is None:
        raise RuntimeError("MongoDB not initialized")

    doc = {
        "fen": fen,
        "opening_name": opening_name,
        "agent_response": agent_response,
        "tools_used": tools_used,
        "created_at": datetime.now(timezone.utc),
    }
    result = await _db.analyses.insert_one(doc)
    logger.info("Analysis saved for FEN: %s (id: %s)", fen, result.inserted_id)
    return str(result.inserted_id)


async def get_analysis_history(limit: int = 20) -> list[dict]:
    if _db is None:
        raise RuntimeError("MongoDB not initialized")

    cursor = _db.analyses.find(
        {}, {"_id": 0, "fen": 1, "opening_name": 1, "agent_response": 1, "tools_used": 1, "created_at": 1}
    ).sort("created_at", -1).limit(limit)

    return await cursor.to_list(length=limit)


async def get_cached_analysis(fen: str) -> dict | None:
    if _db is None:
        return None

    doc = await _db.analyses.find_one(
        {"fen": fen},
        {"_id": 0, "agent_response": 1, "tools_used": 1, "opening_name": 1, "created_at": 1},
        sort=[("created_at", -1)],
    )
    return doc
