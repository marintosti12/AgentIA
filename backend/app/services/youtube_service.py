import logging

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.core.config import settings

logger = logging.getLogger(__name__)

_youtube = None


def init_youtube() -> None:
    global _youtube
    if not settings.youtube_api_key:
        logger.warning("YOUTUBE_API_KEY not set, YouTube service disabled")
        return
    _youtube = build("youtube", "v3", developerKey=settings.youtube_api_key)
    logger.info("YouTube service initialized")


def search_videos(opening_name: str, max_results: int | None = None) -> list[dict]:
    if _youtube is None:
        raise RuntimeError("YouTube service not initialized (check YOUTUBE_API_KEY)")

    if max_results is None:
        max_results = settings.youtube_max_results

    query = f"{opening_name} chess opening tutorial"

    try:
        search_response = (
            _youtube.search()
            .list(
                q=query,
                part="snippet",
                type="video",
                maxResults=max_results,
                order="relevance",
                relevanceLanguage="fr",
                videoEmbeddable="true",
            )
            .execute()
        )
    except HttpError as e:
        logger.error("YouTube API error: %s", e)
        raise RuntimeError(f"YouTube API error: {e.resp.status}") from e

    videos = []
    video_ids = [item["id"]["videoId"] for item in search_response.get("items", [])]

    if not video_ids:
        return videos

    # Fetch video details for duration, view count, etc.
    try:
        details_response = (
            _youtube.videos()
            .list(
                part="contentDetails,statistics",
                id=",".join(video_ids),
            )
            .execute()
        )
    except HttpError:
        details_response = {"items": []}

    details_map = {}
    for item in details_response.get("items", []):
        details_map[item["id"]] = {
            "duration": item.get("contentDetails", {}).get("duration", ""),
            "view_count": int(
                item.get("statistics", {}).get("viewCount", 0)
            ),
        }

    for item in search_response.get("items", []):
        video_id = item["id"]["videoId"]
        snippet = item["snippet"]
        detail = details_map.get(video_id, {})

        videos.append(
            {
                "video_id": video_id,
                "title": snippet.get("title", ""),
                "description": snippet.get("description", ""),
                "channel": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "thumbnail": snippet.get("thumbnails", {})
                .get("high", {})
                .get("url", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
                "duration": detail.get("duration", ""),
                "view_count": detail.get("view_count", 0),
            }
        )

    # Sort by view count to prioritize quality content
    videos.sort(key=lambda v: v["view_count"], reverse=True)

    return videos
