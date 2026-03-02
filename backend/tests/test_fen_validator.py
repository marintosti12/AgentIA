import chess
import pytest
from fastapi import HTTPException

from app.utils.fen_validator import validate_fen


class TestFenValidator:
    def test_valid_starting_position(self, starting_fen):
        board = validate_fen(starting_fen)
        assert board is not None
        assert board.is_valid()

    def test_valid_italian_game(self, italian_game_fen):
        board = validate_fen(italian_game_fen)
        assert board is not None
        assert board.is_valid()

    def test_invalid_format(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_fen("ceci-nest-pas-un-fen")
        assert exc_info.value.status_code == 400
        assert "FEN invalide" in exc_info.value.detail

    def test_empty_string(self):
        with pytest.raises(HTTPException) as exc_info:
            validate_fen("")
        assert exc_info.value.status_code == 400

    def test_illegal_position_no_kings(self):
        # Position sans rois → invalide
        illegal_fen = "8/8/8/8/8/8/8/8 w - - 0 1"
        with pytest.raises(HTTPException) as exc_info:
            validate_fen(illegal_fen)
        assert exc_info.value.status_code == 400

    def test_returns_chess_board(self, starting_fen):
        board = validate_fen(starting_fen)
        assert isinstance(board, chess.Board)

    def test_fen_after_one_move(self):
        # Après 1.e4
        fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"
        board = validate_fen(fen)
        assert board is not None
        assert board.turn is False  # Trait aux noirs

    @pytest.mark.parametrize("fen", [
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
        "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
        "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    ])
    def test_multiple_valid_fens(self, fen):
        board = validate_fen(fen)
        assert board.is_valid()

    @pytest.mark.parametrize("fen", [
        "",
        "invalid",
        "8/8/8/8/8/8/8/8 w - - 0 1",
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP w KQkq - 0 1",  # Rangée manquante
    ])
    def test_multiple_invalid_fens(self, fen):
        with pytest.raises(HTTPException) as exc_info:
            validate_fen(fen)
        assert exc_info.value.status_code == 400
