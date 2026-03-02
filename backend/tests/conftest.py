import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.router import router as v1_router


def _create_test_app() -> FastAPI:
    """Crée une app FastAPI de test sans lifespan (pas de Stockfish réel)."""
    test_app = FastAPI()
    test_app.include_router(v1_router, prefix="/api/v1")
    return test_app


@pytest.fixture
def test_client():
    app = _create_test_app()
    return TestClient(app)


@pytest.fixture
def starting_fen():
    return "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"


@pytest.fixture
def italian_game_fen():
    """Position après 1.e4 e5 2.Nf3 Nc6 3.Bc4"""
    return "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"


@pytest.fixture
def invalid_fen():
    return "ceci-nest-pas-un-fen"


@pytest.fixture
def mock_lichess_response():
    """Réponse type Lichess Explorer avec coups dans un ordre non trié."""
    return {
        "white": 10000,
        "draws": 5000,
        "black": 8000,
        "moves": [
            {
                "uci": "c2c4",
                "san": "c4",
                "white": 1000,
                "draws": 500,
                "black": 500,
                "averageRating": 2350,
            },
            {
                "uci": "e2e4",
                "san": "e4",
                "white": 5000,
                "draws": 2500,
                "black": 3000,
                "averageRating": 2400,
            },
            {
                "uci": "d2d4",
                "san": "d4",
                "white": 3500,
                "draws": 2000,
                "black": 4000,
                "averageRating": 2380,
            },
        ],
    }


@pytest.fixture
def mock_stockfish_evaluation():
    """Réponse type évaluation Stockfish."""
    return {
        "evaluation_type": "cp",
        "evaluation_value": 30,
        "best_move_uci": "e2e4",
        "best_move_san": "e4",
        "depth": 20,
    }
