"""Тесты для работы с категориями"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(auth_client: tuple):
    """Тест создания категории"""
    client, _ = auth_client

    response = await client.post("/api/v1/category/", json={
        "name": "Travel",
        "desc": "Travel photos and videos"
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Travel"
    assert data["desc"] == "Travel photos and videos"


@pytest.mark.asyncio
async def test_create_duplicate_category(auth_client: tuple):
    """Тест создания дубликата категории"""
    client, _ = auth_client

    await client.post("/api/v1/category/", json={
        "name": "Nature",
        "desc": "Nature content"
    })

    response = await client.post("/api/v1/category/", json={
        "name": "Nature",
        "desc": "Another nature content"
    })
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_all_categories(auth_client: tuple):
    """Тест получения всех категорий"""
    client, _ = auth_client

    await client.post("/api/v1/category/", json={"name": "Sports", "desc": "Sports"})
    await client.post("/api/v1/category/", json={"name": "Music", "desc": "Music"})

    response = await client.get("/api/v1/category/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_get_category_by_id(auth_client: tuple):
    """Тест получения категории по ID"""
    client, _ = auth_client

    create_response = await client.post("/api/v1/category/", json={
        "name": "Food",
        "desc": "Food content"
    })
    category_uuid = create_response.json()["uuid"]

    response = await client.get(f"/api/v1/category/{category_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Food"


@pytest.mark.asyncio
async def test_update_category(auth_client: tuple):
    """Тест обновления категории"""
    client, _ = auth_client

    create_response = await client.post("/api/v1/category/", json={
        "name": "Tech",
        "desc": "Technology"
    })
    category_uuid = create_response.json()["uuid"]

    response = await client.put(f"/api/v1/category/{category_uuid}", json={
        "name": "Technology",
        "desc": "All about technology"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Technology"
    assert data["desc"] == "All about technology"


@pytest.mark.asyncio
async def test_delete_category(auth_client: tuple):
    """Тест удаления категории"""
    client, _ = auth_client

    create_response = await client.post("/api/v1/category/", json={
        "name": "ToDelete",
        "desc": "Will be deleted"
    })
    category_uuid = create_response.json()["uuid"]
    ю
    response = await client.delete(f"/api/v1/category/{category_uuid}")
    assert response.status_code == 204

    get_response = await client.get(f"/api/v1/category/{category_uuid}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_assign_category_to_post(auth_client: tuple):
    """Тест назначения категории посту"""
    client, _ = auth_client

    category_response = await client.post("/api/v1/category/", json={
        "name": "Art",
        "desc": "Art content"
    })
    category_uuid = category_response.json()["uuid"]

    post_response = await client.post("/api/v1/posts/", json={
        "caption": "Art post",
        "media_id": "art_media"
    })
    post_uuid = post_response.json()["uuid"]

    response = await client.patch(
        f"/api/v1/posts/{post_uuid}/assign-category",
        params={"category_id": category_uuid}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == category_uuid


@pytest.mark.asyncio
async def test_filter_posts_by_category(auth_client: tuple):
    """Тест фильтрации постов по категории"""
    client, _ = auth_client

    category_response = await client.post("/api/v1/category/", json={
        "name": "Animals",
        "desc": "Animals"
    })
    category_uuid = category_response.json()["uuid"]

    post_response = await client.post("/api/v1/posts/", json={
        "caption": "Animal post",
        "media_id": "animal_media"
    })
    post_uuid = post_response.json()["uuid"]

    await client.patch(
        f"/api/v1/posts/{post_uuid}/assign-category",
        params={"category_id": category_uuid}
    )

    response = await client.get(f"/api/v1/posts/?category_id={category_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert data["posts"][0]["category_id"] == category_uuid
