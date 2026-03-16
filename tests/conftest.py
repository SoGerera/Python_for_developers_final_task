"""Конфигурация для pytest с тестовой базой данных"""
import asyncio
import sys
from pathlib import Path
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

TEST_DB_PATH = Path(__file__).parent / "test.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

from app.models.base import Base

import app.models.user
import app.models.post
import app.models.category
import app.models.comment
import app.models.media
import app.models.subscription
import app.models.refresh_token

from app.main import app
from app.database import get_session

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
    echo=False
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_db():
    """Создаем и очищаем таблицы для каждого теста"""
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from app.api.v1.post_api import _media_id_cache
    _media_id_cache.clear()

    yield

    await test_engine.dispose()
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest_asyncio.fixture
async def db_session(setup_db) -> AsyncGenerator[AsyncSession, None]:
    """Создает тестовую сессию БД для каждого теста"""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Создает тестовый HTTP клиент с переопределенной зависимостью БД"""

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    # Создаем клиент
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient) -> AsyncGenerator[tuple[AsyncClient, dict], None]:
    """Создает авторизованный клиент с токеном"""
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "password": "testpassword123"
    }

    await client.post("/api/v1/auth/register", json=user_data)

    # Логинимся
    login_response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": user_data["username"],
            "password": user_data["password"]
        }
    )

    token_data = login_response.json()
    token = token_data["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

    yield client, user_data

    if "Authorization" in client.headers:
        del client.headers["Authorization"]
