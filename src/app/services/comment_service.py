from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from fastapi import Depends
from app.database import get_session
from app.repositories import CommentRepository
from app.models import Comment


class CommentService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_comment(
        self, post_id: UUID, user_id: UUID, text: str
    ) -> Comment:
        return await CommentRepository.create(
            self.session, post_id=post_id, user_id=user_id, text=text
        )

    async def get_comments_by_post(self, post_id: UUID):
        return await CommentRepository.get_by_post(self.session, post_id)


def get_comment_service(session: AsyncSession = Depends(get_session)):
    return CommentService(session)