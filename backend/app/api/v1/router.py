from fastapi import APIRouter

from app.api.v1.endpoints import evaluate, moves

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok", "service": "agent-ia-echecs"}


router.include_router(evaluate.router, tags=["evaluation"])
router.include_router(moves.router, tags=["moves"])
