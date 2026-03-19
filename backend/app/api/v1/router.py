from fastapi import APIRouter

from app.api.v1.endpoints import agent, evaluate, moves, vector_search, videos

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok", "service": "agent-ia-echecs"}


router.include_router(evaluate.router, tags=["evaluation"])
router.include_router(moves.router, tags=["moves"])
router.include_router(vector_search.router, tags=["vector-search"])
router.include_router(videos.router, tags=["videos"])
router.include_router(agent.router, tags=["agent"])
