import asyncio

from fastapi import APIRouter

from app.models.chess_models import EvaluationResponse
from app.services import stockfish_service
from app.utils.fen_validator import validate_fen

router = APIRouter()


@router.get("/evaluate/{fen:path}", response_model=EvaluationResponse)
async def evaluate_position(fen: str):
    board = validate_fen(fen)
    result = await asyncio.to_thread(stockfish_service.evaluate_position, fen, board)
    return EvaluationResponse(fen=fen, **result)
