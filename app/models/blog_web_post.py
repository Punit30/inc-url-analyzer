from datetime import datetime
from typing import Optional, ClassVar, Union, Callable, TYPE_CHECKING

from sqlmodel import Field, Column, ForeignKey, Relationship, Integer, SQLModel, Boolean, DateTime

if TYPE_CHECKING:
    from app.models.url import URL


class BlogWebPost(SQLModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "blog_web_post"

    id: Optional[int] = Field(default=None, primary_key=True)
    trafficCount: int = Field(sa_column=Column("traffic_count", Integer, default=0))
    engagementRate: int = Field(default=0, sa_column=Column("engagement_rate", Integer, nullable=False))
    dateAnalysed: datetime = Field(
        sa_column=Column("date_analyzed", DateTime, default=0, nullable=False)
    )
    isBrokenOrDeleted: Optional[bool] = Field(
        default=False, sa_column=Column("is_broken_or_deleted", Boolean)
    )
    isFetched: Optional[bool] = Field(
        default=False, sa_column=Column("is_fetched", Boolean)
    )

    # Foreign key
    urlId: int = Field(
        sa_column=Column(
            "url_id", Integer, ForeignKey("url.id"), default=None, nullable=False
        )
    )

    # Relationships
    url: Optional["URL"] = Relationship(back_populates="blogWebPosts")
