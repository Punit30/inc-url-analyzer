from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import selectinload
from sqlmodel import select, func, Session

from app.core.session import get_session
from app.models.blog_web_post import BlogWebPost
from app.models.entity import Entity
from app.models.enums.platform import PlatformEnum
from app.models.enums.url import URLListSortingEnum, URLTypeEnum
from app.models.post import Post
from app.models.url import URL
from app.schemas.responses.error import ErrorResponse
from app.schemas.responses.url import SimpleSuccessResponse, TotalURLCountResponse, URLListingResponse, \
    URLAnalysisSummaryResponse, OverallURLSummaryResponse, URLSuccessItem, URLUploadResponse, URLAnalysisHistoryResponse
from app.services.url import detect_platform, get_platform_summary, is_valid_url
from app.utils.sqs import push_to_sqs
from app.utils.date import  get_utc_range_from_ist_date

router = APIRouter()


# @router.get("/all", response_model=URLListingResponse, responses={
#     200: {"description": "All URL retrieved", "model": URLListingResponse},
#     500: {"model": ErrorResponse}
# }, summary="Get all URL with platform breakdown", tags=["URL"])
# async def url_listing(
#         date_uploaded: Optional[str] = Query(None, description="Filter URLs by creation date (YYYY-MM-DD)"),
#         sort_by: Optional[URLListSortingEnum] = Query("engagement_rate_desc",
#                                                       description="Sort by engagement rate: engagement_rate_asc or engagement_rate_desc"),
#         db: Session = Depends(get_session)):
#     try:
#         created_date_filter = None
#         if date_uploaded:
#             try:
#                 created_date_filter = datetime.strptime(date_uploaded, "%Y-%m-%d").date()
#             except ValueError:
#                 raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
#
#         url_details = []
#         url_type_filters = [
#             (Post, URLTypeEnum.POST),
#             (BlogWebPost, URLTypeEnum.WEB_POST)
#         ]
#
#         for model, url_type in url_type_filters:
#             query = select(model).join(URL).join(Entity)
#             if created_date_filter:
#                 query = query.where(func.date(URL.created_date) == created_date_filter)
#             results = db.exec(query).all()
#
#             for item in results:
#                 url_obj = item.url
#                 if not url_obj or not url_obj.entity or url_obj.type != url_type:
#                     continue
#
#                 rate = getattr(item, "engagementRate", 0)
#                 platform = url_obj.entity.platform
#                 created = url_obj.created_date
#
#                 url_details.append({
#                     "id": url_obj.id,
#                     "url": url_obj.url,
#                     "engagement_rate": rate,
#                     "platform": platform,
#                     "date_uploaded": created.strftime("%Y-%m-%d"),
#                     "is_fetched": getattr(item, "isFetched", False),
#                     "is_broken_or_deleted": getattr(item, "isBrokenOrDeleted", False)
#                 })
#
#         reverse = sort_by.value == "engagement_rate_desc"
#         url_details.sort(
#             key=lambda x: (
#                 x.get("engagement_rate") or 0,
#                 datetime.strptime(x.get("date_uploaded", "1900-01-01"), "%Y-%m-%d")
#             ),
#             reverse=reverse
#         )
#
#         return URLListingResponse(urls=url_details)
#
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Failed to fetch URL details.")

@router.get(
    "/all",
    response_model=URLListingResponse,
    responses={
        200: {"description": "Filtered URLs by date", "model": URLListingResponse},
        400: {"description": "Invalid or missing date format", "model": ErrorResponse},
        500: {"model": ErrorResponse}
    },
    summary="Get URLs only for the given date",
    tags=["URL"]
)
async def url_listing(
        date_uploaded: str = Query(..., description="Filter URLs by creation date (YYYY-MM-DD)"),
        sort_by: Optional[URLListSortingEnum] = Query(
            "engagement_rate_desc",
            description="Sort by engagement rate: engagement_rate_asc or engagement_rate_desc"
        ),
        db: Session = Depends(get_session)
):
    try:
        try:
            start_utc , end_utc = get_utc_range_from_ist_date(datetime.strptime(date_uploaded, "%Y-%m-%d"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        url_data_map = {}

        url_type_filters = [
            (Post, URLTypeEnum.POST),
            (BlogWebPost, URLTypeEnum.WEB_POST)
        ]

        for model, url_type in url_type_filters:
            query = (
                select(model)
                .join(URL)
                .join(Entity)
                .where(URL.created_date.between(start_utc, end_utc))
            )

            results = db.exec(query).all()

            for item in results:
                url_obj = item.url
                if not url_obj or not url_obj.entity or url_obj.type != url_type:
                    continue

                url_id = url_obj.id
                if url_id not in url_data_map:
                    url_data_map[url_id] = {
                        "id": url_id,
                        "url": url_obj.url,
                        "engagement_rate": getattr(item, "engagementRate", 0),
                        "platform": url_obj.entity.platform,
                        "date_uploaded": url_obj.created_date.isoformat(),
                        "date_analyzed": (
                            getattr(item, "dateAnalysed", None).isoformat()
                            if getattr(item, "dateAnalysed", None) else None
                        ),
                        "is_fetched": getattr(item, "isFetched", False),
                        "is_broken_or_deleted": getattr(item, "isBrokenOrDeleted", False)
                    }
                else:
                    # Replace if engagement rate is higher
                    if getattr(item, "engagementRate", 0) > url_data_map[url_id]["engagement_rate"]:
                        url_data_map[url_id]["engagement_rate"] = getattr(item, "engagementRate", 0)
                        url_data_map[url_id]["date_analyzed"] = (
                            getattr(item, "dateAnalysed", None).isoformat()
                            if getattr(item, "dateAnalysed", None) else None
                        )
                        url_data_map[url_id]["is_fetched"] = getattr(item, "isFetched", False)
                        url_data_map[url_id]["is_broken_or_deleted"] = getattr(item, "isBrokenOrDeleted", False)

        url_details = list(url_data_map.values())

        reverse = sort_by.value == "engagement_rate_desc"
        url_details.sort(
            key=lambda x: (
                x.get("engagement_rate") or 0,
                datetime.fromisoformat(
                    (x.get("date_uploaded") or "1900-01-01T00:00:00").replace("Z", "")
                )
            ),
            reverse=reverse
        )

        return URLListingResponse(urls=url_details)

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Failed to fetch URL details.")


@router.get("/summary", response_model=OverallURLSummaryResponse, responses={
    200: {"description": "Platform summary retrieved", "model": OverallURLSummaryResponse},
    500: {"model": ErrorResponse}
}, summary="Get platform summary for all or by date", tags=["URL"])
async def platform_summary(
        date_uploaded: Optional[str] = Query(
            None, description="Filter URLs by creation date (YYYY-MM-DD)"),
        db: Session = Depends(get_session)):
    try:
        created_date_filter = None
        if date_uploaded:
            try:
                start_utc , end_utc = get_utc_range_from_ist_date(datetime.strptime(date_uploaded, "%Y-%m-%d"))
            except ValueError:
                raise HTTPException(
                    status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

        summary = get_platform_summary(db, start_utc, end_utc)

        return OverallURLSummaryResponse(
            total_urls_count=summary["total"],
            facebook_percent=summary["facebook_percent"],
            instagram_percent=summary["instagram_percent"],
            website_percent=summary["website_percent"],
            youtube_percent=summary["youtube_percent"],
            top_performer=summary["top_performer"],
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500, detail="Failed to fetch platform summary.")


@router.get("/urls_count", response_model=TotalURLCountResponse,
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(err))


@router.get("/analysis/{url_id}", response_model=URLAnalysisSummaryResponse, responses={
    200: {"description": "All URL retrieved", "model": URLListingResponse},
    500: {"model": ErrorResponse}
}, summary="Get URL analysis", tags=["URL"])
async def get_url_analysis(url_id: int, db: Session = Depends(get_session)):
    try:
        url: Optional[URL] = db.exec(
            select(URL)
            .options(
                selectinload(URL.entity),
                selectinload(URL.posts),
                selectinload(URL.blogWebPosts)
            )
            .where(URL.id == url_id)
        ).first()

        if not url:
            raise HTTPException(status_code=404, detail="URL not found")

        response_data = {
            "url_id": url.id,
            "post_url": url.url,
            "user_profile_name": url.entity.fullname if url.entity else None,
            "url_type": url.type,
            "platform": url.entity.platform if url.entity else None,
            "latest_likes": None,
            "latest_views": None,
            "latest_comments": None,
            "latest_engagement_rate": 0.0,
            "traffic_count": None,
            "is_broken_or_deleted": False,
            "is_fetched": False
        }

        # Depending on URL type, fetch and update
        if url.type == URLTypeEnum.POST:
            if url.posts:
                latest_post = max(url.posts, key=lambda p: p.dateAnalysed)
                response_data.update({
                    "latest_likes": latest_post.likes,
                    "latest_views": latest_post.views,
                    "latest_comments": latest_post.comments,
                    "latest_engagement_rate": latest_post.engagementRate,
                    "is_broken_or_deleted": latest_post.isBrokenOrDeleted,
                    "is_fetched": latest_post.isFetched
                })

        elif url.type == URLTypeEnum.WEB_POST:
            if url.blogWebPosts:
                latest_blog = max(url.blogWebPosts,
                                  key=lambda b: b.dateAnalysed)
                response_data.update({
                    "latest_engagement_rate": latest_blog.engagementRate,
                    "traffic_count": latest_blog.trafficCount,
                    "is_broken_or_deleted": latest_blog.isBrokenOrDeleted,
                    "is_fetched": latest_blog.isFetched
                })

        else:
            raise HTTPException(
                status_code=400, detail=f"Unsupported URL type: {url.type}")

        return URLAnalysisSummaryResponse(**response_data)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get URL analysis: {str(e)}")


@router.get("/engagement-history/{url_id}", response_model=list[URLAnalysisHistoryResponse], responses={
    200: {"description": "Engagement history retrieved"},
    404: {"description": "URL not found"},
    500: {"description": "Server error"}
}, summary="Get engagement history for a URL", tags=["URL"])
async def get_url_engagement_history(url_id: int, db: Session = Depends(get_session)):
    try:
        url: Optional[URL] = db.exec(
            select(URL)
            .options(
                selectinload(URL.posts),
                selectinload(URL.blogWebPosts)
            )
            .where(URL.id == url_id)
        ).first()

        if not url:
            raise HTTPException(status_code=404, detail="URL not found")

        data_points: list[URLAnalysisHistoryResponse] = []

        if url.type == URLTypeEnum.POST:
            for post in url.posts:
                data_points.append(URLAnalysisHistoryResponse(
                    date_analyzed=post.dateAnalysed.date(),
                    likes=post.likes,
                    views=post.views,
                    comments=post.comments,
                    engagement_rate=post.engagementRate,
                ))

        elif url.type == URLTypeEnum.WEB_POST:
            for blog in url.blogWebPosts:
                data_points.append(URLAnalysisHistoryResponse(
                    date_analyzed=blog.dateAnalysed.date(),
                    traffic_count=blog.trafficCount,
                    engagement_rate=blog.engagementRate,
                ))

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported URL type: {url.type}")

        # Sort by date_analyzed ascending
        return sorted(data_points, key=lambda x: x.date_analyzed)

    except Exception as e:
        print("ereresrr", e)
        raise HTTPException(status_code=500, detail=f"Failed to get engagement history: {str(e)}")


@router.post("/upload-urls", response_model=URLUploadResponse, summary="Upload and classify URLs")
async def upload_urls(
        body: List[str] = Body(..., description="List of URLs to upload"),
        db: Session = Depends(get_session)
):
    added_count = 0
    success_urls: List[URLSuccessItem] = []
    failed_urls: List[str] = []

    unique_urls = list(set(url.strip() for url in body if url.strip()))

    for raw_url in unique_urls:
        if not is_valid_url(raw_url):
            failed_urls.append(raw_url)
            continue

        existing_url = db.exec(select(URL).where(URL.url == raw_url)).first()
        if existing_url:
            failed_urls.append(f"{raw_url} (already exists)")
            continue

        try:
            platform = detect_platform(raw_url)
            url_type = (
                URLTypeEnum.POST
                if platform in [PlatformEnum.FACEBOOK, PlatformEnum.INSTAGRAM, PlatformEnum.YOUTUBE]
                else URLTypeEnum.WEB_POST
            )

            new_url = URL(
                url=raw_url,
                type=url_type,
            )
            db.add(new_url)
            db.commit()
            db.refresh(new_url)

            post_id = web_id = None
            if url_type == URLTypeEnum.POST:
                post = Post(
                    urlId=new_url.id,
                    comments=0,
                    likes=0,
                    views=0,
                    engagementRate=0,
                    dateAnalysed=datetime.now(timezone.utc),
                    isBrokenOrDeleted=False,
                    isFetched=False
                )
                db.add(post)
                db.commit()
                db.refresh(post)
                post_id = post.id
            else:
                blog = BlogWebPost(
                    urlId=new_url.id,
                    trafficCount=0,
                    engagementRate=0,
                    dateAnalysed=datetime.now(timezone.utc),
                    isBrokenOrDeleted=False,
                    isFetched=False
                )
                db.add(blog)
                db.commit()
                db.refresh(blog)
                web_id = blog.id

            added_count += 1
            success_urls.append(URLSuccessItem(
                url_id=new_url.id,
                url=new_url.url,
                platform=platform,
                post_id=post_id,
                web_id=web_id
            ))

        except Exception as e:
            db.rollback()
            failed_urls.append(f"{raw_url} (error: {str(e)})")
    if success_urls:
        push_to_sqs(success_urls)
    return URLUploadResponse(
        success=True,
        message="URL upload completed",
        added_count=added_count,
        failed_urls=failed_urls,
    )


@router.post("/re-analyze-url", response_model=SimpleSuccessResponse, summary="Re-analyze URL by ID",
             responses={
                 200: {"description": "URL re-analysis triggered"},
                 404: {"description": "Missing 'url_id' in request body."},
                 500: {"description": "Server error"}
             }
             )
async def reanalyze_url(
        body: Dict[str, int] = Body(..., example={"url_id": 123}),
        db: Session = Depends(get_session)
):
    url_id = body.get("url_id")
    if not url_id:
        raise HTTPException(
            status_code=400, detail="Missing 'url_id' in request body.")

    url = db.exec(select(URL).where(URL.id == url_id)).first()
    if not url:
        raise HTTPException(
            status_code=404, detail=f"URL with id {url_id} not found.")

    platform = detect_platform(url.url)
    try:
        post_id = web_id = None
        if url.type == URLTypeEnum.POST:
            post = db.exec(select(Post).where(Post.urlId == url.id)).first()
            if post:
                post.isFetched = False
                db.add(post)
                post_id = post.id
        else:
            blog = db.exec(select(BlogWebPost).where(
                BlogWebPost.urlId == url.id)).first()
            if blog:
                blog.isFetched = False
                db.add(blog)
                web_id = blog.id

        db.commit()
        push_to_sqs([URLSuccessItem(
            url_id=url.id,
            url=url.url,
            platform=platform,
            post_id=post_id,
            web_id=web_id,
            is_reanalysis=True
        )])
        return SimpleSuccessResponse(
            success=True,
            message="URL re-analysis triggered",
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Failed to re-analyze URL: {str(e)}")
