from app.models.base import AuditableBaseModel
from typing import Optional, List, ClassVar, Union, Callable, TYPE_CHECKING

from app.models.enums.platform import PlatformEnum
from sqlmodel import Field, Column, ForeignKey, Relationship
from datetime import datetime
from app.utils.date import get_now_for_timezone

if TYPE_CHECKING:
    from app.models.entity import Entity
    from app.models.post import Post
    from app.models.blog_web_post import BlogWebPost

class URL(AuditableBaseModel, table=True):
    __tablename__: str= "url"

    id: Optional[int] = Field(default=None, primary_key=True)
    # engagementRate: int = Field(default=0, sa_column=Column("engagement_rate", nullable=False))
    url: str

    # Foreign key 
    entityId: int = Field(sa_column=Column("entity_id", ForeignKey("entity.id"), nullable=False))

    # Relationships
    entity: Optional["Entity"] = Relationship(back_populates="urls")
    posts: List["Post"] = Relationship(back_populates="url",  sa_relationship_kwargs={"cascade": "all, delete"})
    blogWebPosts: List["BlogWebPost"] = Relationship(back_populates="url",  sa_relationship_kwargs={"cascade": "all, delete"})

