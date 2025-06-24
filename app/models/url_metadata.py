# from app.models.base import AuditableBaseModel
# from typing import Optional, List, ClassVar, Union, Callable, TYPE_CHECKING

# from app.models.url import URL
# from sqlmodel import Field, Column, ForeignKey, Relationship


# class URLMetaData(AuditableBaseModel, table=True):
#     __tablename__: ClassVar[Union[str, Callable[..., str]]] = "url_metadata"

#     id: Optional[int] = Field(default=None, primary_key=True)
#     totalUrlAnalyzed: int = Field(default=0, sa_column=Column("total_url_analyzed"))
#     facebookEngagementRate: int = Field(sa_column=Column("facebook_engagement_rate", default=0, nullable=False))
#     youtubeEngagementRate: int = Field(sa_column=Column("youtube_engagement_rate", default=0, nullable=False))
#     instagramEngagementRate: int = Field(sa_column=Column("instagram_engagement_rate", default=0, nullable=False))
#     websiteEngagementRate: int = Field(sa_column=Column("website_engagement_rate", default=0, nullable=False))
