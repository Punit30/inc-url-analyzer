from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from sqlmodel import select, func

from app.core.session import get_session
from app.models.blog_web_post import BlogWebPost
from app.models.enums.platform import PlatformEnum
from app.models.post import Post
from app.models.url import URL
from app.schemas.Responses.error_response import ErrorResponse
from app.models.enums.url import  URLListSortingEnum
from app.schemas.Responses.url_response import TotalURLCountResponse, URLListingResponse

router = APIRouter()

@router.get("/all", response_model=URLListingResponse, responses={
    200: {"description": "All URL retrieved", "model": URLListingResponse},
    500: {"model": ErrorResponse}
}, summary="Get all URL with platform breakdown")
async def url_listing(
        date_uploaded: Optional[str] = Query(None, description="Filter URLs by creation date (YYYY-MM-DD)"),
        sort_by: Optional[URLListSortingEnum] = Query(None,
                                       description="Sort by engagement rate: engagement_rate_asc or engagement_rate_desc"),
        db: Session = Depends(get_session)):
    pass


@router.get("/url-counts", response_model=TotalURLCountResponse,
            responses={200: {"description": "URL count fetched successfully", "model": TotalURLCountResponse, },
                       500: {"model": ErrorResponse}},
            status_code=status.HTTP_200_OK,
            summary="Get total URL count",
            tags=["URL Stats"])
async def url_count(db: Session = Depends(get_session)):
    try:
        total_urls: int | None = db.exec(select(func.count(URL.id))).first()
        return TotalURLCountResponse(total_urls=total_urls)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.get("/stats")
async def all_url_analysis(params: Dict[str, str], db: Session = Depends(get_session)):
    # Get total URLs
    total_urls = db.query(URL).count()

    # Get platform counts and percentages
    platform_stats = {}

    # Count URLs with posts (Facebook, Instagram, YouTube)
    social_platform_counts = db.query(
        URL.id
    ).join(Post).distinct().count()

    # Count URLs with blog posts (Website)
    website_count = db.query(
        URL.id
    ).join(BlogWebPost).distinct().count()

    # Calculate percentages
    platform_stats = {
        PlatformEnum.FACEBOOK.value: {
            "count": social_platform_counts // 3,  # Approximate split between social platforms
            "percentage": round((social_platform_counts / 3 / total_urls * 100) if total_urls > 0 else 0, 2)
        },
        PlatformEnum.INSTAGRAM.value: {
            "count": social_platform_counts // 3,
            "percentage": round((social_platform_counts / 3 / total_urls * 100) if total_urls > 0 else 0, 2)
        },
        PlatformEnum.YOUTUBE.value: {
            "count": social_platform_counts // 3,
            "percentage": round((social_platform_counts / 3 / total_urls * 100) if total_urls > 0 else 0, 2)
        },
        PlatformEnum.WEBSITE.value: {
            "count": website_count,
            "percentage": round((website_count / total_urls * 100) if total_urls > 0 else 0, 2)
        }
    }

    # Get top performer URL based on engagement rate
    top_url = db.query(URL).order_by(desc(URL.engagementRate)).first()

    # Get latest analyzed date from posts
    latest_date = db.query(func.max(Post.dateAnalysed)).scalar()

    return {
        "total_urls": total_urls,
        "latest_date_analyzed": latest_date,
        "platform_stats": platform_stats,
        "top_performer_url": {
            "url": top_url.url if top_url else None,
            "engagement_rate": top_url.engagementRate if top_url else 0
        }
    }


@router.get("/analysis/{url_id}")
async def get_url_analysis(params: Dict[str, str], db: Session = Depends(get_session)):
    pass
