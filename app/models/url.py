from typing import Optional, List, TYPE_CHECKING, Any

from sqlmodel import Field, Column, ForeignKey, Relationship, String
from pydantic import field_validator
from app.models.base import AuditableBaseModel
from app.models.enums.url import URLTypeEnum

if TYPE_CHECKING:
    from app.models.entity import Entity
    from app.models.post import Post
    from app.models.blog_web_post import BlogWebPost


class URL(AuditableBaseModel, table=True):
    __tablename__: str = "url"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    type: URLTypeEnum

    # Foreign key 
    entityId: int = Field(sa_column=Column("entity_id", ForeignKey("entity.id"), nullable=False))

    # Relationships
    entity: Optional["Entity"] = Relationship(back_populates="urls")
    posts: List["Post"] = Relationship(back_populates="url", sa_relationship_kwargs={"cascade": "all, delete"})
    blogWebPosts: List["BlogWebPost"] = Relationship(back_populates="url",
                                                     sa_relationship_kwargs={"cascade": "all, delete"})