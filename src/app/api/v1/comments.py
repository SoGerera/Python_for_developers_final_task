import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.database import get_session
from app.repositories import CommentRepository
from app.api.v1.auth import get_current_user
from app.models import User

router = APIRouter()


class CommentCreate(BaseModel):
    post_id: uuid.UUID
    text: str = Field(..., min_length=1, description="Текст комментария")


class CommentUpdate(BaseModel):
    text: str


class CommentResponse(BaseModel):
    uuid: uuid.UUID
    post_id: uuid.UUID
    user_id: uuid.UUID
    text: str
    created_at: str

    model_config = {"from_attributes": True}


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CommentResponse)
async def create_comment(
        comment: CommentCreate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    """
    Создать комментарий к посту.
    Требует авторизации.
    """
    from app.repositories.posts import PostRepository
    post_repo = PostRepository(session)
    post = await post_repo.get_by_id(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_obj = await CommentRepository.create(
        session=session,
        post_id=comment.post_id,
        user_id=current_user.uuid,
        text=comment.text
    )
    return CommentResponse(
        uuid=comment_obj.uuid,
        post_id=comment_obj.post_id,
        user_id=comment_obj.user_id,
        text=comment_obj.text,
        created_at=comment_obj.created_at.isoformat() if comment_obj.created_at else None
    )


@router.get("/post/{post_id}", response_model=List[CommentResponse])
async def get_comments_for_post(
        post_id: uuid.UUID,
        session: AsyncSession = Depends(get_session)
):
    """
    Получить все комментарии для поста.
    """
    comments = await CommentRepository.get_by_post_id(session, post_id)
    return [
        CommentResponse(
            uuid=c.uuid,
            post_id=c.post_id,
            user_id=c.user_id,
            text=c.text,
            created_at=c.created_at.isoformat() if c.created_at else None
        )
        for c in comments
    ]


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
        comment_id: uuid.UUID,
        update_data: CommentUpdate,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    """
    Обновить свой комментарий.
    """
    comment = await CommentRepository.get_by_id(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Not authorized to update this comment")

    updated_comment = await CommentRepository.update(session, comment_id, update_data.text)
    return CommentResponse(
        uuid=updated_comment.uuid,
        post_id=updated_comment.post_id,
        user_id=updated_comment.user_id,
        text=updated_comment.text,
        created_at=updated_comment.created_at.isoformat() if updated_comment.created_at else None
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: uuid.UUID,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_session)
):
    """
    Удалить свой комментарий.
    """
    comment = await CommentRepository.get_by_id(session, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment.user_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await CommentRepository.delete(session, comment_id)
    return None