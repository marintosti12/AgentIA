import threading

import chess
from fastapi import HTTPException
from stockfish import Stockfish, StockfishException

from app.core.config import settings

_engine: Stockfish | None = None
_lock = threading.Lock()


def init_engine() -> None:
    global _engine
    try:
        _engine = Stockfish(
            path=settings.stockfish_path,
            depth=settings.stockfish_depth,
        )
    except Exception as e:
        _engine = None
        raise RuntimeError(f"Impossible d'initialiser Stockfish: {e}")


def shutdown_engine() -> None:
    global _engine
    if _engine is not None:
        try:
            del _engine
        except Exception:
            pass
        _engine = None


def evaluate_position(fen: str, board: chess.Board) -> dict:
    if _engine is None:
        raise HTTPException(status_code=503, detail="Stockfish non disponible")

    with _lock:
        try:
            _engine.set_fen_position(fen)
            evaluation = _engine.get_evaluation()
            best_move_uci = _engine.get_best_move()
        except StockfishException as e:
            raise HTTPException(status_code=503, detail=f"Erreur Stockfish: {e}")

    if best_move_uci is None:
        raise HTTPException(status_code=400, detail="Aucun coup possible dans cette position")

    best_move = chess.Move.from_uci(best_move_uci)
    best_move_san = board.san(best_move)

    eval_type = evaluation["type"]  # "cp" or "mate"
    eval_value = evaluation["value"]

    return {
        "evaluation_type": eval_type,
        "evaluation_value": eval_value,
        "best_move_uci": best_move_uci,
        "best_move_san": best_move_san,
        "depth": settings.stockfish_depth,
    }
