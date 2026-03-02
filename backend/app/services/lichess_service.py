import httpx
from fastapi import HTTPException

from app.core.config import settings

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            base_url=settings.lichess_explorer_base_url,
            timeout=settings.lichess_timeout,
            headers={"User-Agent": "AgentIA-Echecs/0.1.0"},
        )
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


async def get_opening_moves(fen: str) -> dict:
    client = get_client()
    try:
        resp = await client.get(
            "/lichess",
            params={
                "fen": fen,
                "variant": "standard",
                "speeds": "blitz,rapid,classical",
                "ratings": "2200,2500",
            },
        )
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Lichess Explorer timeout")
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Erreur de connexion a Lichess Explorer")

    # Lichess Explorer applique un rate limiting strict.
    # En cas de 429, on propage l'erreur avec un header Retry-After
    # pour que le client puisse réessayer après le délai indiqué.
    if resp.status_code == 429:
        raise HTTPException(
            status_code=429,
            detail="Rate limit Lichess Explorer",
            headers={"Retry-After": "60"},
        )

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Lichess Explorer a repondu {resp.status_code}")

    return resp.json()
