from unittest.mock import MagicMock, patch

import chess
import pytest
from fastapi import HTTPException
from stockfish import StockfishException

from app.services import stockfish_service


class TestEvaluatePosition:
    def setup_method(self):
        self.board = chess.Board()
        self.fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    def test_evaluate_centipawns(self):
        mock_engine = MagicMock()
        mock_engine.get_evaluation.return_value = {"type": "cp", "value": 30}
        mock_engine.get_best_move.return_value = "e2e4"

        with patch.object(stockfish_service, "_engine", mock_engine):
            result = stockfish_service.evaluate_position(self.fen, self.board)

        assert result["evaluation_type"] == "cp"
        assert result["evaluation_value"] == 30
        assert result["best_move_uci"] == "e2e4"
        assert result["best_move_san"] == "e4"

    def test_evaluate_mate(self):
        mock_engine = MagicMock()
        mock_engine.get_evaluation.return_value = {"type": "mate", "value": 3}
        mock_engine.get_best_move.return_value = "d2d4"

        with patch.object(stockfish_service, "_engine", mock_engine):
            result = stockfish_service.evaluate_position(self.fen, self.board)

        assert result["evaluation_type"] == "mate"
        assert result["evaluation_value"] == 3

    def test_engine_none_raises_503(self):
        with patch.object(stockfish_service, "_engine", None):
            with pytest.raises(HTTPException) as exc_info:
                stockfish_service.evaluate_position(self.fen, self.board)
            assert exc_info.value.status_code == 503

    def test_best_move_none_raises_400(self):
        mock_engine = MagicMock()
        mock_engine.get_evaluation.return_value = {"type": "cp", "value": 0}
        mock_engine.get_best_move.return_value = None

        with patch.object(stockfish_service, "_engine", mock_engine):
            with pytest.raises(HTTPException) as exc_info:
                stockfish_service.evaluate_position(self.fen, self.board)
            assert exc_info.value.status_code == 400

    def test_stockfish_exception_raises_503(self):
        mock_engine = MagicMock()
        mock_engine.set_fen_position.side_effect = StockfishException("Engine crashed")

        with patch.object(stockfish_service, "_engine", mock_engine):
            with pytest.raises(HTTPException) as exc_info:
                stockfish_service.evaluate_position(self.fen, self.board)
            assert exc_info.value.status_code == 503

    def test_lock_is_used(self):
        mock_engine = MagicMock()
        mock_engine.get_evaluation.return_value = {"type": "cp", "value": 0}
        mock_engine.get_best_move.return_value = "e2e4"
        mock_lock = MagicMock()

        with patch.object(stockfish_service, "_engine", mock_engine), \
             patch.object(stockfish_service, "_lock", mock_lock):
            stockfish_service.evaluate_position(self.fen, self.board)

        mock_lock.__enter__.assert_called_once()
