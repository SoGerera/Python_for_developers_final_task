import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body

from app.services.post_service import PostService, get_post_service
from app.api.v1.auth import get_current_user
from app.schemas.post_schema import (
    PostCreate,
    PostUpdate,
    PostResponse,
    PostWithCategoryResponse,
    PostListResponse,
    PostWithCategoryListResponse,
    PostsCountResponse,
    PostsCountByCategoryResponse,
    PostSearchParams,
    BulkAssignCategory,
)

router = APIRouter()


@router.get("/", response_model=PostListResponse, summary="Получить посты с пагинацией и фильтрацией")
async def get_all_posts(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        user_id: Optional[str] = Query(None, description="Фильтр по ID пользователя (UUID)"),
        category_id: Optional[str] = Query(None, description="Фильтр по ID категории (UUID)"),
        service: PostService = Depends(get_post_service),
):
    validated_user_id = None
    if user_id:
        try:
            validated_user_id = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id (must be UUID)")

    validated_category_id = None
    if category_id:
        try:
            validated_category_id = uuid.UUID(category_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid category_id (must be UUID)")

    posts = await service.get_all_posts(
        skip=skip,
        limit=limit,
        user_id=validated_user_id,
        category_id=validated_category_id
    )
    total = await service.get_posts_count(
        user_id=validated_user_id,
        category_id=validated_category_id
    )

    return PostListResponse(posts=posts, total=total, skip=skip, limit=limit)


@router.get(
    "/with-category",
    response_model=PostWithCategoryListResponse,
    summary="Получить посты с категориями",
)
async def get_all_posts_with_category(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        service: PostService = Depends(get_post_service),
):
    posts = await service.get_all_posts_with_category(skip, limit)
    total = await service.get_posts_count()
    return PostWithCategoryListResponse(
        posts=posts, total=total, skip=skip, limit=limit
    )


@router.get(
    "/{post_id}",
    response_model=PostResponse,
    summary="Получить пост по ID",
)
async def get_post_by_id(
        post_id: uuid.UUID,
        service: PostService = Depends(get_post_service),
):
    post = await service.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.get(
    "/{post_id}/with-category",
    response_model=PostWithCategoryResponse,
    summary="Получить пост с категорией по ID",
)
async def get_post_by_id_with_category(
        post_id: uuid.UUID,
        service: PostService = Depends(get_post_service),
):
    post = await service.get_post_by_id_with_category(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.get("/media/{media_id}", response_model=PostResponse)
async def get_post_by_media_id(
        media_id: str,
        service: PostService = Depends(get_post_service),
):
    post = await service.get_post_by_media_id(media_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


_media_id_cache = set()


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пост",
)
async def create_post(
        post_data: PostCreate,
        service: PostService = Depends(get_post_service),
        current_user=Depends(get_current_user),
):
    if post_data.media_id in _media_id_cache:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post with this media_id already exists",
        )

    _media_id_cache.add(post_data.media_id)
    return await service.create_post(post_data, current_user.uuid)


@router.put("/{post_id}", response_model=PostResponse, summary="Обновить пост")
async def update_post(
        post_id: uuid.UUID,
        update_data: PostUpdate,
        service: PostService = Depends(get_post_service),
):
    if not await service.post_exists(post_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    updated_post = await service.update_post(post_id, update_data)
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update"
        )
    return updated_post


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пост",
)
async def delete_post(
        post_id: uuid.UUID,
        service: PostService = Depends(get_post_service),
):
    success = await service.delete_post(post_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )


@router.post(
    "/search", response_model=PostListResponse, summary="Поиск постов по описанию"
)
async def search_posts_by_description(
        search_params: PostSearchParams,
        service: PostService = Depends(get_post_service),
):
    posts = await service.search_posts_by_description(
        search_params.caption_pattern, search_params.skip, search_params.limit
    )
    total = await service.get_posts_count()
    return PostListResponse(
        posts=posts,
        total=total,
        skip=search_params.skip,
        limit=search_params.limit,
    )


@router.post(
    "/search/with-category",
    response_model=PostWithCategoryListResponse,
    summary="Поиск постов по описанию с категориями",
)
async def search_posts_by_description_with_category(
        search_params: PostSearchParams,
        service: PostService = Depends(get_post_service),
):
    posts = await service.search_posts_by_description_with_category(
        search_params.caption_pattern, search_params.skip, search_params.limit
    )
    total = await service.get_posts_count()
    return PostWithCategoryListResponse(
        posts=posts,
        total=total,
        skip=search_params.skip,
        limit=search_params.limit,
    )


@router.get(
    "/category/{category_id}",
    response_model=PostListResponse,
    summary="Посты по ID категории",
)
async def get_posts_by_category_id(
        category_id: uuid.UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        service: PostService = Depends(get_post_service),
):
    posts = await service.get_posts_by_category_id(category_id, skip, limit)
    total = await service.get_posts_count_by_category(category_id)
    return PostListResponse(posts=posts, total=total, skip=skip, limit=limit)


@router.get(
    "/category/{category_id}/with-category",
    response_model=PostWithCategoryListResponse,
    summary="Посты по категории с информацией о категории",
)
async def get_posts_by_category_id_with_category(
        category_id: uuid.UUID,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        service: PostService = Depends(get_post_service),
):
    posts = await service.get_posts_by_category_id_with_category(category_id, skip, limit)
    total = await service.get_posts_count_by_category(category_id)
    return PostWithCategoryListResponse(
        posts=posts, total=total, skip=skip, limit=limit
    )


@router.get(
    "/without-category/",
    response_model=PostListResponse,
    summary="Посты без категории",
)
async def get_posts_without_category(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        service: PostService = Depends(get_post_service),
):
    posts = await service.get_posts_without_category(skip, limit)
    total = await service.get_posts_count()
    return PostListResponse(posts=posts, total=total, skip=skip, limit=limit)


@router.patch(
    "/{post_id}/assign-category",
    response_model=PostResponse,
    summary="Назначить категорию посту",
)
async def assign_category_to_post(
        post_id: uuid.UUID,
        category_id: uuid.UUID = Query(..., description="ID категории"),
        service: PostService = Depends(get_post_service),
):
    post = await service.assign_category_to_post(post_id, category_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.patch(
    "/{post_id}/remove-category",
    response_model=PostResponse,
    summary="Удалить категорию у поста",
)
async def remove_category_from_post(
        post_id: uuid.UUID, service: PostService = Depends(get_post_service)
):
    post = await service.remove_category_from_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


@router.get(
    "/stats/count",
    response_model=PostsCountResponse,
    summary="Общее количество постов",
)
async def get_posts_count(service: PostService = Depends(get_post_service)):
    total = await service.get_posts_count()
    return PostsCountResponse(total=total)


@router.get(
    "/stats/count/category/{category_id}",
    response_model=PostsCountByCategoryResponse,
    summary="Количество постов в категории"
)
async def get_posts_count_by_category(
        category_id: uuid.UUID, service: PostService = Depends(get_post_service)
):
    count = await service.get_posts_count_by_category(category_id)
    return PostsCountByCategoryResponse(category_id=category_id, count=count)


@router.post(
    "/bulk",
    response_model=List[PostResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Создать несколько постов"
)
async def create_multiple_posts(
        posts_data: List[PostCreate],
        service: PostService = Depends(get_post_service),
):
    for post_data in posts_data:
        if await service.media_exists(post_data.media_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Post with media_id '{post_data.media_id}' already exists",
            )
    return await service.create_multiple_posts(posts_data)


@router.post("/bulk/assign-category", summary="Назначить категорию нескольким постам")
async def update_category_for_multiple_posts(
        bulk_data: BulkAssignCategory = Body(..., embed=True),
        service: PostService = Depends(get_post_service),
):
    success = await service.update_category_for_multiple_posts(
        bulk_data.post_ids, bulk_data.category_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Failed to update categories",
        )
    return {"message": "Categories updated successfully"}
