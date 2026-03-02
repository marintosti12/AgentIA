from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.services import lichess_service


class TestGetOpeningMoves:
    @pytest.fixture(autouse=True)
    def reset_client(self):
        """Reset le client entre chaque test."""
        original = lichess_service._client
        yield
        lichess_service._client = original

    async def test_success(self, mock_lichess_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_lichess_response

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch.object(lichess_service, "get_client", return_value=mock_client):
            result = await lichess_service.get_opening_moves("some/fen")

        assert result == mock_lichess_response
        assert "moves" in result

    async def test_timeout_raises_504(self):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        with patch.object(lichess_service, "get_client", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await lichess_service.get_opening_moves("some/fen")
            assert exc_info.value.status_code == 504

    async def test_connection_error_raises_502(self):
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.ConnectError("connection failed"))

        with patch.object(lichess_service, "get_client", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await lichess_service.get_opening_moves("some/fen")
            assert exc_info.value.status_code == 502

    async def test_rate_limit_raises_429(self):
        mock_response = MagicMock()
        mock_response.status_code = 429

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch.object(lichess_service, "get_client", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await lichess_service.get_opening_moves("some/fen")
            assert exc_info.value.status_code == 429

    async def test_server_error_raises_502(self):
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch.object(lichess_service, "get_client", return_value=mock_client):
            with pytest.raises(HTTPException) as exc_info:
                await lichess_service.get_opening_moves("some/fen")
            assert exc_info.value.status_code == 502

    async def test_empty_moves(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"moves": []}

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)

        with patch.object(lichess_service, "get_client", return_value=mock_client):
            result = await lichess_service.get_opening_moves("some/fen")

        assert result["moves"] == []
