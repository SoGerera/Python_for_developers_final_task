"""Тесты для работы с подписками"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_subscribe_to_user(client: AsyncClient):
    """Тест подписки на пользователя"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "User1",
        "last_name": "Test",
        "username": "subscriber",
        "password": "password123"
    })

    await client.post("/api/v1/auth/register", json={
        "first_name": "User2",
        "last_name": "Test",
        "username": "target_user",
        "password": "password123"
    })

    login_response = await client.post("/api/v1/auth/login", data={
        "username": "subscriber",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/subscribe/target_user",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 201]


@pytest.mark.asyncio
async def test_subscribe_without_auth(client: AsyncClient):
    """Тест подписки без авторизации"""
    response = await client.post("/api/v1/subscribe/someuser")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unsubscribe_from_user(client: AsyncClient):
    """Тест отписки от пользователя"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "User1",
        "last_name": "Test",
        "username": "follower",
        "password": "password123"
    })

    await client.post("/api/v1/auth/register", json={
        "first_name": "User2",
        "last_name": "Test",
        "username": "followed",
        "password": "password123"
    })

    login_response = await client.post("/api/v1/auth/login", data={
        "username": "follower",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    await client.post(
        "/api/v1/subscribe/followed",
        headers={"Authorization": f"Bearer {token}"}
    )

    response = await client.delete(
        "/api/v1/subscribe/followed",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [200, 204]


@pytest.mark.asyncio
async def test_get_user_followers(client: AsyncClient):
    """Тест получения подписчиков пользователя"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "Popular",
        "last_name": "User",
        "username": "popular_user",
        "password": "password123"
    })

    login_response = await client.post("/api/v1/auth/login", data={
        "username": "popular_user",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/subscribe/followers",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_user_following(client: AsyncClient):
    """Тест получения подписок пользователя"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "Active",
        "last_name": "User",
        "username": "active_user",
        "password": "password123"
    })

    login_response = await client.post("/api/v1/auth/login", data={
        "username": "active_user",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = await client.get(
        "/api/v1/subscribe/following",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cannot_subscribe_to_self(client: AsyncClient):
    """Тест подписки на самого себя"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "username": "self_subscriber",
        "password": "password123"
    })

    login_response = await client.post("/api/v1/auth/login", data={
        "username": "self_subscriber",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = await client.post(
        "/api/v1/subscribe/self_subscriber",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in [400, 403]


@pytest.mark.asyncio
async def test_double_subscribe(client: AsyncClient):
    """Тест двойной подписки"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "User1",
        "last_name": "Test",
        "username": "double_sub",
        "password": "password123"
    })

    await client.post("/api/v1/auth/register", json={
        "first_name": "User2",
        "last_name": "Test",
        "username": "target_double",
        "password": "password123"
    })

    login_response = await client.post("/api/v1/auth/login", data={
        "username": "double_sub",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response1 = await client.post(
        "/api/v1/subscribe/target_double",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response1.status_code in [200, 201]

    response2 = await client.post(
        "/api/v1/subscribe/target_double",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response2.status_code in [200, 201, 400]
