from typing import List
import uuid as uuid_lib
from fastapi import APIRouter, Depends, status, Query, HTTPException

from app.schemas.category_schema import (
    CategoryResponse,
    CategoryCreate,
    CategoryUpdate,
)
from app.services.category_service import get_category_service, CategoryService

router = APIRouter()


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать категорию",
)
async def create_category(
        category_data: CategoryCreate,
        service: CategoryService = Depends(get_category_service),
):
    res = await service.add_category(category_data)
    return res


@router.get(
    "/",
    response_model=List[CategoryResponse],
    summary="Получить все категории",
)
async def get_all_categories(
        skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
        limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
        service: CategoryService = Depends(get_category_service),
):
    """
    Получить список всех категорий с пагинацией
    """
    categories = await service.get_all(skip=skip, limit=limit)
    return categories


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Получить категорию по ID",
)
async def get_category(
        category_id: str, service: CategoryService = Depends(get_category_service)
):
    try:
        category_uuid = uuid_lib.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    category = await service.get_by_id(category_uuid)

    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Обновить категорию",
)
async def update_category(
        category_id: str,
        update_data: CategoryUpdate,
        service: CategoryService = Depends(get_category_service),
):
    try:
        category_uuid = uuid_lib.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    category = await service.update(category_uuid, update_data)

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить категорию",
)
async def delete_category(
        category_id: str, service: CategoryService = Depends(get_category_service)
):
    try:
        category_uuid = uuid_lib.UUID(category_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    await service.delete(category_uuid)


@router.get(
    "/search/",
    response_model=List[CategoryResponse],
    summary="Поиск категорий по имени",
)
async def search_categories(
        name: str = Query(..., description="Шаблон для поиска по имени"),
        skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
        limit: int = Query(100, ge=1, le=1000, description="Лимит записей"),
        service: CategoryService = Depends(get_category_service),
):
    categories = await service.search_by_name(name=name, skip=skip, limit=limit)
    return categories


@router.get("/check/{name}", summary="Проверить существование категории по имени")
async def check_category_exists(
        name: str, service: CategoryService = Depends(get_category_service)
):
    exists = await service.check_name(name)
    return {"exists": exists}
