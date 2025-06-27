from datetime import datetime, date
from typing import Optional, List

from pydantic import BaseModel

from app.models.enums.platform import PlatformEnum
from app.models.enums.url import URLTypeEnum


class TotalURLCountResponse(BaseModel):
    total_urls: int | None


class URLDetailResponse(BaseModel):
    id: int
    url: str
    engagement_rate: float
    platform: PlatformEnum
    is_fetched: bool
    is_broken_or_deleted: bool
    date_uploaded: str
    date_analyzed: str


class URLListingResponse(BaseModel):
    urls: List[URLDetailResponse]

class TopPerformingURL(BaseModel):
    url_id: int
    url: str
    platform: PlatformEnum
    engagement_rate: float

class OverallURLSummaryResponse(BaseModel):
    total_urls_count: int
    facebook_percent: float
    instagram_percent: float
    website_percent: float
    youtube_percent: float
    top_performer: Optional[TopPerformingURL]


class EngagementSnapshot(BaseModel):
    date_analysed: datetime
    likes: Optional[int]
    views: Optional[int]
    comments: Optional[int]
    engagement_rate: float


class URLAnalysisSummaryResponse(BaseModel):
    url_id: int
    latest_likes: Optional[int] = None
    latest_views: Optional[int] = None
    latest_comments: Optional[int] = None
    latest_engagement_rate: float
    traffic_count: Optional[int] = None  # Only for BlogWebPost
    user_profile_name: Optional[str] = None  # From Entity.fullname
    post_url: str  # From URL.url
    url_type: URLTypeEnum  # From URL.type
    platform: PlatformEnum

class URLAnalysisHistoryResponse(BaseModel):
    date_analyzed: date
    likes: Optional[int] = None
    views: Optional[int] = None
    comments: Optional[int] = None
    traffic_count: Optional[int] = None
    engagement_rate: float

    class Config:
        orm_mode = True


class URLSuccessItem(BaseModel):
    url_id: int
    url: str
    platform: PlatformEnum
    post_id: Optional[int] = None
    web_id: Optional[int] = None


class URLUploadResponse(BaseModel):
    success: bool
    message: str
    added_count: int
    failed_urls: List[str]
