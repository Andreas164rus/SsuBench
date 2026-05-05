# SsuBench FastAPI

REST API платформа для размещения заданий, откликов исполнителей и перевода виртуальных баллов.

## Стек

- Python 3.13
- FastAPI
- SQLAlchemy (async)
- Alembic
- PostgreSQL
- Docker Compose
- JWT (FastAPI Users)
- bcrypt / argon2

## Архитектура

Проект построен на многослойной архитектуре:

- `app/api/` — маршруты и эндпоинты (контроллеры)
- `app/services/` — бизнес-логика
- `app/crud/` — слой доступа к данным (CRUD операции)
- `app/models/` — SQLAlchemy модели
- `app/schemas/` — Pydantic схемы (валидация)
- `app/core/` — конфигурация, зависимости, утилиты

### Основные модули

| Модуль | Назначение |
|--------|-----------|
| `app.api.routers.auth` | Аутентификация и регистрация (FastAPI Users) |
| `app.api.routers.users` | Управление пользователями (админ и профиль) |
| `app.api.routers.tasks` | CRUD задач, отклики, завершение |
| `app.api.routers.bids` | Отклики исполнителей |
| `app.api.routers.payments` | Платежи и баланс |
| `app.services` | Бизнес-логика (выбор исполнителя, платежи) |
| `app.crud` | Базовые операции с БД |

## Роли и права

| Роль | Доступ |
|------|--------|
| **Заказчик** | Создание задач, выбор исполнителя, подтверждение выполнения, оплата |
| **Исполнитель** | Отклик на задачи, отметка выполнения, просмотр своих задач |
| **Администратор** | Просмотр всех пользователей, удаление/деактивация пользователей |

## Конфигурация окружения (`.env`)

Файл `.env` содержит все переменные окружения для запуска приложения.

## Переменные окружения

### PostgreSQL (для Docker)

| Переменная | Значение | Описание |
|------------|----------|----------|
| `POSTGRES_USER` | `postgres` | Имя пользователя БД |
| `POSTGRES_PASSWORD` | `postgres` | Пароль пользователя БД |
| `POSTGRES_DB` | `fastapi_db` | Название базы данных |
| `POSTGRES_HOST` | `db` | Хост БД (имя сервиса в Docker) |
| `POSTGRES_PORT` | `5432` | Порт PostgreSQL |

### Подключение к БД

| Переменная | Значение | Описание |
|------------|----------|----------|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@db:5432/fastapi_db` | URL для подключения к PostgreSQL (в Docker) |

**Для локальной разработки (SQLite):**  
Раскомментируйте строку ниже:

``` DATABASE_URL=sqlite+aiosqlite:///./fastapi.db```


## Запуск проекта

### Ручной запуск (venv)

```bash
# Клонирование репозитория
git clone <repo-url>
cd FastApiBase

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка окружения
cp .env.example .env
# Отредактируйте .env под ваши параметры

# Применение миграций
alembic upgrade head

# Запуск сервера
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### docker
```
cp .env.example .env

# Запуск контейнеров
docker-compose up --build

# Фоновый режим
docker-compose up -d --build

# Остановка
docker-compose down

# Остановка с удалением томов
docker-compose down -v
```

## Примеры запросов

### Регистрация и получение токенов
```
# Регистрация заказчика
curl -X POST "$BASE_URL/auth/register" \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "customer@example.com",
    "first_name": "Иван",
    "last_name": "Петров",
    "password": "password123",
    "role_id": 1
  }'

# Регистрация исполнителя
curl -X POST "$BASE_URL/auth/register" \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "executor@example.com", 
    "first_name": "Петр",
    "last_name": "Иванов",
    "password": "password123",
    "role_id": 2
  }'

# Вход (получение токена)
curl -X POST "$BASE_URL/auth/jwt/login" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d "username=customer@example.com&password=password123"

```
### Работа с задачами

```
# Создание задачи
curl -X POST "$BASE_URL/task/create/" \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "Разработка API",
    "description": "Нужно создать REST API на FastAPI",
    "price": 100
  }'

# Получение списка задач
curl -X GET "$BASE_URL/task/all/?page=1&size=10" \
  -H "Authorization: Bearer $TOKEN"

# Отклик на задачу
curl -X POST "$BASE_URL/bid/1/response/" \
  -H "Authorization: Bearer $EXECUTOR_TOKEN"
```

## Тесты

Запуск тестов производится из папки ```backend``` слеудющей командой: ```pytest tests/test_tasks.py -v ```
