from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import selectinload
from sqlmodel import select, func, Session

from app.core.session import get_session
from app.models.blog_web_post import BlogWebPost
from app.models.entity import Entity
from app.models.enums.url import URLListSortingEnum, URLTypeEnum
from app.models.post import Post
from app.models.url import URL
from app.schemas.responses.error import ErrorResponse
from app.schemas.responses.url import TotalURLCountResponse, URLListingResponse, URLAnalysisSummaryResponse, \
    OverallURLSummaryResponse
from app.services.url import get_platform_summary

router = APIRouter()


@router.get("/all", response_model=URLListingResponse, responses={
    200: {"description": "All URL retrieved", "model": URLListingResponse},
    500: {"model": ErrorResponse}
}, summary="Get all URL with platform breakdown", tags=["URL"])
async def url_listing(
        date_uploaded: Optional[str] = Query(None, description="Filter URLs by creation date (YYYY-MM-DD)"),
        sort_by: Optional[URLListSortingEnum] = Query("engagement_rate_desc",
                                                      description="Sort by engagement rate: engagement_rate_asc or engagement_rate_desc"),
        db: Session = Depends(get_session)):
    try:
        created_date_filter = None
        if date_uploaded:
            try:
                created_date_filter = datetime.strptime(date_uploaded, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        url_details = []
        url_type_filters = [
            (Post, URLTypeEnum.POST),
            (BlogWebPost, URLTypeEnum.WEB_POST)
        ]

        for model, url_type in url_type_filters:
            query = select(model).join(URL).join(Entity)
            if created_date_filter:
                query = query.where(func.date(URL.created_date) == created_date_filter)
            results = db.exec(query).all()

            for item in results:
                url_obj = item.url
                if not url_obj or not url_obj.entity or url_obj.type != url_type:
                    continue

                rate = getattr(item, "engagementRate", 0)
                platform = url_obj.entity.platform
                created = url_obj.created_date

                url_details.append({
                    "id": url_obj.id,
                    "url": url_obj.url,
                    "engagement_rate": rate,
                    "platform": platform,
                    "date_uploaded": created.strftime("%Y-%m-%d"),
                    "is_fetched": getattr(item, "isFetched", False),
                    "is_broken_or_deleted": getattr(item, "isBrokenOrDeleted", False)
                })

        reverse = sort_by.value == "engagement_rate_desc"
        url_details.sort(
            key=lambda x: (
                x.get("engagement_rate") or 0,
                datetime.strptime(x.get("date_uploaded", "1900-01-01"), "%Y-%m-%d")
            ),
            reverse=reverse
        )

        return URLListingResponse(urls=url_details)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to fetch URL details.")

@router.get("/summary", response_model=OverallURLSummaryResponse, responses={
    200: {"description": "Platform summary retrieved", "model": OverallURLSummaryResponse},
    500: {"model": ErrorResponse}
}, summary="Get platform summary for all or by date", tags=["URL"])
async def platform_summary(
        date_uploaded: Optional[str] = Query(None, description="Filter URLs by creation date (YYYY-MM-DD)"),
        db: Session = Depends(get_session)):

    try:
        created_date_filter = None
        if date_uploaded:
            try:
                created_date_filter = datetime.strptime(date_uploaded, "%Y-%m-%d").date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        summary = get_platform_summary(db, created_date_filter)

        return OverallURLSummaryResponse(
            total_urls_count=summary["total"],
            facebook_percent=summary["facebook_percent"],
            instagram_percent=summary["instagram_percent"],
            website_percent=summary["website_percent"],
            youtube_percent=summary["youtube_percent"],
            top_platform=summary["top_platform"],
            top_url=summary["top_url"]
        )

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to fetch platform summary.")


@router.get("/url-counts", response_model=TotalURLCountResponse,
            responses={200: {"description": "URL count fetched successfully", "model": TotalURLCountResponse, },
                       500: {"model": ErrorResponse}},
            status_code=status.HTTP_200_OK,
            summary="Get total URL count",
            tags=["URL"])
async def url_count(db: Session = Depends(get_session)):
    try:
        total_urls: int | None = db.exec(select(func.count(URL.id))).first()
        return TotalURLCountResponse(total_urls=total_urls)
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.get("/analysis/{url_id}", response_model=URLAnalysisSummaryResponse, responses={
    200: {"description": "All URL retrieved", "model": URLListingResponse},
    500: {"model": ErrorResponse}
}, summary="Get URL analysis", tags=["URL"])
async def get_url_analysis(url_id: int, db: Session = Depends(get_session)):
    try:
        url: Optional[URL] = db.exec(select(URL).options(selectinload(URL.entity), selectinload(URL.posts),
                                                         selectinload(URL.blogWebPosts)).where(
            URL.id == url_id)).first()

        if not url:
            raise HTTPException(status_code=404, detail="URL not found")

        response_data = {
            "url_id": url.id,
            "post_url": url.url,
            "user_profile_name": url.entity.fullname if url.entity else None,
            "url_type": url.type,
            "latest_likes": None,
            "latest_views": None,
            "latest_comments": None,
            "latest_engagement_rate": 0.0,
            "traffic_count": None
        }

        # Depending on URL type, fetch and update
        if url.type == URLTypeEnum.POST:
            if url.posts:
                latest_post = max(url.posts, key=lambda p: p.dateAnalysed)
                response_data.update({
                    "latest_likes": latest_post.likes,
                    "latest_views": latest_post.views,
                    "latest_comments": latest_post.comments,
                    "latest_engagement_rate": latest_post.engagementRate
                })

        elif url.type == URLTypeEnum.WEB_POST:
            if url.blogWebPosts:
                latest_blog = max(url.blogWebPosts, key=lambda b: b.dateAnalysed)
                response_data.update({
                    "latest_engagement_rate": latest_blog.engagementRate,
                    "traffic_count": latest_blog.trafficCount
                })

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported URL type: {url.type}")

        return URLAnalysisSummaryResponse(**response_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get URL analysis: {str(e)}")

# @router.get("/stats")
# async def all_url_analysis(params: Dict[str, str], db: Session = Depends(get_session)):
#     # Get total URLs
#     total_urls = db.query(URL).count()
#
#     # Get platform counts and percentages
#     platform_stats = {}
#
#     # Count URLs with posts (Facebook, Instagram, YouTube)
#     social_platform_counts = db.query(
#         URL.id
#     ).join(Post).distinct().count()
#
#     # Count URLs with blog posts (Website)
#     website_count = db.query(
#         URL.id
#     ).join(BlogWebPost).distinct().count()
#
#     # Calculate percentages
#     platform_stats = {
#         PlatformEnum.FACEBOOK.value: {
#             "count": social_platform_counts // 3,  # Approximate split between social platforms
#             "percentage": round((social_platform_counts / 3 / total_urls * 100) if total_urls > 0 else 0, 2)
#         },
#         PlatformEnum.INSTAGRAM.value: {
#             "count": social_platform_counts // 3,
#             "percentage": round((social_platform_counts / 3 / total_urls * 100) if total_urls > 0 else 0, 2)
#         },
#         PlatformEnum.YOUTUBE.value: {
#             "count": social_platform_counts // 3,
#             "percentage": round((social_platform_counts / 3 / total_urls * 100) if total_urls > 0 else 0, 2)
#         },
#         PlatformEnum.WEBSITE.value: {
#             "count": website_count,
#             "percentage": round((website_count / total_urls * 100) if total_urls > 0 else 0, 2)
#         }
#     }
#
#     # Get top performer URL based on engagement rate
#     top_url = db.query(URL).order_by(desc(URL.engagementRate)).first()
#
#     # Get latest analyzed date from posts
#     latest_date = db.query(func.max(Post.dateAnalysed)).scalar()
#
#     return {
#         "total_urls": total_urls,
#         "latest_date_analyzed": latest_date,
#         "platform_stats": platform_stats,
#         "top_performer_url": {
#             "url": top_url.url if top_url else None,
#             "engagement_rate": top_url.engagementRate if top_url else 0
#         }
#     }
