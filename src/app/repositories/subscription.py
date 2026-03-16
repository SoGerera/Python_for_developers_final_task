import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models import Subscription, User

class SubscriptionRepository:
    @staticmethod
    async def subscribe(session: AsyncSession, follower_id: uuid.UUID, target_id: uuid.UUID):
        exists = await session.execute(
            select(Subscription)
            .where(Subscription.follower_id == follower_id)
            .where(Subscription.target_id == target_id)
        )
        if exists.scalar_one_or_none():
            return None
        sub = Subscription(follower_id=follower_id, target_id=target_id)
        session.add(sub)
        await session.commit()
        return sub

    @staticmethod
    async def unsubscribe(session: AsyncSession, follower_id: uuid.UUID, target_id: uuid.UUID):
        await session.execute(
            delete(Subscription)
            .where(Subscription.follower_id == follower_id)
            .where(Subscription.target_id == target_id)
        )
        await session.commit()

    @staticmethod
    async def get_followers(session: AsyncSession, user_id: uuid.UUID):
        """Получить подписчиков пользователя"""
        result = await session.execute(
            select(User)
            .join(Subscription, Subscription.follower_id == User.uuid)
            .where(Subscription.target_id == user_id)
        )
        return [{"uuid": str(u.uuid), "username": u.username, "first_name": u.first_name, "last_name": u.last_name} 
                for u in result.scalars().all()]

    @staticmethod
    async def get_following(session: AsyncSession, user_id: uuid.UUID):
        """Получить подписки пользователя"""
        result = await session.execute(
            select(User)
            .join(Subscription, Subscription.target_id == User.uuid)
            .where(Subscription.follower_id == user_id)
        )
        return [{"uuid": str(u.uuid), "username": u.username, "first_name": u.first_name, "last_name": u.last_name} 
                for u in result.scalars().all()]