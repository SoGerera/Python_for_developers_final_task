from typing import Any
from sqlalchemy import Column, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, BaseModelMixin

class Post(Base, BaseModelMixin):
    __tablename__ = "posts"

    caption = Column(Text, nullable=True)

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="posts", lazy="joined")

    category_id = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.uuid", ondelete="SET NULL"),
        nullable=True,
    )
    category = relationship("Category", back_populates="posts", lazy="joined")

    media_items = relationship("Media", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Post uuid={self.uuid} user_id={self.user_id}>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": str(self.uuid),
            "caption": self.caption,
            "user_id": str(self.user_id),
            "category_id": str(self.category_id) if self.category_id else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
