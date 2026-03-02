from unittest.mock import AsyncMock, patch

from fastapi import HTTPException


class TestEvaluateEndpoint:
    def test_valid_fen_cp_evaluation(self, test_client, starting_fen, mock_stockfish_evaluation):
        with patch("app.api.v1.endpoints.evaluate.asyncio") as mock_asyncio:
            mock_asyncio.to_thread = AsyncMock(return_value=mock_stockfish_evaluation)
            response = test_client.get(f"/api/v1/evaluate/{starting_fen}")

        assert response.status_code == 200
        data = response.json()
        assert data["fen"] == starting_fen
        assert data["evaluation_type"] == "cp"
        assert data["evaluation_value"] == 30
        assert data["best_move_uci"] == "e2e4"
        assert data["best_move_san"] == "e4"
        assert data["depth"] == 20

    def test_invalid_fen(self, test_client, invalid_fen):
        response = test_client.get(f"/api/v1/evaluate/{invalid_fen}")
        assert response.status_code == 400

    def test_stockfish_unavailable(self, test_client, starting_fen):
        with patch("app.api.v1.endpoints.evaluate.asyncio") as mock_asyncio:
            mock_asyncio.to_thread = AsyncMock(
                side_effect=HTTPException(status_code=503, detail="Stockfish non disponible")
            )
            response = test_client.get(f"/api/v1/evaluate/{starting_fen}")

        assert response.status_code == 503

    def test_mate_evaluation(self, test_client, starting_fen):
        mate_eval = {
            "evaluation_type": "mate",
            "evaluation_value": 3,
            "best_move_uci": "d2d4",
            "best_move_san": "d4",
            "depth": 20,
        }
        with patch("app.api.v1.endpoints.evaluate.asyncio") as mock_asyncio:
            mock_asyncio.to_thread = AsyncMock(return_value=mate_eval)
            response = test_client.get(f"/api/v1/evaluate/{starting_fen}")

        assert response.status_code == 200
        data = response.json()
        assert data["evaluation_type"] == "mate"
        assert data["evaluation_value"] == 3

    def test_response_has_all_fields(self, test_client, starting_fen, mock_stockfish_evaluation):
        with patch("app.api.v1.endpoints.evaluate.asyncio") as mock_asyncio:
            mock_asyncio.to_thread = AsyncMock(return_value=mock_stockfish_evaluation)
            response = test_client.get(f"/api/v1/evaluate/{starting_fen}")

        assert response.status_code == 200
        data = response.json()
        expected_fields = {"fen", "evaluation_type", "evaluation_value", "best_move_uci", "best_move_san", "depth"}
        assert set(data.keys()) == expected_fields
