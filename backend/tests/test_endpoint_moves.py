from unittest.mock import AsyncMock, patch

from fastapi import HTTPException

from app.services import lichess_service


class TestMovesEndpoint:
    def test_valid_fen_with_moves_sorted(self, test_client, starting_fen, mock_lichess_response):
        with patch.object(
            lichess_service, "get_opening_moves",
            new_callable=AsyncMock,
            return_value=mock_lichess_response,
        ):
            response = test_client.get(f"/api/v1/moves/{starting_fen}")

        assert response.status_code == 200
        data = response.json()
        assert data["fen"] == starting_fen
        assert len(data["moves"]) == 3
        # Vérifier le tri décroissant par total_games
        totals = [m["total_games"] for m in data["moves"]]
        assert totals == sorted(totals, reverse=True)
        assert data["moves"][0]["san"] == "e4"
        assert data["moves"][1]["san"] == "d4"
        assert data["moves"][2]["san"] == "c4"

    def test_invalid_fen(self, test_client, invalid_fen):
        response = test_client.get(f"/api/v1/moves/{invalid_fen}")
        assert response.status_code == 400

    def test_lichess_timeout(self, test_client, starting_fen):
        with patch.object(
            lichess_service, "get_opening_moves",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=504, detail="Lichess Explorer timeout"),
        ):
            response = test_client.get(f"/api/v1/moves/{starting_fen}")

        assert response.status_code == 504

    def test_lichess_rate_limit(self, test_client, starting_fen):
        with patch.object(
            lichess_service, "get_opening_moves",
            new_callable=AsyncMock,
            side_effect=HTTPException(status_code=429, detail="Rate limit"),
        ):
            response = test_client.get(f"/api/v1/moves/{starting_fen}")

        assert response.status_code == 429

    def test_empty_moves(self, test_client, starting_fen):
        with patch.object(
            lichess_service, "get_opening_moves",
            new_callable=AsyncMock,
            return_value={"moves": []},
        ):
            response = test_client.get(f"/api/v1/moves/{starting_fen}")

        assert response.status_code == 200
        data = response.json()
        assert data["moves"] == []
        assert data["total_games"] == 0
