from app.models.chess_models import EvaluationResponse, MoveStats, MovesResponse


class TestMoveStats:
    def test_create_with_all_values(self):
        move = MoveStats(
            uci="e2e4",
            san="e4",
            white=5000,
            draws=2500,
            black=3000,
            average_rating=2400,
            total_games=10500,
        )
        assert move.uci == "e2e4"
        assert move.san == "e4"
        assert move.average_rating == 2400
        assert move.total_games == 10500

    def test_create_without_average_rating(self):
        move = MoveStats(
            uci="d2d4",
            san="d4",
            white=100,
            draws=50,
            black=80,
            total_games=230,
        )
        assert move.average_rating is None
        assert move.total_games == 230


class TestMovesResponse:
    def test_create_with_moves(self):
        moves = [
            MoveStats(uci="e2e4", san="e4", white=5000, draws=2500, black=3000, total_games=10500),
            MoveStats(uci="d2d4", san="d4", white=4000, draws=2000, black=4500, total_games=10500),
        ]
        response = MovesResponse(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            total_games=21000,
            moves=moves,
        )
        assert len(response.moves) == 2
        assert response.total_games == 21000

    def test_create_empty_moves(self):
        response = MovesResponse(
            fen="rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
            total_games=0,
            moves=[],
        )
        assert response.moves == []
        assert response.total_games == 0


class TestEvaluationResponse:
    def test_create_cp_evaluation(self):
        response = EvaluationResponse(
            fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
            evaluation_type="cp",
            evaluation_value=30,
            best_move_uci="e7e5",
            best_move_san="e5",
            depth=20,
        )
        assert response.evaluation_type == "cp"
        assert response.evaluation_value == 30
        assert response.depth == 20

    def test_create_mate_evaluation(self):
        response = EvaluationResponse(
            fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
            evaluation_type="mate",
            evaluation_value=3,
            best_move_uci="d1h5",
            best_move_san="Qh5#",
            depth=20,
        )
        assert response.evaluation_type == "mate"
        assert response.evaluation_value == 3
