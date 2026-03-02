from pydantic import BaseModel


class MoveStats(BaseModel):
    uci: str
    san: str
    white: int
    draws: int
    black: int
    average_rating: int | None = None
    total_games: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "uci": "e2e4",
                    "san": "e4",
                    "white": 50000,
                    "draws": 30000,
                    "black": 40000,
                    "average_rating": 2350,
                    "total_games": 120000,
                }
            ]
        }
    }


class MovesResponse(BaseModel):
    fen: str
    total_games: int
    moves: list[MoveStats]

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                    "total_games": 120000,
                    "moves": [
                        {
                            "uci": "e2e4",
                            "san": "e4",
                            "white": 50000,
                            "draws": 30000,
                            "black": 40000,
                            "average_rating": 2350,
                            "total_games": 120000,
                        }
                    ],
                }
            ]
        }
    }


class EvaluationResponse(BaseModel):
    fen: str
    evaluation_type: str  # "cp" or "mate"
    evaluation_value: int
    best_move_uci: str
    best_move_san: str
    depth: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
                    "evaluation_type": "cp",
                    "evaluation_value": 30,
                    "best_move_uci": "e7e5",
                    "best_move_san": "e5",
                    "depth": 20,
                }
            ]
        }
    }
