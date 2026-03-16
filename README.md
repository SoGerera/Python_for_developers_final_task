
# Медиа-хранилище 🖼️📱

**Современная социальная платформа** для публикации, просмотра и совместного использования изображений и видео.


## ✨ Основные возможности

## Основные функции
- Основная лента с публикациями пользователей 
- Создание, изменение и удаление собственных публикаций
- Аутентификация и регистрация пользователей на основе JWT-токенов
- Управление категориями записей
- Возможность комментирования публикаций
- Функционал подписок на других пользователей
- Поиск и фильтрация записей по различным критериям

## 🛠 Технологический стек

```
Python 3.13 -  FastAPI -  SQLAlchemy 2.0 -  Pydantic -  PostgreSQL 15
Alembic -  Pytest (49 тестов) -  Docker -  Poetry
```

## 🚀 Быстрый запуск

### Docker (рекомендуется) — **1 команда**
```bash
git clone <repo> && cd Final-task
docker-compose up --build
```

✅ **Готово!**  
🎯 API: http://localhost:8000  
📚 Документация: http://localhost:8000/api/docs  
📖 ReDoc: http://localhost:8000/api/redoc  

**Остановка**: `docker-compose down` | **Очистка**: `docker-compose down -v`

### Локально (разработка)
```bash
poetry install
# Настроить PostgreSQL + settings.toml
poetry run alembic upgrade head
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 🧪 Тестирование (49 тестов)

```bash
# Docker
docker-compose exec app poetry run pytest -v

# Локально  
poetry run pytest -v  # ~40с, 49 passed
poetry run pytest --cov=src  # Покрытие кода
```

**Результат**:
```
collected 49 items ✓
49 passed in 40s
```

## 📁 Структура проекта

```
├── src/app/          # FastAPI приложение
│   ├── api/v1/       # REST эндпоинты
│   ├── models/       # SQLAlchemy модели
│   ├── schemas/      # Pydantic схемы
│   ├── repositories/ # Репозитории БД
│   └── services/     # Бизнес-логика
├── tests/            # Pytest тесты (auth, posts, comments...)
├── alembic/          # Миграции БД
├── docker-compose.yml
└── pyproject.toml    # Poetry зависимости
```

## 🔌 Ключевые API

| Группа | Базовый путь | Основные методы |
|--------|--------------|-----------------|
| **Auth** | `/api/v1/auth` | `POST /register`, `/login`, `/refresh` |
| **Posts** | `/api/v1/posts` | `GET/POST /`, `GET/{id}`, `POST /search` |
| **Comments** | `/api/v1/comments` | `POST /`, `GET /post/{id}` |
| **Subscribe** | `/api/v1/subscribe` | `POST/DELETE /{user_id}` |

### 💡 Быстрый старт через Swagger
1. Откройте http://localhost:8000/api/docs
2. **Authorize** → `Bearer <access_token>`
3. Тестируйте все эндпоинты в браузере!

### 📤 Пример curl
```bash
# 1. Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"Иван","last_name":"Иванов","username":"user","password":"pass123"}'

# 2. Создать пост
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"caption":"Мой пост","media_id":"media_123"}'
```

## 🗄 Модели БД (PostgreSQL)

```
users → posts → media
     ↘ comments
     ↘ subscriptions
     ↘ refresh_tokens
categories ← posts
```

- ✅ Асинхронный FastAPI + asyncpg
- ✅ Типизация (Pydantic v2)
- ✅ 49 тестов (валидация + БД + авторизация)
- ✅ Автодокументация (Swagger + ReDoc)
- ✅ Docker multi-stage
- ✅ Миграции Alembic
