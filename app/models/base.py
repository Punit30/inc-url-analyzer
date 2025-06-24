from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.utils.date import get_now_for_timezone


class AuditableBaseModel(SQLModel):
    """Base model for all database models."""

    created_date: Optional[datetime] = Field(
        default_factory=get_now_for_timezone,
    )
