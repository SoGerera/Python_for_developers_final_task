
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import Depends
from app.database import get_session
from app.repositories import SubscriptionRepository


class SubscriptionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def subscribe(self, follower_id: UUID, target_id: UUID):
        return await SubscriptionRepository.subscribe(
            self.session, follower_id=follower_id, target_id=target_id
        )

    async def unsubscribe(self, follower_id: UUID, target_id: UUID):
        return await SubscriptionRepository.unsubscribe(
            self.session, follower_id=follower_id, target_id=target_id
        )


def get_subscription_service(session: AsyncSession = Depends(get_session)):
    return SubscriptionService(session)