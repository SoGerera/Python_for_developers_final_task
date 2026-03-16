from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base, BaseModelMixin


class User(Base, BaseModelMixin):
    __tablename__ = "users"

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")