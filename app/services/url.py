from datetime import date
from typing import Optional, Dict, Any
from collections import defaultdict
from urllib.parse import urlparse
from sqlmodel import Session, select, func

from app.models.blog_web_post import BlogWebPost
from app.models.entity import Entity
from app.models.enums.platform import PlatformEnum
from app.models.enums.url import URLTypeEnum
from app.models.post import Post
from app.models.url import URL


def get_platform_summary(
        db: Session, created_date_filter: Optional[date] = None
) -> Dict[str, Any]:
    platform_counts = {
        PlatformEnum.FACEBOOK: 0,
        PlatformEnum.INSTAGRAM: 0,
        PlatformEnum.WEBSITE: 0,
        PlatformEnum.YOUTUBE: 0
    }

    url_data_map = {}

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

            url_id = url_obj.id
            engagement = getattr(item, "engagementRate", 0)

            # If URL not seen before or this post/blog has higher engagement, update
            if (
                url_id not in url_data_map or
                engagement > url_data_map[url_id]["engagement_rate"]
            ):
                url_data_map[url_id] = {
                    "url_id": url_obj.id,
                    "url": url_obj.url,
                    "platform": url_obj.entity.platform,
                    "engagement_rate": engagement
                }

    total_urls = len(url_data_map)

    # Re-calculate platform counts from distinct URLs only
    for url_info in url_data_map.values():
        platform_counts[url_info["platform"]] += 1

    # Get top performer
    top_performer = max(url_data_map.values(), key=lambda x: x["engagement_rate"], default=None)

    return {
        "total": total_urls,
        "facebook_percent": round((platform_counts[PlatformEnum.FACEBOOK] / total_urls) * 100, 2) if total_urls else 0,
        "instagram_percent": round((platform_counts[PlatformEnum.INSTAGRAM] / total_urls) * 100, 2) if total_urls else 0,
        "website_percent": round((platform_counts[PlatformEnum.WEBSITE] / total_urls) * 100, 2) if total_urls else 0,
        "youtube_percent": round((platform_counts[PlatformEnum.YOUTUBE] / total_urls) * 100, 2) if total_urls else 0,
        "top_performer": top_performer
    }
    }
    

def is_valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False


def detect_platform(url: str) -> str:
    try:
        parsed = urlparse(url.lower())
        domain = parsed.netloc.replace("www.", "")

        if domain in {"facebook.com", "m.facebook.com"}:
            return PlatformEnum.FACEBOOK.value
        elif domain in {"instagram.com"}:
            return PlatformEnum.INSTAGRAM.value
        elif domain in {"youtube.com", "youtu.be"}:
            return PlatformEnum.YOUTUBE.value
        else:
            return PlatformEnum.WEBSITE.value

    except Exception:
        return PlatformEnum.WEBSITE.value

