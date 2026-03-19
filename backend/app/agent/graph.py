import logging
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from app.agent.tools import get_all_tools
from app.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Tu es un coach d'echecs expert au service de la Federation Francaise des Echecs (FFE).
Tu accompagnes de jeunes joueurs dans l'apprentissage des ouvertures.

Quand on te donne une position FEN, tu dois :
1. Chercher les coups d'ouverture dans la base Lichess (get_opening_moves)
2. Chercher le contexte de l'ouverture dans Wikichess (search_opening_context)
3. Si la position est hors theorie (pas de coups Lichess), evaluer avec Stockfish (evaluate_position)
4. Si tu identifies l'ouverture, chercher des videos explicatives (search_youtube_videos)

Reponds TOUJOURS en francais. Sois pedagogique et encourage le joueur.
IMPORTANT: Ne formate PAS ta reponse en markdown (pas de #, **, [], etc). Ecris en texte brut uniquement.
Structure ta reponse ainsi :
- Commence par le nom de l'ouverture si identifiee
- Explique le plan et les idees de la position
- Donne les coups recommandes avec justification
- Mentionne le titre d'une video si disponible"""


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


_graph = None


def _should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END


def build_graph():
    tools = get_all_tools()
    model = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=0.3,
    ).bind_tools(tools)

    async def call_model(state: AgentState) -> dict:
        response = await model.ainvoke(state["messages"])
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", _should_continue, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")

    return graph.compile()


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
        logger.info("LangGraph agent compiled")
    return _graph


async def run_agent(fen: str) -> dict:
    graph = get_graph()

    initial_state = {
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=f"Analyse cette position FEN et guide-moi : {fen}"),
        ]
    }

    result = await graph.ainvoke(initial_state)

    final_message = result["messages"][-1]
    response_text = final_message.content if isinstance(final_message, AIMessage) else str(final_message)

    tools_used = []
    for msg in result["messages"]:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["name"] not in tools_used:
                    tools_used.append(tc["name"])

    opening_name = ""
    for msg in result["messages"]:
        content = msg.content if hasattr(msg, "content") else ""
        if isinstance(content, str):
            for name in ["Italienne", "Espagnole", "Sicilienne", "Francaise", "Caro-Kann",
                         "Gambit Dame", "Indienne du Roi", "Pirc", "Anglaise", "Hollandaise"]:
                if name.lower() in content.lower():
                    opening_name = name
                    break
        if opening_name:
            break

    return {
        "fen": fen,
        "response": response_text,
        "tools_used": tools_used,
        "opening_name": opening_name,
    }
