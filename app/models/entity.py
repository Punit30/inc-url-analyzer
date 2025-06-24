from typing import Optional, List, ClassVar, Union, Callable, TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import AuditableBaseModel
from app.models.enums.platform import PlatformEnum

if TYPE_CHECKING:
    from app.models.url import URL


class Entity(AuditableBaseModel, table=True):
    __tablename__: ClassVar[Union[str, Callable[..., str]]] = "entity"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: Optional[str] = None
    fullname: Optional[str] = None
    followers: Optional[int] = None
    platform: PlatformEnum

    # Relationships
    urls: List["URL"] = Relationship(back_populates="entity", sa_relationship_kwargs={"cascade": "all, delete"})
