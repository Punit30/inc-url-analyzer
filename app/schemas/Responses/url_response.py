from pydantic import BaseModel
from typing import Optional, List
from app.models.enums.platform import PlatformEnum

class TotalURLCountResponse(BaseModel):
    total_urls: int | None

class URLDetail(BaseModel):
    url: str
    engagement_rate: float
    platform: PlatformEnum
    date_uploaded: str

class URLListingResponse(BaseModel):
    urls: List[URLDetail]
    total_urls_count: int
    facebook_percent: float
    instagram_percent: float
    website_percent: float
    youtube_percent: float
    top_platform: Optional[str]
    top_url: Optional[str]