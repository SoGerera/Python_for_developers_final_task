"""Тесты для работы с комментариями"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_comment(auth_client: tuple):
    """Тест создания комментария"""
    client, _ = auth_client
    
    # Создаем пост
    post_response = await client.post("/api/v1/posts/", json={
        "caption": "Test post",
        "media_id": "test_media"
    })
    post_uuid = post_response.json()["uuid"]
    
    # Создаем комментарий
    response = await client.post("/api/v1/comments/", json={
        "post_id": post_uuid,
        "text": "Great post!"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Great post!"
    assert data["post_id"] == post_uuid


@pytest.mark.asyncio
async def test_create_comment_without_auth(client: AsyncClient):
    """Тест создания комментария без авторизации"""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = await client.post("/api/v1/comments/", json={
        "post_id": fake_uuid,
        "text": "Comment"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_comment_to_nonexistent_post(auth_client: tuple):
    """Тест создания комментария к несуществующему посту"""
    client, _ = auth_client
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = await client.post("/api/v1/comments/", json={
        "post_id": fake_uuid,
        "text": "Comment"
    })
    assert response.status_code in [404, 400]  # В зависимости от реализации


@pytest.mark.asyncio
async def test_get_comments_for_post(auth_client: tuple):
    """Тест получения комментариев для поста"""
    client, _ = auth_client
    
    # Создаем пост
    post_response = await client.post("/api/v1/posts/", json={
        "caption": "Test post",
        "media_id": "test_media"
    })
    post_uuid = post_response.json()["uuid"]
    
    # Создаем несколько комментариев
    await client.post("/api/v1/comments/", json={
        "post_id": post_uuid,
        "text": "Comment 1"
    })
    await client.post("/api/v1/comments/", json={
        "post_id": post_uuid,
        "text": "Comment 2"
    })
    
    # Получаем комментарии
    response = await client.get(f"/api/v1/comments/post/{post_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


@pytest.mark.asyncio
async def test_update_own_comment(auth_client: tuple):
    """Тест обновления своего комментария"""
    client, _ = auth_client
    
    # Создаем пост
    post_response = await client.post("/api/v1/posts/", json={
        "caption": "Test post",
        "media_id": "test_media"
    })
    post_uuid = post_response.json()["uuid"]
    
    # Создаем комментарий
    comment_response = await client.post("/api/v1/comments/", json={
        "post_id": post_uuid,
        "text": "Original comment"
    })
    comment_uuid = comment_response.json()["uuid"]
    
    # Обновляем комментарий
    response = await client.put(f"/api/v1/comments/{comment_uuid}", json={
        "text": "Updated comment"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["text"] == "Updated comment"


@pytest.mark.asyncio
async def test_delete_own_comment(auth_client: tuple):
    """Тест удаления своего комментария"""
    client, _ = auth_client
    
    # Создаем пост
    post_response = await client.post("/api/v1/posts/", json={
        "caption": "Test post",
        "media_id": "test_media"
    })
    post_uuid = post_response.json()["uuid"]
    
    # Создаем комментарий
    comment_response = await client.post("/api/v1/comments/", json={
        "post_id": post_uuid,
        "text": "To be deleted"
    })
    comment_uuid = comment_response.json()["uuid"]
    
    # Удаляем комментарий
    response = await client.delete(f"/api/v1/comments/{comment_uuid}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_create_comment_with_empty_text(auth_client: tuple):
    """Тест создания комментария с пустым текстом"""
    client, _ = auth_client
    
    # Создаем пост
    post_response = await client.post("/api/v1/posts/", json={
        "caption": "Test post",
        "media_id": "test_media"
    })
    post_uuid = post_response.json()["uuid"]
    
    # Пытаемся создать комментарий с пустым текстом
    response = await client.post("/api/v1/comments/", json={
        "post_id": post_uuid,
        "text": ""
    })
    # В зависимости от валидации может быть 400 или 422
    assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_get_comments_for_nonexistent_post(auth_client: tuple):
    """Тест получения комментариев для несуществующего поста"""
    client, _ = auth_client
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = await client.get(f"/api/v1/comments/post/{fake_uuid}")
    # Может вернуть 404 или пустой список в зависимости от реализации
    assert response.status_code in [200, 404]
    if response.status_code == 200:
        assert len(response.json()) == 0
