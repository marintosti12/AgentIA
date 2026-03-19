import logging

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.agent.graph import run_agent
from app.services import mongodb_service
from app.utils.fen_validator import validate_fen

logger = logging.getLogger(__name__)

router = APIRouter()


class AgentResponse(BaseModel):
    fen: str
    response: str
    tools_used: list[str]
    opening_name: str


class HistoryEntry(BaseModel):
    fen: str
    opening_name: str
    agent_response: str
    tools_used: list[str]
    created_at: str


class HistoryResponse(BaseModel):
    count: int
    entries: list[HistoryEntry]


@router.post("/agent/analyze", response_model=AgentResponse)
async def analyze_position(fen: str = Query(..., description="Position FEN a analyser")):
    validate_fen(fen)

    result = await run_agent(fen)

    try:
        await mongodb_service.save_analysis(
            fen=result["fen"],
            agent_response=result["response"],
            tools_used=result["tools_used"],
            opening_name=result["opening_name"],
        )
    except Exception as e:
        logger.warning("Failed to save analysis to MongoDB: %s", e)

    return AgentResponse(**result)


@router.get("/agent/history", response_model=HistoryResponse)
async def get_history(limit: int = Query(20, ge=1, le=100)):
    entries = await mongodb_service.get_analysis_history(limit=limit)
    formatted = []
    for e in entries:
        formatted.append(HistoryEntry(
            fen=e.get("fen", ""),
            opening_name=e.get("opening_name", ""),
            agent_response=e.get("agent_response", ""),
            tools_used=e.get("tools_used", []),
            created_at=str(e.get("created_at", "")),
        ))
    return HistoryResponse(count=len(formatted), entries=formatted)
