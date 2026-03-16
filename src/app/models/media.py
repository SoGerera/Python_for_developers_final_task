from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, BaseModelMixin


class Media(Base, BaseModelMixin):
    __tablename__ = "media"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.uuid", ondelete="CASCADE"), nullable=False)
    url = Column(String, nullable=False)
    caption = Column(String, nullable=True)
    media_type = Column(String, nullable=False)

    post = relationship("Post", back_populates="media_items")
