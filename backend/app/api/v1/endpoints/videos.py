from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services import youtube_service

router = APIRouter()


class VideoResult(BaseModel):
    video_id: str
    title: str
    description: str
    channel: str
    published_at: str
    thumbnail: str
    url: str
    embed_url: str
    duration: str
    view_count: int


class VideosResponse(BaseModel):
    opening: str
    count: int
    videos: list[VideoResult]


@router.get("/videos/{opening}", response_model=VideosResponse)
async def get_videos(
    opening: str,
    max_results: int = Query(5, ge=1, le=10, description="Nombre de vidéos"),
):
    try:
        videos = youtube_service.search_videos(
            opening_name=opening, max_results=max_results
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    if not videos:
        raise HTTPException(
            status_code=404,
            detail=f"Aucune vidéo trouvée pour l'ouverture '{opening}'",
        )

    return VideosResponse(
        opening=opening,
        count=len(videos),
        videos=[VideoResult(**v) for v in videos],
    )
