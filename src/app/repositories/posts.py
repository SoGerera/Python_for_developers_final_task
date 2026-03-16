from uuid import UUID
from typing import List, Optional, Any

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import Post
from app.database import get_session


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, post_id: Any) -> Optional[Post]:
        result = await self.db.execute(select(Post).where(Post.uuid == post_id))
        return result.scalar_one_or_none()

    async def get_by_id_with_category(self, post_id: Any) -> Optional[Post]:
        """Получить пост с категорией"""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.category))
            .where(Post.uuid == post_id)
        )
        return result.scalar_one_or_none()

    async def get_by_media_id(self, media_id: Any) -> Optional[Post]:
        """Получить пост по media_id через связь с Media"""
        from app.models.media import Media
        result = await self.db.execute(
            select(Post).join(Media).where(Media.url.contains(str(media_id)))
        )
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 100,
        user_id: Optional[Any] = None,
        category_id: Optional[Any] = None
    ) -> List[Post]:
        """Получить все посты с опциональной фильтрацией"""
        query = select(Post)
        
        if user_id:
            query = query.where(Post.user_id == user_id)
        if category_id:
            query = query.where(Post.category_id == category_id)
            
        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_all_with_category(
        self, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """Получить все посты с категориями"""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.category))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, post_data: dict) -> Post:
        """Создать новый пост"""
        post = Post(**post_data)
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def update(self, post_id: Any, update_data: dict) -> Optional[Post]:
        post = await self.get_by_id(post_id)
        if not post:
            return None

        for key, value in update_data.items():
            setattr(post, key, value)

        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete(self, post_id: Any) -> bool:
        post = await self.get_by_id(post_id)
        if post:
            await self.db.delete(post)
            await self.db.commit()
            return True
        return False

    async def search_by_description(
        self, caption_pattern: str, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        result = await self.db.execute(
            select(Post)
            .where(Post.caption.ilike(f"%{caption_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search_by_description_with_category(
        self, caption_pattern: str, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """Поиск постов с категориями"""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.category))
            .where(Post.caption.ilike(f"%{caption_pattern}%"))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    # Работа с категориями
    async def get_by_category_id(
        self, category_id: Any, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """Получить посты по категории"""
        result = await self.db.execute(
            select(Post)
            .where(Post.category_id == category_id)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_category_id_with_category(
        self, category_id: Any, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """Получить посты по категории с загрузкой категорий"""
        result = await self.db.execute(
            select(Post)
            .where(Post.category_id == category_id)
            .options(selectinload(Post.category))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_posts_without_category(
        self, skip: int = 0, limit: int = 100
    ) -> List[Post]:
        """Получить посты без категории"""
        result = await self.db.execute(
            select(Post).where(Post.category_id.is_(None)).offset(skip).limit(limit)
        )
        return result.scalars().all()

    async def assign_category(self, post_id: Any, category_id: Any) -> Optional[Post]:
        """Назначить категорию посту"""
        post = await self.get_by_id(post_id)
        if post:
            post.category_id = category_id
            await self.db.commit()
            await self.db.refresh(post)
        return post

    async def remove_category(self, post_id: Any) -> Optional[Post]:
        """Убрать категорию у поста"""
        post = await self.get_by_id(post_id)
        if post:
            post.category_id = None
            await self.db.commit()
            await self.db.refresh(post)
        return post

    # Проверки
    async def exists_by_id(self, post_id: Any) -> bool:
        post = await self.get_by_id(post_id)
        return post is not None

    async def exists_by_media_id(self, media_id: Any) -> bool:
        post = await self.get_by_media_id(media_id)
        return post is not None

    # Статистика
    async def get_count(
        self,
        user_id: Optional[Any] = None,
        category_id: Optional[Any] = None
    ) -> int:
        """Получить общее количество постов с фильтрацией"""
        query = select(func.count(Post.uuid))
        
        if user_id:
            query = query.where(Post.user_id == user_id)
        if category_id:
            query = query.where(Post.category_id == category_id)
            
        result = await self.db.execute(query)
        return result.scalar()

    async def get_count_by_category(self, category_id: Any) -> int:
        """Получить количество постов в категории"""
        result = await self.db.execute(
            select(func.count(Post.uuid)).where(Post.category_id == category_id)
        )
        return result.scalar()

    # Пакетные операции
    async def create_many(self, posts_data: List[dict]) -> List[Post]:
        """Создать несколько постов"""
        posts = []
        for data in posts_data:
            post = Post(**data)
            posts.append(post)
            self.db.add(post)

        await self.db.commit()

        # Refresh всех созданных постов
        for post in posts:
            await self.db.refresh(post)

        return posts

    async def update_category_for_posts(
        self, post_ids: List[UUID], category_id: Any
    ) -> bool:
        """Обновить категорию для нескольких постов"""

        await self.db.execute(
            update(Post)
            .where(Post.uuid.in_(post_ids))
            .values(category_id=category_id)
        )
        await self.db.commit()
        return True


async def get_post_reposetory(
    db: AsyncSession = Depends(get_session),
) -> PostRepository:
    return PostRepository(db)