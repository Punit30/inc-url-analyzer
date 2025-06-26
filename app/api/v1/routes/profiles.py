from collections import Counter, defaultdict
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlmodel import Session, select
from sqlalchemy.orm import joinedload

from app.core.session import get_session
from app.models.entity import Entity
from app.models.url import URL
from app.models.enums.platform import PlatformEnum
from app.models.enums.profile import ProfileSortBy
from app.schemas.responses.error import ErrorResponse
from app.schemas.responses.profile_response import (
    ProfileAnalyticsResponse,
    ProfileMetricsResponse,
)

router = APIRouter()


@router.get(
    "/profile-metrics",
    response_model=ProfileMetricsResponse,
    responses={
        200: {"description": "Profiles metrics with sorting and breakdown", "model": ProfileMetricsResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get metrics of all profiles",
    description="""
Returns per-profile aggregated metrics including:
- Likes, comments, views, and average engagement rate
- Top performing profile
- Most used platform
- Platform-wise onboarding stats
"""
)
async def profile_metrics(
    db: Session = Depends(get_session),
    platform: str = Query(
        "all", description="Filter by platform or use 'all'"),
    sort_by: ProfileSortBy = Query(
        ProfileSortBy.created_desc, description="Sort by 'created_desc' or 'engagement_rate_desc'")
):
    try:
        query = select(Entity).options(
            joinedload(Entity.urls).joinedload(URL.posts),
            joinedload(Entity.urls).joinedload(URL.blogWebPosts)
        )

        entities = db.exec(query).unique().all()
        output = []
        top_performer = None
        highest_avg_eng_rate = -1
        platform_counter = Counter()
        onboard_counter = Counter()

        for entity in entities:
            platform_data = {}
            onboard_counter[entity.platform.value] += 1

            for url in entity.urls or []:
                for post in url.posts or []:
                    plat = entity.platform.value
                    data = platform_data.setdefault(plat, {
                        "id": entity.id,
                        "username": entity.username,
                        "fullname": entity.fullname,
                        "platform": plat,
                        "followers": entity.followers,
                        "created_date": entity.created_date,
                        "total_likes": 0,
                        "total_comments": 0,
                        "total_views": 0,
                        "engagement_rate_sum": 0,
                        "post_count": 0,
                        "broken_or_deleted_count": 0,
                    })
                    data["total_likes"] += post.likes
                    data["total_comments"] += post.comments
                    data["total_views"] += post.views or 0
                    data["engagement_rate_sum"] += post.engagementRate
                    data["post_count"] += 1
                    if post.isBrokenOrDeleted:
                        data["broken_or_deleted_count"] += 1

                for blog in url.blogWebPosts or []:
                    plat = PlatformEnum.WEBSITE.value
                    data = platform_data.setdefault(plat, {
                        "id": entity.id,
                        "username": entity.username,
                        "fullname": entity.fullname,
                        "platform": plat,
                        "followers": entity.followers,
                        "created_date": entity.created_date,
                        "total_likes": 0,
                        "total_comments": 0,
                        "total_views": 0,
                        "engagement_rate_sum": 0,
                        "post_count": 0,
                        "broken_or_deleted_count": 0,
                    })
                    data["total_views"] += blog.trafficCount
                    data["engagement_rate_sum"] += blog.engagementRate
                    data["post_count"] += 1
                    if blog.isBrokenOrDeleted:
                        data["broken_or_deleted_count"] += 1

            for plat_key, record in platform_data.items():
                avg_eng_rate = round(
                    record["engagement_rate_sum"] / record["post_count"], 2
                ) if record["post_count"] > 0 else 0

                record["total_engagement_rate"] = avg_eng_rate
                record.pop("engagement_rate_sum", None)
                record.pop("post_count", None)

                if avg_eng_rate > highest_avg_eng_rate:
                    highest_avg_eng_rate = avg_eng_rate
                    top_performer = {
                        "id": record["id"],
                        "username": record["username"],
                        "fullname": record["fullname"],
                        "platform": record["platform"],
                        "average_engagement_rate": avg_eng_rate
                    }

                platform_counter[plat_key] += 1
                if platform.lower() == "all" or platform.upper() == plat_key:
                    output.append(record)

        # Sort output based on sort_by parameter
        if sort_by == ProfileSortBy.engagement_rate_desc:
            output.sort(key=lambda x: x["total_engagement_rate"], reverse=True)
        else:  # created_desc
            output.sort(key=lambda x: x.get(
                "created_date") or "", reverse=True)

        most_used_platform = platform_counter.most_common(
            1)[0][0] if platform_counter else None

        total_profiles = sum(onboard_counter.values())
        platform_distribution = {
            plat.value: {
                "count": onboard_counter.get(plat.value, 0),
                "percentage": round((onboard_counter.get(plat.value, 0) / total_profiles) * 100, 2)
                if total_profiles > 0 else 0
            }
            for plat in PlatformEnum
        }

        return {
            "profiles": output,
            "top_performer": top_performer,
            "most_used_platform": most_used_platform,
            "profile_onboarded": {
                "total_profiles": total_profiles,
                "platform_distribution": platform_distribution
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/analytics",
    response_model=ProfileAnalyticsResponse,
    responses={
        200: {"description": "Profile analytics and post/blog comparison", "model": ProfileAnalyticsResponse},
        404: {"description": "Entity not found"},
        500: {"model": ErrorResponse}

    },
    summary="Profile analytics and comparison",
    description="""
Returns metrics for a specific profile:
- Average engagement rate
- Total views
- Total comments
- Total likes
- Detailed comparison analysis (per post/blog with URL, platform, engagement rate)
"""
)
async def all_profile_analysis(
    entity_id: int = Query(...,
                           description="ID of the entity/profile to analyze"),
    db: Session = Depends(get_session)
):
    try:
        query = select(Entity).where(Entity.id == entity_id).options(
            joinedload(Entity.urls).joinedload(URL.posts),
            joinedload(Entity.urls).joinedload(URL.blogWebPosts)
        )

        entity = db.exec(query).unique().first()

        if not entity:
            return JSONResponse(
                status_code=404,
                content={"detail": "Entity not found"}
            )

        total_likes = total_comments = total_views = engagement_sum = post_count = 0
        comparison_analysis = []

        for url in entity.urls or []:
            for post in url.posts or []:
                total_likes += post.likes
                total_comments += post.comments
                total_views += post.views or 0
                engagement_sum += post.engagementRate
                post_count += 1

                comparison_analysis.append({
                    "id": url.id,
                    "url": url.url,
                    "platform": entity.platform.value,
                    "engagement_rate": post.engagementRate
                })

            for blog in url.blogWebPosts or []:
                total_views += blog.trafficCount
                engagement_sum += blog.engagementRate
                post_count += 1

                comparison_analysis.append({
                    "id": url.id,
                    "url": url.url,
                    "platform": "WEBSITE",
                    "engagement_rate": blog.engagementRate
                })

        avg_engagement_rate = round(
            engagement_sum / post_count, 2) if post_count > 0 else 0

        return {
            "id": entity.id,
            "username": entity.username,
            "fullname": entity.fullname,
            "platform": entity.platform.value,
            "profile_analysis": {
                "avg_engagement_rate": avg_engagement_rate,
                "total_views": total_views,
                "total_comments": total_comments,
                "total_likes": total_likes
            },
            "comparison_analysis": comparison_analysis
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
