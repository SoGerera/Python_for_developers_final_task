import secrets
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models import RefreshToken
import uuid

class RefreshTokenRepository:
    @staticmethod
    async def create(session: AsyncSession, user_id: uuid.UUID, expires_in: int = 604800):  # 7 дней
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        rt = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        session.add(rt)
        await session.commit()
        await session.refresh(rt)
        return rt

    @staticmethod
    async def get_valid(session: AsyncSession, token: str):
        result = await session.execute(
            select(RefreshToken)
            .where(RefreshToken.token == token)
            .where(RefreshToken.expires_at > datetime.now(timezone.utc))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def delete_by_token(session: AsyncSession, token: str):
        await session.execute(delete(RefreshToken).where(RefreshToken.token == token))
        await session.commit()