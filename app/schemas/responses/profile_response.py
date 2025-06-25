from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from app.models.enums.platform import PlatformEnum


class ProfileMetrics(BaseModel):
    id: int
    username: str
    fullname: str
    platform: PlatformEnum
    followers: Optional[int]
    created_date: Optional[datetime]
    total_likes: int
    total_comments: int
    total_views: int
    total_engagement_rate: float
    broken_or_deleted_count: int


class TopPerformer(BaseModel):
    id: int
    username: str
    fullname: str
    platform: PlatformEnum
    average_engagement_rate: float


class PlatformDistribution(BaseModel):
    count: int
    percentage: float


class ProfileOnboarded(BaseModel):
    total_profiles: int
    platform_distribution: dict[PlatformEnum, PlatformDistribution]


class ProfileMetricsResponse(BaseModel):
    profiles: List[ProfileMetrics]
    top_performer: Optional[TopPerformer]
    most_used_platform: Optional[PlatformEnum]
    profile_onboarded: ProfileOnboarded


class ProfileAnalysis(BaseModel):
    avg_engagement_rate: float
    total_views: int
    total_comments: int
    total_likes: int


class ComparisonAnalysisItem(BaseModel):
    id: int
    url: str
    platform: PlatformEnum | str
    engagement_rate: float


class ProfileAnalyticsResponse(BaseModel):
    id: int
    username: str
    fullname: str
    platform: PlatformEnum
    profile_analysis: ProfileAnalysis
    comparison_analysis: List[ComparisonAnalysisItem]
