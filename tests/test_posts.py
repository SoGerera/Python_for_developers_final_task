"""Тесты для работы с постами"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_post_success(auth_client: tuple):
    """Тест успешного создания поста"""
    client, _ = auth_client
    
    response = await client.post("/api/v1/posts/", json={
        "caption": "My first post",
        "media_id": "test_media_001"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["caption"] == "My first post"
    assert "uuid" in data


@pytest.mark.asyncio
async def test_create_post_without_auth(client: AsyncClient):
    """Тест создания поста без авторизации"""
    response = await client.post("/api/v1/posts/", json={
        "caption": "Test post",
        "media_id": "test_media_002"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_posts(auth_client: tuple):
    """Тест получения всех постов"""
    client, _ = auth_client
    
    # Создаем несколько постов
    await client.post("/api/v1/posts/", json={"caption": "Post 1", "media_id": "media_1"})
    await client.post("/api/v1/posts/", json={"caption": "Post 2", "media_id": "media_2"})
    await client.post("/api/v1/posts/", json={"caption": "Post 3", "media_id": "media_3"})
    
    # Получаем все посты
    response = await client.get("/api/v1/posts/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3
    assert len(data["posts"]) >= 3


@pytest.mark.asyncio
async def test_get_posts_with_pagination(auth_client: tuple):
    """Тест пагинации постов"""
    client, _ = auth_client
    
    # Создаем 5 постов
    for i in range(5):
        await client.post("/api/v1/posts/", json={
            "caption": f"Post {i}",
            "media_id": f"media_{i}"
        })
    
    # Получаем первую страницу (2 элемента)
    response = await client.get("/api/v1/posts/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["posts"]) == 2
    assert data["limit"] == 2
    assert data["skip"] == 0


@pytest.mark.asyncio
async def test_get_post_by_id(auth_client: tuple):
    """Тест получения поста по ID"""
    client, _ = auth_client
    
    # Создаем пост
    create_response = await client.post("/api/v1/posts/", json={
        "caption": "Test post",
        "media_id": "test_media"
    })
    post_uuid = create_response.json()["uuid"]
    
    # Получаем пост по ID
    response = await client.get(f"/api/v1/posts/{post_uuid}")
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == post_uuid
    assert data["caption"] == "Test post"


@pytest.mark.asyncio
async def test_get_nonexistent_post(auth_client: tuple):
    """Тест получения несуществующего поста"""
    client, _ = auth_client
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = await client.get(f"/api/v1/posts/{fake_uuid}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_own_post(auth_client: tuple):
    """Тест обновления своего поста"""
    client, _ = auth_client
    
    # Создаем пост
    create_response = await client.post("/api/v1/posts/", json={
        "caption": "Original caption",
        "media_id": "test_media"
    })
    post_uuid = create_response.json()["uuid"]
    
    # Обновляем пост
    response = await client.put(f"/api/v1/posts/{post_uuid}", json={
        "caption": "Updated caption"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["caption"] == "Updated caption"


@pytest.mark.asyncio
async def test_update_nonexistent_post(auth_client: tuple):
    """Тест обновления несуществующего поста"""
    client, _ = auth_client
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = await client.put(f"/api/v1/posts/{fake_uuid}", json={
        "caption": "Updated"
    })
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_own_post(auth_client: tuple):
    """Тест удаления своего поста"""
    client, _ = auth_client
    
    # Создаем пост
    create_response = await client.post("/api/v1/posts/", json={
        "caption": "To be deleted",
        "media_id": "test_media"
    })
    post_uuid = create_response.json()["uuid"]
    
    # Удаляем пост
    response = await client.delete(f"/api/v1/posts/{post_uuid}")
    assert response.status_code == 204
    
    # Проверяем, что пост удален
    get_response = await client.get(f"/api/v1/posts/{post_uuid}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_post(auth_client: tuple):
    """Тест удаления несуществующего поста"""
    client, _ = auth_client
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    
    response = await client.delete(f"/api/v1/posts/{fake_uuid}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_filter_posts_by_user(client: AsyncClient):
    """Тест фильтрации постов по пользователю"""
    # Создаем двух пользователей
    await client.post("/api/v1/auth/register", json={
        "first_name": "User1",
        "last_name": "Test",
        "username": "user1",
        "password": "password123"
    })
    
    await client.post("/api/v1/auth/register", json={
        "first_name": "User2",
        "last_name": "Test",
        "username": "user2",
        "password": "password123"
    })
    
    # Логинимся как user1 и создаем пост
    login1 = await client.post("/api/v1/auth/login", data={
        "username": "user1",
        "password": "password123"
    })
    token1 = login1.json()["access_token"]
    
    response1 = await client.post("/api/v1/posts/", 
        json={"caption": "User1 post", "media_id": "media1"},
        headers={"Authorization": f"Bearer {token1}"}
    )
    user1_id = response1.json()["user_id"]
    
    # Логинимся как user2 и создаем пост
    login2 = await client.post("/api/v1/auth/login", data={
        "username": "user2",
        "password": "password123"
    })
    token2 = login2.json()["access_token"]
    
    await client.post("/api/v1/posts/",
        json={"caption": "User2 post", "media_id": "media2"},
        headers={"Authorization": f"Bearer {token2}"}
    )
    
    # Фильтруем посты по user1
    response = await client.get(f"/api/v1/posts/?user_id={user1_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["posts"][0]["user_id"] == user1_id


@pytest.mark.asyncio
async def test_get_posts_count(auth_client: tuple):
    """Тест получения количества постов"""
    client, _ = auth_client
    
    # Создаем несколько постов
    for i in range(3):
        await client.post("/api/v1/posts/", json={
            "caption": f"Post {i}",
            "media_id": f"media_{i}"
        })
    
    # Получаем количество
    response = await client.get("/api/v1/posts/stats/count")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 3


@pytest.mark.asyncio
async def test_create_post_with_invalid_data(auth_client: tuple):
    """Тест создания поста с невалидными данными"""
    client, _ = auth_client
    
    # Пост без обязательного поля media_id
    response = await client.post("/api/v1/posts/", json={
        "caption": "Test"
    })
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_create_duplicate_media_id(auth_client: tuple):
    """Тест создания поста с существующим media_id"""
    client, _ = auth_client
    
    # Создаем первый пост
    await client.post("/api/v1/posts/", json={
        "caption": "First post",
        "media_id": "duplicate_media"
    })
    
    # Пытаемся создать второй с тем же media_id
    response = await client.post("/api/v1/posts/", json={
        "caption": "Second post",
        "media_id": "duplicate_media"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()
