import logging

import httpx
from fastapi import HTTPException

from app.core.config import settings

logger = logging.getLogger(__name__)

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        headers = {
            "User-Agent": "AgentIA-Echecs/0.1.0",
            "Accept": "application/json",
        }
        if settings.lichess_token:
            headers["Authorization"] = f"Bearer {settings.lichess_token}"
        _client = httpx.AsyncClient(
            base_url=settings.lichess_explorer_base_url,
            timeout=settings.lichess_timeout,
            headers=headers,
        )
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def get_opening_moves(fen: str) -> dict:
    client = get_client()

    # Try lichess database first, then masters
    for endpoint in ["/lichess", "/masters"]:
        try:
            resp = await client.get(
                endpoint,
                params={
                    "fen": fen,
                    "variant": "standard",
                    "speeds": "blitz,rapid,classical",
                    "ratings": "2200,2500",
                },
            )
            if resp.status_code == 200:
                return resp.json()
            logger.warning("Lichess %s returned %d", endpoint, resp.status_code)
        except httpx.TimeoutException:
            logger.warning("Lichess %s timeout", endpoint)
        except httpx.HTTPError as e:
            logger.warning("Lichess %s error: %s", endpoint, e)

    # If explorer fails, return empty result
    logger.error("All Lichess Explorer endpoints failed for FEN: %s", fen)
    return {"moves": [], "white": 0, "draws": 0, "black": 0}
