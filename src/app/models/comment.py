from sqlalchemy import Column, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, BaseModelMixin


class Comment(Base, BaseModelMixin):
    __tablename__ = "comments"

    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.uuid", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)

    post = relationship("Post")
    user = relationship("User")
