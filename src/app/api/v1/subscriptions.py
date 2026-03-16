import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.repositories import SubscriptionRepository
from app.api.v1.auth import get_current_user
from app.models import User

router = APIRouter()


@router.post("/{target_user_id}")
async def subscribe(
        target_user_id: str,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    # Попытка парсить как UUID, если не получается - ищем по username
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        # Ищем пользователя по username
        from app.repositories import UserRepository
        target_user = await UserRepository.get_by_username(session, target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        target_uuid = target_user.uuid

    if current_user.uuid == target_uuid:
        raise HTTPException(status_code=400, detail="Cannot subscribe to yourself")

    result = await SubscriptionRepository.subscribe(session, current_user.uuid, target_uuid)
    if not result:
        return {"message": "Already subscribed"}
    return {"message": "Subscribed", "status_code": 201}


@router.delete("/{target_user_id}", status_code=status.HTTP_200_OK)
async def unsubscribe(
        target_user_id: str,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    # Попытка парсить как UUID, если не получается - ищем по username
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        # Ищем пользователя по username
        from app.repositories import UserRepository
        target_user = await UserRepository.get_by_username(session, target_user_id)
        if not target_user:
            raise HTTPException(status_code=404, detail="User not found")
        target_uuid = target_user.uuid

    await SubscriptionRepository.unsubscribe(session, current_user.uuid, target_uuid)
    return {"message": "Unsubscribed"}


@router.get("/followers")
async def get_followers(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    """Получить список подписчиков текущего пользователя"""
    followers = await SubscriptionRepository.get_followers(session, current_user.uuid)
    return followers


@router.get("/following")
async def get_following(
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    """Получить список подписок текущего пользователя"""
    following = await SubscriptionRepository.get_following(session, current_user.uuid)
    return following