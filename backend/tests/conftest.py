import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.core.db import get_async_session, Base
from fastapi_users.password import PasswordHelper
from passlib.context import CryptContext
from app.models.user import User
from app.models.role import Role

context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")
password_helper = PasswordHelper(context)

# Тестовая async БД
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)


async def override_get_db():
    async with AsyncSession(engine) as session:
        yield session


app.dependency_overrides[get_async_session] = override_get_db


@pytest.fixture(autouse=True, scope="function")
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine) as session:
        roles_data = [Role(name="customer"), Role(name="executor"), Role(name="admin")]
        session.add_all(roles_data)
        admin = User(
            username="admin",
            first_name="Admin",
            last_name="Adminov",
            hashed_password=password_helper.hash("admpass"),
            role_id=3,  # admin
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        customer_first = User(
            username="customer_first",
            first_name="cus",
            last_name="tomer",
            hashed_password=password_helper.hash("customer_1"),
            role_id=1,
            is_active=True,
            is_superuser=True,
            balance=100,
        )
        session.add(customer_first)
        customer_second = User(
            username="customer_second",
            first_name="cus2",
            last_name="tomer2",
            hashed_password=password_helper.hash("customer_2"),
            role_id=1,
            is_active=True,
            is_superuser=True,
            balance=100,
        )
        session.add(customer_second)
        executor_first = User(
            username="executor_first",
            first_name="exe",
            last_name="cutor",
            hashed_password=password_helper.hash("executor_first"),
            role_id=2,
            is_active=True,
            is_superuser=True,
        )
        session.add(executor_first)
        executor_second = User(
            username="executor_second",
            first_name="exe2",
            last_name="cutor2",
            hashed_password=password_helper.hash("executor_second"),
            role_id=2,
            is_active=True,
            is_superuser=True,
        )
        session.add(executor_second)

        await session.commit()
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture()
async def admin_token():
    """Возвращает токен админа"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/auth/jwt/login", data={"username": "admin", "password": "admpass"}
        )
        return response.json()["access_token"]


@pytest.fixture()
async def customer_first_token():
    """Возвращает токен первого заказчика"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "customer_first", "password": "customer_1"},
        )
        return response.json()["access_token"]


@pytest.fixture()
async def customer_second_token():
    """Возвращает токен второго заказчика"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "customer_second", "password": "customer_2"},
        )
        return response.json()["access_token"]


@pytest.fixture()
async def executor_first_token():
    """Возвращает токен первого исполнителя"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "executor_first", "password": "executor_first"},
        )
        return response.json()["access_token"]


@pytest.fixture()
async def executor_second_token():
    """Возвращает токен второго исполнителя"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/auth/jwt/login",
            data={"username": "executor_second", "password": "executor_second"},
        )
        return response.json()["access_token"]


@pytest.fixture
async def created_task(customer_first_token, client):
    """Создает задачу и возвращает ее"""
    response = await client.post(
        "/task/create/",
        json={"title": "Test Task", "description": "Desc", "price": 50},
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    return response.json()


@pytest.fixture
async def created_task_too_expensive(customer_first_token, client):
    """Создает задачу и возвращает ее"""
    response = await client.post(
        "/task/create/",
        json={"title": "Test Task", "description": "Desc", "price": 5000},
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    return response.json()


@pytest.fixture
async def response_for_task(created_task, executor_first_token, client):
    """Отклик на задачу и возвращает отклик"""
    response = await client.post(
        f"/bid/{created_task['id']}/response/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )
    return response.json()


@pytest.fixture
async def response_for_task_by_second_executor(
    created_task, executor_second_token, client
):
    """Отклик на задачу и возвращает отклик"""
    response = await client.post(
        f"/bid/{created_task['id']}/response/",
        headers={"Authorization": f"Bearer {executor_second_token}"},
    )
    return response.json()


@pytest.fixture
async def selected_executor_for_a_task(
    created_task, response_for_task, customer_first_token, client
):
    """возврщает задачу, в которой выбран исполнитель"""
    response = await client.post(
        f"/task/{created_task['id']}/user/{4}/",
        headers={"Authorization": f"Bearer {customer_first_token}"},
    )
    return response.json()


@pytest.fixture
async def done_executor_task(
    created_task,
    response_for_task,
    customer_first_token,
    executor_first_token,
    selected_executor_for_a_task,
    client,
):
    """Возвращет задачу, в который исполнитель завершил работу"""
    response = await client.post(
        f"/task/done_task_executor/{created_task['id']}/",
        headers={"Authorization": f"Bearer {executor_first_token}"},
    )

    return response.json()


@pytest.fixture
async def created_some_task(customer_first_token, client):
    """Создает несколько задач"""
    tasks = []
    for k in range(5):
        response = await client.post(
            "/task/create/",
            json={
                "title": f"Test Task{k + 1}",
                "description": "Desc",
                "price": (k + 1) * 2,
            },
            headers={"Authorization": f"Bearer {customer_first_token}"},
        )
        tasks.append(response.json())
    return tasks
