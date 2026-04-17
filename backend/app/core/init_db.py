from app.crud.role import role_crud
from app.models.role import Role
import contextlib
from app.core.config import settings
from app.core.db import get_async_session
from app.core.user import get_user_db, get_user_manager
from app.schemas.user import UserCreate
from fastapi_users.exceptions import UserAlreadyExists
from datetime import datetime

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_user(
    username: str,
    first_name: str,
    last_name: str,
    password: str,
):
    try:
        # Получение объекта асинхронной сессии.
        async with get_async_session_context() as session:
            # Получение объекта класса SQLAlchemyUserDatabase.
            async with get_user_db_context(session) as user_db:
                # Получение объекта класса UserManager.
                async with get_user_manager_context(user_db) as user_manager:
                    # Создание пользователя.
                    await user_manager.create(
                        UserCreate(
                            username=username,
                            is_superuser=True,
                            first_name=first_name,
                            last_name=last_name,
                            password=password,
                        )
                    )
    # В случае, если такой пользователь уже есть, ничего не предпринимать.
    except UserAlreadyExists:
        pass


# Корутина, проверяющая, указаны ли в настройках данные для суперюзера.
# Если да, то вызывается корутина create_user для создания суперпользователя.
async def create_superusers():
    if settings.username_admin is not None and settings.password_admin is not None:
        await create_user(
            settings.username_admin,
            settings.first_name_admin,
            settings.last_name_admin,
            settings.password_admin,
        )


async def create_roles():
    objs = [
        {"name": "Заказчик"},
        {"name": "Исполнитель"},
        {"name": "Админ"},
    ]
    async with get_async_session_context() as session:
        for obj in objs:
            exiting_obj = await role_crud.get_by_name(obj.get("name"), session)
            if exiting_obj is None:
                db_obj = Role(**obj)
                session.add(db_obj)
        await session.commit()
