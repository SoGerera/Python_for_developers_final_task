"""Тесты для аутентификации и авторизации"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient):
    """Тест регистрации нового пользователя"""
    response = await client.post("/api/v1/auth/register", json={
        "first_name": "Ivan",
        "last_name": "Ivanov",
        "username": "ivan_test",
        "password": "secure123456"
    })
    assert response.status_code == 201
    assert response.json()["message"] == "User registered"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    """Тест регистрации с существующим username"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "duplicate_user",
        "password": "password123"
    }

    response1 = await client.post("/api/v1/auth/register", json=user_data)
    assert response1.status_code == 201

    response2 = await client.post("/api/v1/auth/register", json=user_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_data(client: AsyncClient):
    """Тест регистрации с невалидными данными"""
    response = await client.post("/api/v1/auth/register", json={
        "first_name": "Test",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Тест успешного логина"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "username": "test_login",
        "password": "password123"
    })

    response = await client.post("/api/v1/auth/login", data={
        "username": "test_login",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    """Тест логина с неправильным паролем"""
    await client.post("/api/v1/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "username": "test_wrong_pass",
        "password": "correctpassword"
    })

    response = await client.post("/api/v1/auth/login", data={
        "username": "test_wrong_pass",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    """Тест логина несуществующего пользователя"""
    response = await client.post("/api/v1/auth/login", data={
        "username": "nonexistent",
        "password": "password123"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Тест обновления токена"""
    # Регистрация и логин
    await client.post("/api/v1/auth/register", json={
        "first_name": "Test",
        "last_name": "User",
        "username": "test_refresh",
        "password": "password123"
    })

    login_response = await client.post("/api/v1/auth/login", data={
        "username": "test_refresh",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh", params={"token": refresh_token})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(client: AsyncClient):
    """Тест обновления с невалидным токеном"""
    response = await client.post("/api/v1/auth/refresh", params={"token": "invalid_token"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_change_password_success(auth_client: tuple):
    """Тест успешной смены пароля"""
    client, user_data = auth_client

    response = await client.post("/api/v1/auth/change-password", json={
        "old_password": user_data["password"],
        "new_password": "newpassword123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated"

    del client.headers["Authorization"]
    login_response = await client.post("/api/v1/auth/login", data={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 401

    login_response = await client.post("/api/v1/auth/login", data={
        "username": user_data["username"],
        "password": "newpassword123"
    })
    assert login_response.status_code == 200


@pytest.mark.asyncio
async def test_change_password_wrong_old(auth_client: tuple):
    """Тест смены пароля с неправильным старым паролем"""
    client, _ = auth_client

    response = await client.post("/api/v1/auth/change-password", json={
        "old_password": "wrongpassword",
        "new_password": "newpassword123"
    })
    assert response.status_code == 400
    assert "invalid old password" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_change_password_too_short(auth_client: tuple):
    """Тест смены пароля на слишком короткий"""
    client, user_data = auth_client

    response = await client.post("/api/v1/auth/change-password", json={
        "old_password": user_data["password"],
        "new_password": "short"
    })
    assert response.status_code == 400
    assert "at least 8 characters" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client: AsyncClient):
    """Тест доступа к защищенному эндпоинту без токена"""
    response = await client.post("/api/v1/auth/change-password", json={
        "old_password": "test",
        "new_password": "test1234"
    })
    assert response.status_code == 401
