import chess
from fastapi import HTTPException


def validate_fen(fen: str) -> chess.Board:
    try:
        board = chess.Board(fen)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"FEN invalide: {e}")
    if not board.is_valid():
        raise HTTPException(status_code=400, detail="FEN invalide: position illegale")
    return board
