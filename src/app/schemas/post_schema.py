from uuid import UUID

from typing import Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.category_schema import CategoryResponse


class PostBase(BaseModel):
    caption: Optional[str] = None
    category_id: UUID | None = None


class PostCreate(PostBase):
    caption: str
    media_id: str


class PostUpdate(PostBase):
    caption: Optional[str] = None


class PostResponse(PostBase):
    model_config = ConfigDict(
        from_attributes=True, exclude={"updated_at", "created_at"}
    )

    uuid: UUID
    user_id: UUID


class PostWithCategoryResponse(PostResponse):
    category: Optional[CategoryResponse] = None


class PostListResponse(BaseModel):
    posts: list[PostResponse]
    total: int
    skip: int
    limit: int


class PostWithCategoryListResponse(BaseModel):
    posts: list[PostWithCategoryResponse]
    total: int
    skip: int
    limit: int


class PostsCountResponse(BaseModel):
    total: int


class PostsCountByCategoryResponse(BaseModel):
    category_id: UUID
    count: int


class PostSearchParams(BaseModel):
    caption_pattern: str
    skip: int = 0
    limit: int = 100


class BulkAssignCategory(BaseModel):
    post_ids: list[UUID]
    category_id: UUID
