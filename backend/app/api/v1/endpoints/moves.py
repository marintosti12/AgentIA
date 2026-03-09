from fastapi import APIRouter, Query

from app.models.chess_models import MovesResponse, MoveStats
from app.services import lichess_service
from app.utils.fen_validator import validate_fen

router = APIRouter()


@router.get("/moves", response_model=MovesResponse)
async def get_moves(fen: str = Query(..., description="Position FEN")):
    _ = validate_fen(fen)
    data = await lichess_service.get_opening_moves(fen)

    moves = []
    for m in data.get("moves", []):
        total = m.get("white", 0) + m.get("draws", 0) + m.get("black", 0)
        moves.append(
            MoveStats(
                uci=m["uci"],
                san=m["san"],
                white=m.get("white", 0),
                draws=m.get("draws", 0),
                black=m.get("black", 0),
                average_rating=m.get("averageRating"),
                total_games=total,
            )
        )

    moves.sort(key=lambda m: m.total_games, reverse=True)

    total_games = sum(m.total_games for m in moves)

    return MovesResponse(fen=fen, total_games=total_games, moves=moves)
