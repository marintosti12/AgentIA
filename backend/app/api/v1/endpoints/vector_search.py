from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services import milvus_service

router = APIRouter()


class SearchResult(BaseModel):
    title: str
    chunk: str
    source: str
    opening_name: str
    score: float


class VectorSearchResponse(BaseModel):
    query: str
    results: list[SearchResult]


@router.get("/vector-search", response_model=VectorSearchResponse)
async def vector_search(
    query: str = Query(..., description="Recherche textuelle sur les ouvertures"),
    top_k: int = Query(5, ge=1, le=20, description="Nombre de résultats"),
):
    try:
        results = milvus_service.search(query=query, top_k=top_k)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return VectorSearchResponse(
        query=query,
        results=[SearchResult(**r) for r in results],
    )
