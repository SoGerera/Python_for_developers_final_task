import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models import Comment

class CommentRepository:
    @staticmethod
    async def create(session: AsyncSession, post_id: uuid.UUID, user_id: uuid.UUID, text: str):
        comment = Comment(post_id=post_id, user_id=user_id, text=text)
        session.add(comment)
        await session.commit()
        await session.refresh(comment)
        return comment

    @staticmethod
    async def get_by_id(session: AsyncSession, comment_id: uuid.UUID):
        result = await session.execute(
            select(Comment).where(Comment.uuid == comment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_post_id(session: AsyncSession, post_id: uuid.UUID):
        result = await session.execute(
            select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at)
        )
        return result.scalars().all()

    @staticmethod
    async def update(session: AsyncSession, comment_id: uuid.UUID, text: str):
        comment = await CommentRepository.get_by_id(session, comment_id)
        if comment:
            comment.text = text
            await session.commit()
            await session.refresh(comment)
        return comment

    @staticmethod
    async def delete(session: AsyncSession, comment_id: uuid.UUID):
        await session.execute(
            delete(Comment).where(Comment.uuid == comment_id)
        )
        await session.commit()