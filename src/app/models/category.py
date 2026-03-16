import asyncio
from typing import Any

from sqlalchemy import Column, String, Text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import relationship

from app.models.base import Base, BaseModelMixin


class Category(Base, BaseModelMixin):
    __tablename__ = "categories"

    name = Column(String, nullable=False, unique=True)
    desc = Column(Text)

    posts = relationship("Post", back_populates="category")

    def __repr__(self) -> str:
        return f"uuid - {self.uuid}, name - {self.name} desc - {self.desc}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "desc": self.desc,
        }


async def create_db():
    engine = create_async_engine(
        "postgresql+asyncpg://user:password@localhost:5432/postgres"
    )

    async with engine.begin() as _:
        pass


if __name__ == "__main__":
    asyncio.run(create_db())
