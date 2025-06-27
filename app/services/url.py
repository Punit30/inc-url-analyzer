from datetime import date
from typing import Optional, Dict
from urllib.parse import urlparse
from sqlmodel import Session, select, func
from app.models.post import Post
from app.models.blog_web_post import BlogWebPost
from app.models.url import URL
from app.models.enums.platform import PlatformEnum
from app.models.entity import Entity
from app.models.enums.url import URLTypeEnum
from urllib.parse import urlparse
from app.models.enums.platform import PlatformEnum


def get_platform_summary(
    db: Session, created_date_filter: Optional[date] = None
) -> Dict[str, any]:
    platform_counts = {
        PlatformEnum.FACEBOOK: 0,
        PlatformEnum.INSTAGRAM: 0,
        PlatformEnum.WEBSITE: 0,
        PlatformEnum.YOUTUBE: 0
    }

    total_urls = 0

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
            if not item.url or not item.url.entity or item.url.type != url_type:
                continue
            platform = item.url.entity.platform
            platform_counts[platform] += 1
            total_urls += 1

    return {
        "total": total_urls,
        "facebook_percent": round((platform_counts[PlatformEnum.FACEBOOK] / total_urls) * 100, 2) if total_urls else 0,
        "instagram_percent": round((platform_counts[PlatformEnum.INSTAGRAM] / total_urls) * 100, 2) if total_urls else 0,
        "website_percent": round((platform_counts[PlatformEnum.WEBSITE] / total_urls) * 100, 2) if total_urls else 0,
        "youtube_percent": round((platform_counts[PlatformEnum.YOUTUBE] / total_urls) * 100, 2) if total_urls else 0,
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
