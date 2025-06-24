from typing import Optional, ClassVar, Union, Callable, TYPE_CHECKING

from sqlmodel import Field, Column, ForeignKey, Relationship, Integer, SQLModel, Boolean

if TYPE_CHECKING:
    from app.models.url import URL


class Post(SQLModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "post"

    id: Optional[int] = Field(default=None, primary_key=True)
    comments: int
    likes: int
    views: Optional[int] = None
    engagementRate: int = Field(default=0, sa_column=Column("engagement_rate", Integer, nullable=False))
    dateAnalysed: int = Field(
        sa_column=Column("date_analyzed", Integer, default=0, nullable=False)
    )
    isBrokenOrDeleted: Optional[bool] = Field(
        default=False, sa_column=Column("is_broken_or_deleted", Boolean)
    )
    isFetched: Optional[bool] = Field(
        default=False, sa_column=Column("is_fetched", Boolean)
    )

    # Foreign key
    urlId: int = Field(
        sa_column=Column("url_id", Integer, ForeignKey("url.id"), nullable=False)
    )

    # Relationships
    url: Optional["URL"] = Relationship(back_populates="posts")
