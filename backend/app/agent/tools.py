import asyncio
import logging

import chess
from langchain_core.tools import tool

from app.services import lichess_service, milvus_service, stockfish_service, youtube_service

logger = logging.getLogger(__name__)


@tool
def evaluate_position(fen: str) -> str:
    """Evalue une position d'echecs avec le moteur Stockfish.
    Utilise cet outil quand la position semble hors de la theorie des ouvertures
    ou quand tu veux donner le meilleur coup objectif.
    Argument: fen - la position en notation FEN.
    """
    try:
        board = chess.Board(fen)
        result = stockfish_service.evaluate_position(fen, board)
        eval_type = result["evaluation_type"]
        eval_value = result["evaluation_value"]
        best_san = result["best_move_san"]

        if eval_type == "mate":
            eval_text = f"Mat en {eval_value} coups"
        else:
            eval_text = f"{eval_value / 100:+.2f} pions"

        return (
            f"Evaluation Stockfish (profondeur {result['depth']}): {eval_text}. "
            f"Meilleur coup: {best_san}."
        )
    except Exception as e:
        logger.error("Stockfish evaluation error: %s", e)
        return f"Erreur d'evaluation Stockfish: {e}"


@tool
async def get_opening_moves(fen: str) -> str:
    """Recupere les coups d'ouverture depuis la base de donnees Lichess.
    Utilise cet outil pour connaitre les coups les plus joues dans cette position
    et leurs statistiques (victoires, nulles, defaites).
    Argument: fen - la position en notation FEN.
    """
    try:
        data = await lichess_service.get_opening_moves(fen)
        moves = data.get("moves", [])

        if not moves:
            return "Aucune partie trouvee dans la base Lichess pour cette position. La position est probablement hors de la theorie des ouvertures."

        total = data.get("white", 0) + data.get("draws", 0) + data.get("black", 0)
        lines = [f"Position trouvee dans {total} parties. Coups les plus joues:"]

        for m in moves[:5]:
            m_total = m.get("white", 0) + m.get("draws", 0) + m.get("black", 0)
            if m_total == 0:
                continue
            win_pct = round(m.get("white", 0) / m_total * 100)
            draw_pct = round(m.get("draws", 0) / m_total * 100)
            lines.append(
                f"- {m.get('san', m.get('uci', '?'))}: {m_total} parties "
                f"(Blancs {win_pct}%, Nulles {draw_pct}%, Noirs {100 - win_pct - draw_pct}%)"
            )

        return "\n".join(lines)
    except Exception as e:
        logger.error("Lichess moves error: %s", e)
        return f"Erreur Lichess: {e}"


@tool
def search_opening_context(query: str) -> str:
    """Recherche des informations sur les ouvertures dans la base Wikichess (base vectorielle Milvus).
    Utilise cet outil pour trouver le nom de l'ouverture, son histoire, ses variantes et ses principes.
    Argument: query - une description de la position ou le nom de l'ouverture.
    """
    try:
        results = milvus_service.search(query=query, top_k=3)
        if not results:
            return "Aucun resultat trouve dans la base Wikichess."

        lines = []
        for r in results:
            lines.append(f"[{r['opening_name']}] {r['chunk']}")

        return "\n\n".join(lines)
    except Exception as e:
        logger.error("Milvus search error: %s", e)
        return f"Erreur recherche Wikichess: {e}"


@tool
def search_youtube_videos(opening_name: str) -> str:
    """Recherche des videos YouTube explicatives sur une ouverture d'echecs.
    Utilise cet outil uniquement quand tu as identifie le nom de l'ouverture.
    Argument: opening_name - le nom de l'ouverture (ex: 'Sicilienne', 'Italienne').
    """
    try:
        videos = youtube_service.search_videos(opening_name=opening_name, max_results=3)
        if not videos:
            return f"Aucune video trouvee pour '{opening_name}'."

        lines = [f"Videos trouvees pour '{opening_name}':"]
        for v in videos:
            lines.append(f"- \"{v['title']}\" par {v['channel']} ({v['view_count']} vues) - {v['url']}")

        return "\n".join(lines)
    except Exception as e:
        logger.error("YouTube search error: %s", e)
        return f"Erreur YouTube: {e}"


def get_all_tools():
    return [evaluate_position, get_opening_moves, search_opening_context, search_youtube_videos]
