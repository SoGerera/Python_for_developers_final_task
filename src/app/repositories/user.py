import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User

class UserRepository:
    @staticmethod
    async def get_by_username(session: AsyncSession, username: str):
        result = await session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(session: AsyncSession, user_id: uuid.UUID):
        result = await session.execute(select(User).where(User.uuid == user_id))
        return result.scalar_one_or_none()