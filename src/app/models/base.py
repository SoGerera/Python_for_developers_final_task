import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlalchemy.orm import DeclarativeBase, declarative_mixin
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    pass


def utc_now():
    """Возвращает текущее время UTC"""
    return datetime.now(timezone.utc)


@declarative_mixin
class BaseModelMixin:
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(
        DateTime, nullable=False, default=utc_now, onupdate=utc_now
    )
